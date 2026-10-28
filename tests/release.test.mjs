import test from 'node:test';import assert from 'node:assert/strict';
import{releaseLabel}from'../site/release.js';
test('release timestamp uses Eastern calendar date across UTC midnight and daylight saving',()=>{
 assert.equal(releaseLabel('2026-10-28T01:28:26Z'),'Oct 27, 2026 · 9:28 PM EDT');
 assert.equal(releaseLabel('2026-12-28T01:28:26Z'),'Dec 27, 2026 · 8:28 PM EST');
 assert.equal(releaseLabel('2026-10-27T21:28:26-04:00'),'Oct 27, 2026 · 9:28 PM EDT');
});
test('missing or ambiguous release times never display the visitor current time',()=>{
 for(const value of [null,undefined,'','invalid','2026-10-27','2026-10-27T21:28:26'])assert.equal(releaseLabel(value),null);
});
