"""Reviewed identity decisions. Original files are immutable.

Official PA identity is a candidate, not a blanket pitch attribution. Explicit
exceptions preserve sensor-supported mid-PA changes and conflicting sources.
"""
import json, pandas as pd, numpy as np
from identity_audit import ROOT,OUT,FEATURES,SCALE
x=pd.read_pickle(OUT/'working_reconciled.pkl');x['FinalPitcher']=x.Pitcher
entries={};cases=[]
def decide(rows,to,status,reason,case,source=''):
 for idx,r in rows.iterrows():
  assert r.PitchUID not in entries, (case,r.PitchUID)
  target=to or r.Pitcher
  entries[r.PitchUID]={'uid':r.PitchUID,'season':r.Season,'game':r.GameLabel.strip(),'gameUID':r.GameUID,'no':int(r.PitchNo),'original':r.Pitcher,'candidate':target,'applied':target!=r.Pitcher,'status':status,'reason':reason,'case':case,'source':source,'team':r.PitcherTeam}
  x.loc[idx,'FinalPitcher']=target
 cases.append({'case':case,'n':len(rows),'original':'; '.join(rows.Pitcher.unique()),'candidate':to or 'Original retained','status':status,'reason':reason,'source':source,'game':rows.GameLabel.iloc[0].strip() if len(rows) else ''})
# Physical release/movement and pauses locate the actual change inside the PA.
retain={(5971,'Burton, Clay'),(6484,'Walling, Jake'),(6874,'Carron, Andrew'),(6891,'Zimmerman, Andrew'),(6954,'Cowdrey, Harrison'),(7415,'Asher, Nolan'),(7436,'Lara, Lawrence'),(7438,'Lovett, Hunter'),(7675,'Rone, Isaac')}
external={(7405,'Courtwright, Reid'),(7421,'Kosobud, John')}
c=x[x.OfficialIdentity.ne('')&x.Pitcher.ne(x.OfficialIdentity)]
for (gid,fr,to),q in c.groupby(['PBP_GameID','Pitcher','OfficialIdentity']):
 case=f'official-{int(gid)}-{int(q.PitchNo.min())}'
 if (int(gid),fr) in retain:
  decide(q,None,'retained-mid-PA','The official event names the pitcher at PA completion. Earlier pitch release/movement still matches the original pitcher; retain the physical pitcher across the mid-PA substitution.',case,q.OfficialURL.iloc[0])
 elif (int(gid),fr) in external:
  decide(q,None,'unresolved-source-conflict','Official box/PBP omits this recorded pitcher, but release and movement contradict the proposed replacement. Keep the TrackMan identity pending scorebook/video confirmation; do not copy the PA pitcher.',case,q.OfficialURL.iloc[0])
 else:
  if int(gid)==7443 and fr=='Hagen, Joey' and to=='McGowan, John':to='Mason, Andrew'
  decide(q,to,'official-supported','Official appearance/substitution record reconciled with pitch order, release and movement. '+q.OfficialBasis.iloc[0]+(' Pitches 215–217 are Mason before the mid-PA change to McGowan at 218.' if case=='official-7443-215' else ''),case,q.OfficialURL.iloc[0])
# Unaligned event inside a continuous, independently resolved appearance.
q=x[x.PBP_GameID.eq(7413)&x.PitchNo.eq(295)]
decide(q,'Long, Austin','official-supported','Same uninterrupted Long appearance as adjacent pitches. Official Dominican roster and game box resolve the stale Doty identity.','official-7413-295','https://dustars.com/sports/baseball/stats/2026')
# Practice decisions use within-recording continuity plus other-recording profiles.
practice=[
 ('0e01ff87-fb9d-4a78-91ef-a68def06792e','Kempf, Will',180,187,'Christmas, Aidan','After a long recording pause, five stale/interleaved Kempf names have Christmas release and 88–91 mph fastballs, continuing among correctly named Christmas pitches. Kempf preceding outing is 81–83 mph with a different slot.'),
 ('e07f93ad-75c3-4b00-9c18-ba754d2d7b6c','Carr, Aidan',28,28,'Cowdrey, Harrison','Last pitch of Cowdrey inning matches his 87 mph, ~20-inch carry fastball and follows pitch 27 without a substitution pause. Carr’s later outing has a different fastball shape; this is an early name change.'),
 ('f906ccbc-ed49-490c-b299-fafbaeeb04a8','Slechter, Logan',148,148,'Carr, Aidan','First pitch after an outing break shifts to Carr’s high release and shorter extension and continues directly into named Carr pitches 149–152. Population nearest-neighbor Cowdrey is not sufficient to override this continuity.'),
 ('580c6ce5-4d66-40c4-aa74-66948825236c','Tegge, Cameron',117,117,'Schira, TJ','Right-handed pitch matches Schira immediately before a long substitution pause; the left-handed Tegge release begins at pitch 118. The PA-completion pitcher must not be backfilled.'),
 ('7bb74768-8ad2-4d92-ab50-361fc692b9fb','Heavern, Zach',1,20,'Livengood, Josh','First top-half outing has ~7.0 ft release and continues into named Livengood innings; Heavern throws from a different slot in the bottom half.'),
 ('a54eb46d-592c-425d-9e1d-45f5b7a8a4b3','Gerber, Jack',45,58,'Morgan, Luc','Inning 2 release shifts from Gerber (~6.0 ft) to Morgan (~5.2 ft, 2.4 ft side), continuing into the named Morgan outing.'),
 ('707488ea-b9ba-4f55-8106-833180c053a5','Livengood, Josh',66,72,'Gentile, Austin','Seven pitches begin the same low-slot outing continued under Gentile at pitch 73. Livengood earlier release is over 7 ft. Nearest population model alone suggested Zimmerman; same-game continuity resolves Gentile.'),
 ('707488ea-b9ba-4f55-8106-833180c053a5','Gentile, Austin',125,125,'Zimmerman, Trevor','First pitch of next outing matches named Zimmerman pitches 126 onward in release and extension.'),
 ('707488ea-b9ba-4f55-8106-833180c053a5','Kempf, Will',194,194,'Tegge, Cameron','Isolated right-handed name inside Tegge outing; pitch is left-handed and matches surrounding Tegge pitches.'),
 ('bddab60a-a8ce-4012-a4c8-85d1b008651e','Christmas, Aidan',156,176,'Kinsbrunner, David','Entire fourth-bottom outing has distinctive sidearm release (~4.0 ft height, 4.7 ft side) and low-70s velocity, consistent with Kinsbrunner in other recordings and inconsistent with Christmas.'),
 ('485d1d71-c54e-4af8-a691-39273917adbd','Bergeron, Lawson',68,89,'Zimmerman, Trevor','Right-handed inning follows left-handed Bergeron; ~5.1 ft height and long extension match Zimmerman. Next bottom-half entry is explicitly Zimmerman before McGriff.'),
 ('141a7990-86a8-41a2-bf68-68e20fc845e2','Christmas, Aidan',203,203,'Hansen, Aiden','Left-handed release and movement match Hansen pitches 205 onward; Christmas is right-handed.'),
 ('141a7990-86a8-41a2-bf68-68e20fc845e2','Zimmerman, Trevor',204,204,'Hansen, Aiden','Left-handed pitch between the Hansen-shaped 203 and named Hansen 205; ~-2.8 ft side matches Hansen, not right-handed Zimmerman.'),
 ('141a7990-86a8-41a2-bf68-68e20fc845e2','Carr, Aidan',180,180,'Zimmerman, Trevor','First pitch of following Zimmerman appearance; lower release, longer extension and breaking-ball shape align with Zimmerman pitches 181 onward.'),
 ('c01127f3-0c68-4c10-95d4-3198cd8731b3','McGriff, Ethan',99,99,'Gentile, Austin','First pitch of Gentile outing has the same distinctive submarine release (~2.6 ft height, 3.4 ft side) as following Gentile pitches.'),
 ('dd2b062d-86f8-40ae-950a-2dd1202047da','Waddle, Carson',71,73,'Shewmaker, Quinten','Three left-handed pitches immediately precede named Shewmaker with matching release; Waddle is right-handed. Recorded inning/half also lagged the transition and remains source context.'),
 ('dd2b062d-86f8-40ae-950a-2dd1202047da','Shewmaker, Quinten',83,83,'Zimmerman, Trevor','First right-handed pitch before named Zimmerman at 84; release/extension match his changeup, while Shewmaker is left-handed.'),
 ('cd9df7ca-465a-4d02-9340-7dab150f407e','Sickles, David',142,151,'Heavern, Zach','Inning 5 release rises from Sickles ~5.2 ft to ~6.1 ft, matching the next named Heavern inning and its arsenal. Both outings have consistent extension and pitch shapes.'),
 ('bcfd293e-42f9-4aa6-bde2-619c4db952f4','Cowdrey, Harrison',0,9999,'','special'),
]
for game,old,lo,hi,to,reason in practice:
 q=x[x.GameUID.eq(game)&x.Pitcher.eq(old)&x.PitchNo.between(lo,hi)]
 if reason=='special':
  for innings,to in [([3,4],'Heavern, Zach'),([5,6],'Christmas, Aidan')]:
   z=q[q.Inning.isin(innings)]
   decide(z,to,'strong-inference','Two consecutive innings form a separate release/movement cluster, matching this pitcher in other recordings. Cowdrey innings 1–2 retain his higher release and distinct fastball/breaking-ball shape. Independently corroborates the prior Cowdrey investigation.',f'practice-{game[:8]}-{innings[0]}')
 else:
  assert len(q), (game,old,lo)
  decide(q,to,'strong-inference',reason,f'practice-{game[:8]}-{lo}')
# This outing is clearly different, but the candidate identity is not established.
q=x[x.GameUID.eq('dd2b062d-86f8-40ae-950a-2dd1202047da')&x.Pitcher.eq('Cowdrey, Harrison')&x.Inning.eq(2)]
decide(q,'Unidentified pitcher · Sep 22 2024','unresolved-identity','Abrupt full-inning shift in velocity, spin, movement and release relative to Cowdrey inning 1. No sufficiently distinctive matching pitcher established. Remove from Cowdrey personal totals while retaining team/contact records; coach chart needed.','unresolved-cowdrey-20240922')
# Every other screened identity candidate stays visible, without forced reassignment.
for file in ['identity_pitch_candidates.csv','identity_block_candidates.csv']:
 q=pd.read_csv(OUT/file)
 for i,r in q.iterrows():
  uids=str(r.get('UIDs',r.get('PitchUID',''))).split('|');z=x[x.PitchUID.isin(uids)&~x.PitchUID.isin(entries)]
  if z.empty:continue
  decide(z,None,'retained-model-flag',f"Shape-only candidate: {r.Best}. Variation/overlap or insufficient independent evidence; original identity retained. Scores are distances, not probabilities.",f'model-{file[:5]}-{i}')
pd.DataFrame(entries.values()).to_csv(OUT/'identity_decisions.csv',index=False)
(OUT/'identity_cases.json').write_text(json.dumps(cases,indent=2))
x.to_pickle(OUT/'working_identity_corrected.pkl')
print('Identity decisions',len(entries),'changes',sum(r['applied'] for r in entries.values()))
print(pd.DataFrame(entries.values()).groupby(['status','applied']).size().to_string())
