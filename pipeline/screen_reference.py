from pathlib import Path
import json
import numpy as np
import pandas as pd

import argparse
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);args=ap.parse_args()
ROOT=args.source
OUT=Path(__file__).resolve().parent
hist=pd.read_csv(ROOT/'Colonels_Analytics/data/centre_pitch_by_pitch_master.csv',low_memory=False)
fall=pd.read_csv(ROOT/'Fall26/Fall26_Studio/audit/pitches_clean.csv',low_memory=False)


def scan(d, label, source):
    d=d.copy().reset_index(drop=True)
    d['AHB']=np.where(d.PitcherThrows.eq('Left'),-d.HorzBreak,d.HorzBreak)
    d['ArmRelease']=np.where(d.PitcherThrows.eq('Left'),-d.RelSide,d.RelSide)
    features=['RelSpeed','InducedVertBreak','AHB','SpinRate']
    scales=np.array([1.7,3.,3.,160.])
    # Only flag agreement between two differently weighted shape comparisons.
    weights=np.array([[1,1,1,1],[1.5,1,1,.5],[1,1.3,1.3,.4]])
    ok=d[features].notna().all(axis=1)&d.RelSpeed.between(45,105)&d.SpinRate.between(300,4000)
    blank={'Undefined','Other','Unknown','nan',''}
    d[label]=d[label].astype(str)
    d['Scope']=source
    flags=[];evaluated=0;groups=0
    for key,g in d[ok].groupby(['Pitcher','GameUID']):
        families=[t for t,n in g[label].value_counts().items() if n>=4 and t not in blank]
        if len(families)<2:continue
        groups+=1
        X=g[features].to_numpy(float)
        labs=g[label].to_numpy()
        # Leave target out of its own prototype. Alternatives are disjoint.
        for j,(idx,row) in enumerate(g.iterrows()):
            protos=[];names=[];sizes=[]
            for typ in families:
                member=np.flatnonzero(labs==typ)
                member=member[member!=j]
                if len(member)<4:continue
                core=X[member]
                med=np.median(core,axis=0)
                dist=np.linalg.norm((core-med)/scales,axis=1)
                keep=dist<=max(2.5,float(np.quantile(dist,.75)))
                if keep.sum()>=4:med=np.median(core[keep],axis=0)
                names.append(typ);protos.append(med);sizes.append(len(member))
            if len(names)<2:continue
            evaluated+=1
            delta=(np.array(protos)-X[j])/scales
            dist=np.sqrt((delta[None,:,:]**2*weights[:,None,:]).sum(axis=2))
            best=dist.argmin(axis=1)
            if not np.all(best==best[0]):continue
            k=int(best[0]);alt=names[k];orig=row[label]
            if alt==orig:continue
            oi=names.index(orig) if orig in names else None
            own=float(dist[0,oi]) if oi is not None else np.nan
            near=float(dist[0,k]); margin=own-near
            # A screening threshold, NOT an empirical error probability.
            strong=(oi is not None and near<=2.5 and own>=4.5 and margin>=2.5)
            sparse=(oi is None and near<=2.0)
            if not (strong or sparse):continue
            q=(X-X[j])/scales
            nd=np.linalg.norm(q,axis=1);nd[j]=np.inf
            nearest=np.argsort(nd)[:min(7,len(nd)-1)]
            knn=float(np.mean(labs[nearest]==alt))
            if strong and knn<.7:continue
            rec={c:row[c] for c in ['PitchUID','Pitcher','PitcherTeam','GameUID','PitchNo','TaggedPitchType','RelSpeed','InducedVertBreak','HorzBreak','AHB','SpinRate','RelHeight','RelSide','Extension','PitchMovementConfidence','PitchReleaseConfidence'] if c in row}
            rec.update(Source=source,CurrentType=orig,Alternative=alt,OwnDistance=own,AlternativeDistance=near,DistanceMargin=margin,NeighborAgreement=knn,AlternativeSupport=sizes[k],Screen='strong-same-outing' if strong else 'sparse-label-review',AlternativePrototype=dict(zip(features,np.round(protos[k],2))))
            for col in ['Season','GameDate','GameLabel','Session','SessionNo','SourceFile','Eligible','DecisionConfidence','ReviewReason']:
                if col in row:rec[col]=row[col]
            flags.append(rec)
    flags=pd.DataFrame(flags)
    if len(flags):flags=flags.sort_values(['Screen','DistanceMargin'],ascending=[True,False])
    flags.to_csv(OUT/f'{source}_pitch_tag_screen.csv',index=False)
    print(source,'rows',len(d),'measured',int(ok.sum()),'evaluated multi-family',evaluated,'outings',groups,'flags',len(flags))
    if len(flags):
        print(flags.groupby(['Screen','CurrentType','Alternative']).size().to_string())
        print('CENTRE TOP',flags[flags.PitcherTeam.eq('CEN_COL')].head(30).to_json(orient='records'))
    return flags

H=scan(hist,'PitchType','historical')
print('FALL TYPE OPTIONS',[c for c in fall if any(x in c.lower() for x in ['type','final','eligible'])])
flabel='CleanPitchType' if 'CleanPitchType' in fall else 'FinalPitchType' if 'FinalPitchType' in fall else 'PitchType' if 'PitchType' in fall else 'TaggedPitchType'
F=scan(fall,flabel,'fall26_reviewed')
