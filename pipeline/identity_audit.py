"""Read-only, seven-season identity/type investigation. Never changes source exports.

Scores are standardized shape distances, NOT identity probabilities. PBP matches
and continuity evidence are exported for adjudication before any corrections.
"""
from pathlib import Path
import json, re, hashlib, shutil
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT.parents[1]
OUT=ROOT/'audit_2026_10_27'
OUT.mkdir(exist_ok=True)
FEATURES=['RelSpeed','InducedVertBreak','HorzBreak','SpinRate','RelHeight','RelSide','Extension']
SCALE=np.array([2.2,4.,4.,200.,.25,.30,.45])

def canonical(s):
 if not isinstance(s,str):return ''
 return {'Vallone, Tristen':'Vallone, Tristan','Taylor, Wesley':'Taylor, Wes','Tayor, Wesley':'Taylor, Wes'}.get(s.strip(),s.strip())

def key(s):
 s=canonical(s).lower()
 if ',' in s:last,first=s.split(',',1)
 else:
  words=s.split();first=' '.join(words[:-1]);last=words[-1] if words else ''
 return re.sub('[^a-z]','',last),re.sub('[^a-z]','',first)

def names_match(a,b):
 la,fa=key(a);lb,fb=key(b)
 return bool(la and lb and (la==lb or (min(len(la),len(lb))>=4 and (la.startswith(lb) or lb.startswith(la)))) and (not fa or not fb or fa[0]==fb[0]))

def load():
 h=pd.read_csv(SRC/'Colonels_Analytics/data/centre_pitch_by_pitch_master.csv',low_memory=False)
 f=pd.read_csv(SRC/'Fall26/Fall26_Studio/audit/pitches_clean.csv',low_memory=False)
 f=f.rename(columns={'Top/Bottom':'TopBottom'})
 f['Season']='Fall 2026';f['GameDate']=f['SortDate'];f['GameLabel']=f.Session
 f['SessionType']=np.where(f.Session.str.startswith('LW'),'Fall Scrimmage','Fall Intrasquad')
 f['PitchType']=f.CleanPitchType.str.replace('ChangeUp','Changeup')
 f['SourceFile']=f.Session+' TM.csv';f['PitchOfGame']=f.PitchNo
 f['PAofGame']=f.PA;f['PBP_GameID']=np.nan
 a=pd.concat([h,f],ignore_index=True,sort=False)
 a['Pitcher']=a.Pitcher.map(canonical);a['Batter']=a.Batter.map(canonical)
 a['Eligible']=~a.Excluded.fillna(False).astype(bool)
 current={}
 baseline=OUT/'baseline_data'
 data_dir=baseline if (baseline/'index.json').exists() else ROOT/'site/data'
 for path in data_dir.glob('*.json'):
  if path.stem not in ['fall-2023','spring-2024','fall-2024','spring-2025','fall-2025','spring-2026','fall-2026']:continue
  d=json.loads(path.read_text())['pitches'];cols=d['columns']
  for row in d['rows']:
   r=dict(zip(cols,row));current[r['u']]=r['t']
 a['AtlasType']=a.PitchUID.map(current).fillna(a.PitchType)
 a['Identity']=a.Pitcher
 for c in FEATURES:a[c]=pd.to_numeric(a[c],errors='coerce')
 # Sensor-quality exclusions apply only to screening, never delete events.
 good=a.PitchReleaseConfidence.isin(['High','Medium']) & a.RelSpeed.between(40,105)
 a['Measured']=good & a[FEATURES].notna().all(axis=1)
 a['Half']=a.TopBottom.str.lower()
 a=a.sort_values(['GameUID','PitchNo'],kind='stable').reset_index(drop=True)
 assert len(a)==40126 and a.PitchUID.nunique()==40126
 return a

def pbp_screen(a):
 p=pd.read_csv(SRC/'Colonels_Analytics/data/pbp_events_all_games.csv',low_memory=False)
 # Recover the exact PBP event already aligned by the master, with unique
 # inning/half/description keys; ambiguous repeated text is not forced.
 ps={}
 for k,g in p[p.IsPA.eq(True)].groupby(['PBP_GameID','Inning','Half','Description'],dropna=False):
  if len(g)==1:ps[k]=g.iloc[0]
 a['PBPIdentity']='';a['PBPIdentityStatus']='unavailable';a['PBPEvent']=np.nan
 people={k:list(g.Pitcher.dropna().unique()) for k,g in a.groupby(['Season','PitcherTeam'])}
 for k,g in a[a.ContextSource.eq('Matched')].groupby(['PBP_GameID','Inning','Half','PA_Description'],dropna=False):
  pr=ps.get(k)
  if pr is None or not isinstance(pr.PitcherPBP,str):continue
  # Name candidates are limited to the same season and defensive team.
  candidates=people.get((g.Season.iloc[0],g.PitcherTeam.iloc[0]),[])
  matches=[n for n in candidates if names_match(n,pr.PitcherPBP)]
  a.loc[g.index,'PBPEvent']=pr.EventIdx
  a.loc[g.index,'PBPIdentityRaw']=pr.PitcherPBP
  if len(matches)!=1:
   a.loc[g.index,'PBPIdentityStatus']='unresolved-name';continue
  who=matches[0];a.loc[g.index,'PBPIdentity']=who
  a.loc[g.index,'PBPIdentityStatus']=np.where(g.Pitcher.eq(who),'agrees','conflict')
 cols=['PitchUID','Season','GameLabel','GameUID','PitchNo','Inning','Half','Pitcher','PitcherTeam','Batter','PA_Description','PBPIdentity','PBPIdentityRaw','PBPEvent','PBP_GameID','PBP_File','AtlasType']+FEATURES
 conflicts=a[a.PBPIdentityStatus.eq('conflict')]
 conflicts[cols].to_csv(OUT/'pbp_identity_conflicts.csv',index=False)
 print('PBP',a.PBPIdentityStatus.value_counts().to_dict(),flush=True)
 print(conflicts.groupby(['Season','GameLabel','Pitcher','PBPIdentity']).size().to_string(),flush=True)
 return a

def shape_screen(a):
 # A pitcher can have multiple valid release shapes. Prototypes use each
 # established pitch family, so a dropped slot on a breaker is not itself an
 # identity change. Models are fitted only on other recordings.
 measured=a[a.Measured].copy()
 output=[];pitchflags=[]
 for (season,team),pool in measured.groupby(['Season','PitcherTeam']):
  if len(pool)<20:continue
  for game,game_rows in pool.groupby('GameUID'):
   train=pool[pool.GameUID.ne(game)]
   prot=[];pnames=[];ptypes=[];support=[]
   for (who,typ),g in train.groupby(['Pitcher','AtlasType']):
    if len(g)<8:continue
    x=g[FEATURES].to_numpy(float);med=np.median(x,axis=0)
    # Trim gross mislabeled training pitches without deleting source records.
    dist=np.sqrt(np.mean(((x-med)/SCALE)**2,axis=1));core=x[dist<=max(2.,np.quantile(dist,.8))]
    if len(core)<8:continue
    prot.append(np.median(core,axis=0));pnames.append(who);ptypes.append(typ);support.append(len(core))
   if not prot:continue
   proto=np.array(prot);pnames=np.array(pnames);ptypes=np.array(ptypes)
   x=game_rows[FEATURES].to_numpy(float)
   dd=(x[:,None,:]-proto[None,:,:])/SCALE
   dist=np.sqrt(np.mean(dd**2,axis=2))
   # Release-only distance provides a second view independent of pitch tags.
   rel=np.sqrt(np.mean(dd[:,:,4:]**2,axis=2))
   pitchers=list(dict.fromkeys(pnames));scores=np.column_stack([dist[:,pnames==w].min(axis=1) for w in pitchers]);rels=np.column_stack([rel[:,pnames==w].min(axis=1) for w in pitchers])
   scoreframe=pd.DataFrame(scores,index=game_rows.index,columns=pitchers)
   relframe=pd.DataFrame(rels,index=game_rows.index,columns=pitchers)
   # Inning blocks flag persistent shifts, including an entire outing whose
   # identity was never updated by the operator.
   for (inn,half,who),block in game_rows.groupby(['Inning','Half','Pitcher']):
    if len(block)<3:continue
    av=scoreframe.loc[block.index].median().sort_values();best=av.index[0]
    own=float(av.get(who,np.nan));bestd=float(av.iloc[0]);bestrel=float(relframe.loc[block.index,best].median());ownrel=float(relframe.loc[block.index,who].median()) if who in pitchers else np.nan
    handwrong=float(((block.RelSide>0)!=(block.PitcherThrows=='Right')).mean())
    if (best!=who and (own-bestd>1.0 or ownrel-bestrel>1.4)) or own>2.7 or handwrong>.25:
     candidates=[{'pitcher':str(w),'distance':round(float(v),3),'release':round(float(relframe.loc[block.index,w].median()),3)} for w,v in av.head(5).items()]
     output.append({'Season':season,'Team':team,'GameLabel':block.GameLabel.iloc[0],'GameUID':game,'Inning':inn,'Half':half,'Pitcher':who,'N':len(block),'Start':block.PitchNo.min(),'End':block.PitchNo.max(),'Best':best,'OwnDistance':own,'BestDistance':bestd,'Margin':own-bestd,'OwnRelease':ownrel,'BestRelease':bestrel,'HandMismatch':handwrong,'Candidates':json.dumps(candidates),'UIDs':'|'.join(block.PitchUID)})
   # Individual release mismatches can expose a missed name change at the
   # start or end of an appearance even when block medians hide it.
   same_game=set(game_rows.Pitcher)
   for j,(idx,r) in enumerate(game_rows.iterrows()):
    if r.Pitcher not in pitchers:continue
    oi=pitchers.index(r.Pitcher);rank=np.argsort(scores[j]);bi=int(rank[0]);best=pitchers[bi]
    if best==r.Pitcher:continue
    if (scores[j,oi]>=3 and scores[j,bi]<=1.5 and scores[j,oi]-scores[j,bi]>=1.7 and rels[j,oi]>=2 and rels[j,bi]<=1.7) or ((r.RelSide>0)!=(r.PitcherThrows=='Right')):
     pitchflags.append({'PitchUID':r.PitchUID,'Season':season,'GameLabel':r.GameLabel,'GameUID':game,'PitchNo':r.PitchNo,'Inning':r.Inning,'Half':r.Half,'Pitcher':r.Pitcher,'Best':best,'SameGame':best in same_game,'OwnDistance':scores[j,oi],'BestDistance':scores[j,bi],'OwnRelease':rels[j,oi],'BestRelease':rels[j,bi],**{c:r[c] for c in FEATURES}})
 b=pd.DataFrame(output);q=pd.DataFrame(pitchflags)
 b.sort_values('Margin',ascending=False).to_csv(OUT/'identity_block_candidates.csv',index=False)
 q.to_csv(OUT/'identity_pitch_candidates.csv',index=False)
 print('IDENTITY SCREEN',len(b),'blocks',len(q),'pitches',flush=True)
 print(b[b.Team.eq('CEN_COL')].sort_values('Margin',ascending=False).drop(columns=['UIDs','Candidates']).round(2).to_string(index=False),flush=True)
 return a

def main():
 a=load()
 backup=OUT/'baseline_data';backup.mkdir(exist_ok=True)
 for p in (ROOT/'site/data').glob('*.json'):
  target=backup/p.name
  if not target.exists():shutil.copy2(p,target)
 a=pbp_screen(a);a=shape_screen(a);a.to_pickle(OUT/'working_source.pkl')
 pd.DataFrame([{'file':str(p.relative_to(SRC)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in [SRC/'Colonels_Analytics/data/centre_pitch_by_pitch_master.csv',SRC/'Colonels_Analytics/data/pbp_events_all_games.csv',SRC/'Fall26/Fall26_Studio/audit/pitches_clean.csv',SRC/'Fall26/cleaned/history_fixes.csv']]).to_csv(OUT/'source_manifest.csv',index=False)

if __name__=='__main__':main()
