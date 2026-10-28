"""Exploratory follow-up for the unidentified September 22 outing; no corrections."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'audit_2026_10_27'
a=pd.read_pickle(OUT/'final_audit_frame.pkl')
cols=['RelSpeed','InducedVertBreak','HorzBreak','SpinRate','RelHeight','RelSide','Extension']
scale=np.array([2,4,4,200,.25,.3,.5])
target=a[a.GameUID.eq('dd2b062d-86f8-40ae-950a-2dd1202047da')&a.PitchNo.between(32,46)]
assert len(target)==15
# Compare like physical families without assuming the source type is correct.
# This small-sample distance is exploratory, not an identity probability.
def families(g):
 return g[(g.RelSpeed>76)&(g.InducedVertBreak>0)],g[(g.RelSpeed<75)&(g.InducedVertBreak<0)]
tfb,tcb=families(target)
ref=a[a.PitcherTeam.eq('CEN_COL')&a.Measured&~a.GameUID.eq(target.GameUID.iloc[0])&a.Season.isin(['Spring 2024','Fall 2024','Spring 2025'])]
candidates=[]
for (name,game,label),g in ref.groupby(['FinalPitcher','GameUID','GameLabel']):
 fb,cb=families(g)
 if len(fb)<3 or len(cb)<2:continue
 distance=np.mean([np.sqrt(np.mean(((p[cols].median().values-t[cols].median().values)/scale)**2)) for p,t in [(fb,tfb),(cb,tcb)]])
 candidates.append({'pitcher':name,'game':label,'distance':round(float(distance),4),'fastballs':len(fb),'curves':len(cb),'fastballMedian':fb[cols].median().round(3).to_dict(),'curveMedian':cb[cols].median().round(3).to_dict()})
result={'status':'historical-comparison-superseded-by-user-confirmation','note':'This comparison originally left the outing unidentified because references overlapped. The user subsequently confirmed all 15 pitches as Rone on October 27, 2026; the current overlay uses that confirmation. This script preserves the statistical comparison and does not change labels.','target':{'fastballMedian':tfb[cols].median().round(3).to_dict(),'curveMedian':tcb[cols].median().round(3).to_dict()},'candidates':sorted(candidates,key=lambda c:c['distance'])[:10],'officialChecks':[{'url':'https://centrecolonels.com/sports/baseball/schedule/2024','finding':'Published schedule ends in May; September intrasquad absent.'},{'url':'https://centrecolonels.com/sports/baseball/schedule/2025','finding':'Published schedule starts in February 2025; September intrasquad absent.'},{'url':'https://centrecolonels.com/sports/baseball/archives?season=2024&path=baseball','finding':'Archive jumps from October 1 giving campaign to August 27 sportsmanship announcement; no September game report.'},{'url':'https://centrecolonels.com/sports/baseball/archives?season=0&path=baseball&q=intrasquad','finding':'Search returns 2019 USA Baseball staff announcement and 2010 Black/Gold game; no 2024 intrasquad.'}]}
(OUT/'unidentified_followup.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'decision':result['note'],'bestCandidates':[{k:c[k] for k in ['pitcher','game','distance']} for c in result['candidates'][:3]]},indent=2))
