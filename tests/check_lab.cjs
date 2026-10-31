const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const core=html.match(/<script id="physics-core">([\s\S]*?)<\/script>/)[1];
const context={module:{exports:{}}};vm.runInNewContext(core,context);
const golden=JSON.parse(fs.readFileSync(path.join(__dirname,'physics-golden.json')));
for(const x of golden){const y=context.module.exports; if(Math.abs(y.area(x.m,x.s)/x.area-1)>1e-12)throw Error('Area mismatch');y.qnm(x.m,x.s).forEach((v,i)=>{if(Math.abs(v/x.qnm[i]-1)>1e-12)throw Error('QNM mismatch')});}
const data=JSON.parse(html.match(/<script id="study-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
if(data.synthetic.cases.length!==16||data.examples.length!==16)throw Error('Missing cases');
for(const m of html.matchAll(/<script(?: id="physics-core")?>([\s\S]*?)<\/script>/g))new vm.Script(m[1]);
if(/<script[^>]+src=|<link[^>]+href=/.test(html))throw Error('External runtime dependency');
console.log('PASS: Python/JavaScript physics parity, 16 embedded cases, script syntax, no external runtime dependencies');
