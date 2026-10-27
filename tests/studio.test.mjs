import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';
import{unpack,zone}from'../site/metrics.js';
import{consecutivePairs,pairSummary,countCells,locationCell,locationCells,contactCell,contactCells,gradedContact,hardAir,matchedChange,changeValue,rateEvidence}from'../site/studio-metrics.js';
import{studioSelection,coachingBrief,studioURL}from'../site/studio.js';
import{studioDefaults,studioPitchMatch}from'../site/studio-metrics.js';
import{interpretQuery}from'../site/query.js';
const dir=new URL('../site/data/',import.meta.url),read=n=>JSON.parse(fs.readFileSync(new URL(n,dir),'utf8')),I=read('index.json'),seasons=I.seasons.map(s=>({s,p:unpack(read(s.toLowerCase().replace(' ','-')+'.json').pitches)})),fall=seasons.at(-1).p,all=seasons.flatMap(s=>s.p),centre=p=>I.players[p.p].centre;
test('consecutive-pitch counts independently reconcile across all seven seasons',()=>{
 assert.deepEqual(seasons.map(s=>consecutivePairs(s.p).pairs.length),[1420,6710,2724,6533,2179,8289,1107]);
 assert.deepEqual(seasons.map(s=>consecutivePairs(s.p,centre).pairs.length),[1420,3909,2724,3700,1993,4030,886]);
 const s=pairSummary(consecutivePairs(fall,centre).pairs);assert.deepEqual([s.n,s.swings,s.whiffs],[886,337,90]);
});
test('second-pitch filtering preserves the previous type and real sequence boundaries',()=>{
 const filtered=consecutivePairs(fall,p=>centre(p)&&p.t==='Slider').pairs;
 const fbsl=filtered.filter(p=>p.key==='Fastball|Slider'),s=pairSummary(fbsl);assert.deepEqual([s.n,s.swings,s.whiffs],[97,37,16]);assert.ok(Math.abs(s.speedGap+9.471348453608245)<1e-9);
 const valid=new Set(consecutivePairs(fall).pairs.map(p=>p.after.u));
 for(const uid of['46f7f7d0-cfcc-11f1-a524-0d1db0dcf834','812088a0-cfd6-11f1-a524-0d1db0dcf834','4c7adb10-c33c-11f1-9d42-85b2c9519a90'])assert.ok(!valid.has(uid),uid);
 const before={g:1,pa:'X',p:1,b:2,order:1,recording:'A',balls:0,strikes:0,call:'BallCalled'},after={...before,order:2,balls:1,recording:'B'};
 assert.equal(consecutivePairs([before,after]).pairs.length,0);
});
test('missing speed or location never becomes a zero-valued pair measurement',()=>{
 const id=I.players.find(p=>p.name==='Cowdrey, Harrison'&&p.centre).id,pairs=consecutivePairs(fall,p=>p.p===id).pairs.filter(p=>p.key==='Fastball|Curveball'),s=pairSummary(pairs);
 assert.equal(pairs.length,10);assert.equal(s.speedN,9);assert.ok(Math.abs(s.speedGap+11.50438888888889)<1e-8);
 assert.equal(pairSummary([{before:{v:null,rs:null,rh:6,px:null,pz:2,loc:false},after:{call:'BallCalled',v:80,rs:1,rh:6,px:0,pz:2,loc:true}}]).speedGap,null);
 assert.equal(pairSummary([{before:{v:null,rs:null,rh:6,px:null,pz:2,loc:false},after:{call:'BallCalled',v:80,rs:1,rh:6,px:0,pz:2,loc:true}}]).plateGap,null);
});
test('count and location cells have explicit denominators and catcher-view orientation',()=>{
 const rows=fall.filter(centre),cells=countCells(rows);assert.equal(cells.reduce((n,c)=>n+c.rows.length,0),1192);assert.equal(cells.find(c=>c.key==='0-2').s.whiffs,12);assert.equal(cells.find(c=>c.key==='0-2').s.swings,23);
 assert.equal(locationCell({loc:true,px:2,pz:4.5}),'0:4');assert.equal(locationCell({loc:true,px:-2,pz:.5}),'4:0');assert.equal(locationCell({loc:true,px:-2.5,pz:5}),'4:4');assert.equal(locationCell({loc:false,px:0,pz:2}),null);assert.equal(locationCell({loc:true,px:2.6,pz:2}),null);
 const grid=locationCells(rows);assert.equal(grid.reduce((n,c)=>n+c.rows.length,0),1149);assert.equal(new Set(grid.flatMap(c=>c.rows.map(p=>p.u))).size,1149);
 assert.deepEqual(rateEvidence([{call:'Undefined',loc:false},{call:'BallCalled',loc:false},{call:'StrikeSwinging',loc:false}],'swing'),{k:1,n:2,value:.5,label:'Swings / known pitches'});
});
test('contact cells partition all usable pairs once and honor inclusive hard-air boundaries',()=>{
 assert.equal(gradedContact(all).length,5361);assert.equal(gradedContact(all.filter(p=>I.players[p.b].centre)).length,3531);
 const cells=contactCells(all);assert.equal(cells.reduce((s,c)=>s+c.n,0),5361);assert.equal(new Set(cells.flatMap(c=>c.rows.map(p=>p.u))).size,5361);
 for(const la of[8,20,32]){const p={call:'InPlay',ev:95,la};assert.equal(hardAir([p]).length,1);assert.ok(['hard|line','hard|drive'].includes(contactCell(p)))}
 assert.equal(contactCell({call:'InPlay',ev:95,la:32.01}),'hard|high');assert.equal(contactCell({call:'InPlay',ev:null,la:20}),null);
 const conflicting=all.find(p=>p.u==='88f801f0-e19b-11ef-b797-15d283526c3f');assert.equal(conflicting.result,'Strikeout');assert.equal(gradedContact([conflicting]).length,1);
});
test('matched development compares consistent pitch types and measurement-specific sample sizes',()=>{
 const a=seasons.find(s=>s.s==='Fall 2025').p.filter(p=>I.games[p.g].kind==='Fall Intrasquad'&&p.t==='Fastball'&&centre(p)),b=fall.filter(p=>I.games[p.g].kind==='Fall Intrasquad'&&p.t==='Fastball'&&centre(p));
 const changes=matchedChange(a,b,{metric:'v',min:10}),id=I.players.find(p=>p.name==='Kosobud, John'&&p.centre).id,k=changes.find(p=>p.id===id);assert.deepEqual([k.before.n,k.after.n],[70,42]);assert.ok(Math.abs(k.delta-1.9284447619047569)<.00001);
 const asher=I.players.find(p=>p.name==='Asher, Nolan'&&p.centre).id;assert.equal(a.filter(p=>p.p===asher).length,83);assert.equal(changeValue(a.filter(p=>p.p===asher),'v').n,82);
 assert.equal(matchedChange(a,b,{metric:'v',min:10000}).length,0);
});
test('baseball queries expose the actual applied filters without fabricating an answer',()=>{
 const q=interpretQuery('Cowdrey slider vs lefties two strikes Fall 2026',I);assert.equal(I.players[Number(q.patch.person)].name,'Cowdrey, Harrison');assert.equal(q.patch.type,'Slider');assert.equal(q.patch.hand,'L');assert.equal(q.patch.count,'two');assert.equal(q.patch.season,'Fall 2026');
 const hit=interpretQuery('Graham Johnson contact vs lefties Fall 2026',I);assert.equal(hit.patch.studioRole,'hit');assert.equal(hit.patch.studioArm,'L');assert.equal(hit.patch.hand,'all');assert.equal(hit.patch.studioMode,'contact');
 const dev=interpretQuery('Kosobud development Fall 2025 Fall 2026',I);assert.equal(dev.patch.studioPeriod,'Fall 2025');assert.equal(dev.patch.season,'Fall 2026');assert.equal(dev.patch.studioMode,'change');
 const exact=interpretQuery('Asher 0-2',I);assert.equal(exact.patch.studioCount,'0-2');
 assert.equal(interpretQuery('a completely unsupported request',I),null);
 const alias=interpretQuery('Davis Peterson contact',I,p=>p.name==='Petersen, Davis'?'Davis Peterson':'');assert.equal(I.players[Number(alias.patch.person)].name,'Petersen, Davis');
});

test('query counts, handedness and locations survive selection, pair pivots and export samples',()=>{
 const query=interpretQuery('Graham Johnson contact 0-2',I),playerRows=fall.filter(p=>String(p.b)===query.patch.person);
 assert.equal(gradedContact(playerRows).length,16);assert.equal(studioSelection(playerRows,fall,query.patch).length,0);
 const base={...studioDefaults,studioMode:'command',studioCount:'0-2',studioCell:'2:1'};
 assert.equal(studioSelection(fall.filter(centre),fall,base).length,6);
 const pairState={...base,studioMode:'pairs'},pairs=studioSelection(fall.filter(centre),fall,pairState);
 assert.ok(pairs.length>0);assert.ok(pairs.every(p=>p.balls===0&&p.strikes===2&&locationCell(p)==='2:1'));
 assert.deepEqual(pairs.map(p=>p.u),consecutivePairs(fall,p=>centre(p)&&p.balls===0&&p.strikes===2&&locationCell(p)==='2:1').pairs.map(p=>p.after.u));
 assert.equal(studioSelection(fall.filter(centre),fall,{...studioDefaults,studioMode:'pairs',studioPair:'Fastball|Slider'}).length,97);
 assert.equal(studioSelection(fall.filter(p=>I.players[p.b].centre),fall,{...studioDefaults,studioMode:'contact',studioBin:'hard|drive'}).length,7);
 const changeState={...studioDefaults,studioMode:'change',studioCount:'0-2',studioArm:'L'};
 assert.ok(!studioPitchMatch({balls:0,strikes:1,hand:'Left'},changeState));assert.ok(!studioPitchMatch({balls:0,strikes:2,hand:'Right'},changeState));assert.ok(studioPitchMatch({balls:0,strikes:2,hand:'Left'},changeState));
 const spring=interpretQuery('Spring 2026 intrasquad Asher',I);assert.equal(spring.patch.kind,'Spring Intrasquad');
 const href=studioURL({season:'Fall 2026',team:'centre'},pairState),saved=JSON.parse(new URL(href,'https://atlas.example').searchParams.get('view'));assert.equal(saved.studioCount,'0-2');assert.equal(saved.studioCell,'2:1');
});
test('coaching studies select the profile team and its actual count',()=>{
 const id=I.players.find(p=>!p.centre&&p.pitching>0).id,html=coachingBrief(fall.filter(p=>p.p===id),{id,role:'pitch',state:{season:'Fall 2026',team:'centre'},team:'opponents',playerName:I.players[id].display}),href=html.match(/href="([^"]+)"/)[1],saved=JSON.parse(new URL(href,'https://atlas.example').searchParams.get('view'));
 assert.equal(saved.team,'opponents');assert.equal(saved.person,String(id));
 const rows=fall.filter(centre),c=countCells(rows).filter(c=>c.s.swings>=8).sort((a,b)=>b.s.whiff-a.s.whiff)[0],brief=coachingBrief(rows,{id:1,role:'pitch',state:{season:'Fall 2026'},team:'centre',playerName:'Test'}),link=brief.match(/href="([^"]+)"/)[1];
 assert.equal(JSON.parse(new URL(link,'https://atlas.example').searchParams.get('view')).studioCount,c.key);
});
