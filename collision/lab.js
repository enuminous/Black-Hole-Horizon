'use strict';
(() => {
  const orbit=window.BHOrbit, fields=window.BHFields, $=id=>document.getElementById(id);
  const amber='#ffab71', blue='#80d6e3', ivory='#e9eedf', muted='#a7b1b5';
  const clocks={orbit:-160,field:12,ns:0};
  let view='orbit',playing=false,stamp=0,lastPaint=0,animationId=0;
  const cache=new Map(), shell=document.createElement('canvas');
  const sepRows=orbit.tracks.A.map((a,i)=>[a[0],Math.hypot(...a.slice(1,4).map((v,k)=>v-orbit.tracks.B[i][k+1]))]);
  const ns=window.makeNeutronStarView({data:window.BHNSData,$,setup,line,label,read,repaint:()=>{if(view==='ns')draw();}});
  function limits(){if(view==='ns')return [0,ns.last];return view==='field'?[0,36]:$('window').value==='end'?[-260,50]:[orbit.tracks.A[0][0],orbit.tracks.C.at(-1)[0]]}
  function sample(rows,t){
    if(t<rows[0][0] || t>rows.at(-1)[0])return null;
    let lo=0,hi=rows.length-1;
    while(hi-lo>1){const mid=(lo+hi)>>1;if(rows[mid][0]<=t)lo=mid;else hi=mid;}
    const a=rows[lo],b=rows[hi],p=(t-a[0])/(b[0]-a[0]);
    return a.map((v,i)=>v+(b[i]-v)*p);
  }
  function linear(arr,t,dt){
    const k=Math.max(0,Math.min(arr.length-1,t/dt)),lo=Math.floor(k),hi=Math.min(arr.length-1,lo+1);
    return arr[lo]+(arr[hi]-arr[lo])*(k-lo);
  }
  function setup(id){
    const c=$(id),rect=c.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);
    const w=Math.round(rect.width),h=Math.round(rect.height);
    if(c.width!==Math.round(w*dpr)||c.height!==Math.round(h*dpr)){c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);}
    const ctx=c.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
    ctx.font='11px ui-monospace, monospace';return {ctx,w,h};
  }
  function line(g,x,y,u,v,color,width=1){
    g.beginPath();g.moveTo(x,y);g.lineTo(u,v);g.lineWidth=width;g.strokeStyle=color;g.stroke();
  }
  function label(g,s,x,y,color=muted){g.fillStyle=color;g.fillText(s,x,y)}
  function legend(items){$('legend').replaceChildren(...items.map(([n,c])=>{const s=document.createElement('span'),b=document.createElement('b');b.style.background=c;s.append(b,n);return s;}))}
  function keys(a,b,c){$('keyA').textContent=a;$('keyB').textContent=b;$('keyC').textContent=c}
  function read(a,b,c){$('valueA').textContent=a;$('valueB').textContent=b;$('valueC').textContent=c}
  function settings(){
    const o=view==='orbit',arm=$('arm').value,pulse=arm.startsWith('pulse');
    const neutron=view==='ns';
    $('nsTab').setAttribute('aria-pressed',neutron);
    $('nsControls').hidden=!neutron;$('nsCSV').hidden=!neutron;$('scalarFiles').hidden=neutron;
    $('timeUnit').textContent=neutron?'ms':'M';
    $('scrub').step=neutron?'any':'.1';
    $('orbTab').setAttribute('aria-pressed',o);$('fieldTab').setAttribute('aria-pressed',view==='field');
    $('orbitControls').hidden=!o;$('fieldControls').hidden=view!=='field';
    if(neutron) ns.settings();
    else {
    $('viewTitle').textContent=o?'Orbital plane':'Scalar field cross-section';
    $('runid').textContent=o?'SXS:BBH:0305 · LEV 5':'C1 · HEAD-ON CLOSE LIMIT';
    $('scene').setAttribute('aria-label',o?'Projected horizon centers from the SXS numerical simulation':'Signed scalar field in a radial shell around a common horizon');
    $('jump').textContent=o?'Common horizon':'Restart at zero';
    $('signalTitle').textContent=o?'Horizon separation':'Scalar probe waveform';
    $('signalUnit').textContent=o?'distance / M':'rφ at r* = 20 M';
    $('chart').setAttribute('aria-label',$('signalTitle').textContent);
    $('noteTitle').textContent=o?'Reading the collision':'Reading the scalar experiment';
    $('note').textContent=o?'The tracks follow the coordinate centers from a SpEC numerical-relativity evolution. Circle sizes encode area-equivalent radii. Time zero marks the first recorded common apparent horizon. The two individual horizons remain visible for their measured overlap.':'This equal-mass head-on model begins with a common horizon. The shell shows signed rφ, reconstructed from the ℓ = 0, 2 and 4 angular components. The SXS orbit in the other view is a separate simulation with a separate clock.';
    $('context').textContent=o?'Spatial units are the total mass M. The view projects the simulated centers onto the x–y plane.':pulse?'The initial pulse is prescribed. The dashed reference trace uses a conventional scalar with the matched effective mass when available.':'The scalar starts at zero in a prescribed magnetic environment. Field strength and coupling are illustrative.';
    $('method').textContent=o?'SXS record ↗':'Source protocol';$('method').href=o?'https://doi.org/10.5281/zenodo.13182440':'SOURCE-PROTOCOL.md';
    $('caption').textContent=o?'3D coordinate distance between the individual horizon centers. Their joint record ends just after the first common horizon.':pulse?'Solid line: C1. Dashed line when available: matched Klein–Gordon comparison. The cursor follows the selected simulation time.':'The signed signal is sampled every 0.2 M. The polarity and field-off controls share the same vertical scale as the +B and 2B runs.';
    keys(...(o?['Phase','Separation','Common mass']:['Probe radius','Mode amplitude','Time window']));
    legend(o?[['Horizon A',amber],['Horizon B',blue],['Common horizon',ivory]]:[['Negative rφ',blue],['Zero','#566067'],['Positive rφ',amber]]);
    }
    const [lo,hi]=limits();$('scrub').min=lo;$('scrub').max=hi;
    clocks[view]=Math.max(lo,Math.min(hi,clocks[view]));draw();
  }
  function orbitalScene(t){
    const {ctx:g,w,h}=setup('scene'),cx=w/2,cy=h/2,scale=Math.min((w-54)/20,(h-27)/17);
    const px=x=>cx+x*scale,py=y=>cy-y*scale;
    g.fillStyle='#101519';g.fillRect(0,0,w,h);
    for(let n=-40;n<=40;n+=2){
      line(g,px(n),0,px(n),h,n===0?'#384247':'#202a2d');
      line(g,0,py(n),w,py(n),n===0?'#384247':'#202a2d');
    }
    label(g,'y / M',10,17);label(g,'x / M',w-46,h-8);
    for(const n of [-6,-4,-2,2,4,6])label(g,String(n),px(n)+3,h-9,'#7c898e');
    const selected={};for(const name of ['A','B','C'])selected[name]=sample(orbit.tracks[name],t);
    function trail(name,color){
      const rows=orbit.tracks[name],visible=rows.filter(r=>r[0]>=t-220 && r[0]<=t);
      if(!visible.length)return;g.beginPath();
      visible.forEach((r,i)=>i?g.lineTo(px(r[1]),py(r[2])):g.moveTo(px(r[1]),py(r[2])));
      if(selected[name])g.lineTo(px(selected[name][1]),py(selected[name][2]));
      g.lineWidth=1.6;g.strokeStyle=color;g.globalAlpha=.73;g.stroke();g.globalAlpha=1;
    }
    if($('tails').checked){trail('A',amber);trail('B',blue);trail('C',ivory);}
    function horizon(name,color){
      const r=selected[name];if(!r)return;
      const x=px(r[1]),y=py(r[2]),radius=2*r[4]*scale;
      const grad=g.createRadialGradient(x,y,radius*.52,x,y,radius*1.32);
      grad.addColorStop(0,'#080b0d');grad.addColorStop(.71,'#101518');grad.addColorStop(.76,color);
      grad.addColorStop(.80,color+'63');grad.addColorStop(1,color+'00');
      g.fillStyle=grad;g.beginPath();g.arc(x,y,radius*1.32,0,Math.PI*2);g.fill();
      label(g,name==='C'?'COMMON':name,x+radius*.8+5,y-radius*.83-3,color);
    }
    horizon('C',ivory);horizon('B',blue);horizon('A',amber);
    const sep=sample(sepRows,t);read(t<0?'Binary':selected.A?'Overlap':'Remnant',sep?sep[1].toFixed(3)+' M':'—',selected.C?selected.C[5].toFixed(4)+' M':'—');
  }
  function unpack(key){
    if(!cache.has(key)){const a=fields.arms[key],bytes=Uint8Array.from(atob(a.packed),c=>c.charCodeAt(0));
      const dv=new DataView(bytes.buffer);const arr=new Float64Array(bytes.length/2);
      for(let i=0;i<arr.length;i++)arr[i]=dv.getInt16(2*i,true)/32767*a.scale[Math.floor(i/fields.nx)%3];
      cache.set(key,arr);}
    return cache.get(key);
  }
  const fieldFamily=key=>key.startsWith('pulse')?['pulse1','pulseMinus']:['B1','B2'];
  const scales=new Map();
  function colorLimit(key){
    const family=fieldFamily(key),k=family[0];if(scales.has(k))return scales.get(k);
    let lim=1e-20;
    for(const name of family){const buf=unpack(name);
      for(let t=0;t<fields.nt;t++)for(let x=0;x<fields.nx;x++){
        const i=t*3*fields.nx+x;
        lim=Math.max(lim,Math.abs(buf[i])+Math.abs(buf[i+fields.nx])+Math.abs(buf[i+2*fields.nx]));}}
    scales.set(k,lim);return lim;
  }
  function fieldScene(t){
    const {ctx:g,w,h}=setup('scene'),key=$('arm').value,arr=unpack(key),lim=colorLimit(key);
    const W=292,H=170; if(shell.width!==W){shell.width=W;shell.height=H;}
    const ctx=shell.getContext('2d'),img=ctx.createImageData(W,H);
    const cx=(W-1)/2,cy=(H-1)/2,R=H*.45,frame=Math.min(fields.nt-1,t/fields.dt),i0=Math.floor(frame),i1=Math.min(i0+1,fields.nt-1),frac=frame-i0;
    const radial=new Float64Array(3*fields.nx);
    for(let i=0;i<radial.length;i++)radial[i]=arr[i0*radial.length+i]*(1-frac)+arr[i1*radial.length+i]*frac;
    for(let y=0;y<H;y++)for(let x=0;x<W;x++){
      const dx=x-cx,dy=y-cy,r=Math.hypot(dx,dy)/R*28,j=4*(y*W+x);
      let red=16,green=21,blueCh=25;
      if(r>=4 && r<=28){
        const u=dy/(Math.hypot(dx,dy)||1),u2=u*u,P=[1,(3*u2-1)/2,(35*u2*u2-30*u2+3)/8];
        const q=(r-4)/fields.dx,k=Math.floor(q),b=Math.min(k+1,fields.nx-1);
        let v=0;for(let l=0;l<3;l++)v+=P[l]*((1-q+k)*radial[l*fields.nx+k]+(q-k)*radial[l*fields.nx+b]);
        const level=Math.min(1,Math.asinh(10*Math.abs(v)/lim)/Math.asinh(10)),tone=v<0?[85,196,220]:[255,160,92];
        red=23+(tone[0]-23)*level;green=31+(tone[1]-31)*level;blueCh=36+(tone[2]-36)*level;
      }
      img.data[j]=red;img.data[j+1]=green;img.data[j+2]=blueCh;img.data[j+3]=255;
    }
    ctx.putImageData(img,0,0);g.fillStyle='#101519';g.fillRect(0,0,w,h);
    const factor=Math.min(w/W,h/H),dw=W*factor,dh=H*factor,sx=(w-dw)/2,sy=(h-dh)/2;
    g.drawImage(shell,sx,sy,dw,dh);
    for(const radius of [4,12,20,28]){
      const rr=R*factor*radius/28;g.beginPath();g.arc(w/2,h/2,rr,0,2*Math.PI);g.strokeStyle=radius===20?'#98a6a8':'#475458';g.lineWidth=.65;g.setLineDash(radius===20?[3,4]:[]);g.stroke();g.setLineDash([]);
    }
    label(g,'r* / M',14,21);label(g,'4',w/2+R*factor*4/28+2,h/2-3);label(g,'28',w/2+R*factor+3,h/2-3);
    const l=+$('modeSel').value,value=linear(fields.arms[key].trace[l],t,.2);
    read('r* = 20 M',value===0?'0':value.toExponential(2),'0–36 M');
  }
  function signalChart(t){
    const {ctx:g,w,h}=setup('chart'),L=58,R=w-18,T=10,B=h-24,[lo,hi]=limits(),o=view==='orbit';
    const x=v=>L+(v-lo)/(hi-lo)*(R-L);
    let primary,secondary=null,peak;
    if(o){primary=sepRows.filter(row=>row[0]>=lo && row[0]<=hi);peak=Math.max(1,...primary.map(r=>r[1]))*1.08;}
    else{const key=$('arm').value,l=+$('modeSel').value;
      primary=fields.arms[key].trace[l].map((v,i)=>[i*.2,v]);
      if(fields.arms[key].matched?.[l])secondary=fields.arms[key].matched[l].map((v,i)=>[i*.2,v]);
      peak=Math.max(...fieldFamily(key).flatMap(k=>fields.arms[k].trace[l].map(Math.abs)))*1.08 || 1;}
    const y=v=>o?B-(B-T)*v/peak:(B+T)/2-v*(B-T)/(2*peak);
    for(const v of (o?[0,peak/2,peak]:[-peak,0,peak])){
      line(g,L,y(v),R,y(v),'#384045');label(g,o?v.toFixed(1):v===0?'0':v.toExponential(0),5,y(v)+4);}
    for(let j=0;j<=4;j++){const v=lo+j*(hi-lo)/4;label(g,String(Math.round(v)),Math.max(L-6,Math.min(R-18,x(v)-8)),h-5);}
    if(o){g.setLineDash([3,4]);line(g,x(0),T,x(0),B,'#a3a59a');g.setLineDash([]);}
    function curve(rows,color,dash){
      g.beginPath();rows.forEach(([a,b],i)=>i?g.lineTo(x(a),y(b)):g.moveTo(x(a),y(b)));g.strokeStyle=color;g.lineWidth=2;g.setLineDash(dash);g.stroke();g.setLineDash([]);}
    curve(primary,amber,[]);if(secondary)curve(secondary,blue,[4,6]);line(g,x(t),T,x(t),B,ivory);
  }
  function draw(){
    const t=clocks[view];$('time').textContent=(t>0&&view==='orbit'?'+':'')+t.toFixed(view==='ns'?2:1).replace('-','−');
    $('scrub').value=t;$('scrub').setAttribute('aria-valuetext',t.toFixed(view==='ns'?2:1)+(view==='ns'?' ms':' M'));
    if(view==='ns'){ns.scene(t);ns.chart(t);return;}
    if(view==='orbit')orbitalScene(t);else fieldScene(t);
    signalChart(t);
  }
  function pause(){playing=false;cancelAnimationFrame(animationId);$('play').textContent='▶ Play';$('play').setAttribute('aria-label','Play simulation');}
  function tick(now){if(!playing)return;
    const [lo,hi]=limits(),delta=Math.min((now-stamp)/1000,.2);stamp=now;
    clocks[view]=Math.min(hi,clocks[view]+delta*(hi-lo)/20*Number($('speed').value));
    if(now-lastPaint>30||clocks[view]>=hi){draw();lastPaint=now;}
    if(clocks[view]>=hi)pause();else animationId=requestAnimationFrame(tick);
  }
  $('play').onclick=()=>{if(playing){pause();return;}const [lo,hi]=limits();if(clocks[view]>=hi)clocks[view]=lo;
    playing=true;stamp=performance.now();$('play').textContent='Ⅱ Pause';$('play').setAttribute('aria-label','Pause simulation');animationId=requestAnimationFrame(tick);};
  function select(v){pause();view=v;settings();}
  $('nsTab').onclick=()=>select('ns');
  $('orbTab').onclick=()=>select('orbit');$('fieldTab').onclick=()=>select('field');
  $('scrub').oninput=()=>{pause();clocks[view]=Number($('scrub').value);draw();};
  $('jump').onclick=()=>{pause();clocks[view]=view==='ns'?ns.midpoint:0;draw();};
  for(const id of ['window','tails','arm','modeSel','nsScale','nsTrack'])$(id).onchange=settings;
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});window.addEventListener('resize',draw);
  function openLinkedMode(){
    if(location.hash==='#neutron-star')select('ns');else if(location.hash==='#scalar')select('field');
  }
  window.addEventListener('hashchange',openLinkedMode);
  settings();openLinkedMode();
})();
