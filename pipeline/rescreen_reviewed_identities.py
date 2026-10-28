"""Read-only second-pass identity screen on corrected data; never auto-reassigns."""
import json,pandas as pd
import identity_audit as core
original_out=core.OUT
x=pd.read_pickle(original_out/'final_audit_frame.pkl').copy()
x['Pitcher']=x.FinalPitcher;x['AtlasType']=x.FinalType
# Use the exact same reviewed handedness as the build, including new identities
# that have no correctly named original-season reference.
overlay=json.loads((core.ROOT/'pipeline/pitch_review_overlay.json').read_text())
hands={e['uid']:e['hand'] for e in overlay if e['field']=='pitcher'}
for idx,row in x.iterrows():
 if row.PitchUID in hands:x.loc[idx,'PitcherThrows']=hands[row.PitchUID]
core.OUT=original_out/'confirmation_rescreen';core.OUT.mkdir(exist_ok=True)
core.shape_screen(x)
print('All source records screened:',len(x),'eligible:',int(x.Eligible.sum()),flush=True)
