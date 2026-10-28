"""Export the reviewed, versioned UID overlay, full coverage ledger and report."""
import pandas as pd,numpy as np,json,gzip,hashlib
from identity_audit import ROOT,OUT
x=pd.read_pickle(OUT/'final_audit_frame.pkl');ids=pd.read_csv(OUT/'identity_decisions.csv').fillna('');types=pd.read_csv(OUT/'type_decisions_final.csv').fillna('');im={r['uid']:r for r in ids.to_dict('records')};tm={r['uid']:r for r in types.to_dict('records')}
raw=pd.read_pickle(OUT/'working_source_raw.pkl').set_index('PitchUID')
# Preserve every previously published player ID, including reserved inactive IDs.
registry_path=ROOT/'pipeline/player_registry.json'
if not registry_path.exists():
 registry=json.loads((OUT/'baseline_data/index.json').read_text())['players']
 registry_path.write_text(json.dumps([{k:p[k] for k in ('id','name','display','team','centre')} for p in registry],separators=(',',':')))
changes=[];ledger=[];events=[]
for i,r in x.iterrows():
 identity=im.get(r.PitchUID);typ=tm.get(r.PitchUID)
 hand=r.PitcherThrows;pid=str(r.PitcherId) if pd.notna(r.PitcherId) else ''
 if r.FinalPitcher!=r.Pitcher:
  target=x[x.Pitcher.eq(r.FinalPitcher)&x.PitcherTeam.eq(r.PitcherTeam)&x.Pitcher.eq(x.FinalPitcher)]
  if len(target):
   h=target.PitcherThrows.dropna().mode();hand=h.iloc[0] if len(h) else ''
   pp=target.PitcherId.dropna().mode();pid=str(pp.iloc[0]) if len(pp) else ''
  else:
   rr=x[x.FinalPitcher.eq(r.FinalPitcher)&x.PitcherTeam.eq(r.PitcherTeam)&x.Measured];side=rr.RelSide.median()
   hand='Left' if side<-.75 else 'Right' if side>.75 else '';pid=''
  if r.FinalPitcher=='Hoover, B.' and r.PitcherTeam=='BIR_COL':hand='Right' # 2024 official BSC roster: Ben Hoover, RHP.
  changes.append({'uid':r.PitchUID,'field':'pitcher','before':r.Pitcher,'after':r.FinalPitcher,'hand':hand,'pitcherId':pid,'status':identity['status'],'case':identity['case'],'reason':identity['reason'],'source':identity['source']})
 if r.FinalType!=r.AtlasType:
  changes.append({'uid':r.PitchUID,'field':'type','before':r.AtlasType,'after':r.FinalType,'status':typ['status'],'case':'type-'+r.PitchUID,'reason':typ['reason'],'source':'User-reported Cowdrey arsenal + supplied TrackMan measurements' if r.FinalPitcher=='Cowdrey, Harrison' else 'Supplied TrackMan measurements'})
 record={'PitchUID':r.PitchUID,'Season':r.Season,'Game':r.GameLabel.strip(),'PitchNo':r.PitchNo,'Eligible':bool(r.Eligible),'Team':r.PitcherTeam,'OriginalFilePitcher':raw.loc[r.PitchUID].get('Source_Pitcher',''),'PreviousAtlasPitcher':r.Pitcher,'ReviewedPitcher':r.FinalPitcher,'ReviewedHand':hand,'OriginalTag':r.TaggedPitchType,'PreviousAtlasType':r.AtlasType,'ReviewedType':r.FinalType,'IdentityStatus':identity['status'] if identity else 'screened-no-change','TypeStatus':typ['status'] if typ else ('reviewed-fall-retained' if r.Season=='Fall 2026' else 'screened-no-change'),'MeasuredForScreen':bool(r.Measured),'OfficialPitcherAtPAEnd':r.OfficialIdentity,'IdentityReason':identity['reason'] if identity else 'No supported identity correction established; this is not independent certification.','TypeReason':typ['reason'] if typ else 'Prior analytical label retained; absence of a flag does not verify pitch intent.','Source':identity['source'] if identity else r.OfficialURL}
 ledger.append(record)
for r in ids.to_dict('records'):events.append({**r,'kind':'identity','pitcher':r['candidate'] if r['applied'] else r['original']})
for r in types.to_dict('records'):events.append({**r,'kind':'type','screen':'Identity-aware review'})
def safe(v):
 if isinstance(v,dict):return {k:safe(z) for k,z in v.items()}
 if isinstance(v,list):return [safe(z) for z in v]
 if isinstance(v,(float,np.floating)) and not np.isfinite(v):return None
 if isinstance(v,np.integer):return int(v)
 if isinstance(v,np.bool_):return bool(v)
 return v
(ROOT/'pipeline/pitch_review_overlay.json').write_text(json.dumps(safe(changes),separators=(',',':'),ensure_ascii=False))
(ROOT/'pipeline/pitch_review_events.json').write_text(json.dumps(safe(events),separators=(',',':'),ensure_ascii=False))
public=ROOT/'site/review';public.mkdir(exist_ok=True)
ld=pd.DataFrame(ledger);csv=ld.to_csv(index=False);(OUT/'all_pitch_decisions.csv').write_text(csv);(public/'all-pitch-decisions.csv.gz').write_bytes(gzip.compress(csv.encode(),mtime=0))
ids.to_csv(public/'pitcher-decisions.csv',index=False);types.to_csv(public/'pitch-type-decisions.csv',index=False)
cases=json.loads((OUT/'identity_cases.json').read_text());(ROOT/'pipeline/pitch_review_cases.json').write_text(json.dumps(cases,separators=(',',':'),ensure_ascii=False))
summary={'date':'2026-10-27','records':len(x),'eligible':int(x.Eligible.sum()),'seasons':7,'officialGames':94,'officialAligned':int(x.OfficialIdentity.ne('').sum()),'identityChanges':int(ids.applied.sum()),'knownIdentityChanges':int((ids.applied&ids.status.ne('unresolved-identity')).sum()),'identityOfficial':int((ids.applied&ids.status.eq('official-supported')).sum()),'identityInferred':int((ids.applied&ids.status.eq('strong-inference')).sum()),'identityConfirmed':int((ids.applied&ids.status.eq('user-confirmed')).sum()),'unidentified':int(x.FinalPitcher.str.startswith('Unidentified pitcher').sum()),'typeChanges':int((x.FinalType!=x.AtlasType).sum()),'identityRetained':int((~ids.applied).sum()),'typeRetained':int((~types.applied).sum()),'cowdreyRemoved':int((x.Pitcher.eq('Cowdrey, Harrison')&x.FinalPitcher.ne(x.Pitcher)).sum()),'cowdreySlidersBefore':int((x.Pitcher.eq('Cowdrey, Harrison')&x.AtlasType.eq('Slider')).sum()),'cowdreySlidersAfter':int((x.FinalPitcher.eq('Cowdrey, Harrison')&x.FinalType.eq('Slider')).sum()),'cowdreyUnclassified':int((x.FinalPitcher.eq('Cowdrey, Harrison')&x.FinalType.eq('Unclassified')).sum()),'cases':cases}
(ROOT/'pipeline/pitch_review_summary.json').write_text(json.dumps(summary,separators=(',',':'),ensure_ascii=False));print({k:v for k,v in summary.items() if k!='cases'})
assert len(ld)==40126 and ld.PitchUID.nunique()==40126
assert len(changes)==summary['identityChanges']+summary['typeChanges']
