import ast,hashlib,json,pathlib,collections,subprocess
root=pathlib.Path('work/branches'); rows=[]; unique={}
for branch in sorted(root.iterdir()):
 if branch.name=='upstream':continue
 for p in sorted(branch.rglob('*')):
  if not p.is_file():continue
  data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest();rel=p.relative_to(branch).as_posix()
  row={'branch':branch.name.replace('--','/'),'path':rel,'sha256':sha,'bytes':len(data),'lines':data.count(b'\n'),'kind':'asset','review':'inventory'}
  if p.suffix in {'.py','.sh','.js','.mjs','.patch'} or rel.startswith('scripts/') and not p.suffix:
   row['kind']='code';row['review']='static-index'
  elif p.suffix=='.md':row['kind']='documentation'
  elif p.suffix in {'.json','.toml','.ini','.yaml','.yml','.lock','.urdf'}:row['kind']='configuration'
  if p.suffix=='.py':
   try:
    t=ast.parse(data.decode());row['syntax']='ok';row['summary']=ast.get_docstring(t) or ''
    row['symbols']=[{'name':n.name,'line':n.lineno,'end':n.end_lineno,'doc':ast.get_docstring(n) or ''} for n in ast.walk(t) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]
    row['imports']=sorted(set(n.module or '' for n in ast.walk(t) if isinstance(n,ast.ImportFrom))|set(a.name for n in ast.walk(t) if isinstance(n,ast.Import) for a in n.names))
   except Exception as e:row['syntax']=str(e)
  rows.append(row);unique.setdefault(sha,[]).append(row)
pathlib.Path('outputs/code_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
summary={'branch_files':len(rows),'unique_blobs':len(unique),'code_occurrences':sum(r['kind']=='code' for r in rows),'unique_code_files':sum(v[0]['kind']=='code' for v in unique.values()),'unique_code_lines':sum(v[0]['lines'] for v in unique.values() if v[0]['kind']=='code'),'python_parse_errors':[r for r in rows if r.get('syntax') not in (None,'ok')]}
pathlib.Path('work/inventory_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
for branch in ['libero-pro/native','real/franka','real/rainbow','dexjoco/native','humanoid-arena/native','robodojo-behavior/native']:
 print('\nBRANCH',branch)
 groups=collections.defaultdict(list)
 for r in rows:
  if r['branch']==branch and r['kind']=='code':groups[r['path'].split('/')[0]].append(r)
 for k,rs in groups.items(): print(k,len(rs),sum(r['lines'] for r in rs))
