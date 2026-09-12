#!/usr/bin/env python3
"""Temporary Grok adapter to the existing command harness; no scoring logic."""
import json, os, subprocess, sys, time, tempfile
from pathlib import Path

env=os.environ
context=Path(env['BEOPSUNY_EVAL_CONTEXT_FILE']).read_text()
prompt=Path(env['BEOPSUNY_EVAL_PROMPT_FILE']).read_text()
output=Path(env['BEOPSUNY_EVAL_OUTPUT_FILE'])
workspace=Path(env['BEOPSUNY_EVAL_WORKSPACE'])
ident=env['BEOPSUNY_EVAL_PROMPT_ID']
traces=Path(env['BEOPSUNY_GROK_TRACE_DIR']);traces.mkdir(parents=True,exist_ok=True)
context+='\n평가 대상 답변을 작성한다. 이 context와 지정된 현재 runtime 사본 및 setup만 사용하고 개인 skill/기억/다른 평가 결과를 읽지 않는다. 실제 확인 경로와 실패를 정직하게 보고한다. 도구는 자료 읽기·검색만 허용되며 외부 행동을 실행하지 않는다.\n'
if 'o4-05' in ident:
 data=Path(tempfile.mkdtemp(prefix='empty-o4-05-', dir=env['BEOPSUNY_DATA_ROOT']));env['BEOPSUNY_DATA_ROOT']=str(data)
 context+=f'\n[평가 환경 전제] 로컬 미러가 없다. 유일한 데이터 루트 {data} 는 비어 있다. 다른 설치 경로를 찾지 말고 법망 API·law.go.kr degradation 경로로 답하라.\n'
context+=f"\n[평가 환경] BEOPSUNY_DATA_ROOT={env.get('BEOPSUNY_DATA_ROOT')}이다. 법령·판례 자료는 이 공개 미러 root에서 읽는다. 스킬의 추가 reference는 /tmp/beopsuny-release09/public-runtime-currency/skills/beopsuny 아래의 현재 runtime 사본에서 필요할 때 읽는다. 그 밖의 설치본·개인 파일은 읽지 않는다.\n"
argv=['timeout','-k','10s','900','grok','--permission-mode','dontAsk','-m',env['BEOPSUNY_EVAL_MODEL'],'--effort','high','--no-subagents','--tools','read_file,list_dir,grep,web_fetch','--disallowed-tools','web_search,write,search_replace,run_terminal_command,scheduler_create,scheduler_delete,monitor,workflow,use_tool,search_tool,image_gen,image_edit,image_to_video,reference_to_video','--max-turns','18','--system-prompt-override',context,'--output-format','streaming-messages-json','-p',prompt]
for denied in ['/','/tmp','/private','/private/tmp','/tmp/beopsuny-release09','/private/tmp/beopsuny-release09','/Users/**','/private/var/**','/var/**','/etc/**','/private/etc/**','/tmp/beopsuny-knowledge*/**','/private/tmp/beopsuny-knowledge*/**','/tmp/beopsuny-m8/**','/private/tmp/beopsuny-m8/**','/tmp/beopsuny-release09/knowledge*','/private/tmp/beopsuny-release09/knowledge*']:
 argv[argv.index('--max-turns'):argv.index('--max-turns')]=['--deny',f'Read({denied})']
start=time.monotonic()
with (traces/f'{ident}.stdout').open('w') as out,(traces/f'{ident}.stderr').open('w') as err:
 result=subprocess.run(argv,cwd=workspace,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
final=None
for line in (traces/f'{ident}.stdout').read_text().splitlines():
 try:event=json.loads(line)
 except ValueError:continue
 if event.get('type')=='result':final=event
meta={'returncode':result.returncode,'seconds':time.monotonic()-start,'result':final,'isolation':'explicit tool exclusions; no host sandbox (read-only profile failed before model launch); inspect actual tool trace'}
(traces/f'{ident}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
if result.returncode or not final or final.get('is_error') or final.get('subtype')!='success' or not final.get('result','').strip():
 print('Grok execution failed or lacked completed output; see trace metadata.',file=sys.stderr);sys.exit(result.returncode or 1)
output.write_text(final['result'])
