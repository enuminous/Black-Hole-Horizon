"""Bounded Kerr-area and ideal ringdown model; no detector data inference."""
import numpy as np
from scipy.optimize import least_squares

TSUN = 4.9254909476412675e-6  # G M_sun/c^3, seconds (LAL convention)
RSUN_KM = TSUN * 299792.458
COEFF = [(1.5251, -1.1568, .1292, .7000, 1.4187, -.4990),
         (1.3673, -1.0260, .1628, .1000, .5436, -.4731)]

def area(m, chi):
    m, chi = np.asarray(m), np.asarray(chi)
    if np.any(m <= 0) or np.any(np.abs(chi) > 1):
        raise ValueError('Kerr area needs positive mass and |spin| <= 1')
    return 8*np.pi*(RSUN_KM*m)**2*(1+np.sqrt(1-chi**2))

def qnm(m, chi, n=0):
    f1,f2,f3,q1,q2,q3 = COEFF[n]
    omega = f1+f2*(1-np.asarray(chi))**f3
    q = q1+q2*(1-np.asarray(chi))**q3
    f = omega/(2*np.pi*np.asarray(m)*TSUN)
    return f, q/(np.pi*f)

def invert(f, tau):
    q = np.pi*np.asarray(f)*np.asarray(tau)
    if np.any(q <= .7):
        raise ValueError('quality factor outside inverse fit domain')
    chi = 1-((q-.7)/1.4187)**(1/(-.4990))
    if np.any(chi < 0) or np.any(chi > .99):
        raise ValueError('recovered spin outside fit domain [0,.99]')
    omega = 1.5251-1.1568*(1-chi)**.1292
    return omega/(2*np.pi*np.asarray(f)*TSUN), chi

def basis(t, f, tau):
    env = np.exp(-t/tau)
    return np.column_stack((env*np.cos(2*np.pi*f*t), env*np.sin(2*np.pi*f*t)))

def design(t, p, two=False):
    if not two:
        return basis(t, *np.exp(p))
    m, chi = np.exp(p[0]), p[1]
    return np.column_stack([basis(t, *qnm(m, chi, n)) for n in (0,1)])

def logarea(p, two=False):
    m,chi = (np.exp(p[0]),p[1]) if two else invert(*np.exp(p))
    return float(np.log(area(m,chi)))

def fit(t, y, two=False):
    """Variable projection, then full-model local Gaussian covariance."""
    if two:
        lo,hi = [np.log(20),0.], [np.log(150),.99]
        starts = [[np.log(68),s] for s in (.3,.68,.9)]
    else:
        lo,hi = np.log([100,.0005]), np.log([500,.02])
        starts = [np.log([f,.004]) for f in (180,270,380)]
    def residual(p):
        d=design(t,p,two); a=np.linalg.lstsq(d,y,rcond=None)[0]
        return d@a-y
    opts=[least_squares(residual,s,bounds=(lo,hi),xtol=1e-9,ftol=1e-9,gtol=1e-9,max_nfev=150) for s in starts]
    opt=min(opts,key=lambda r:np.dot(r.fun,r.fun)); p=opt.x
    d=design(t,p,two); a=np.linalg.lstsq(d,y,rcond=None)[0]
    out={'optimizer_success':bool(opt.success),'boundary':bool(np.any(np.minimum(p-np.asarray(lo),np.asarray(hi)-p)<1e-5)),
         'rss':float(opt.fun@opt.fun),'dof':len(y)-len(p)-len(a),'parameters':p.tolist(),'amplitudes':a.tolist()}
    try:
        eps=1e-5; j=[]; grad=[]
        for k in range(2):
            step=np.eye(2)[k]*eps
            j.append((design(t,p+step,two)@a-design(t,p-step,two)@a)/(2*eps))
            grad.append((logarea(p+step,two)-logarea(p-step,two))/(2*eps))
        jac=np.column_stack(j+[d[:,i] for i in range(d.shape[1])])
        info=jac.T@jac
        # Do not scale by RSS: the injected unit noise variance is known.
        if np.linalg.cond(info)>1e14: raise ValueError('ill-conditioned covariance')
        cov=np.linalg.inv(info)[:2,:2]
        var=float(np.asarray(grad)@cov@np.asarray(grad))
        if var<=0: raise ValueError('invalid area variance')
        out.update(valid=bool(opt.success and not out['boundary']),log_area=logarea(p,two),sigma_log_area=np.sqrt(var))
    except (ValueError,np.linalg.LinAlgError,FloatingPointError) as exc:
        out.update(valid=False,reason=str(exc))
    return out

def wilson(k,n,z=1.959963984540054):
    if not n:return [None,None]
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d
    h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [float(c-h),float(c+h)]
