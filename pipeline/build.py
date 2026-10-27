#!/usr/bin/env python3
"""Build static Centre Atlas data from reviewed sources. Original exports stay untouched."""
from pathlib import Path
import argparse,json,math,hashlib,collections,datetime,sys
import pandas as pd
import numpy as np
from replay_data import make_replay
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT.parents[1]);args=ap.parse_args();SRC=args.source
OUT=ROOT/'site/data';OUT.mkdir(exist_ok=True,parents=True)
def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x) for x in v]
 if isinstance(v,(np.integer,)):return int(v)
 if isinstance(v,(float,np.floating)):return round(float(v),4) if math.isfinite(v) else None
 if isinstance(v,(np.bool_,)):return bool(v)
 return v

def dump(name,data):
 (OUT/name).write_text(json.dumps(clean(data),separators=(',',':'),ensure_ascii=False,allow_nan=False))
def n(v):
 try:return float(v) if math.isfinite(float(v)) else None
 except:return None
def yes(v):return v is True or str(v).lower() in ('true','1')
def name(v):
 if not isinstance(v,str) or not v.strip():return 'Unknown player'
 v=v.strip();return {'Vallone, Tristen':'Vallone, Tristan','Taylor, Wesley':'Taylor, Wes','Tayor, Wesley':'Taylor, Wes'}.get(v,v)
def s(v):return str(v) if pd.notna(v) else ''
def avg(xs):
 xs=[x for x in xs if x is not None];return sum(xs)/len(xs) if xs else None
def ratio(a,b):return a/b if b else None
def pack(rows):
 if not rows:return {'columns':[],'rows':[]}
 keys=list(rows[0]);return {'columns':keys,'rows':[[r.get(k) for k in keys] for r in rows]}
def numrow(r,k):return n(r.get(k))
H=SRC/'Colonels_Analytics';F=SRC/'Fall26/Fall26_Studio'
h=pd.read_csv(H/'data/centre_pitch_by_pitch_master.csv',low_memory=False)
fall=json.load(open(F/'site/data/fall.json'))
fall_raw=pd.read_csv(F/'audit/pitches_clean.csv',low_memory=False)
fall_lookup=fall_raw.set_index('PitchUID').to_dict('index')
meta=json.load(open(H/'site/data/meta.json'));pbp=json.load(open(H/'site/data/pbp.json'))
manifest=[]
for p in [H/'data/centre_pitch_by_pitch_master.csv',H/'data/pbp_events_all_games.csv',H/'site/data/pbp.json',F/'site/data/fall.json',F/'audit/pitches_clean.csv',F/'audit/plate_appearances.csv',H/'site/data/meta.json',H/'fielding_app/data_build/fielder_lines.csv',H/'fielding_app/data_build/throws.csv',SRC/'Trackman Folders/Spring25/Games/Berry 2 PP.csv']:
 manifest.append({'file':str(p.relative_to(SRC)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
# Exact-ID overlay repairs R's mangled numerical column prefixes, preserving original master.
berry=SRC/'Trackman Folders/Spring25/Games/Berry 2 PP.csv';bp=pd.read_csv(berry);bp=bp.rename(columns={c:c[1:] for c in bp if c.startswith(('X1B_','X2B_','X3B_'))}).set_index('PitchUID');repairs=collections.Counter()
for c in bp:
 if c.startswith(('1B_','2B_','3B_')) and c in h:
  mapped=h.PitchUID.map(bp[c]);mask=h[c].isna()&mapped.notna();h.loc[mask,c]=mapped[mask];repairs[c]=int(mask.sum())
# Apply only extreme cross-family statistical candidates; preserve original and all remaining candidates.
screen=pd.read_csv(ROOT/'pipeline/historical_pitch_tag_screen.csv').set_index('PitchUID')
def family(t):return 'fast' if t in ('Fastball','Sinker','Cutter') else 'break' if t in ('Slider','Curveball','Sweeper') else 'off' if t in ('Changeup','Splitter') else t
corrections={};flags={};hi=h.set_index('PitchUID')
for uid,r in screen.iterrows():
 strong=(r.DistanceMargin>=7 and r.AlternativeDistance<=1.5 and r.NeighborAgreement==1 and r.AlternativeSupport>=8 and family(r.CurrentType)!=family(r.Alternative) and not yes(hi.loc[uid,'Flag_ReleaseSideVsHand']))
 reason=f"Same-outing shape screen: {int(r.AlternativeSupport)} alternative pitches; {r.AlternativeDistance:.2f} scaled distance to alternative; {r.NeighborAgreement:.0%} agreement among seven neighbors. Statistical inference, not verified pitch intent."
 entry={'uid':uid,'original':r.CurrentType,'candidate':r.Alternative,'applied':strong,'reason':reason,'margin':n(r.DistanceMargin),'distance':n(r.AlternativeDistance),'support':int(r.AlternativeSupport),'screen':r.Screen,'pitcher':name(r.Pitcher),'season':r.Season,'date':r.GameDate,'no':int(r.PitchNo)}
 flags[uid]=entry
 if strong:corrections[uid]=r.Alternative
players=[];playerids={}
def player(nm,team):
 nm=name(nm);team=team or 'Unknown';key=(nm,team)
 if key not in playerids:
  playerids[key]=len(players);players.append({'id':len(players),'name':nm,'display':' '.join(nm.split(', ')[::-1]),'team':team,'centre':team=='CEN_COL','seasons':[],'pitching':0,'hitting':0,'fielding':0})
 return playerids[key]
games=[];gmap={};oldg={};pbpg={}
for i,g in enumerate(meta['games']):
 item={'id':len(games),'key':g['key'],'date':g['date'],'season':g['season'],'kind':g['session'],'opponent':g['opp'],'label':g['label'],'tracked':bool(g['tracked']),'pbp':g['pbp'],'n':g['n'] or 0}
 games.append(item);oldg[i]=item['id']
 if g['seq'] is not None:gmap[int(g['seq'])]=item['id']
 if g['pbp'] is not None:pbpg[int(g['pbp'])]=item['id']
fg={}
for g in fall['sessions']:
 gid=len(games);fg[g['id']]=gid;games.append({'id':gid,'key':g['id'],'date':g['date'],'season':'Fall 2026','kind':'Fall Intrasquad' if g['competition']=='intrasquad' else 'Fall Scrimmage','opponent':g['opponent'],'label':g['label']+' · '+('Intrasquad' if g['opponent']=='Centre' else g['opponent']),'tracked':True,'pbp':None,'n':sum(p['session']==g['id'] for p in fall['pitches'])})
seasons=['Fall 2023','Spring 2024','Fall 2024','Spring 2025','Fall 2025','Spring 2026','Fall 2026']
P={x:[] for x in seasons};A={x:[] for x in seasons};B={x:[] for x in seasons};R={x:[] for x in seasons};positions=collections.defaultdict(list);team_positions=collections.defaultdict(list)
# One consistent field of play schema. Raw horizontal coordinates retained; view orientation handled once by client.
for r in h.to_dict('records'):
 uid=r['PitchUID'];team=s(r['PitcherTeam']);bt=s(r['BatterTeam']);pi=player(r['Pitcher'],team);bi=player(r['Batter'],bt);ci=player(r['Catcher'],team) if isinstance(r['Catcher'],str) else None;season=r['Season'];gid=gmap[int(r['GameSeq'])]
 loc=r['PitchLocationConfidence'] in ('High','Medium') and n(r['PlateLocSide']) is not None and n(r['PlateLocHeight']) is not None
 ev=r['PitchCall']=='InPlay' and r['HitLaunchConfidence'] in ('High','Medium') and n(r['ExitSpeed']) is not None
 landing=ev and r['HitLandingConfidence'] in ('High','Medium') and n(r['Distance']) is not None and n(r['Bearing']) is not None
 hand=s(r['PitcherThrows']);rawhb=n(r['HorzBreak']);t=corrections.get(uid,r['PitchType'])
 resolved=s(r['PA_Result']) if yes(r['IsPA']) and s(r['PA_Result']) not in ('','Incomplete','Unknown') else s(r['PlayResult'])
 pr={'u':uid,'g':gid,'p':pi,'b':bi,'c':ci,'t':t,'ot':r['TaggedPitchType'],'baseType':r['PitchType'],'no':int(r['PitchNo']),'inn':r['Inning'],'half':s(r['TopBottom']),'hand':hand,'bats':s(r['BatterSide']),'v':n(r['RelSpeed']),'ivb':n(r['InducedVertBreak']),'hb':rawhb,'ahb':(-rawhb if hand.startswith('L') else rawhb) if rawhb is not None else None,'spin':n(r['SpinRate']),'rh':n(r['RelHeight']),'rs':n(r['RelSide']),'ext':n(r['Extension']),'vaa':n(r['VertApprAngle']),'px':n(r['PlateLocSide']),'pz':n(r['PlateLocHeight']),'loc':loc,'ev':n(r['ExitSpeed']) if ev else None,'la':n(r['Angle']) if ev else None,'dir':n(r['Direction']) if ev else None,'dist':n(r['Distance']) if landing else None,'bearing':n(r['Bearing']) if landing else None,'call':s(r['PitchCall']),'result':resolved,'rawResult':s(r['PlayResult']),'hit':s(r['TaggedHitType']),'balls':n(r['Balls']),'strikes':n(r['Strikes']),'pa':f'H{gid}-{int(r["PAofGame"])}' if n(r['PAofGame']) is not None else None,'review':2 if uid in corrections else 1 if uid in flags else 0,'lc':s(r['PitchLocationConfidence']),'hc':s(r['HitLaunchConfidence']),'rc':s(r['PitchReleaseConfidence']),'outs':n(r['Outs']) if n(r['Outs']) in (0,1,2) else None,'base':int(r['On1B'])+2*int(r['On2B'])+4*int(r['On3B']) if n(r['On1B']) is not None else None,'score':n(r['ScoreDiff_Pitching']),'context':'matched' if r['ContextSource']=='Matched' else 'estimated' if str(r['ContextSource']).startswith('Estimated') else 'trackman','mid':s(r['MidPA_Events']),'seqno':n(r['PitchofPA']),'order':n(r['PitchOfGame']),'recording':s(r['GameUID'])}
 P[season].append(pr)
 if yes(r['IsPA']):
  event=s(r['PA_Result']);uncertain=event=='Sacrifice' and r['TaggedHitType']!='FlyBall'
  if event=='Sacrifice' and r['TaggedHitType']=='FlyBall':event='SacFly'
  A[season].append({'id':pr['pa'],'g':gid,'p':pi,'b':bi,'event':event,'ab':yes(r['IsAB']),'tb':int(r['TotalBases']) if n(r['TotalBases']) else 0,'rbi':n(r['PA_RBI']),'outs':n(r['PA_OutsOnPlay']),'uncertain':uncertain,'scenario':False,'repeat':False,'u':uid})
 fielders={}
 for pos in ('1B','2B','3B','SS','LF','CF','RF'):
  x=n(r.get(pos+'_PositionAtReleaseZ'));y=n(r.get(pos+'_PositionAtReleaseX'));nm=r.get(pos+'_Name')
  if x is not None and y is not None and abs(x)<450 and 0<y<450:
   fi=player(nm,team) if isinstance(nm,str) and nm else None;fielders[pos]={'id':fi,'x':x,'y':y}
   if fi is not None:positions[(season,fi,pos)].append([x,y])
   if team=='CEN_COL':team_positions[(season,pos)].append([x,y])
 if r['PitchCall']=='InPlay':
  rr=dict(r);rr['PlayResult']={'Groundout':'Out','Flyout':'Out','Lineout':'Out','Popout':'Out','InPlayOut':'Out','SacFly':'Sacrifice','SacBunt':'Sacrifice'}.get(resolved,resolved)
  rr['TaggedHitType']={'Groundout':'GroundBall','Flyout':'FlyBall','Lineout':'LineDrive','Popout':'Popup','SacFly':'FlyBall','SacBunt':'Bunt'}.get(resolved,r['TaggedHitType'])
  replay=make_replay(rr)
  if resolved!=s(r['PlayResult']):replay['outcomeNote']+=' Displayed outcome follows reconciled PA scoring; original TrackMan result is retained in the pitch inspector.'
  if replay['available']:replay['points']=replay['points'][::4]
  replay.pop('coefficients',None);R[season].append({'u':uid,'fielders':fielders,**replay})
for p in fall['pitches']:
 fr=fall_lookup[p['uid']];season='Fall 2026';pi=player(p['pitcher'],p['pitcherTeam']);bi=player(p['batter'],p['batterTeam']);ci=player(p['catcher'],p['pitcherTeam']) if p.get('catcher') else None
 pr={'u':p['uid'],'g':fg[p['session']],'p':pi,'b':bi,'c':ci,'t':p['type'].replace('ChangeUp','Changeup'),'ot':p['original'],'baseType':p['original'].replace('ChangeUp','Changeup'),'no':p['no'],'inn':p['inning'],'half':p['half'],'hand':p['hand'],'bats':p['bats'],'v':p['v'],'ivb':p['ivb'],'hb':-p['hb'] if p['hand'].startswith('L') and p['hb'] is not None else p['hb'],'ahb':p['hb'],'spin':p['spin'],'rh':p['rh'],'rs':p['rs'],'ext':p['ext'],'vaa':n(fr.get('VertApprAngle')),'px':p['px'],'pz':p['pz'],'loc':p['loc'],'ev':p['ev'],'la':p['la'],'dir':p['direction'] if p['ev'] is not None else None,'dist':p['distance'] if p['landing'] else None,'bearing':p['bearing'] if p['landing'] else None,'call':p['call'],'result':p['result'],'rawResult':s(fr.get('Raw_PlayResult')) or s(fr.get('PlayResult')) or p['result'],'hit':p['hitType'],'balls':p['balls'],'strikes':p['strikes'],'pa':'F'+str(p['pa']),'review':3,'lc':'Reviewed usable' if p['loc'] else 'Unavailable','hc':p['launchConfidence'],'rc':s(fr.get('PitchReleaseConfidence')),'outs':n(fr.get('Outs')) if n(fr.get('Outs')) in (0,1,2) else None,'base':None,'score':None,'context':'trackman','mid':'','seqno':n(fr.get('PitchofPA')),'order':p['no'],'recording':s(fr.get('GameUID'))}
 P[season].append(pr)
 fielders={}
 for pos,f in p.get('fielders',{}).items():
  if n(f['x']) is None or n(f['y']) is None:continue
  fi=player(f['name'],p['pitcherTeam']) if f.get('name') else None;fielders[pos]={'id':fi,'x':f['x'],'y':f['y']}
  if fi is not None:positions[(season,fi,pos)].append([f['x'],f['y']])
  if p['pitcherTeam']=='CEN_COL':team_positions[(season,pos)].append([f['x'],f['y']])
 if p.get('replay'):
  re=dict(p['replay']);re.pop('coefficients',None)
  if re.get('endReason')=='ground-model':re['endReason']='ground'
  if re.get('available'):re['points']=re['points'][::4]
  R[season].append({'u':p['uid'],'fielders':fielders,**re})
for p in fall['pas']:
 if p['event'] in ('Incomplete','Unscored'):continue
 A['Fall 2026'].append({'id':'F'+str(p['id']),'g':fg[p['session']],'p':player(p['pitcher'],p['pitcherTeam']),'b':player(p['batter'],p['batterTeam']),'event':p['event'],'ab':p['ab'],'tb':p['tb'],'rbi':None,'outs':None,'uncertain':False,'scenario':p['scenario'],'repeat':p['repeat'],'u':p['rows'][-1]})
# Full-game Centre batting remains a separate collection; no concatenation into tracked totals.
c=pbp['cols']
for i in range(pbp['n']):
 g=games[oldg[c['g'][i]]];pl=meta['players'][c['bat'][i]] if c['bat'][i] is not None and c['bat'][i]>=0 else {'name':'Unknown player','code':'CEN_COL'};event=pbp['events'][c['ev'][i]]
 B[g['season']].append({'id':'B'+str(i),'g':g['id'],'p':None,'b':player(pl['name'],'CEN_COL'),'event':event,'ab':event not in ('Walk','IntentionalWalk','HitByPitch','SacFly','SacBunt','CatcherInterference','Unknown','Incomplete'),'tb':{'Single':1,'Double':2,'Triple':3,'HomeRun':4}.get(event,0),'rbi':c['rbi'][i],'outs':None,'uncertain':False,'scenario':False,'repeat':False,'u':None,'desc':c['desc'][i]})
D=[]
for r in pd.read_csv(H/'fielding_app/data_build/fielder_lines.csv').to_dict('records'):
 D.append({'season':r['Season'],'p':player(r['Player'],'CEN_COL'),'pos':r['PosLabel'],'g':r['G'],'po':r['PO'],'a':r['A'],'e':r['E'],'dp':r['DP'],'outs':r['Outs'],'tc':r['TC']})
T=[]
for r in pd.read_csv(H/'fielding_app/data_build/throws.csv').to_dict('records'):
 if not yes(r['IsCentreCatcher']):continue
 T.append({'u':r['PitchUID'],'season':r['Season'],'g':gmap[int(r['GameSeq'])],'p':player(r['Catcher'],'CEN_COL'),'target':r['Target'],'pop':n(r['PopTime']),'speed':n(r['ThrowSpeed']),'exchange':n(r['ExchangeTime'])})
# Fall catcher throws: exact eligible UID, confidence-gated, target inferred from base endpoint.
fall_raw=pd.read_csv(F/'audit/pitches_clean.csv',low_memory=False)
eligible_fall={p['uid'] for p in fall['pitches']}
for r in fall_raw.to_dict('records'):
 if r['PitchUID'] not in eligible_fall or r['CatcherTeam']!='CEN_COL' or n(r['PopTime']) is None:continue
 if r['CatcherThrowLocationConfidence'] not in ('High','Medium') or r['CatcherThrowReleaseConfidence'] not in ('High','Medium'):continue
 x=n(r['BasePositionX']);z=n(r['BasePositionZ'])
 if x is None or z is None:continue
 targets={'1B':(63.64,63.64),'2B':(127.28,0),'3B':(63.64,-63.64)}
 target=min(targets,key=lambda k:math.hypot(x-targets[k][0],z-targets[k][1]))
 if math.hypot(x-targets[target][0],z-targets[target][1])>40:target='Unknown'
 T.append({'u':r['PitchUID'],'season':'Fall 2026','g':fg[r['SessionId']],'p':player(r['Catcher'],'CEN_COL'),'target':target,'pop':n(r['PopTime']),'speed':n(r['ThrowSpeed']),'exchange':n(r['ExchangeTime'])})
def stats(rows,pas):
 swings=[r for r in rows if r['call']=='InPlay' or r['call']=='StrikeSwinging' or r['call'].startswith('FoulBall')];known=[r for r in rows if r['call'] not in ('','Undefined')];locs=[r for r in rows if r['loc']];zone=lambda r:abs(r['px'])<=.83 and 1.5<=r['pz']<=3.5;outside=[r for r in locs if not zone(r)];ev=[r['ev'] for r in rows if r['ev'] is not None];las=[r['la'] for r in rows if r['la'] is not None];events=collections.Counter(p['event'] for p in pas);ab=sum(p['ab'] for p in pas);hits=sum(p['tb']>0 for p in pas);bb=sum(events[x] for x in ('BB','Walk','IntentionalWalk'));hp=events['HBP']+events['HitByPitch'];sf=events['SF']+events['SacFly'];k=events['K']+events['Strikeout'];tb=sum(p['tb'] for p in pas);whiff=sum(r['call']=='StrikeSwinging' for r in rows);csw=sum(r['call'] in ('StrikeCalled','StrikeSwinging') for r in rows);chase=sum(r in swings for r in outside);den=ab+bb+hp+sf
 return {'n':len(rows),'velo':avg([r['v'] for r in rows]),'maxV':max((r['v'] for r in rows if r['v'] is not None),default=None),'swings':len(swings),'whiffs':whiff,'whiff':ratio(whiff,len(swings)),'known':len(known),'cswN':csw,'csw':ratio(csw,len(known)),'locN':len(locs),'zoneN':sum(zone(r) for r in locs),'zone':ratio(sum(zone(r) for r in locs),len(locs)),'chaseN':chase,'outside':len(outside),'chase':ratio(chase,len(outside)),'bip':sum(r['call']=='InPlay' for r in rows),'evN':len(ev),'ev':avg(ev),'maxEV':max(ev,default=None),'hardN':sum(x>=95 for x in ev),'hard':ratio(sum(x>=95 for x in ev),len(ev)),'laN':len(las),'sweet':ratio(sum(8<=x<=32 for x in las),len(las)),'pa':len(pas),'ab':ab,'h':hits,'tb':tb,'bb':bb,'hbp':hp,'sf':sf,'k':k,'avg':ratio(hits,ab),'obp':ratio(hits+bb+hp,den),'slg':ratio(tb,ab),'ops':ratio(hits+bb+hp,den)+ratio(tb,ab) if den and ab else None,'kRate':ratio(k,len(pas)),'bbRate':ratio(bb,len(pas)),'uncertain':sum(p['uncertain'] for p in pas)}
summary=[];profiles=[]
for season in seasons:
 rows=P[season];pas=A[season];spring=B[season];pr=[p for p in rows if players[p['p']]['centre']];br=[p for p in rows if players[p['b']]['centre']];ba=[p for p in pas if players[p['b']]['centre']];pa=[p for p in pas if players[p['p']]['centre']];outcome=spring or ba
 summary.append({'season':season,'n':len(rows),'tracked':sum(g['season']==season and g['tracked'] for g in games),'pbpGames':len({p['g'] for p in spring}),'pitching':stats(pr,pa),'batting':stats(br,outcome),'trackedBatting':stats(br,ba),'bip':sum(r['call']=='InPlay' for r in rows),'launch':sum(r['ev'] is not None for r in rows),'location':sum(r['loc'] for r in rows),'replays':sum(r['available'] for r in R[season])})
 for pl in players:
  pp=[r for r in rows if r['p']==pl['id']];bpitches=[r for r in rows if r['b']==pl['id']];bp=[r for r in (outcome if pl['centre'] else pas) if r['b']==pl['id']];ppa=[r for r in pas if r['p']==pl['id']]
  if not (pp or bpitches or bp):continue
  pl['seasons'].append(season);pl['pitching']+=len(pp);pl['hitting']+=len(bpitches);profiles.append({'p':pl['id'],'season':season,'pitching':stats(pp,ppa),'batting':stats(bpitches,bp)})
 dump(season.lower().replace(' ','-')+'.json',{'pitches':pack(rows),'pas':pack(pas),'pbp':pack(spring)})
 dump('replays-'+season.lower().replace(' ','-')+'.json',R[season])
 print(season,len(rows),len(pas),len(spring),'replays',sum(r['available'] for r in R[season]),flush=True)
positionSummary=[]
for (season,pi,pos),xy in positions.items():
 a=np.array(xy);positionSummary.append({'season':season,'p':pi,'pos':pos,'n':len(a),'x':float(np.median(a[:,0])),'y':float(np.median(a[:,1])),'depth':float(np.median(np.linalg.norm(a,axis=1))) });players[pi]['fielding']+=len(a)
audit=list(flags.values())
for a in fall['audit']:
 audit.append({'uid':a['uid'],'original':a['original'],'candidate':a['clean'],'applied':a['original']!=a['clean'],'reason':a['reason'],'margin':a.get('margin'),'distance':a.get('distance'),'support':None,'screen':'Reviewed Fall 2026 · '+a['status'],'pitcher':name(a['pitcher']),'season':'Fall 2026','date':None,'no':a['pitch'],'eligible':a['eligible']})
dump('audit.json',audit)
teamPositionSummary=[]
for (season,pos),xy in team_positions.items():
 a=np.array(xy);teamPositionSummary.append({'season':season,'pos':pos,'n':len(a),'x':float(np.median(a[:,0])),'y':float(np.median(a[:,1])),'depth':float(np.median(np.linalg.norm(a,axis=1)))})
dump('defense.json',{'lines':D,'throws':T,'positions':positionSummary,'teamPositions':teamPositionSummary})
index={'title':'Centre Atlas','version':'1.0.0','built':datetime.date.today().isoformat(),'cutoff':'2026-10-24','seasons':seasons,'summary':summary,'players':players,'profiles':profiles,'games':games,'totals':{'pitches':sum(map(len,P.values())),'trackedSessions':160,'pbpGames':138,'registeredSessions':len(games),'trackedPA':sum(map(len,A.values())),'pbpCentrePA':sum(map(len,B.values())),'historicalChanges':len(corrections),'historicalFlags':len(flags)-len(corrections),'fallChanges':sum(a['original']!=a['clean'] and a['eligible'] for a in fall['audit'])},'manifest':manifest,'berryRepairs':dict(repairs),'aliases':[{'source':'Vallone, Tristen','canonical':'Vallone, Tristan','basis':'Coach-confirmed alias in existing cleaner; same recorded player ID.'},{'source':'Taylor, Wesley','canonical':'Taylor, Wes','basis':'Documented same-player mapping in draft source; numeric IDs differ.'}]}
dump('index.json',index)
assert index['totals']['pitches']==40123
assert len({r['u'] for rows in P.values() for r in rows})==40123
assert index['totals']['trackedPA']==10618
assert len(games)==204
assert sum(len(v) for v in B.values())==5570
fb=summary[-1]['batting'];assert (fb['pa'],fb['ab'],fb['h'],fb['tb'],fb['bb'],fb['hbp'],fb['sf'])==(302,236,78,115,49,16,1),fb
print('BUILD VERIFIED',index['totals'])
