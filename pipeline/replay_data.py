"""Conservative batted-ball replay: source fits, bounded by reported tracking extent.
No fielder routes or catch coordinates are inferred. Outcomes remain operator tags.
"""
import math

def number(v):
    try:
        v=float(v)
        return v if math.isfinite(v) else None
    except (TypeError,ValueError): return None

def polynomial(c,t):
    value=0.0
    for coefficient in reversed(c): value=value*t+coefficient
    return value

def make_replay(row):
    result,kind=row['PlayResult'],row['TaggedHitType']
    air=kind in ('FlyBall','LineDrive','Popup')
    caught=air and result in ('Out','Sacrifice')
    category='caught' if caught else 'hit' if result in ('Single','Double','Triple','HomeRun') else 'other'
    label='Caught · inferred' if caught else {'HomeRun':'Home run','FieldersChoice':'Fielder’s choice','Error':'Reached on error'}.get(result,result)
    note=('Air-ball tag + recorded '+result.lower()+'. The files do not identify the fielder, catch time or catch point.' if caught else
          'Recorded hit. The files do not include the later pickup, throw or baserunning.' if category=='hit' else
          'Inconsistent sacrifice scoring: line drive, zero runs and zero recorded outs. PA outcome withheld pending confirmation.' if result=='Unscored' else 'Recorded result; an out on a ground ball or bunt does not establish an airborne catch.')
    data={'category':category,'outcome':label,'outcomeNote':note,'catchInferred':caught,
          'outsOnPlay':number(row.get('OutsOnPlay')),'available':False,'points':[],
          'lastTrackedDistance':number(row.get('LastTrackedDistance')),'duration':None,'endReason':None}
    if row['HitLaunchConfidence'] not in ('High','Medium'):
        data['reason']='Ball flight withheld: launch confidence is '+(str(row['HitLaunchConfidence']) if isinstance(row['HitLaunchConfidence'],str) and row['HitLaunchConfidence'] else 'missing')+'. Available positioning and the recorded outcome remain accessible.'
        return data
    coeff=[]
    for axis in 'XYZ':
        values=[number(row.get(f'HitTrajectory{axis}c{i}')) for i in range(9)]
        while values and values[-1] is None: values.pop()
        if len(values)<2 or any(v is None for v in values):
            data['reason']='Ball flight withheld: incomplete trajectory coefficients.';return data
        coeff.append(values)
    point=lambda t:[polynomial(c,t) for c in coeff]
    last=data['lastTrackedDistance'];hang=number(row.get('HangTime'))
    if last is None or last<=0:
        data['reason']='Ball flight withheld: no reported tracking extent.';return data
    start=point(0)
    if not 0<=start[1]<=8 or math.hypot(start[0],start[2])>=last:
        data['reason']='Ball flight withheld: invalid launch point or tracking extent.';return data
    # Contact is t=0. MeasuredDuration is blank in all six source exports.
    # First crossing of the reported radial extent is a conservative fit boundary,
    # not an observation of the catch time. Never extrapolate a rolling ball.
    trusted_hang=hang if row['HitLandingConfidence'] in ('High','Medium') and hang and 0<hang<=8 else None
    cap=trusted_hang or 8.0
    end=None;end_reason=None
    for i in range(1,4001):
        t=cap*i/4000;v=point(t)
        if not all(math.isfinite(x) for x in v) or abs(v[0])>600 or abs(v[2])>600 or v[1]>250:
            data['reason']='Ball flight withheld: trajectory fails physical bounds.';return data
        ground=v[1]<=0;extent=math.hypot(v[0],v[2])>=last
        if ground or extent:
            lo=cap*(i-1)/4000;hi=t
            for _ in range(35):
                mid=(lo+hi)/2;mv=point(mid)
                if mv[1]<=0 or math.hypot(mv[0],mv[2])>=last: hi=mid
                else: lo=mid
            end=(lo+hi)/2;v=point(end)
            end_reason='ground' if abs(v[1])<1e-6 else 'tracking'
            break
    if end is None and trusted_hang: end=cap;end_reason='reported-hang'
    if end is None or end<=0:
        data['reason']='Ball flight withheld: no defensible endpoint within the fitted interval.';return data
    points=[]
    for i in range(121):
        t=end*i/120;x,h,z=point(t)
        # The display convention is lateral (+first base), forward, height; feet.
        points.append([round(t,6),round(z,5),round(x,5),round(max(0,h),5)])
    data.update(available=True,points=points,duration=round(end,6),endReason=end_reason,
                coefficients=coeff,reason='TrackMan polynomial fit, stopped at the earliest reported tracking-distance boundary, ground crossing or reliable reported hang time. Time is reconstructed from the fit; no catch location is assigned.')
    return data
