"""Identity-aware, conservative shape review. Distances are not probabilities."""
import json,numpy as np,pandas as pd
from identity_audit import ROOT,OUT
x=pd.read_pickle(OUT/'working_identity_corrected.pkl');x['FinalType']=x.AtlasType
F=['RelSpeed','InducedVertBreak','HorzBreak','SpinRate'];S=np.array([2.,4.,4.,200.])
entries=[]
def fam(t):return 'fast' if t in ('Fastball','Sinker','Cutter') else 'break' if t in ('Slider','Curveball','Sweeper') else 'off' if t in ('Changeup','Splitter') else 'unknown'
def score(row,train,allowed=None):
 proto=[];labels=[];sizes=[]
 for t,g in train.groupby('AtlasType'):
  if t in ('Undefined','Other','Knuckleball') or (allowed is not None and t not in allowed) or len(g)<8:continue
  values=g[F].to_numpy(float);m=np.median(values,axis=0);d=np.sqrt(np.mean(((values-m)/S)**2,axis=1));core=values[d<=max(1.6,np.quantile(d,.8))]
  if len(core)<8:continue
  proto.append(np.median(core,axis=0));labels.append(t);sizes.append(len(core))
 if not proto:return None
 d=np.sqrt(np.mean(((np.array(proto)-row[F].to_numpy(float))/S)**2,axis=1));order=np.argsort(d);bi=order[0];best=labels[bi];own=float(d[labels.index(row.AtlasType)]) if row.AtlasType in labels else None
 # Independent nearby examples, without the pitch itself.
 good=train[train.AtlasType.isin(labels)];v=good[F].to_numpy(float);nd=np.sqrt(np.mean(((v-row[F].to_numpy(float))/S)**2,axis=1));ix=np.argsort(nd)[:9]
 agreement=float(np.mean(good.AtlasType.iloc[ix].eq(best)))
 return best,float(d[bi]),own,agreement,int(sizes[bi]),float(d[order[1]]-d[bi]) if len(order)>1 else None
# Fit within pitcher/season, omitting the target recording where possible.
for (season,who,team),g in x.groupby(['Season','FinalPitcher','PitcherTeam']):
 measured=g[g.Measured];cow=who=='Cowdrey, Harrison';allowed=['Fastball','Curveball','Changeup']+(['Cutter'] if season not in ('Fall 2023','Spring 2024') else []) if cow else None
 for recording,q in g.groupby('GameUID'):
  train=measured[measured.GameUID.ne(recording)]
  external=len(train)>=35
  if not external:train=measured
  for idx,r in q.iterrows():
   if not r.Measured:
    if cow and r.AtlasType in ('Slider','Sinker','Undefined'):
     x.loc[idx,'FinalType']='Unclassified';entries.append({'uid':r.PitchUID,'season':season,'pitcher':who,'game':r.GameLabel.strip(),'no':int(r.PitchNo),'original':r.AtlasType,'candidate':'Unclassified','applied':True,'status':'unresolved-type','reason':'Reported Cowdrey arsenal excludes slider/sinker, but usable tracking is unavailable; no specific replacement forced.','distance':None,'ownDistance':None,'agreement':None,'support':0})
    continue
   z=score(r,train.drop(index=idx,errors='ignore'),allowed)
   if not z:continue
   best,dist,own,agree,support,gap=z
   invalid=cow and r.AtlasType in ('Slider','Sinker','Undefined')
   margin=(own-dist) if own is not None else None
   alternative=best!=r.AtlasType
   # Strict cross-family changes need compact alternative and overwhelming
   # neighbor consensus. Overlapping breaking-ball names are retained.
   strong=alternative and dist<=1.1 and agree>=8/9 and support>=12 and own is not None and own>=2.6 and margin>=1.8 and fam(best)!=fam(r.AtlasType)
   if cow and alternative and not invalid:
    strong=dist<=1.25 and agree>=8/9 and support>=12 and own is not None and own>=2.5 and margin>=1.7
   changed=False;status='retained-candidate'
   if invalid:
    if dist<=2.0 and (agree>=2/3 or (gap is not None and gap>=1.0)):changed=True;status='arsenal-inference'
    else:best='Unclassified';changed=True;status='unresolved-type'
   elif strong and not who.startswith('Unidentified'):
    changed=True;status='shape-inference'
   flagged=alternative and ((margin is not None and margin>=.8) or own is None)
   if changed or flagged:
    reason=(f"{'Other-recording' if external else 'Same-season leave-one-pitch-out'} shape comparison after pitcher correction: alternative distance {dist:.2f}; " + (f"current-type distance {own:.2f}; " if own is not None else 'current type lacks a supported cluster; ') +f"{agree:.0%} agreement among nine nearest reference pitches; {support} cluster examples. Statistical inference, not verified pitch intent.")
    if invalid:reason='User-reported Cowdrey no-slider arsenal constraint. '+reason
    if not changed:reason+=' Original retained: evidence below correction threshold or overlapping pitch-family names.'
    if status=='unresolved-type':reason+=' Specific replacement remains unresolved.'
    entries.append({'uid':r.PitchUID,'season':season,'pitcher':who,'game':r.GameLabel.strip(),'no':int(r.PitchNo),'original':r.AtlasType,'candidate':best,'applied':changed,'status':status,'reason':reason,'distance':dist,'ownDistance':own,'agreement':agree,'support':support})
    if changed:x.loc[idx,'FinalType']=best
pd.DataFrame(entries).to_csv(OUT/'type_decisions.csv',index=False)
x.to_pickle(OUT/'working_types_corrected.pkl')
z=pd.DataFrame(entries);print(z.groupby(['status','applied']).size().to_string());print('changes',z.applied.sum());print(z[z.applied].groupby(['pitcher','original','candidate']).size().to_string())
