"""Evolve signed pulse and magnetic-source arms on a common close-limit exterior."""
import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np
from scatter import Exterior, Z, BARE_MASS

ROOT=Path(__file__).resolve().parent
ARMS=('pulse0','pulse1','pulseMinus','B0','B1','Bminus','B2')
FIELD=np.array([0,0,0,0,1,-1,2.])[:,None]
SEED=np.array([0,1,-1,0,0,0,0.])[:,None]
ELLS=(0,2,4)
def mix(v):
    """Coefficients of P2 times an l=0,2 field, in the P0,P2,P4 basis."""
    return np.stack([v[1]/5,v[0]+2*v[1]/7,18*v[1]/35])
def source_modes(equator,pole):
    return np.stack([(2*equator+pole)/3,2*(pole-equator)/3])

def solve(dx):
    grid=Exterior(dx,[-28,76],.03)
    r,f,x=grid.r,grid.f,grid.x
    s=.5*r*r*np.exp(-(r-9)**2/18)
    ds=s*(2/r-(r-9)/9)
    equator, pole=f*ds**2/r**2,4*s**2/r**4
    current=2e-5*FIELD**2
    j0=source_modes(equator,pole)[:,None,:]*current
    n=len(r); arms=len(ARMS)
    state=np.zeros((2+10*arms,n))
    def parts(y):
        return (y[2:2+4*arms].reshape((2,2,arms,n)),y[2+4*arms:].reshape((2,3,arms,n)))
    base,dist=parts(state)
    state[0]=grid.initial_psi
    base[0,0]=1e-4*SEED*np.exp(-(x-8)**2/8)/r
    angular=np.array([0,6,20])[:,None,None]/r**2
    def rhs(y):
        out=np.empty_like(y); psi,vel=y[:2]
        acc=grid.d2(psi)-grid.vz*psi
        out[:2]=vel,acc
        k,h,b,*_=grid.geometry(psi,vel,acc)
        (u,p),(w,q)=parts(y)
        seed_rhs,dist_rhs=parts(out)
        v=p/Z
        seed_rhs[0]=v
        seed_rhs[1]=Z*grid.flux_divergence(u)-f*((Z*angular[:2]+BARE_MASS**2)*u+j0)
        dist_rhs[0]=q/Z+mix(-(k+h)*v+b*grid.d1(u))
        induced=mix(Z*grid.flux_divergence(u,k-h,b*v)-f*BARE_MASS**2*k*u)
        # sqrt(-g) F², keeping terms through first order in the quadrupolar metric.
        j1=mix(source_modes(-h*equator,-k*pole)[:,None,:]*current)
        dist_rhs[1]=Z*grid.flux_divergence(w)+induced-f*((Z*angular+BARE_MASS**2)*w+j1)
        out[:,:5]=0;out[:,-5:]=0
        return out
    dt=dx/4
    samples=np.rint((np.arange(4,28.01,.4)-x[0])/dx).astype(int)
    probe=int(round((20-x[0])/dx))
    traces=[];snapshots=[]
    for step in range(round(36/dt)+1):
        if step%round(.2/dt)==0:
            (u,_),(w,_)=parts(state)
            total=w.copy();total[:2]+=u
            traces.append(total[...,probe]*r[probe])
            if step%round(.4/dt)==0:
                snapshots.append(total[...,samples]*r[samples])
        if step==round(36/dt):break
        k1=rhs(state);k2=rhs(state+dt*k1/2);k3=rhs(state+dt*k2/2);k4=rhs(state+dt*k3)
        state+=dt/6*(k1+2*k2+2*k3+k4)
    result=np.array(traces),np.array(snapshots)
    assert all(np.isfinite(a).all() for a in result)
    return result

def norm(a):return float(np.linalg.norm(a))
def write_results(records):
    order=sorted(records,reverse=True)
    fine,frames=records[min(order)]
    with zipfile.ZipFile(ROOT/'BH-SCAT-001-Replay.zip') as z:
        ref=np.genfromtxt(io.BytesIO(z.read('BH-SCAT-001/results/small-fine.csv')),delimiter=',',names=True)
    checks={}; diagnostics={}
    for ell,l in enumerate(ELLS):
        y=fine[:,ell,4];length=norm(y);assert length>0
        errors=[norm(records[h][0][:,ell,4]-records[h2][0][:,ell,4]) for h,h2 in zip(order,order[1:])]
        values=dict(field_reversal=norm(y-fine[:,ell,5])/length,doubling=norm(fine[:,ell,6]-4*y)/(4*length),
                    zero=float(np.max(abs(fine[:,ell,3]))),last_refinement=errors[-1]/length,
                    convergence_order=float(np.log2(errors[0]/errors[1])),peak=float(np.max(abs(y))))
        diagnostics['l'+str(l)]=values
        checks['l'+str(l)]=bool(values['field_reversal']<=1e-9 and values['doubling']<=1e-9 and values['zero']==0
                                 and values['last_refinement']<.1 and errors[1]<errors[0])
    for i,label in enumerate(('zero','plus','minus')):
        for ell,l in enumerate((0,2)):
            y=ref[f'C1_l{l}_{label}_x20'];diff=norm(fine[:,ell,i]-y)
            checks[f'pulse_{label}_{l}']=bool(diff<=1e-9*norm(y))
    result=dict(checks=checks,diagnostics=diagnostics,protocol_sha256=hashlib.sha256((ROOT/'SOURCE-PROTOCOL.md').read_bytes()).hexdigest())
    (ROOT/'source-results.json').write_text(json.dumps(result,indent=2)+'\n')
    data={}
    with (ROOT/'signals.csv').open('w') as out:
        writer=csv.writer(out,lineterminator='\n')
        writer.writerow(['time_M']+[f'{a}_l{l}' for a in ARMS for l in ELLS])
        for n,row in enumerate(fine):writer.writerow([round(n*.2,1)]+row.T.ravel().tolist())
    for a,name in enumerate(ARMS):
        cube=frames[:,:,a,:]
        scale=np.max(abs(cube),axis=(0,2));scale[scale==0]=1
        packed=np.rint(cube/scale[None,:,None]*32767).astype('<i2')
        data[name]=dict(scale=scale.tolist(),packed=base64.b64encode(packed.tobytes()).decode(),
                        trace=fine[:,:,a].T.tolist())
        if a<3:data[name]['matched']=[ref[f'KG_l{l}_{("zero","plus","minus")[a]}_x20'].tolist() for l in (0,2)]
    obj=dict(dt=.4,traceDt=.2,start=4,dx=.4,nx=frames.shape[-1],nt=len(frames),arms=data)
    (ROOT/'fields.js').write_text('window.BHFields='+json.dumps(obj,separators=(',',':'))+';\n')
    print(json.dumps(result));return all(checks.values())
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--grid',type=float,choices=(.2,.1,.05));args=ap.parse_args()
    args.work.mkdir(exist_ok=True,parents=True)
    if args.grid:
        tr,sn=solve(args.grid);np.savez(args.work/f'g{args.grid}.npz',trace=tr,snap=sn)
    else:
        rec={}
        for h in (.2,.1,.05):
            with np.load(args.work/f'g{h}.npz') as d:rec[h]=(d['trace'],d['snap'])
        raise SystemExit(0 if write_results(rec) else 1)
