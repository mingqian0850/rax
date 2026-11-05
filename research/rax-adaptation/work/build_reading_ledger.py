import collections
import hashlib
import json
import pathlib
import subprocess
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
rows = json.loads((OUT / 'code_inventory.json').read_text())
branches = [x for x in json.loads((ROOT/'work/branch_inventory.json').read_text()) if x['branch'] != 'upstream']
commits = {x['branch']: x['commit'] for x in branches}

# Full-file reading attested in this session. Partial inspection is deliberately separate.
full = {
 'libero-pro/native': {
  'services/benchmarks.py', 'services/libero_pro/__init__.py',
  'services/libero_pro/benchmark.py', 'services/libero_pro/backend.py',
  'services/libero_pro/tasks.py', 'services/libero_pro/tools.py',
  'services/libero_pro/session.py', 'services/libero_pro/process.py',
  'services/libero_pro/server.py', 'services/libero_pro/checks.py',
  'services/libero_pro/task_rules.py', 'services/libero_pro/demonstrations.py',
  'services/libero_pro/demo_tools.py', 'services/mcp_contract.py',
  'services/adaptation.py', 'services/transfer.py', 'services/controller/storage.py',
  'services/workspace/recipes.py', 'scripts/bootstrap_sources.sh',
  'scripts/setup_host_env.sh', 'scripts/setup_libero_pro_env.sh',
  'scripts/setup_libero_pro_data.py', 'scripts/host_env.sh',
  'scripts/doctor.sh', 'scripts/libero_pro_doctor.py',
  'local_tests/unit/test_adaptation.py', 'local_tests/unit/conftest.py',
 },
 'real/franka': {'services/backends.py','services/workspace/recipes.py',
                 'services/franka/servo.py','services/franka/ik.py','services/franka/bridges.py'},
 'real/rainbow': {'services/backends.py','services/workspace/recipes.py','services/skill_library.py'},
 'humanoid-arena/native': {'services/humanoid/robot.py'},
}
partial = {
 'libero-pro/native': {'services/controller/supervisor.py','services/controller/frontend.py',
  'services/controller/parallel_batch.py','scripts/configure_auto_research.py',
  'scripts/setup_libero_pro_demos.py','local_tests/unit/test_libero_pro_backend.py'},
 'real/franka': {'services/franka/backend.py'},
 'real/rainbow': {'services/rby1/backend.py','services/rby1/controller_modes.py'},
}
known = {(r['branch'],r['path']) for r in rows}
missing = [(b,p) for groups in (full,partial) for b,paths in groups.items() for p in paths if (b,p) not in known]
if missing:
 print('Ledger entries not present (not credited):',missing)
deep_hashes = {r['sha256'] for r in rows if r['path'] in full.get(r['branch'],set())}
part_hashes = {r['sha256'] for r in rows if r['path'] in partial.get(r['branch'],set())}
by_sha = collections.defaultdict(list)
checks = []
for r in rows:
 p = pathlib.PurePosixPath(r['path'])
 if p.suffix in ('.html','.Dockerfile') or p.name == 'Dockerfile':
  r['kind']='code'
 if r['kind']=='code':
  r['review'] = 'full-file-read' if r['sha256'] in deep_hashes else 'targeted-read' if r['sha256'] in part_hashes else 'static-index-only'
 by_sha[r['sha256']].append(r)
for sha,group in by_sha.items():
 r=group[0]
 if r['path'].endswith('.sh'):
  p=ROOT/'work/branches'/r['branch'].replace('/','--')/r['path']
  proc=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True)
  checks.append({'branch':r['branch'],'path':r['path'],'sha256':sha,'returncode':proc.returncode,'stderr':proc.stderr})
codes=[g for g in by_sha.values() if g[0]['kind']=='code']
summary={
 'branch_files':len(rows),'unique_blobs':len(by_sha),'code_occurrences':sum(r['kind']=='code' for r in rows),
 'unique_code_files':len(codes),'unique_code_lines':sum(g[0]['lines'] for g in codes),
 'review_unique_files':dict(collections.Counter(g[0]['review'] for g in codes)),
 'python_parse_errors':[{'branch':r['branch'],'path':r['path'],'error':r['syntax']} for r in rows if r.get('syntax') not in (None,'ok')],
 'shell_syntax_checks':len(checks),'shell_syntax_failures':sum(c['returncode']!=0 for c in checks),
 'classification':'Python, shell, JS/MJS, patches, HTML including inline scripts, Dockerfiles, extensionless scripts; URDF/config/assets listed separately',
 'note':'Full-file-read is textual inspection, not proof of runtime correctness. Hash-identical copies share the reading status. External dependencies and skills-lib are excluded from these repository counts.'
}
(OUT/'code_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(OUT/'reading_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(OUT/'shell-syntax-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
(OUT/'source-lock.json').write_text(json.dumps({'recorded':'2026-11-05','origin':'https://github.com/mingqian0850/rax.git','upstream':'https://github.com/robot-agent-exploration/rax.git','branches':branches,'libero_pro_commit':'eafdb809426b13153aa1e4c42d6601844217dfec','hf_data_revision':'c86fc3b8293185a6f373677018ff3e37f8391602','paper':'https://arxiv.org/html/2610.22496v1','skills_lib':{'franka':'f1845de5c915b9e16590b86fbb64e957f020f5a1','rby1':'d749168be6f85764db89182096656bd05e58f04b','simulation':'95418f056e28e6e78e6e4e2d9f1ce04e096f9206'}},ensure_ascii=False,indent=2)+'\n')
lines=['# 全代码导航与逐文件阅读台账','','这是 SHA256 去重后的全部代码文件目录。相同内容在多个分支出现时只列一项；不同版本分别列出。','',
       '状态：**精读**＝已全文阅读；**局部**＝只阅读了相关函数或片段；**索引**＝已建立静态目录/符号信息，尚未精读。测试通过不自动改变阅读状态。','',
       f'共 {summary["unique_code_files"]} 个不同代码文件版本，{summary["unique_code_lines"]} 行。原始、可机器处理的完整清单为同目录 code_inventory.json。','']
labels={'full-file-read':'精读','targeted-read':'局部','static-index-only':'索引'}
for g in sorted(codes,key=lambda g:(g[0]['path'].split('/')[0],g[0]['path'],g[0]['branch'])):
 r=g[0];url=f'https://github.com/robot-agent-exploration/rax/blob/{commits[r["branch"]]}/{urllib.parse.quote(r["path"])}'
 lines += [f'## {r["path"]} · {r["sha256"][:10]}','',f'- 状态：{labels[r["review"]]}；{r["lines"]} 行；[固定版本源码]({url})',f'- 分支：'+', '.join(sorted(set(x['branch'] for x in g)))]
 if r.get('summary'):
  lines.append('- 模块说明（源码自述，未独立验证）：'+r['summary'].split('\n\n')[0].replace('\n',' ')[:350])
 symbols=r.get('symbols',[])
 if symbols:
  lines.append('- 符号定位：'+', '.join(f'`{s["name"]}` L{s["line"]}' for s in symbols))
 lines.append('')
(OUT/'全代码导航.md').write_text('\n'.join(lines))
print(json.dumps(summary,ensure_ascii=False,indent=2))
