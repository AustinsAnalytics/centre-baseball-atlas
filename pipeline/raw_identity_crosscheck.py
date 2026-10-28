"""Cross-check raw name/ID/hand against the derived archive; read-only."""
from pathlib import Path
import pandas as pd,json
from identity_audit import ROOT,SRC,OUT,canonical
a=pd.read_pickle(OUT/'working_source.pkl');parts=[]
cols=['PitchUID','PitchNo','Pitcher','PitcherId','PitcherThrows','TaggedPitchType','AutoPitchType','RelHeight','RelSide','GameUID','Date']
for source in a.SourceFile.dropna().unique():
 p=SRC/'Trackman Folders'/source
 if not p.exists():p=SRC/'Fall26'/source
 if not p.exists():continue
 read=pd.read_excel if p.suffix=='.xlsx' else pd.read_csv
 opts={} if p.suffix=='.xlsx' else {'low_memory':False}
 raw=read(p,usecols=lambda c:c in cols,**opts);raw['RawSourceFile']=str(p.relative_to(SRC));parts.append(raw)
raw=pd.concat(parts,ignore_index=True).drop_duplicates('PitchUID');raw['Pitcher']=raw.Pitcher.map(canonical)
raw=raw.rename(columns={c:'Source_'+c for c in raw if c!='PitchUID'})
j=a.merge(raw,on='PitchUID',how='left',validate='one_to_one')
ids={pid:list(g.Source_Pitcher.dropna().unique()) for pid,g in j.groupby('Source_PitcherId')}
j['RawIdOtherNames']=j.Source_PitcherId.map(lambda x:'|'.join(ids.get(x,[])))
mask=j.Pitcher.ne(j.Source_Pitcher)|j.PitcherThrows.ne(j.Source_PitcherThrows)|j.PitcherId.ne(j.Source_PitcherId)
j.loc[mask,['PitchUID','Season','GameLabel','PitchNo','Pitcher','PitcherId','PitcherThrows','Source_Pitcher','Source_PitcherId','Source_PitcherThrows','RawIdOtherNames','Source_RawSourceFile']].to_csv(OUT/'raw_identity_differences.csv',index=False)
j.to_pickle(OUT/'working_source_raw.pkl')
print('Raw rows',len(raw),'matched',j.Source_Pitcher.notna().sum(),'identity metadata differences',mask.sum())
print(j[mask].groupby(['Pitcher','Source_Pitcher','PitcherThrows','Source_PitcherThrows']).size().to_string())
