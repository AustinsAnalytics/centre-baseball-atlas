import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import{fileURLToPath}from'node:url';import{unpack,stats,zone,swing,wilson,situationMatch,roomDefaults,nextCount,sequenceIssues,orderSequence,groups}from'../site/metrics.js';
import{roomRows,pitchCSV,sequenceHTML}from'../site/room.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../site/data'),read=n=>JSON.parse(fs.readFileSync(path.join(root,n),'utf8')),index=read('index.json'),seasons=index.seasons.map(s=>{const d=read(s.toLowerCase().replace(' ','-')+'.json');return{s,pitches:unpack(d.pitches),pas:unpack(d.pas),pbp:unpack(d.pbp)}}),all=seasons.flatMap(s=>s.pitches),fall=seasons.at(-1),centre=id=>index.players[id].centre;
test('every eligible record is unique and matches independently reconciled coverage',()=>{assert.equal(all.length,40123);assert.equal(new Set(all.map(p=>p.u)).size,40123);assert.equal(index.games.length,204);assert.equal(index.games.filter(g=>g.tracked).length,160);assert.equal(seasons.reduce((n,s)=>n+s.pas.length,0),10618);assert.equal(seasons.reduce((n,s)=>n+s.pbp.length,0),5570);assert.deepEqual(seasons.map(s=>s.pitches.length),[2012,9329,3732,9025,3006,11498,1521])});
test('Fall Centre batting includes Graham Johnson confirmed single',()=>{const p=fall.pitches.filter(p=>centre(p.b)),a=fall.pas.filter(p=>centre(p.b)),s=stats(p,a);assert.deepEqual([s.pa,s.ab,s.h,s.tb,s.bb,s.hbp,s.sf],[302,236,78,115,49,16,1]);const id=index.players.find(p=>p.name==='Johnson, Graham'&&p.centre).id,j=stats(p.filter(p=>p.b===id),a.filter(p=>p.b===id));assert.deepEqual([j.pa,j.ab,j.h,j.tb,j.bb,j.sf],[23,18,9,15,4,1]);assert.equal(j.avg,.5);assert.equal(j.obp,13/23);assert.equal(j.slg,15/18)});
test('confidence gates and selected sample totals agree with build',()=>{assert.equal(all.filter(p=>p.loc).length,39730);assert.equal(all.filter(p=>p.ev!==null).length,5361);for(const d of seasons){const a=stats(d.pitches.filter(p=>centre(p.p)),d.pas.filter(p=>centre(p.p))),s=index.summary.find(x=>x.season===d.s).pitching;for(const k of['n','swings','whiffs','cswN','known','locN','zoneN','chaseN','outside','pa','ab','h','bb','k'])assert.equal(a[k],s[k],`${d.s} ${k}`)}});
test('PBP games cannot be appended to tracked PA without replacing overlaps',()=>{const pbpG=new Set(seasons.flatMap(s=>s.pbp).map(p=>p.g));assert.equal(pbpG.size,138);assert.equal([...pbpG].filter(g=>!index.games[g].tracked).length,44);const combined=seasons.flatMap(s=>s.pbp).concat(seasons.flatMap(s=>s.pas).filter(p=>centre(p.b)&&index.games[p.g].kind!=='Spring Game'));assert.equal(combined.filter(p=>index.games[p.g].season==='Fall 2026').length,302);assert.equal(combined.filter(p=>index.games[p.g].kind==='Spring Game').length,5570)});
test('empty, missing, intentional walk and sacrifice denominators are safe',()=>{const p={call:'Undefined',loc:false,px:null,pz:null,ev:null,la:null,v:null};const s=stats([p],[]);assert.equal(s.known,0);assert.equal(s.csw,null);assert.equal(s.chase,null);assert.equal(s.ev,null);assert.equal(s.avg,null);const a=stats([],[{event:'Single',ab:true,tb:1},{event:'IntentionalWalk',ab:false,tb:0},{event:'SacBunt',ab:false,tb:0},{event:'SacFly',ab:false,tb:0},{event:'CatcherInterference',ab:false,tb:0}]);assert.equal(a.bb,1);assert.equal(a.obp,2/3);assert.equal(a.avg,1);assert.equal(a.pa,5)});
test('documented aliases are unified without merging Michael Vallone',()=>{assert.equal(index.players.filter(p=>p.centre&&/Vallone, Trist[ae]n/.test(p.name)).length,1);assert.equal(index.players.filter(p=>p.centre&&/^Taylor, Wes/.test(p.name)).length,1);assert.ok(index.players.some(p=>p.name==='Vallone, Michael'&&!p.centre))});
test('all replay paths are finite, bounded, monotonic and never invent fall LW fielders',()=>{let total=0;for(const s of index.seasons){const reps=read('replays-'+s.toLowerCase().replace(' ','-')+'.json'),pitches=new Map(seasons.find(d=>d.s===s).pitches.map(p=>[p.u,p]));for(const r of reps){const p=pitches.get(r.u);assert.ok(p);if(r.available){total++;assert.ok(r.duration>0&&r.duration<=8);assert.equal(r.points.length,31);let t=-1;for(const pt of r.points){assert.ok(pt.every(Number.isFinite));assert.ok(pt[0]>=t);assert.ok(pt[3]>=0&&pt[3]<=250);assert.ok(Math.abs(pt[1])<=600&&Math.abs(pt[2])<=600);t=pt[0]}assert.ok(['ground','tracking','reported-hang'].includes(r.endReason))}if(index.games[p.g].opponent==='Lindsey Wilson')assert.equal(Object.keys(r.fielders).length,0)}}assert.equal(total,5354)});
test('correction ledger separates identity changes, type changes and retained evidence',()=>{const a=read('audit.json');assert.equal(a.filter(r=>r.kind==='identity'&&r.applied).length,816);assert.equal(a.filter(r=>r.kind!=='identity'&&r.season!=='Fall 2026'&&r.applied).length,348);assert.equal(a.filter(r=>r.season==='Fall 2026'&&r.applied&&r.eligible).length,82);for(const r of a.filter(r=>r.applied&&r.season!=='Fall 2026')){const p=all.find(p=>p.u===r.uid);assert.ok(p);if(r.kind==='identity'){assert.equal(index.players[p.p].name,r.candidate);assert.equal(index.players[p.op].name,r.original)}else assert.equal(p.t,r.candidate);assert.ok(r.reason.length>30)}assert.ok(a.some(r=>r.status==='unresolved-source-conflict'&&!r.applied));});
test('Wilson intervals honor sample uncertainty',()=>{const a=wilson(3,10),b=wilson(30,100);assert.ok(a[1]-a[0]>b[1]-b[0]);assert.deepEqual(wilson(0,0),[null,null]);assert.ok(wilson(0,10)[0]>=0)});
test('opponent histories use tracked PA, never Centre-only PBP pools',()=>{const opp=index.profiles.filter(p=>!centre(p.p)&&p.batting.n>0);assert.ok(opp.length>500);assert.ok(opp.some(p=>p.batting.pa>0));for(const p of opp){const d=seasons.find(s=>s.s===p.season);assert.equal(p.batting.pa,d.pas.filter(a=>a.b===p.p).length)}});
test('replays follow reconciled outcomes while preserving raw operator results',()=>{const p=all.find(p=>p.u==='3d0c4a60-cea7-11ee-86dd-137448f5b72c');assert.equal(p.result,'Error');assert.equal(p.rawResult,'Double');for(const s of seasons){const reps=new Map(read('replays-'+s.s.toLowerCase().replace(' ','-')+'.json').map(r=>[r.u,r]));for(const p of s.pitches.filter(p=>['Groundout','FieldersChoice','Error'].includes(p.result)&&p.call==='InPlay'))assert.equal(reps.get(p.u).catchInferred,false,p.u)}});
test('unnamed fielders remain in team positioning geometry and fall throws are target-specific',()=>{const d=read('defense.json');assert.equal(d.teamPositions.filter(p=>p.season==='Fall 2023').reduce((n,p)=>n+p.n,0),13103);assert.ok(d.teamPositions.filter(p=>p.season==='Fall 2024').reduce((n,p)=>n+p.n,0)>24000);assert.equal(d.throws.filter(p=>p.season==='Fall 2026'&&p.target==='2B').length,9)});

test('historical context remains PA-start evidence and fall has no invented bases or scores',()=>{
 assert.equal(all.filter(p=>p.context==='matched').length,27029);assert.equal(all.filter(p=>p.context==='estimated').length,214);
 for(const p of fall.pitches){assert.equal(p.base,null);assert.equal(p.score,null);assert.ok([0,1,2].includes(p.outs));assert.equal(p.context,'trackman')}
 const gj=fall.pitches.find(p=>p.no===317&&p.result==='Single'&&index.players[p.b].name==='Johnson, Graham');assert.equal(gj.rawResult,'Sacrifice');
 for(const p of all.filter(p=>p.context==='matched')){assert.ok(Number.isInteger(p.base)&&p.base>=0&&p.base<=7);assert.ok(Number.isFinite(p.score))}
});
test('situation filters distinguish unknown, empty, estimated and hitting-team score direction',()=>{
 const p={balls:1,strikes:2,inn:7,half:'Top',outs:2,base:2,score:1,context:'matched',call:'StrikeSwinging'};
 assert.ok(situationMatch(p,{...roomDefaults,exactCount:'1-2',inning:'7',outs:'2',bases:'risp',score:'ahead'}));
 assert.equal(situationMatch({...p,base:null}, {...roomDefaults,bases:'empty'}),false);
 assert.equal(situationMatch({...p,score:null}, {...roomDefaults,score:'tied'}),false);
 assert.equal(situationMatch({...p,context:'estimated'}, {...roomDefaults,bases:'risp'}),false);
 assert.ok(situationMatch({...p,context:'estimated'}, {...roomDefaults,bases:'risp',context:'estimated'}));
 assert.ok(situationMatch(p,{...roomDefaults,roomRole:'hit',score:'behind'}));
 assert.equal(situationMatch(p,{...roomDefaults,roomRole:'hit',score:'ahead'}),false);
 assert.equal(situationMatch({...p,outs:null},{...roomDefaults,outs:'0'}),false);
 assert.equal(situationMatch(p,{...roomDefaults,callFilter:'take'}),false);
 assert.ok(situationMatch(p,{...roomDefaults,callFilter:'swing'}));
 assert.equal(fall.pitches.filter(p=>situationMatch(p,{...roomDefaults,bases:'risp'})).length,0);
});
test('recorded sequence order survives pitch-number resets, and continuity flags gaps',()=>{
 assert.equal(nextCount({balls:1,strikes:2,call:'FoulBall'}),'1-2');assert.equal(nextCount({balls:3,strikes:2,call:'BallCalled'}),'terminal');
 const a=[{order:100,no:100,balls:0,strikes:0,call:'StrikeCalled'},{order:101,no:1,balls:0,strikes:1,call:'FoulBall'},{order:102,no:2,balls:0,strikes:2,call:'StrikeSwinging'}];
 assert.deepEqual(orderSequence([a[2],a[0],a[1]]),a);assert.equal(sequenceIssues(a).length,0);
 assert.equal(sequenceIssues([a[0],a[2]]).length,1);assert.equal(sequenceIssues(a.slice(1)).length,1);
 for(const p of all)assert.ok(Number.isFinite(p.order),p.u);
 const mixed=Object.values(groups(all.filter(p=>p.pa),'pa')).filter(a=>new Set(a.map(p=>p.p)).size>1);assert.equal(mixed.filter(a=>a[0].pa.startsWith('H')).length,11);
});

test('specific matchups, sequence exports and catcher-view orientation remain consistent',()=>{
 const id=index.players.find(p=>p.name==='Johnson, Graham'&&p.centre).id,levi=index.players.find(p=>p.name==='Wade, Levi'&&!p.centre).id;
 const rows=roomRows(fall.pitches.filter(p=>p.b===id),{...roomDefaults,roomRole:'hit',rival:String(levi)},index);assert.equal(rows.length,3);assert.equal(stats(rows).evN,1);
 const csv=pitchCSV(rows,index);assert.ok(csv.every(r=>r.length===csv[0].length));assert.equal(csv[1][0],rows[0].u);assert.ok(csv[0].includes('ContextSource'));
 const p={...rows[0],px:1,pz:2,loc:true},html=sequenceHTML([p],p,null,index,{note:x=>x,table:()=>''});assert.ok(html.includes('cx="142"'));assert.ok(html.includes('cy="192"'));
});
