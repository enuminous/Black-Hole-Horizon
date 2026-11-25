'use strict';
// Matter density is held at the most recent saved slice; the mass curve uses its own cadence.
window.makeNeutronStarView = function ({data, $, setup, line, label, read, repaint}) {
  const frames=data.frames, mass=data.mass, last=frames.at(-1)[0];
  const atlas=new Image();
  atlas.onload=repaint;
  atlas.src='data:image/png;base64,'+data.png;
  function leftIndex(rows,t){
    let lo=0,hi=rows.length;
    while(lo+1<hi){const m=(lo+hi)>>1;if(rows[m][0]<=t)lo=m;else hi=m;}
    return lo;
  }
  function massAt(t){
    const i=leftIndex(mass,t),a=mass[i],b=mass[Math.min(i+1,mass.length-1)];
    return a===b?a[1]:a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0]);
  }
  function settings(){
    $('viewTitle').textContent='Neutron-star matter in the orbital plane';
    $('runid').textContent='EINSTEIN TOOLKIT · GW230529-LIKE BINARY';
    $('scene').setAttribute('aria-label','Equatorial rest-mass density and tracked black-hole puncture');
    $('jump').textContent='Midpoint of mass gain';
    $('signalTitle').textContent='Black-hole horizon mass';
    $('signalUnit').textContent='solar masses';
    $('chart').setAttribute('aria-label','Quasilocal black-hole mass over elapsed simulation time in milliseconds');
    $('noteTitle').textContent='Reading the tidal disruption';
    $('note').textContent='A nonspinning 3.6 M☉ black hole and a 1.4 M☉ neutron star start 45 km apart. Follow the dense core as it stretches and leaves matter around the hole. The colors show rest-mass density in a single equatorial slice. The cross marks the tracked puncture position.';
    $('context').textContent='Time starts at the first saved slice. The jump marks half the net horizon-mass gain over the displayed interval.';
    $('method').href='https://doi.org/10.5281/zenodo.18940220';$('method').textContent='Simulation dataset ↗';
    $('caption').textContent='The curve follows horizon mass through the same simulation. The dashed line marks the midpoint of its net gain. Matter still visible in the slice can be bound to the remnant.';
    $('keyA').textContent='Density frame';$('keyB').textContent='Frame time';$('keyC').textContent='Horizon mass';
    const badge=document.createElement('span');badge.className='density-key';
    const ramp=document.createElement('i');ramp.setAttribute('aria-hidden','true');
    badge.append('Density · g/cm³',document.createTextNode('10⁸'),ramp,document.createTextNode('10¹⁵'));
    $('legend').replaceChildren(badge);
  }
  function scene(t){
    const i=leftIndex(frames,t), frame=frames[i], {ctx:g,w,h}=setup('scene');
    const half=Number($('nsScale').value),side=Math.max(1,Math.min(h-32,w-55)),x=(w-side)/2,y=(h-side)/2;
    g.fillStyle='#101519';g.fillRect(0,0,w,h);
    if(atlas.naturalWidth){
      const crop=data.n*half/data.halfKm,margin=(data.n-crop)/2;
      g.drawImage(atlas,(i%data.cols)*data.n+margin,Math.floor(i/data.cols)*data.n+margin,crop,crop,x,y,side,side);
    }
    g.strokeStyle='#56606a';g.lineWidth=1;g.strokeRect(x,y,side,side);
    if($('nsTrack').checked){
      const px=x+side*(frame[1]+half)/(2*half),py=y+side*(half-frame[2])/(2*half);
      for(const [c,l] of [['#101519',3.5],['#82d5e3',1.5]]){
        line(g,px-7,py,px+7,py,c,l);line(g,px,py-7,px,py+7,c,l);
      }
      label(g,'BH',px+9,py-5,'#a4edff');
    }
    label(g,'+'+half,x-24,y+8);label(g,'0',x-11,y+side/2+4);label(g,'−'+half,x-27,y+side-2);
    label(g,'−'+half,x,y+side+12);label(g,'x / km',x+side/2-15,y+side+12);label(g,'+'+half,x+side-24,y+side+12);
    label(g,'y / km',4,13);
    read((i+1)+' / '+frames.length,frame[0].toFixed(2)+' ms',massAt(t).toFixed(3)+' M☉');
  }
  function chart(t){
    const {ctx:g,w,h}=setup('chart'),L=45,R=w-16,T=12,B=h-27;
    const x=time=>L+(R-L)*time/last;
    const min=Math.floor(Math.min(...mass.map(v=>v[1]))*2)/2,max=Math.ceil(Math.max(...mass.map(v=>v[1]))*2)/2;
    const y=m=>B-(B-T)*(m-min)/(max-min);
    for(let m=min;m<=max;m+=.5){line(g,L,y(m),R,y(m),'#384045');label(g,m.toFixed(1),9,y(m)+3);}
    for(let j=0;j<=4;j++){const time=j*last/4;label(g,time.toFixed(1),Math.min(R-33,x(time)-4),h-6);}
    g.setLineDash([3,4]);line(g,x(data.midpointMs),T,x(data.midpointMs),B,'#98a1a5');g.setLineDash([]);
    g.beginPath();mass.forEach(([time,m],i)=>i?g.lineTo(x(time),y(m)):g.moveTo(x(time),y(m)));g.strokeStyle='#ffab71';g.lineWidth=2;g.stroke();
    line(g,x(t),T,x(t),B,'#e9eedf');g.beginPath();g.arc(x(t),y(massAt(t)),3,0,2*Math.PI);g.fillStyle='#ffab71';g.fill();
  }
  return {last,midpoint:data.midpointMs,settings,scene,chart};
};
