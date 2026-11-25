// Verify the exact data shipped to the offline player.
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), assert=require('node:assert/strict');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8'),ctx={window:{}};
for (const f of ['orbits.js','fields.js']) vm.runInNewContext(read(f),ctx);
const {BHOrbit:o,BHFields:s}=ctx.window;
assert.equal(o.source,'SXS:BBH:0305');assert.equal(o.tracks.C[0][0],0);
assert(o.tracks.A.at(-1)[0]>0 && o.tracks.C.at(-1)[0]>o.tracks.A.at(-1)[0]);
for(const rows of Object.values(o.tracks)) for(let i=0;i<rows.length;i++){
  assert(rows[i].length===7 && rows[i].every(Number.isFinite));assert(rows[i][4]>0);
  if(i)assert(rows[i][0]>rows[i-1][0]);
}
assert.deepEqual(o.tracks.A.map(r=>r[0]),o.tracks.B.map(r=>r[0]));
const csv=read('signals.csv').trim().split('\n').map(r=>r.split(','));
assert.equal(csv.length,182);assert.deepEqual(csv.slice(1).map(r=>+r[0]),Array.from({length:181},(_,i)=>i/5));
for(const [key,a] of Object.entries(s.arms)){
  assert.equal(Buffer.from(a.packed,'base64').length,s.nx*s.nt*3*2);
  for(const [l,p] of [0,2,4].entries()){
    const n=csv[0].indexOf(key+'_l'+p);assert(n>0);
    a.trace[l].forEach((v,i)=>assert.equal(v,+csv[i+1][n]));
  }
}
for(let l=0;l<3;l++)for(let i=0;i<181;i++){
  assert.equal(s.arms.B0.trace[l][i],0);assert.equal(s.arms.Bminus.trace[l][i],s.arms.B1.trace[l][i]);
  assert.equal(s.arms.B2.trace[l][i],4*s.arms.B1.trace[l][i]);
}
const result=JSON.parse(read('source-results.json'));
assert(Object.values(result.checks).every(v=>v===true));
new vm.Script(read('lab.js'));
console.log('Verified SXS horizon coverage, all published traces, magnetic controls and browser script.');
