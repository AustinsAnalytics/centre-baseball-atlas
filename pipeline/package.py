"""Make deterministic repository data archives and a portable website ZIP."""
from pathlib import Path
import gzip,json,zipfile,hashlib
root=Path(__file__).resolve().parents[1]
for p in (root/'site/data').glob('*.json'):
 p.with_suffix('.json.gz').write_bytes(gzip.compress(p.read_bytes(),compresslevel=9,mtime=0))
files=[]
for p in root.rglob('*'):
 if not p.is_file() or any(x in p.parts for x in ('__pycache__','.git','.qa')):continue
 rel=p.relative_to(root).as_posix()
 if p.suffix=='.zip' or rel=='upload-manifest.json' or (rel.startswith('site/data/') and p.suffix=='.json'):continue
 files.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'upload-manifest.json').write_text(json.dumps(files))
with zipfile.ZipFile(root/'Centre-Atlas-website.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in (root/'site').rglob('*'):
  if p.is_file() and '.qa' not in p.parts and p.suffix!='.gz':z.write(p,p.relative_to(root/'site'))
print(f'{len(files)} repository files; {sum(f["bytes"] for f in files):,} bytes. Portable site ZIP created.')
