"""Compact evidence packet for human-readable identity adjudication; no edits."""
import pandas as pd,json,numpy as np
from identity_audit import OUT,FEATURES
x=pd.read_pickle(OUT/'working_reconciled.pkl'); boxes={r['game']:r for r in json.loads((OUT/'official_pitching.json').read_text())}
lines=[]
for gid,g in x[x.PBP_GameID.notna()].groupby('PBP_GameID',sort=True):
 c=g[g.OfficialIdentity.ne('')&g.Pitcher.ne(g.OfficialIdentity)]
 if c.empty:continue
 lines.append('\n### '+str(int(gid))+' '+g.GameLabel.iloc[0])
 for t in boxes[int(gid)]['teams']:lines.append(t['team']+': '+', '.join(p['name']+' '+p.get('IP','?')+'IP/'+p.get('NP','?')+'p' for p in t['pitchers']))
 for (who,to),q in c.groupby(['Pitcher','OfficialIdentity']):
  lines.append(f'CHANGE {who} -> {to}: {len(q)} rows, pitch {int(q.PitchNo.min())}-{int(q.PitchNo.max())}')
  for inn,iq in q.groupby('Inning'):
   block=g[g.Inning.eq(inn)&g.Half.eq(iq.Half.iloc[0])].sort_values('PitchNo')
   lines.append('inning '+str(inn)+' '+iq.Half.iloc[0])
   lines.append(block[['PitchNo','Pitcher','OfficialIdentity','Batter','PitchofPA','Balls','Strikes','PitchType','RelSpeed','RelHeight','RelSide','Extension','PA_Description']].round(2).to_string(index=False))
(OUT/'identity_evidence_packet.txt').write_text('\n'.join(lines))
print(len(lines),'lines generated')
