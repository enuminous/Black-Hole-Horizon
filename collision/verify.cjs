// Verify the exact data shipped to the offline player.
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), assert=require('node:assert/strict');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8'),ctx={window:{}};
for (const f of ['orbits.js','fields.js','bhns-data.js']) vm.runInNewContext(read(f),ctx);
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

const home=read('../index.html'), area=read('../area.html');
assert(home.includes('<h1>Black hole collision lab'));
assert(home.includes('<base href="./collision/">') && home.includes('href="../area.html"'));
for(const f of ['lab.js','fields.js','orbits.js','bhns.js','bhns-data.js']) assert(home.includes('<script>'+read(f)+'</script>'), f+' is missing or stale on the home page');
assert(home.includes('<style>'+read('lab.css')+'</style>'));
assert(!/<script[^>]+src=|<link[^>]+rel="stylesheet"/.test(home));
assert(area.includes('href="index.html">Open the collision simulator') && area.includes('id="explorer"'));

const ns=ctx.window.BHNSData, img=Buffer.from(ns.png,'base64');
assert.equal(ns.frames.length,50);
assert.equal(img.subarray(1,4).toString(),'PNG');
assert.equal(img.readUInt32BE(16),ns.n*ns.cols);
assert.equal(img.readUInt32BE(20),ns.n*Math.ceil(ns.frames.length/ns.cols));
for(const rows of [ns.frames,ns.mass]){
  assert.equal(rows[0][0],0);
  rows.forEach((row,i)=>{assert(row.every(Number.isFinite));if(i)assert(row[0]>rows[i-1][0]);});
  assert(Math.abs(rows.at(-1)[0]-14.828486)<1e-5);
}
assert(ns.frames.every(row=>row.length===4 && row[3]>0));
assert(Math.abs(ns.mass[0][1]-3.598994)<1e-5 && Math.abs(ns.mass.at(-1)[1]-4.740721)<1e-5);
const massRows=read('bhns-horizon-mass.csv').trim().split('\n').slice(1).map(row=>row.split(',').map(Number));
assert.equal(massRows.length,ns.mass.length);
for(let i=0;i<massRows.length;i++)for(let j=0;j<2;j++)assert(Math.abs(massRows[i][j]-ns.mass[i][j])<1e-7);
assert(ns.midpointMs>0 && ns.midpointMs<ns.frames.at(-1)[0]);
new vm.Script(read('bhns.js'));assert(home.includes('id="nsTab"') && home.includes('id="nsScale"'));
console.log('Verified the 50-frame neutron-star replay and accompanying horizon-mass data.');
