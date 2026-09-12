#!/usr/bin/env python3
import json,os,subprocess,time,tempfile,sys,hashlib
from pathlib import Path
e=os.environ;c=Path(e['BEOPSUNY_EVAL_CONTEXT_FILE']).read_text();p=Path(e['BEOPSUNY_EVAL_PROMPT_FILE']).read_text();ident=e['BEOPSUNY_EVAL_PROMPT_ID'];w=Path(e['BEOPSUNY_EVAL_WORKSPACE']);out=Path(e['BEOPSUNY_EVAL_OUTPUT_FILE']);t=Path(e['BEOPSUNY_CLAUDE_TRACE_DIR']);t.mkdir(parents=True,exist_ok=True)
if (t/f'{ident}.stdout').exists(): raise RuntimeError('refusing to overwrite an existing execution')
runtime='/tmp/beopsuny-final-runtime-smoke/runtime'
data=e['BEOPSUNY_DATA_ROOT']
if 'o4-05' in ident:
 data=tempfile.mkdtemp(prefix='empty-o4-05-');e['BEOPSUNY_DATA_ROOT']=data
 c+='\n[평가 환경 전제] 로컬 미러가 없다. 지정 데이터 root는 비어 있다. 다른 설치 경로를 찾지 말고 법망 API·law.go.kr degradation 경로로 답하라.\n'
c+=f'\n[평가 환경] BEOPSUNY_DATA_ROOT={data}. 추가 스킬 reference는 {runtime}/skills/beopsuny에서 읽는다. 개인 설치본·다른 평가 출력은 이용하지 않는다. 실제 확인 경로와 실패를 정직하게 보고한다. 도구는 자료 읽기·검색만 허용된다.\n'
a=['timeout','-k','10s','900','claude','-p','--safe-mode','--restricted','--strict-mcp-config','--permission-mode','dontAsk','--model',e['BEOPSUNY_EVAL_MODEL'],'--effort','high','--tools','Read,Glob,Grep,WebFetch,WebSearch','--allowedTools','Read,Glob,Grep,WebFetch,WebSearch','--add-dir',runtime,data,'--system-prompt',c,'--output-format','stream-json','--verbose',p]
start=time.monotonic()
with (t/f'{ident}.stdout').open('w') as o,(t/f'{ident}.stderr').open('w') as z:q=subprocess.run(a,stdin=subprocess.DEVNULL,text=True,cwd=w,env=e,stdout=o,stderr=z)
final=None
for line in (t/f'{ident}.stdout').read_text().splitlines():
 try:x=json.loads(line)
 except ValueError:continue
 if x.get('type')=='result':final=x
meta={'returncode':q.returncode,'seconds':time.monotonic()-start,'result':final,'full_context_sha256':hashlib.sha256(c.encode()).hexdigest(),'isolation':'CLI safe-mode + restricted read boundaries + read/search tool allowlist; inspect actual tool trace'}
(t/f'{ident}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
if q.returncode or not final or final.get('is_error') or not final.get('result','').strip():sys.exit(q.returncode or 1)
out.write_text(final['result'])
