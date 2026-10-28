"""Tight before/after check for the user-confirmed Rone follow-up release."""
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'audit_2026_10_27';base=OUT/'pre_rone_confirmation';new=ROOT/'site/data'
def read(p):return json.loads(p.read_text())
def unpack(t):return [dict(zip(t['columns'],r)) for r in t['rows']]
i=read(new/'index.json');oldi=read(base/'index.json');changes=Counter();pa_changes=0
rone=set();hand=set()
for season in i['seasons']:
 name=season.lower().replace(' ','-')+'.json';a=read(base/name);b=read(new/name)
 for old,p in zip(unpack(a['pitches']),unpack(b['pitches'])):
  assert old['u']==p['u'];diff={k for k in old if old[k]!=p[k]};changes.update(diff)
  assert diff <= {'p','identity','t','review','hand'},(p['u'],diff)
  if 'p' in diff:
   assert oldi['players'][old['p']]['name'].startswith('Unidentified pitcher')
   assert i['players'][p['p']]['name']=='Rone, Isaac'
   assert p['recording']=='dd2b062d-86f8-40ae-950a-2dd1202047da' and 32<=p['no']<=46
   rone.add(p['u'])
  if 't' in diff:assert p['u']=='a31b78b0-7917-11ef-a782-b30d481af723' and old['t']=='Slider' and p['t']=='Changeup'
  if 'hand' in diff:
   assert i['players'][p['p']]['name']=='Hoover, B.' and old['hand']=='' and p['hand']=='Right';hand.add(p['u'])
 for old,p in zip(unpack(a['pas']),unpack(b['pas'])):
  diff={k for k in old if old[k]!=p[k]};assert diff <= {'p'}
  if diff:pa_changes+=1;assert i['players'][p['p']]['name']=='Rone, Isaac'
 assert a['pbp']==b['pbp']
 assert (base/('replays-'+name)).read_bytes()==(new/('replays-'+name)).read_bytes()
assert len(rone)==15 and len(hand)==14 and changes['t']==1 and pa_changes==5
assert (base/'defense.json').read_bytes()==(new/'defense.json').read_bytes()
for p in oldi['players']:
 assert all(p[k]==i['players'][p['id']][k] for k in ['id','name','team','centre'])
result={'changedFields':dict(changes),'ronePitches':len(rone),'ronePA':pa_changes,'hooverHand':len(hand),'allOtherPitchFieldsUnchanged':True,'allPublishedPlayerIDsStable':True}
(OUT/'rone_confirmation_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
