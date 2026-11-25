"""Linear C1 and Klein–Gordon solvers on the leading Brill–Lindquist close-limit metric."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import numpy as np
from scipy.special import lambertw

HERE = Path(__file__).resolve().parent
LABELS = ('zero', 'plus', 'minus')
EPSILON = 1e-4
Z = 1 + 6 * 0.5**2
BARE_MASS = 0.20

class Exterior:
    def __init__(self, dx, limits, half_separation):
        self.h = dx
        self.x = np.arange(round((limits[1] - limits[0])/dx) + 1)*dx + limits[0]
        w = lambertw(np.exp(self.x/2-1)).real
        self.r = r = 2*(1+w)
        self.f = f = w/(1+w)
        L = 2.0  # (ell-1)(ell+2)/2, ell=2, M=1
        self.A = (L*(L+1)*r*r + 3*L*r + 6)/(r*r*(L*r+3))
        self.B = (L*r*r-3*L*r-3)/(r*f*(L*r+3))
        self.vz = 2*f*(L*L*(L+1)*r**3 + 3*L*L*r*r + 9*L*r+9)/(r**3*(L*r+3)**2)
        self.r2 = r*r
        self.area_face = ((r[:-1]+r[1:])/2)**2
        rho = (r-1+np.sqrt(r*(r-2)))/2
        # Binary conformal factor: 1 + 1/(2 rho) + a² P2/(2 rho³).
        self.initial_K = k = 2*half_separation**2/(rho**3*(1+1/(2*rho)))
        dk_drho = k*(-2/rho-2/(2*rho+1))
        dk_dr = dk_drho/(1-1/(4*rho**2))
        self.initial_psi = r/(L+1)*(k+f/(L+3/r)*(k-r*dk_dr))

    def d1(self, u):
        v = np.zeros_like(u)
        v[...,2:-2] = (u[...,:-4]-8*u[...,1:-3]+8*u[...,3:-1]-u[...,4:])/(12*self.h)
        return v

    def d2(self, u):
        v = np.zeros_like(u)
        v[...,2:-2] = (-u[...,:-4]+16*u[...,1:-3]-30*u[...,2:-2]+16*u[...,3:-1]-u[...,4:])/(12*self.h**2)
        return v

    def geometry(self, psi, vel, acc):
        r, f, d = self.r, self.f, self.d1
        def even(z):
            dz = d(z)
            k = self.A*z + dz
            # Martel–Poisson/Zerilli inverse, Lambda/2=2+3/r.
            h = (r*d(k)-(2+3/r)*dz)/f + 3*z/r**2
            return k, h
        k,h = even(psi)
        kt,ht = even(vel)
        shift = r/f*d(vel) + self.B*vel
        shift_t = r/f*d(acc) + self.B*acc
        return k,h,shift,kt,ht,shift_t

    def flux_divergence(self, field, gradient_weight=1., drift=None):
        grad = np.diff(field, axis=-1)/self.h
        if isinstance(gradient_weight, np.ndarray):
            grad *= (gradient_weight[1:]+gradient_weight[:-1])/2
        if drift is not None:
            grad += (drift[...,1:]+drift[...,:-1])/2
        flux = self.area_face*grad
        result = np.zeros_like(field)
        result[...,1:-1] = np.diff(flux, axis=-1)/(self.h*self.r2[1:-1])
        return result

    def c1_rhs(self, state, geo):
        # pi is the kinetic-weighted canonical momentum divided by r².
        phi,p,quad,pq = state
        k,h,b,_,_,_ = geo
        v = p/Z
        qv = pq/Z-(k+h)*v+b*self.d1(phi)
        dp = Z*self.flux_divergence(phi)-self.f*BARE_MASS**2*phi
        dpq = Z*(self.flux_divergence(quad)+self.flux_divergence(phi,k-h,b*v))
        dpq -= self.f*(Z*6/self.r2*quad+BARE_MASS**2*(quad+k*phi))
        return v,dp,qv,dpq

    def kg_rhs(self, state, geo, mu):
        # A separate fourth-order, expanded wave operator acts on u=r phi.
        u,v,w,z = state
        k,h,b,kt,ht,bt = geo
        r,f,d = self.r,self.f,self.d1
        pot = f*(2/r**3+mu**2)
        phi, phit = u/r, v/r
        grad = d(phi)
        lap = self.d2(phi) + 2*f/r*grad
        source = (-2*h*lap + (d(k-h)+bt)*grad
                  + (d(b)+2*f*b/r-kt-ht)*phit
                  + 2*b*d(phit) + f*mu**2*h*phi)
        return v,self.d2(u)-pot*u,z,self.d2(w)-(pot+6*f/r**2)*w+r*source

    def rhs(self, state, mu):
        result = np.empty_like(state)
        psi, vel = state[:2]
        acc = self.d2(psi)-self.vz*psi
        geo = self.geometry(psi,vel,acc)
        result[:2] = vel,acc
        block=(4,3,len(psi))
        result[2:14].reshape(block)[:] = self.c1_rhs(state[2:14].reshape(block),geo)
        result[14:].reshape(block)[:] = self.kg_rhs(state[14:].reshape(block),geo,mu)
        # Hold the end buffers at their initial data outside the measurement cone.
        result[:,:5]=0
        result[:,-5:]=0
        return result

def simulate(dx, limits, a, mismatch, tag):
    tic=time.monotonic()
    grid=Exterior(dx,limits,a)
    x,r=grid.x,grid.r
    dt=dx/4
    mu=BARE_MASS if mismatch else BARE_MASS/np.sqrt(Z)
    state=np.zeros((26,len(x)))
    state[0]=grid.initial_psi
    pulse=np.exp(-(x-8)**2/8)
    for arm,amp in enumerate((0.,EPSILON,-EPSILON)):
        state[2+arm]=amp*pulse/r
        state[14+arm]=amp*pulse
    rec=[]
    size=0.
    max_zero=0.
    mismatch0={}
    extract=[np.argmin(abs(x-point)) for point in (18.,20.)]
    cols=['t']
    for point in (18,20):
        cols.extend([f'psi_g_x{point}'])
        for code in ('C1','KG'):
            for ell in (0,2):
                cols.extend(f'{code}_l{ell}_{label}_x{point}' for label in LABELS)
    n=round(36/dt)
    for j in range(n+1):
        if j % round(.2/dt)==0:
            t=j*dt
            row=[t]
            geo=grid.geometry(state[0],state[1],grid.d2(state[0])-grid.vz*state[0])
            cone=abs(x-20)<=36-t+1e-10
            size=max(size,max(np.max(abs(arr[cone])) for arr in geo[:3]))
            if j==0 and a:
                for name,arr in zip(('K','H'),geo[:2]):
                    mismatch0[name]=float(np.linalg.norm((arr-grid.initial_K)[cone])/np.linalg.norm(grid.initial_K[cone]))
            for i in extract:
                row.append(state[0,i])
                for start,weight in ((2,r[i]),(14,1.)):
                    for offset in (0,6):
                        row.extend(weight*state[start+offset:start+offset+3,i])
            rec.append(row)
        max_zero=max(max_zero,float(np.max(abs(state[[2,5,8,11,14,17,20,23],:]))))
        if j==n:break
        k1=grid.rhs(state,mu)
        k2=grid.rhs(state+dt/2*k1,mu)
        k3=grid.rhs(state+dt/2*k2,mu)
        k4=grid.rhs(state+dt*k3,mu)
        state+=dt/6*(k1+2*k2+2*k3+k4)
    assert np.isfinite(state).all() and np.isfinite(rec).all()
    directory=HERE/'results';directory.mkdir(exist_ok=True)
    np.savetxt(directory/(tag+'.csv'),rec,delimiter=',',header=','.join(cols),comments='',fmt='%.16e')
    meta=dict(dx=dx,dt=dt,domain=limits,a=a,mu_comparator=mu,Z=Z,m=BARE_MASS,
              max_metric_in_probe_cone=size,initial_metric_relative_L2=mismatch0,
              max_abs_zero_full_grid_all_steps=max_zero,wall_seconds=time.monotonic()-tic,
              protocol_sha256=hashlib.sha256((HERE/'protocol.md').read_bytes()).hexdigest())
    (directory/(tag+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
    print(tag,json.dumps(meta),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('tag')
    ap.add_argument('--dx',type=float,required=True)
    ap.add_argument('--domain',nargs=2,type=float,default=[-28,76])
    ap.add_argument('--half-separation',type=float,default=.06)
    ap.add_argument('--wrong-mass',action='store_true')
    args=ap.parse_args()
    simulate(args.dx,args.domain,args.half_separation,args.wrong_mass,args.tag)
