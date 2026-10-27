import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {portraitFor,portraitKey} from '../site/portraits.js';

const site=new URL('../site/',import.meta.url);
const catalog=JSON.parse(fs.readFileSync(new URL('assets/players/portraits.json',site),'utf8'));
const index=JSON.parse(fs.readFileSync(new URL('data/index.json',site),'utf8'));

test('portrait assets match named Centre identities, asset hashes and valid crop bounds',()=>{
 const counts={};
 for(const [key,photo] of Object.entries(catalog.players)){
  const matches=index.players.filter(p=>portraitKey(p)===key);
  assert.equal(matches.length,1,key);
  assert.ok(matches[0].centre,key);
  assert.equal(photo.name,matches[0].display,key);
  assert.match(photo.file,/^assets\/players\/[a-z-]+\.(webp|jpg)$/);
  const bytes=fs.readFileSync(new URL(photo.file,site));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),photo.sha256,key);
  if(photo.file.endsWith('.webp')){assert.equal(bytes.toString('ascii',0,4),'RIFF');assert.equal(bytes.toString('ascii',8,12),'WEBP')}
  else assert.equal(bytes.readUInt16BE(0),0xffd8);
  const [x,y,edge]=photo.crop;
  assert.ok([photo.width,photo.height,x,y,edge].every(Number.isFinite),key);
  assert.ok(x>=0&&y>=0&&edge>0&&x+edge<=photo.width&&y+edge<=photo.height,key);
  if(photo.sourceType==='user')assert.equal(photo.sourcePage,null);
  else assert.match(photo.sourcePage,/^https:\/\/(centrecolonels\.com|sewaneetigers\.com|mountathletics\.com)\//);
  assert.equal(portraitFor({...matches[0],team:'OTHER'},catalog),null);
  counts[photo.sourceType]=(counts[photo.sourceType]||0)+1;
 }
 assert.deepEqual(counts,{centre:24,mount:1,user:8,sewanee:1});
 const missing=index.players.filter(p=>p.centre&&p.seasons.includes('Fall 2026')&&!portraitFor(p,catalog)).map(p=>p.display).sort();
 assert.deepEqual(missing,[...catalog.missingCurrent].sort());
 assert.deepEqual(missing,['Cooper Burgin','Mason Dugan']);
});
