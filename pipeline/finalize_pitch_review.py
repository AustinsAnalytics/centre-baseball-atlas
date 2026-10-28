"""Apply explicitly reviewed Cowdrey shape anchors and refresh latest identities."""
import numpy as np,pandas as pd,json
from identity_audit import OUT,ROOT
x=pd.read_pickle(OUT/'working_types_corrected.pkl');ident=pd.read_pickle(OUT/'working_identity_corrected.pkl').set_index('PitchUID');x['FinalPitcher']=x.PitchUID.map(ident.FinalPitcher)
d=pd.read_csv(OUT/'type_decisions.csv').fillna('');by={r['uid']:r for r in d.to_dict('records')}
# Sparse early seasons cannot learn a changeup from only three reference tags.
# Hand-reviewed separated shape regions resolve only clear families. The cutter /
# curve boundary remains unforced in the overlapping negative-to-zero IVB band.
for i,r in x[x.FinalPitcher.eq('Cowdrey, Harrison')&x.Measured].iterrows():
 v,ivb,hb,spin=r.RelSpeed,r.InducedVertBreak,r.HorzBreak,r.SpinRate
 candidate=None;why=''
 if 68<=v<=79 and ivb<=-6 and hb<5 and 1950<=spin<=2850:
  candidate='Curveball';why='Clear high-spin, downward-breaking shape in Cowdrey’s reported no-slider arsenal.'
 elif 73<=v<=83 and 7<=ivb<=21 and hb>=9 and 1400<=spin<=2100:
  candidate='Changeup';why='Slower arm-side pitch with reduced spin, separated from the breaking-ball and fastball cores.'
 elif r.Season not in ('Fall 2023','Spring 2024') and 76<=v<=83 and 1<=ivb<=12 and -10<=hb<=6 and 2100<=spin<=2700:
  candidate='Cutter';why='Established later-season cutter core: mid/low-80s or upper-70s speed, shallow vertical break, limited horizontal run and elevated spin. Curve/cutter overlap below +1 inch IVB is not forced.'
 elif v>=83 and ivb>=15 and -1<=hb<=12 and 1950<=spin<=2550:
  candidate='Fastball';why='High-velocity, high-carry fastball core separated from the slower cutter and breaking ball.'
 if candidate and candidate!=r.FinalType:
  # Already-mislabeled identities are gone before this arsenal-specific pass.
  x.loc[i,'FinalType']=candidate
  by[r.PitchUID]={'uid':r.PitchUID,'season':r.Season,'pitcher':r.FinalPitcher,'game':r.GameLabel.strip(),'no':int(r.PitchNo),'original':r.AtlasType,'candidate':candidate,'applied':candidate!=r.AtlasType,'status':'arsenal-shape-review','reason':why+' Identity was reviewed first. Analytical shape label under the user-reported arsenal constraint; pitch intent is not independently verified.','distance':None,'ownDistance':None,'agreement':None,'support':None}
# Updated identity boundary cases do not silently inherit another pitcher's review.
for uid,r in list(by.items()):
 who=ident.loc[uid,'FinalPitcher']
 if r['pitcher']!=who:
  r['pitcher']=who
  if r['applied']:
   x.loc[x.PitchUID.eq(uid),'FinalType']=x.loc[x.PitchUID.eq(uid),'AtlasType'];r['applied']=False;r['status']='retained-after-identity-review';r['reason']='Identity boundary changed during final review; type retained pending reference review.'
pd.DataFrame(by.values()).to_csv(OUT/'type_decisions_final.csv',index=False)
x.to_pickle(OUT/'final_audit_frame.pkl')
print('New applied type decisions',sum(bool(r['applied']) for r in by.values()))
print(x[x.FinalPitcher.eq('Cowdrey, Harrison')].groupby(['Season','FinalType']).size().to_string())
