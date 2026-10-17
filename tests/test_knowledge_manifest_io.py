"""Credential boundaries using synthetic tokens and in-memory HTTP responses."""

from __future__ import annotations

import io
import json
import os
import unittest
import urllib.parse
import urllib.request
import urllib.response
from contextlib import redirect_stdout
from email.message import Message
from unittest.mock import patch

from tests.test_knowledge_manifest_ingest import load_helper


TRUSTED_URL = "https://raw.githubusercontent.com/sungjunlee/beopsuny-knowledge/main/example.yaml"
FAKE_TOKEN = "synthetic-knowledge-token"


class MemoryHTTPHandler(urllib.request.BaseHandler):
    """Replace only the transport; urllib still performs real redirect handling."""

    handler_order = 100

    def __init__(self, replies):
        self.replies = replies
        self.requests = []

    def http_open(self, request):
        self.requests.append(request)
        status, location, body = self.replies[request.full_url]
        headers = Message()
        if location is not None:
            headers["Location"] = location
        response = urllib.response.addinfourl(
            io.BytesIO(body), headers, request.full_url, status
        )
        response.msg = "synthetic response"
        return response

    https_open = http_open


class KnowledgeManifestIOTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_helper()
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def read_requests(self, source, replies):
        transport = MemoryHTTPHandler(replies)
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), transport
        )
        # An unexpected URL must fail the test, never fall back to the network.
        with patch.object(urllib.request, "urlopen", side_effect=opener.open):
            text = self.helper.read_text_source(source)
        self.assertEqual(text, "synthetic body")
        return transport.requests

    def test_trusted_https_origin_receives_preferred_token(self):
        os.environ.update(
            BEOPSUNY_KNOWLEDGE_TOKEN=FAKE_TOKEN, GITHUB_TOKEN="synthetic-fallback"
        )
        for source in (
            TRUSTED_URL,
            TRUSTED_URL.replace(".com/", ".com:443/"),
            TRUSTED_URL.replace("raw.githubusercontent.com", "RAW.GITHUBUSERCONTENT.COM"),
        ):
            with self.subTest(source=source):
                requests = self.read_requests(
                    source, {source: (200, None, b"synthetic body")}
                )
                self.assertEqual(requests[0].get_header("Authorization"), f"Bearer {FAKE_TOKEN}")
                self.assertEqual(requests[0].get_header("User-agent"), "beopsuny-knowledge-ingest")

    def test_github_token_fallback_and_anonymous_fetch(self):
        for environment, expected in (
            ({"GITHUB_TOKEN": "synthetic-fallback"}, "Bearer synthetic-fallback"),
            (
                {"BEOPSUNY_KNOWLEDGE_TOKEN": "", "GITHUB_TOKEN": "synthetic-fallback"},
                "Bearer synthetic-fallback",
            ),
            ({}, None),
        ):
            with (
                self.subTest(environment=environment),
                patch.dict(os.environ, environment, clear=True),
            ):
                requests = self.read_requests(
                    TRUSTED_URL, {TRUSTED_URL: (200, None, b"synthetic body")}
                )
                self.assertEqual(requests[0].get_header("Authorization"), expected)

    def test_other_origins_ports_and_userinfo_never_receive_token(self):
        for variable in ("BEOPSUNY_KNOWLEDGE_TOKEN", "GITHUB_TOKEN"):
            with patch.dict(os.environ, {variable: FAKE_TOKEN}, clear=True):
                for source in (
                    "http://raw.githubusercontent.com/example.yaml",
                    "http://unrelated.example/example.yaml",
                    "https://unrelated.example/example.yaml",
                    "https://api.github.com/example.yaml",
                    "https://raw.githubusercontent.com.evil.example/example.yaml",
                    "https://raw.githubusercontent.com./example.yaml",
                    "https://raw.githubusercontent.com:444/example.yaml",
                    "https://raw.githubusercontent.com:0/example.yaml",
                    "https://raw.githubusercontent.com@evil.example/example.yaml",
                    "https://user@raw.githubusercontent.com/example.yaml",
                    "https://user:password@raw.githubusercontent.com/example.yaml",
                    "https://@raw.githubusercontent.com/example.yaml",
                ):
                    with self.subTest(variable=variable, source=source):
                        requests = self.read_requests(
                            source, {source: (200, None, b"synthetic body")}
                        )
                        self.assertIsNone(requests[0].get_header("Authorization"))

    def test_malformed_ports_never_receive_token(self):
        os.environ["BEOPSUNY_KNOWLEDGE_TOKEN"] = FAKE_TOKEN
        for port in ("invalid", "65536", "-1"):
            source = f"https://raw.githubusercontent.com:{port}/example.yaml"
            with self.subTest(port=port):
                requests = self.read_requests(
                    source, {source: (200, None, b"synthetic body")}
                )
                self.assertIsNone(requests[0].get_header("Authorization"))

    def test_redirects_drop_token_including_same_origin_and_downgrade(self):
        os.environ["BEOPSUNY_KNOWLEDGE_TOKEN"] = FAKE_TOKEN
        for status in (301, 302, 303, 307, 308):
            for location in (
                "https://unrelated.example/asset.yaml",
                "http://raw.githubusercontent.com/asset.yaml",
                "https://raw.githubusercontent.com:444/asset.yaml",
                "https://raw.githubusercontent.com/asset.yaml",
                "/asset.yaml",
                "//unrelated.example/asset.yaml",
            ):
                destination = urllib.parse.urljoin(TRUSTED_URL, location)
                with self.subTest(status=status, location=location):
                    requests = self.read_requests(TRUSTED_URL, {
                        TRUSTED_URL: (status, location, b""),
                        destination: (200, None, b"synthetic body"),
                    })
                    self.assertEqual(len(requests), 2)
                    self.assertEqual(
                        requests[0].get_header("Authorization"), f"Bearer {FAKE_TOKEN}"
                    )
                    self.assertIsNone(requests[1].get_header("Authorization"))

    def test_redirect_chain_does_not_restore_token_on_return_to_trusted_origin(self):
        os.environ["GITHUB_TOKEN"] = FAKE_TOKEN
        middle = "https://unrelated.example/redirect"
        final = "https://raw.githubusercontent.com/final.yaml"
        requests = self.read_requests(TRUSTED_URL, {
            TRUSTED_URL: (302, middle, b""),
            middle: (307, final, b""),
            final: (200, None, b"synthetic body"),
        })
        self.assertEqual(len(requests), 3)
        self.assertIsNone(requests[1].get_header("Authorization"))
        self.assertIsNone(requests[2].get_header("Authorization"))

    def test_anonymous_redirect_to_trusted_origin_stays_anonymous(self):
        os.environ["GITHUB_TOKEN"] = FAKE_TOKEN
        source = "https://unrelated.example/redirect"
        requests = self.read_requests(source, {
            source: (302, TRUSTED_URL, b""),
            TRUSTED_URL: (200, None, b"synthetic body"),
        })
        self.assertTrue(all(request.get_header("Authorization") is None for request in requests))

    def test_redirect_auth_failure_keeps_skip_and_strict_exit_behavior(self):
        os.environ["BEOPSUNY_KNOWLEDGE_TOKEN"] = FAKE_TOKEN
        destination = "https://unrelated.example/private.yaml"
        for strict, expected_exit in ((False, 0), (True, 1)):
            with self.subTest(strict=strict):
                transport = MemoryHTTPHandler({
                    TRUSTED_URL: (302, destination, b""),
                    destination: (401, None, b""),
                })
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), transport)
                output = io.StringIO()
                args = ["--manifest-url", TRUSTED_URL] + (["--strict"] if strict else [])
                with (
                    patch.object(urllib.request, "urlopen", side_effect=opener.open),
                    redirect_stdout(output),
                ):
                    result = self.helper.main(args)
                packet = json.loads(output.getvalue())
                self.assertEqual(result, expected_exit)
                self.assertEqual(packet["status"], "skipped")
                self.assertTrue(packet["continue_live_legal_research"])
                self.assertIsNone(packet["injection_packet"])
                self.assertNotIn(FAKE_TOKEN, output.getvalue())
                self.assertIsNone(transport.requests[-1].get_header("Authorization"))


if __name__ == "__main__":
    unittest.main()
