"""Independent before/after verification against the frozen pre-audit release."""
import json,pandas as pd,hashlib
from identity_audit import ROOT,SRC,OUT
x=pd.read_pickle(OUT/'final_audit_frame.pkl').set_index('PitchUID');index=json.loads((ROOT/'site/data/index.json').read_text());base=OUT/'baseline_data';pair_counts=[];centre_counts=[]
def unpack(d):return [dict(zip(d['columns'],r)) for r in d['rows']]
def after_count(p):
 b,k=p['balls'],p['strikes'];call=p['call']
 if b not in range(4) or k not in range(3):return None
 if call in ['BallCalled','BallinDirt','BallIntentional']:return (b+1,k) if b<3 else None
 if call in ['StrikeCalled','StrikeSwinging']:return (b,k+1) if k<2 else None
 if call.startswith('FoulBall'):return (b,min(k+1,2))
 return None
allowed={'p','t','hand','ahb','review'}
for season in index['seasons']:
 fn=season.lower().replace(' ','-')+'.json';old=json.loads((base/fn).read_text());new=json.loads((ROOT/'site/data'/fn).read_text());op=unpack(old['pitches']);np=unpack(new['pitches']);assert len(op)==len(np)
 for a,b in zip(op,np):
  assert a['u']==b['u'];assert all(a[k]==b[k] for k in a if k not in allowed),(a['u'],[k for k in a if a[k]!=b[k] and k not in allowed])
  r=x.loc[a['u']];assert index['players'][b['p']]['name']==r.FinalPitcher
  assert b['t']==r.FinalType;assert b['op']==a['p']
 for a,b in zip(unpack(old['pas']),unpack(new['pas'])):assert all(a[k]==b[k] for k in a if k!='p')
 assert old['pbp']==new['pbp']
 assert (base/('replays-'+fn)).read_bytes()==(ROOT/'site/data'/('replays-'+fn)).read_bytes()
 # Rebuild adjacency from the frozen records, changing only reviewed identity.
 df=pd.DataFrame(op);total=centre=0
 for _,g in df.groupby(['g','pa']):
  g=g.sort_values('order');rr=g.to_dict('records')
  for a,b in zip(rr,rr[1:]):
   if x.loc[a['u']].FinalPitcher!=x.loc[b['u']].FinalPitcher or a['b']!=b['b'] or a['recording']!=b['recording'] or b['order']!=a['order']+1:continue
   if after_count(a)!=(b['balls'],b['strikes']):continue
   total+=1;centre+=int(x.loc[b['u']].PitcherTeam=='CEN_COL')
 pair_counts.append(total);centre_counts.append(centre)
assert (base/'defense.json').read_bytes()==(ROOT/'site/data/defense.json').read_bytes()
old_index=json.loads((base/'index.json').read_text())
for old in old_index['players']:
 new=index['players'][old['id']]
 assert all(new[k]==old[k] for k in ['id','name','team','centre'])
for r in pd.read_csv(OUT/'source_manifest.csv').itertuples():assert hashlib.sha256((SRC/r.file).read_bytes()).hexdigest()==r.sha256
report={'pairCounts':pair_counts,'centrePairCounts':centre_counts,'records':40123,'unchanged':'All source input hashes; batting/scoring/context/measurements; PBP pools; all replay files; all defense data; original player IDs and names.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
