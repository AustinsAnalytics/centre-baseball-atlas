"""Reconstruct pitching changes from official starters and explicit substitutions.

Does not use the exported p-home/p-away lineup cells, which lose p/dh starters.
Substitution sides are resolved against both official pitching lists, avoiding
the erroneous assumption that every change belongs to the current half's defense.
"""
import json,re
from functools import lru_cache
import pandas as pd
from identity_audit import ROOT,SRC,OUT,names_match,key,canonical
a=pd.read_pickle(OUT/'working_source.pkl');p=pd.read_csv(SRC/'Colonels_Analytics/data/pbp_events_all_games.csv',low_memory=False)
boxes={r['game']:r for r in json.loads((OUT/'official_pitching.json').read_text())}
evidence=[];timeline=[];names=[]
a['OfficialIdentity']='';a['OfficialRawName']='';a['OfficialBasis']='';a['OfficialURL']=''

@lru_cache(maxsize=None)
def resolve(raw,season,team):
 aliases={('WIL_QUA','Z. Shepher'):'Sheperd, Zach',('CAR_COL','J. jr'):'Hartman, Jake',('CHI_MRN','W. Hartrick'):'Hatrick, Wade',('WHE_COL','J. Hook'):'Van Hook, JD',('SEW_TIG','John Parker Rambo'):'Parker Rambo, John',('SPA_UNI','A. Harbison'):'Harbison, Drew',('DOM_UNI','L. Downing'):'Downing, Langdon',('DOM_UNI','A. Long'):'Long, Austin',('DEP_UNI','J. Thometz'):'Thometz, Jake'}
 if (team,raw) in aliases:return aliases[(team,raw)],'documented-name-resolution'
 pool=a[(a.Season==season)&(a.PitcherTeam==team)].Pitcher.unique()
 found=[n for n in pool if names_match(n,raw)]
 if len(found)==1:return found[0],'resolved'
 # Preserve the official abbreviation when the player has no tracked identity;
 # do not invent a first name, or collapse different first initials.
 last,first=key(raw)
 same_last=[n for n in pool if key(n)[0]==last]
 if same_last:return '',f'possible alias: {same_last}'
 if ',' in raw:return canonical(raw),'new-official-name'
 words=raw.split();return f'{words[-1]}, {" ".join(words[:-1])}','new-official-name'

for gid,g in a[a.PBP_GameID.notna()].groupby('PBP_GameID'):
 box=boxes[int(gid)];ev=p[p.PBP_GameID.eq(gid)];src=pd.read_csv(SRC/'Spring PlayByPlay data'/g.PBP_File.dropna().iloc[0])
 season=g.Season.iloc[0];centre_home=src.homeTeam.iloc[0]=='Centre'
 tables=box['teams'];assert len(tables)==2,(gid,len(tables))
 sides={('home' if centre_home else 'away'):next(t for t in tables if t['team']=='Centre'),('away' if centre_home else 'home'):next(t for t in tables if t['team']!='Centre')}
 # The opponent code comes from defensive records, not similar team names.
 opponent=next(t for t in g.PitcherTeam.unique() if t!='CEN_COL')
 codes={('home' if centre_home else 'away'):'CEN_COL',('away' if centre_home else 'home'):opponent}
 cur={side:tab['pitchers'][0]['name'] for side,tab in sides.items()};basis={side:'Official pitching table: starter' for side in sides}
 source_by_row={int(k):v for k,v in ev.groupby('SrcRow')}
 mapped={}
 for rowidx,r in src.iterrows():
  desc=str(r.get('Play Description',''))
  m=re.match(r'^([^;]+?) to p(?: for (.+?))?\s*\.?\s*$',desc)
  if m:
   incoming=m.group(1).strip();outgoing=(m.group(2) or '').rstrip('.').strip()
   matches=[(side,n['name']) for side,tab in sides.items() for n in tab['pitchers'] if names_match(n['name'],incoming)]
   exact=[(side,nm) for side,nm in matches if key(nm)[0]==key(incoming)[0]]
   if exact:matches=exact
   if len(matches)==1:
    side,nm=matches[0];cur[side]=nm;basis[side]=f'Explicit substitution, source row {rowidx+2}: {desc}'
    timeline.append({'game':int(gid),'source_row':rowidx+2,'side':side,'pitcher':nm,'description':desc,'url':box['url']})
   else:
    evidence.append({'game':int(gid),'source_row':rowidx+2,'issue':'unresolved substitution','text':desc,'matches':str(matches)})
  if rowidx not in source_by_row:continue
  for pr in source_by_row[rowidx].itertuples():
   if not pr.IsPA:continue
   side='home' if pr.Half=='top' else 'away';raw=cur[side];who,status=resolve(raw,season,codes[side])
   mapped[(pr.Inning,pr.Half,pr.Description)]=(who,raw,basis[side],status)
 for k,pa in g[g.ContextSource.eq('Matched')].groupby(['Inning','Half','PA_Description'],dropna=False):
  match=mapped.get(k)
  if not match:continue
  who,raw,why,status=match
  a.loc[pa.index,['OfficialIdentity','OfficialRawName','OfficialBasis','OfficialURL']]=[who,raw,why,box['url']]
  if status!='resolved':names.append({'game':int(gid),'team':pa.PitcherTeam.iloc[0],'raw':raw,'resolved':who,'status':status,'url':box['url']})

conf=a[a.OfficialIdentity.ne('')&a.Pitcher.ne(a.OfficialIdentity)]
columns=['PitchUID','Season','GameLabel','GameUID','PitchNo','Inning','Half','Pitcher','PitcherTeam','Batter','PAofGame','PitchofPA','PA_Description','OfficialIdentity','OfficialRawName','OfficialBasis','OfficialURL','RelSpeed','RelHeight','RelSide']
conf[columns].to_csv(OUT/'official_identity_conflicts.csv',index=False)
pd.DataFrame(timeline).to_csv(OUT/'official_substitutions.csv',index=False)
pd.DataFrame(evidence).to_csv(OUT/'official_substitution_issues.csv',index=False)
pd.DataFrame(names).drop_duplicates().to_csv(OUT/'official_name_resolution.csv',index=False)
a.to_pickle(OUT/'working_reconciled.pkl')
print('Official coverage',a.OfficialIdentity.ne('').sum(),'conflicts',len(conf),'substitution issues',len(evidence))
print(conf.groupby(['Season','GameLabel','Pitcher','OfficialIdentity']).size().to_string())
print('Names',pd.DataFrame(names).drop_duplicates().to_string(index=False))
