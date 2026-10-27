export const finite=x=>typeof x==='number'&&Number.isFinite(x);
export const mean=xs=>{const a=xs.filter(finite);return a.length?a.reduce((s,x)=>s+x,0)/a.length:null};
export const ratio=(a,b)=>b?a/b:null;
export const swing=p=>p.call==='InPlay'||p.call==='StrikeSwinging'||p.call.startsWith('FoulBall');
export const zone=p=>p.loc&&Math.abs(p.px)<=.83&&p.pz>=1.5&&p.pz<=3.5;
export const known=p=>p.call&&p.call!=='Undefined';
export function stats(rows,pas=[]){
 const sw=rows.filter(swing),wh=rows.filter(p=>p.call==='StrikeSwinging').length,kn=rows.filter(known),lc=rows.filter(p=>p.loc),out=lc.filter(p=>!zone(p)),ev=rows.map(p=>p.ev).filter(finite),la=rows.map(p=>p.la).filter(finite),csw=rows.filter(p=>['StrikeCalled','StrikeSwinging'].includes(p.call)).length;
 const ct=evs=>pas.filter(p=>evs.includes(p.event)).length,ab=pas.filter(p=>p.ab).length,h=pas.filter(p=>p.tb>0).length,tb=pas.reduce((s,p)=>s+p.tb,0),bb=ct(['BB','Walk','IntentionalWalk']),hbp=ct(['HBP','HitByPitch']),sf=ct(['SF','SacFly']),k=ct(['K','Strikeout']),hr=ct(['HR','HomeRun']),den=ab+bb+hbp+sf,obp=ratio(h+bb+hbp,den),slg=ratio(tb,ab);
 return {n:rows.length,velo:mean(rows.map(p=>p.v)),maxV:rows.some(p=>finite(p.v))?Math.max(...rows.map(p=>p.v).filter(finite)):null,swings:sw.length,whiffs:wh,whiff:ratio(wh,sw.length),known:kn.length,cswN:csw,csw:ratio(csw,kn.length),locN:lc.length,zoneN:lc.filter(zone).length,zone:ratio(lc.filter(zone).length,lc.length),outside:out.length,chaseN:out.filter(swing).length,chase:ratio(out.filter(swing).length,out.length),bip:rows.filter(p=>p.call==='InPlay').length,evN:ev.length,ev:mean(ev),maxEV:ev.length?Math.max(...ev):null,hardN:ev.filter(v=>v>=95).length,hard:ratio(ev.filter(v=>v>=95).length,ev.length),laN:la.length,sweet:ratio(la.filter(v=>v>=8&&v<=32).length,la.length),pa:pas.length,ab,h,tb,bb,hbp,sf,k,hr,avg:ratio(h,ab),obp,slg,ops:obp!==null&&slg!==null?obp+slg:null,babip:ratio(h-hr,ab-k-hr+sf),kRate:ratio(k,pas.length),bbRate:ratio(bb,pas.length),uncertain:pas.filter(p=>p.uncertain).length};
}
export function groups(rows,key){return rows.reduce((m,r)=>{const k=typeof key==='function'?key(r):r[key];(m[k]??=[]).push(r);return m},{})}
export function unpack(data){return data.rows.map(row=>Object.fromEntries(data.columns.map((k,i)=>[k,row[i]])))}
export const fmt=(x,d=1)=>finite(x)?x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
export const pct=x=>finite(x)?`${(x*100).toFixed(1)}%`:'—';
export const slash=x=>finite(x)?x.toFixed(3).replace(/^0/,''):'—';
export const int=x=>finite(x)?x.toLocaleString('en-US',{maximumFractionDigits:0}):'—';
export const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const colors={Fastball:'#cd9652',Sinker:'#d36d54',Cutter:'#b18bd0',Slider:'#528fc1',Sweeper:'#6dc2da',Curveball:'#5ca996',Changeup:'#bcba61',Splitter:'#d39aa8',Knuckleball:'#aa9177',Other:'#889892',Undefined:'#889892'};
export const color=t=>colors[t]||'#889892';
export const short={Fastball:'FB',Sinker:'SI',Cutter:'CT',Slider:'SL',Sweeper:'SW',Curveball:'CB',Changeup:'CH',Splitter:'SP',Knuckleball:'KN',Undefined:'?'};
export function wilson(k,n){if(!n)return[null,null];const z=1.96,p=k/n,a=1+z*z/n,c=(p+z*z/(2*n))/a,r=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/a;return[Math.max(0,c-r),Math.min(1,c+r)]}

export const roomDefaults={roomRole:'pitch',rival:'all',exactCount:'all',inning:'all',half:'all',outs:'all',bases:'all',score:'all',context:'matched',callFilter:'all',roomPage:0,roomQuery:''};
// Unknown base/score snapshots must never be treated as empty bases or a tie.
export function situationMatch(p,s){
 if(s.exactCount&&s.exactCount!=='all'&&`${p.balls}-${p.strikes}`!==s.exactCount)return false;
 if(s.inning&&s.inning!=='all'&&(s.inning==='extras'?!(p.inn>=10):p.inn!==Number(s.inning)))return false;
 if(s.half&&s.half!=='all'&&p.half!==s.half)return false;
 if(s.outs&&s.outs!=='all'&&(!finite(p.outs)||p.outs!==Number(s.outs)))return false;
 const contextual=(s.bases&&s.bases!=='all')||(s.score&&s.score!=='all');
 if(contextual&&(p.context!=='matched'&&!(s.context==='estimated'&&p.context==='estimated')))return false;
 if(s.bases&&s.bases!=='all'){
  if(!Number.isInteger(p.base)||p.base<0||p.base>7)return false;
  if(s.bases==='empty'&&p.base!==0||s.bases==='on'&&p.base===0||s.bases==='risp'&&!(p.base&6)||s.bases==='loaded'&&p.base!==7)return false;
 }
 if(s.score&&s.score!=='all'){
  if(!finite(p.score))return false;
  const lead=p.score*(s.roomRole==='hit'?-1:1);
  if(s.score==='ahead'&&lead<=0||s.score==='behind'&&lead>=0||s.score==='tied'&&lead!==0||s.score==='close'&&Math.abs(lead)>2)return false;
 }
 if(s.callFilter&&s.callFilter!=='all'){
  if(s.callFilter==='swing'&&!swing(p)||s.callFilter==='whiff'&&p.call!=='StrikeSwinging'||s.callFilter==='inplay'&&p.call!=='InPlay'||s.callFilter==='take'&&(!known(p)||swing(p)||p.call==='HitByPitch'))return false;
 }
 return true;
}
export const baseLabel=b=>!Number.isInteger(b)?'Unknown':b===0?'Empty':[1,2,4].filter(n=>b&n).map(n=>({1:'1B',2:'2B',4:'3B'}[n])).join(' + ');
export const orderSequence=rows=>rows.slice().sort((a,b)=>(a.order??a.no)-(b.order??b.no));
export function nextCount(p){
 if(!Number.isInteger(p.balls)||!Number.isInteger(p.strikes)||p.balls<0||p.balls>3||p.strikes<0||p.strikes>2)return null;
 if(['BallCalled','BallinDirt','BallIntentional'].includes(p.call))return p.balls===3?'terminal':`${p.balls+1}-${p.strikes}`;
 if(['StrikeCalled','StrikeSwinging'].includes(p.call))return p.strikes===2?'terminal':`${p.balls}-${p.strikes+1}`;
 if(p.call.startsWith('FoulBall'))return `${p.balls}-${Math.min(2,p.strikes+1)}`;
 if(['InPlay','HitByPitch'].includes(p.call))return 'terminal';
 return null;
}
export function sequenceIssues(rows){const a=orderSequence(rows),issues=[];if(a.length&&(a[0].balls!==0||a[0].strikes!==0))issues.push('The first recorded pitch begins after 0–0. Earlier pitches are not supplied here.');for(let i=1;i<a.length;i++){const expected=nextCount(a[i-1]);if(expected&&expected!==`${a[i].balls}-${a[i].strikes}`)issues.push(`Before recorded pitch ${i+1}: count continuity differs from the preceding call. This may reflect a missing record, correction or restarted count.`)}return issues;}
