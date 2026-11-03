#!/usr/bin/env python3
"""Bulk grid values/sources row order stays aligned across sort (#371).

The template's inline script is executed against the parsed report DOM.
Sorting either table must apply one row-id order to both, including when
visible names match and when a reviewer has typed into Verified.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/beopsuny/assets/templates/report_bulk_grid.html"

_VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
}
_TBODY_RE = re.compile(r"(<tbody\b[^>]*>)(.*?)(</tbody>)", re.DOTALL | re.IGNORECASE)

# DOM subset the template script actually uses. Node is the JS engine;
# the skill template itself stays self-contained and does not load this.
_NODE_HARNESS = r"""
const payload = JSON.parse(require("fs").readFileSync(0, "utf8"));

function parseSimple(selector) {
  let i = 0;
  let tag = "*";
  const classes = [];
  const attrs = [];
  if (selector[i] && selector[i] !== "." && selector[i] !== "[") {
    const match = /^[A-Za-z][A-Za-z0-9-]*/.exec(selector);
    if (!match) throw new Error("bad selector " + selector);
    tag = match[0].toUpperCase();
    i = match[0].length;
  }
  while (i < selector.length) {
    if (selector[i] === ".") {
      const match = /^[A-Za-z_-][A-Za-z0-9_-]*/.exec(selector.slice(i + 1));
      if (!match) throw new Error("bad class in " + selector);
      classes.push(match[0]);
      i += 1 + match[0].length;
    } else if (selector[i] === "[") {
      const end = selector.indexOf("]", i);
      if (end < 0) throw new Error("bad attr in " + selector);
      const body = selector.slice(i + 1, end);
      const eq = body.indexOf("=");
      if (eq === -1) attrs.push({ name: body.trim(), value: null });
      else {
        let value = body.slice(eq + 1).trim();
        if (
          (value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))
        ) {
          value = value.slice(1, -1);
        }
        attrs.push({ name: body.slice(0, eq).trim(), value });
      }
      i = end + 1;
    } else {
      throw new Error("bad selector " + selector);
    }
  }
  return { tag, classes, attrs };
}

function matches(node, simple) {
  if (!node || node.nodeType !== 1) return false;
  if (simple.tag !== "*" && node.tagName !== simple.tag) return false;
  if (simple.classes.length) {
    const classes = (node.getAttribute("class") || "").split(/\s+/).filter(Boolean);
    for (const name of simple.classes) {
      if (classes.indexOf(name) === -1) return false;
    }
  }
  for (const attr of simple.attrs) {
    const actual = node.getAttribute(attr.name);
    if (actual === null) return false;
    if (attr.value !== null && actual !== attr.value) return false;
  }
  return true;
}

function descendants(node, out) {
  for (const kid of node.childNodes || []) {
    if (kid.nodeType === 1) {
      out.push(kid);
      descendants(kid, out);
    }
  }
  return out;
}

function qsa(root, selector) {
  const parts = selector.trim().split(/\s+/).filter(Boolean).map(parseSimple);
  let level = [root];
  for (const part of parts) {
    const next = [];
    for (const node of level) {
      for (const candidate of descendants(node, [])) {
        if (matches(candidate, part)) next.push(candidate);
      }
    }
    level = next;
  }
  return level;
}

function textOf(node) {
  if (node.nodeType === 3) return node.text || "";
  let out = "";
  for (const kid of node.childNodes || []) out += textOf(kid);
  return out;
}

function build(spec, parent) {
  if (spec.type === "text") {
    return { nodeType: 3, text: spec.text, parentNode: parent, childNodes: [] };
  }
  const node = {
    nodeType: 1,
    tagName: String(spec.tag || "").toUpperCase(),
    attrs: Object.assign({}, spec.attrs || {}),
    childNodes: [],
    parentNode: parent,
    _listeners: {},
  };
  node.childNodes = (spec.children || []).map((child) => build(child, node));
  node.getAttribute = function (name) {
    if (!Object.prototype.hasOwnProperty.call(node.attrs, name)) return null;
    return String(node.attrs[name]);
  };
  node.setAttribute = function (name, value) {
    node.attrs[name] = String(value);
  };
  node.querySelectorAll = function (sel) {
    return qsa(node, sel);
  };
  node.querySelector = function (sel) {
    return qsa(node, sel)[0] || null;
  };
  node.addEventListener = function (type, fn) {
    if (!node._listeners[type]) node._listeners[type] = [];
    node._listeners[type].push(fn);
  };
  node.appendChild = function (child) {
    if (child.parentNode) {
      child.parentNode.childNodes = child.parentNode.childNodes.filter((item) => item !== child);
    }
    child.parentNode = node;
    node.childNodes.push(child);
    return child;
  };
  Object.defineProperty(node, "children", {
    get() {
      return node.childNodes.filter((item) => item.nodeType === 1);
    },
  });
  Object.defineProperty(node, "textContent", {
    get() {
      return textOf(node);
    },
    set(value) {
      node.childNodes = [{ nodeType: 3, text: String(value), parentNode: node, childNodes: [] }];
    },
  });
  Object.defineProperty(node, "id", {
    get() {
      return Object.prototype.hasOwnProperty.call(node.attrs, "id") ? String(node.attrs.id) : "";
    },
    set(value) {
      node.attrs.id = String(value);
    },
  });
  Object.defineProperty(node, "hidden", {
    get() {
      return Object.prototype.hasOwnProperty.call(node.attrs, "hidden");
    },
    set(value) {
      if (value) node.attrs.hidden = "";
      else delete node.attrs.hidden;
    },
  });
  if (node.tagName === "TABLE") {
    Object.defineProperty(node, "tBodies", {
      get() {
        return node.children.filter((item) => item.tagName === "TBODY");
      },
    });
  }
  if (node.tagName === "TBODY" || node.tagName === "THEAD") {
    Object.defineProperty(node, "rows", {
      get() {
        return node.children.filter((item) => item.tagName === "TR");
      },
    });
  }
  return node;
}

function enclosingPanel(table) {
  let node = table.parentNode;
  while (node) {
    if (node.nodeType === 1 && matches(node, parseSimple(".table-panel"))) return node;
    node = node.parentNode;
  }
  return null;
}

const documentRoot = build(payload.tree, null);
new Function("document", payload.script)(documentRoot);

function tables() {
  return qsa(documentRoot, "table[data-sortable]");
}

function tableAt(index) {
  const found = tables();
  if (!found[index]) throw new Error("no sortable table " + index);
  return found[index];
}

function fireClick(node, label) {
  const fns = (node._listeners && node._listeners.click) || [];
  if (!fns.length) throw new Error(label + " has no click listener");
  for (const fn of fns) fn.call(node, { type: "click", target: node });
}

function snapshot() {
  return {
    tables: tables().map((table) => {
      const panel = enclosingPanel(table);
      const body = table.tBodies[0];
      const rows = body ? Array.prototype.slice.call(body.rows) : [];
      return {
        ids: rows.map((row) => row.getAttribute("data-row-id") || ""),
        labels: rows.map((row) => (row.children[0] ? row.children[0].textContent.trim() : "")),
        cells: rows.map((row) => row.children.map((cell) => cell.textContent)),
        hidden: panel ? panel.hidden : null,
        headerSorts: qsa(table, "thead th").map((th) => th.getAttribute("aria-sort")),
      };
    }),
    switches: qsa(documentRoot, ".switcher button").map((button) => ({
      target: button.getAttribute("data-target"),
      pressed: button.getAttribute("aria-pressed"),
    })),
  };
}

const shots = {};
for (const action of payload.actions || []) {
  if (action.op === "snapshot") {
    shots[action.name] = snapshot();
  } else if (action.op === "clickHeader") {
    const headers = qsa(tableAt(action.table), "thead th");
    if (!headers[action.column]) throw new Error("no header " + action.column);
    const button = headers[action.column].querySelector("button");
    if (!button) throw new Error("header has no button");
    fireClick(button, "header " + action.table + ":" + action.column);
  } else if (action.op === "clickSwitch") {
    const button = qsa(documentRoot, ".switcher button").find(
      (item) => item.getAttribute("data-target") === action.target
    );
    if (!button) throw new Error("no switch " + action.target);
    fireClick(button, "switch " + action.target);
  } else if (action.op === "setCellText") {
    const body = tableAt(action.table).tBodies[0];
    const rows = Array.prototype.slice.call(body.rows);
    const row = rows.find((item) => (item.getAttribute("data-row-id") || "") === action.rowId);
    if (!row) throw new Error("missing row " + action.rowId);
    const cell = row.children[action.cell];
    if (!cell) throw new Error("missing cell " + action.cell);
    cell.textContent = action.text;
  } else {
    throw new Error("unknown action " + action.op);
  }
}
process.stdout.write(JSON.stringify(shots));
"""


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root: dict = {"type": "element", "tag": "#document", "attrs": {}, "children": []}
        self.stack = [self.root]
        self.script_parts: list[str] = []
        self._script_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = {
            "type": "element",
            "tag": tag,
            "attrs": {key: "" if value is None else value for key, value in attrs},
            "children": [],
        }
        self.stack[-1]["children"].append(node)
        if tag in _VOID_TAGS:
            return
        self.stack.append(node)
        if tag == "script":
            self._script_depth += 1

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]["tag"] != tag:
                continue
            if tag == "script":
                self._script_depth = max(0, self._script_depth - 1)
            del self.stack[index:]
            return

    def handle_data(self, data: str) -> None:
        if self._script_depth:
            self.script_parts.append(data)
            return
        if data:
            self.stack[-1]["children"].append({"type": "text", "text": data})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID_TAGS:
            self.handle_endtag(tag)


def parse_template(html: str) -> tuple[dict, str]:
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root, "".join(builder.script_parts)


def replace_tbodies(html: str, bodies: list[str]) -> str:
    matches = list(_TBODY_RE.finditer(html))
    if len(matches) != len(bodies):
        raise AssertionError(f"expected {len(bodies)} tbodies, found {len(matches)}")
    chunks: list[str] = []
    cursor = 0
    for match, body in zip(matches, bodies):
        chunks.append(html[cursor : match.start(2)])
        chunks.append(body)
        cursor = match.end(2)
    chunks.append(html[cursor:])
    return "".join(chunks)


def run_grid(html: str, actions: list[dict]) -> dict:
    node = shutil.which("node")
    if not node:
        raise AssertionError("node is required to execute the bulk grid inline script")
    tree, script = parse_template(html)
    if "function sortTable" not in script:
        raise AssertionError("template script did not parse")
    env = os.environ.copy()
    env.pop("FORCE_COLOR", None)
    env.pop("NO_COLOR", None)
    proc = subprocess.run(
        [node, "-e", _NODE_HARNESS],
        input=json.dumps({"tree": tree, "script": script, "actions": actions}, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        check=False,
        timeout=20,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "bulk grid script failed\n"
            f"stdout={proc.stdout[-2000:]}\nstderr={proc.stderr[-2000:]}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"harness returned non-JSON: {proc.stdout[:500]}") from exc


def _ids(snapshot: dict) -> list[list[str]]:
    return [list(table["ids"]) for table in snapshot["tables"]]


def _labels(snapshot: dict) -> list[list[str]]:
    return [list(table["labels"]) for table in snapshot["tables"]]


def _cells_by_id(snapshot: dict, table_index: int) -> dict[str, list[str]]:
    return {row_id: cells for row_id, cells in zip(snapshot["tables"][table_index]["ids"], snapshot["tables"][table_index]["cells"])}


class BulkGridRowOrderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = TEMPLATE.read_text(encoding="utf-8")

    def test_template_rows_share_stable_ids_and_stay_self_contained(self) -> None:
        tree, script = parse_template(self.html)
        ids: list[list[str]] = []
        for node in _walk_elements(tree):
            if node["tag"] != "table" or "data-sortable" not in node["attrs"]:
                continue
            tbodies = [child for child in node["children"] if child.get("tag") == "tbody"]
            self.assertEqual(len(tbodies), 1)
            row_ids = [
                child["attrs"].get("data-row-id", "")
                for child in tbodies[0]["children"]
                if child.get("tag") == "tr"
            ]
            ids.append(row_ids)
        self.assertEqual(ids, [["row-1", "row-2"], ["row-1", "row-2"]])
        self.assertIn("data-row-id", script)
        self.assertNotIn("<script", script)
        self.assertIsNone(re.search(r"<script\b[^>]*\bsrc\s*=", self.html, flags=re.IGNORECASE))
        self.assertIn("HTML-escape", self.html)

    def test_sorting_either_table_keeps_sample_row_ids_and_typed_cells(self) -> None:
        shots = run_grid(
            self.html,
            [
                {"op": "snapshot", "name": "initial"},
                {"op": "setCellText", "table": 0, "rowId": "row-1", "cell": 3, "text": "m-verified"},
                {"op": "setCellText", "table": 0, "rowId": "row-2", "cell": 3, "text": "a-verified"},
                {"op": "snapshot", "name": "edited"},
                {"op": "clickHeader", "table": 0, "column": 0},
                {"op": "clickHeader", "table": 0, "column": 0},
                {"op": "snapshot", "name": "values-desc"},
                {"op": "clickSwitch", "target": "sources-panel"},
                {"op": "snapshot", "name": "sources-view"},
                {"op": "clickHeader", "table": 1, "column": 1},
                {"op": "snapshot", "name": "sources-asc"},
                {"op": "clickHeader", "table": 1, "column": 1},
                {"op": "snapshot", "name": "sources-desc"},
                {"op": "clickHeader", "table": 0, "column": 3},
                {"op": "snapshot", "name": "verified-asc"},
                {"op": "clickSwitch", "target": "all"},
                {"op": "snapshot", "name": "both-view"},
            ],
        )
        initial = shots["initial"]
        self.assertEqual(_ids(initial), [["row-1", "row-2"], ["row-1", "row-2"]])
        self.assertEqual([table["hidden"] for table in initial["tables"]], [False, True])
        self.assertEqual(initial["switches"][0]["pressed"], "true")

        edited = _cells_by_id(shots["edited"], 0)
        self.assertEqual(edited["row-1"][3], "m-verified")
        self.assertEqual(edited["row-2"][3], "a-verified")

        # Sample names sort A then B, so the second click is descending: B then A.
        # Sources were still hidden — the audit case, checked before the toggle.
        self.assertEqual(_ids(shots["values-desc"]), [["row-2", "row-1"], ["row-2", "row-1"]])
        self.assertEqual(shots["values-desc"]["tables"][0]["headerSorts"], ["descending", "none", "none", "none"])
        self.assertEqual(shots["values-desc"]["tables"][1]["headerSorts"], ["none", "none", "none"])
        self.assertEqual([table["hidden"] for table in shots["values-desc"]["tables"]], [False, True])
        self.assertEqual(_cells_by_id(shots["values-desc"], 0), edited)
        self.assertEqual(_cells_by_id(shots["values-desc"], 1), _cells_by_id(shots["edited"], 1))

        sources_view = shots["sources-view"]
        self.assertEqual(_ids(sources_view), [["row-2", "row-1"], ["row-2", "row-1"]])
        self.assertEqual([table["hidden"] for table in sources_view["tables"]], [True, False])
        self.assertEqual(
            [item["pressed"] for item in sources_view["switches"]],
            ["false", "true", "false"],
        )

        self.assertEqual(_ids(shots["sources-asc"])[0], _ids(shots["sources-asc"])[1])
        self.assertEqual(_ids(shots["sources-desc"])[0], _ids(shots["sources-desc"])[1])
        self.assertEqual(_ids(shots["sources-desc"])[0], list(reversed(_ids(shots["sources-asc"])[0])))
        self.assertNotEqual(_ids(shots["sources-asc"])[0], _ids(shots["sources-desc"])[0])
        self.assertEqual(shots["sources-desc"]["tables"][0]["headerSorts"], ["none", "none", "none", "none"])
        self.assertEqual(shots["sources-desc"]["tables"][1]["headerSorts"][1], "descending")
        self.assertEqual(_cells_by_id(shots["sources-desc"], 0)["row-1"][3], "m-verified")
        self.assertIn("A MSA section", _cells_by_id(shots["sources-desc"], 1)["row-1"][1])
        self.assertIn("B NDA", _cells_by_id(shots["sources-desc"], 1)["row-2"][0])

        # Typed Verified text is the sort key. "a-verified" precedes "m-verified".
        self.assertEqual(_ids(shots["verified-asc"]), [["row-2", "row-1"], ["row-2", "row-1"]])
        both = shots["both-view"]
        self.assertEqual(_ids(both), [["row-2", "row-1"], ["row-2", "row-1"]])
        self.assertEqual([table["hidden"] for table in both["tables"]], [False, False])
        self.assertEqual(both["switches"][2]["pressed"], "true")
        self.assertEqual(_cells_by_id(both, 0)["row-2"][3], "a-verified")
        self.assertIn("B NDA", "".join(_cells_by_id(both, 1)["row-2"]))

    def test_same_display_name_follows_row_id_from_either_table(self) -> None:
        html = replace_tbodies(
            self.html,
            [
                """
<tr data-row-id="r1"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="10">10</td><td data-sort-value="m">m</td><td data-sort-value="">사람-r1</td></tr>
<tr data-row-id="r2"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="2">2</td><td data-sort-value="a">a</td><td data-sort-value="">사람-r2</td></tr>
<tr data-row-id="r3"><th scope="row" data-sort-value="다름">다름</th><td data-sort-value="2">2</td><td data-sort-value="z">z</td><td data-sort-value="">사람-r3</td></tr>
""",
                """
<tr data-row-id="r1"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="zzz">근거-r1</td><td data-sort-value="3">quote-r1</td></tr>
<tr data-row-id="r2"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="aaa">근거-r2</td><td data-sort-value="1">quote-r2</td></tr>
<tr data-row-id="r3"><th scope="row" data-sort-value="다름">다름</th><td data-sort-value="mmm">근거-r3</td><td data-sort-value="2">quote-r3</td></tr>
""",
            ],
        )
        shots = run_grid(
            html,
            [
                {"op": "snapshot", "name": "initial"},
                {"op": "clickHeader", "table": 0, "column": 1},
                {"op": "snapshot", "name": "values-asc"},
                {"op": "clickHeader", "table": 0, "column": 1},
                {"op": "snapshot", "name": "values-desc"},
                {"op": "clickHeader", "table": 1, "column": 1},
                {"op": "snapshot", "name": "sources-asc"},
            ],
        )
        self.assertEqual(shots["initial"]["tables"][0]["labels"], ["동일", "동일", "다름"])
        self.assertEqual(shots["initial"]["tables"][1]["labels"], ["동일", "동일", "다름"])
        # 10 sorts after 2. Tied 2s keep document order r2 then r3.
        self.assertEqual(_ids(shots["values-asc"]), [["r2", "r3", "r1"], ["r2", "r3", "r1"]])
        self.assertEqual(_ids(shots["values-desc"]), [["r1", "r2", "r3"], ["r1", "r2", "r3"]])
        # Sources column order aaa/mmm/zzz is r2, r3, r1 — not the values numeric order.
        self.assertEqual(_ids(shots["sources-asc"]), [["r2", "r3", "r1"], ["r2", "r3", "r1"]])
        values_cells = _cells_by_id(shots["sources-asc"], 0)
        source_cells = _cells_by_id(shots["sources-asc"], 1)
        self.assertEqual(values_cells["r1"][3], "사람-r1")
        self.assertEqual(values_cells["r2"][3], "사람-r2")
        self.assertEqual(source_cells["r1"][1], "근거-r1")
        self.assertEqual(source_cells["r2"][1], "근거-r2")
        self.assertNotEqual(values_cells["r1"], values_cells["r2"])

    def test_crossed_initial_order_realigns_by_row_id(self) -> None:
        html = replace_tbodies(
            self.html,
            [
                """
<tr data-row-id="r1"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="1">1</td><td data-sort-value="a">a</td><td data-sort-value="">사람-r1</td></tr>
<tr data-row-id="r2"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="2">2</td><td data-sort-value="b">b</td><td data-sort-value="">사람-r2</td></tr>
""",
                """
<tr data-row-id="r2"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="zzz">근거-r2</td><td data-sort-value="b">quote-r2</td></tr>
<tr data-row-id="r1"><th scope="row" data-sort-value="동일">동일</th><td data-sort-value="aaa">근거-r1</td><td data-sort-value="a">quote-r1</td></tr>
""",
            ],
        )
        shots = run_grid(
            html,
            [
                {"op": "snapshot", "name": "initial"},
                {"op": "clickHeader", "table": 0, "column": 1},
                {"op": "snapshot", "name": "asc"},
                {"op": "clickHeader", "table": 0, "column": 1},
                {"op": "snapshot", "name": "desc"},
            ],
        )
        self.assertEqual(_ids(shots["initial"]), [["r1", "r2"], ["r2", "r1"]])
        self.assertEqual(shots["initial"]["tables"][0]["labels"], ["동일", "동일"])
        self.assertEqual(_ids(shots["asc"]), [["r1", "r2"], ["r1", "r2"]])
        self.assertEqual(_ids(shots["desc"]), [["r2", "r1"], ["r2", "r1"]])
        self.assertEqual(_cells_by_id(shots["desc"], 0)["r1"][3], "사람-r1")
        self.assertEqual(_cells_by_id(shots["desc"], 1)["r1"][1], "근거-r1")
        self.assertEqual(_cells_by_id(shots["desc"], 1)["r2"][1], "근거-r2")

    def test_rows_without_ids_keep_positional_correspondence(self) -> None:
        html = replace_tbodies(
            self.html,
            [
                """
<tr><th scope="row" data-sort-value="A">A</th><td data-sort-value="10">10</td><td data-sort-value="x">x</td><td data-sort-value="">va</td></tr>
<tr><th scope="row" data-sort-value="B">B</th><td data-sort-value="2">2</td><td data-sort-value="y">y</td><td data-sort-value="">vb</td></tr>
""",
                """
<tr><th scope="row" data-sort-value="A">A</th><td data-sort-value="src-z">sa</td><td data-sort-value="1">ta</td></tr>
<tr><th scope="row" data-sort-value="B">B</th><td data-sort-value="src-a">sb</td><td data-sort-value="2">tb</td></tr>
""",
            ],
        )
        shots = run_grid(
            html,
            [
                {"op": "clickHeader", "table": 0, "column": 1},
                {"op": "snapshot", "name": "values-asc"},
                {"op": "clickHeader", "table": 1, "column": 2},
                {"op": "snapshot", "name": "sources-asc"},
            ],
        )
        self.assertEqual(_labels(shots["values-asc"]), [["B", "A"], ["B", "A"]])
        self.assertEqual(shots["values-asc"]["tables"][0]["cells"][0][3], "vb")
        self.assertEqual(shots["values-asc"]["tables"][1]["cells"][0][1], "sb")
        self.assertEqual(_labels(shots["sources-asc"]), [["A", "B"], ["A", "B"]])
        self.assertEqual(shots["sources-asc"]["tables"][0]["cells"][0][3], "va")
        self.assertEqual(shots["sources-asc"]["tables"][1]["cells"][0][2], "ta")


def _walk_elements(node: dict):
    if node.get("type") != "element":
        return
    yield node
    for child in node.get("children", []):
        yield from _walk_elements(child)


if __name__ == "__main__":
    unittest.main()
