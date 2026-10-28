"""Cache public pitching lines to independently verify starter/substitution identities."""
from pathlib import Path
import concurrent.futures,subprocess,json,re,html,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'audit_2026_10_27';CACHE=OUT/'official_boxes';CACHE.mkdir(exist_ok=True)
a=pd.read_pickle(OUT/'working_source.pkl')
def text(s):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def one(item):
 gid,file=item;year=re.search(r'/?(20\d\d)/',file).group(1);slug=re.search(r'centre_baseball_\d{4}_\d+_(.+)_pbp_\d+\.csv$',file).group(1)
 url=f'https://centrecolonels.com/sports/baseball/stats/{year}/{slug}/boxscore/{int(gid)}';path=CACHE/f'{int(gid)}.html'
 if not path.exists():
  r=subprocess.run(['/usr/bin/curl','--silent','--show-error','--fail','--location','--max-time','35','--max-filesize','8000000',url,'--output',str(path)],capture_output=True,text=True)
  if r.returncode:return {'game':int(gid),'url':url,'error':r.stderr}
 raw=path.read_text();tables=[]
 for table in re.findall(r'<table\b.*?</table>',raw,re.S|re.I):
  cap=re.search(r'<caption>(.*?)</caption>',table,re.S)
  if not cap or 'Pitching Stats' not in text(cap.group(1)):continue
  body=re.search(r'<tbody[^>]*>(.*?)</tbody>',table,re.S);rows=[]
  if not body:continue
  for tr in re.findall(r'<tr\b.*?</tr>',body.group(1),re.S):
   cells=re.findall(r'<td([^>]*)>(.*?)</td>',tr,re.S)
   if not cells:continue
   nm=re.sub(r'\s*\((?:W|L|S),.*','',text(cells[0][1])).strip()
   row={'name':nm}
   for attr,content in cells[1:]:
    label=re.search(r'data-label="([^"]+)"',attr)
    if label:row[label.group(1)]=text(content)
   if 'IP' in row:rows.append(row)
  tables.append({'team':text(cap.group(1)).replace(' - Pitching Stats',''),'pitchers':rows})
 return {'game':int(gid),'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'teams':tables}
items=list(a[['PBP_GameID','PBP_File']].dropna().drop_duplicates().itertuples(index=False,name=None))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(one,items):
  results.append(r)
  if len(results)%15==0:print('Verified boxes',len(results),'/',len(items),flush=True)
(OUT/'official_pitching.json').write_text(json.dumps(results,indent=2))
print('Complete',len(results),'failures',[(r['game'],r.get('error','missing tables')) for r in results if not r.get('teams')],flush=True)
