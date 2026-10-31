"""Execute the frozen injection/recovery matrix. See PROTOCOL.md."""
import csv,json,platform,time
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import chi2
from model import area,qnm,basis,fit,wilson,invert

ROOT=Path(__file__).resolve().parent
def main():
    started=time.time(); rng=np.random.default_rng(20261031)
    t=np.arange(0,.08,1/4096); f,tau=qnm(68,.68)
    # Same initial amplitude for all cuts; only frequency-scale cases renormalize SNR.
    fundamental=basis(t,f,tau)[:,0]
    amp=30/np.linalg.norm(fundamental)
    cases=[]
    for ratio in (1.5,1.02):
        for s in (.8,.9,1.,1.1,1.2,1.3):
            h=basis(t,f*s,tau/s)[:,0];h*=30/np.linalg.norm(h)
            cases.append((f'scale_R{ratio:g}_s{s:g}',ratio,s,0.,False,h))
    overtone=basis(t,*qnm(68,.68,1))@np.array([np.cos(1),-np.sin(1)])
    for start in (0.,.005,.01):
        cases.append((f'overtone_single_t{start*1000:g}ms',1.5,1.,start,False,amp*(fundamental+overtone)))
    cases.append(('overtone_two_t0ms',1.5,1.,0.,True,amp*(fundamental+overtone)))
    allrows=[]; summaries=[]; examples=[]
    for ci,(name,ratio,scale,start,two,h) in enumerate(cases):
        mask=t>=start; tx=t[mask]-start;hx=h[mask]
        ai=area(68,.68)/ratio
        rows=[]
        for i in range(200):
            noise=rng.normal(size=len(t));y=(h+noise)[mask]
            # Independent premerger measurement; no merger fit or imposed area sign.
            logai=np.log(ai)+rng.normal(0,.03)
            out=fit(tx,y,two)
            row={'case':name,'trial':i,'valid':out['valid'],'optimizer_success':out['optimizer_success'],'boundary':out['boundary'],
                 'invalid_reason':out.get('reason','boundary fit' if out['boundary'] else 'optimizer failure' if not out['optimizer_success'] else ''),
                 'rss':out['rss'],'dof':out['dof'],'log_initial_area':float(logai),
                 'log_final_area':out.get('log_area'),'sigma_log_final_area':out.get('sigma_log_area'),
                 'log_ratio':None,'sigma_log_ratio':None,'coverage':None,'decrease':None,'significant_decrease':None}
            if out['valid']:
                lr=out['log_area']-logai;sig=np.hypot(out['sigma_log_area'],.03)
                row.update(log_ratio=lr,sigma_log_ratio=sig,coverage=abs(lr-np.log(ratio))<=1.6448536269514722*sig,
                           decrease=lr<0,significant_decrease=lr+1.6448536269514722*sig<0)
            rows.append(row)
            if i==0:
                from model import design
                recovered=design(tx,np.asarray(out['parameters']),two)@out['amplitudes']
                examples.append({'case':name,'time_ms':(tx*1000).tolist(),'injected':hx.tolist(),'observed':y.tolist(),'recovered':recovered.tolist()})
        valid=[r for r in rows if r['valid']]; n=len(valid)
        summary={'case':name,'true_ratio':ratio,'scale':scale,'start_ms':start*1000,'two_modes':two,'trials':len(rows),
                 'valid':n,'invalid':len(rows)-n,'optimizer_failures':sum(not r['optimizer_success'] for r in rows),
                 'boundary_fits':sum(r['boundary'] for r in rows),'retained_snr':float(np.linalg.norm(hx)),
                 'median_inferred_ratio':float(np.median([np.exp(r['log_ratio']) for r in valid])) if n else None,
                 'median_area_relative_bias':float(np.median([np.exp(r['log_ratio'])/ratio-1 for r in valid])) if n else None,
                 'median_residual_p':float(np.median([chi2.sf(r['rss'],r['dof']) for r in rows])),
                 'expected_noiseless_ratio':ratio/scale**2 if name.startswith('scale') else ratio}
        for key in ('coverage','decrease','significant_decrease'):
            k=int(sum(r[key] for r in valid))
            summary[key]={'count':k,'denominator':n,'fraction':k/n if n else None,'wilson95':wilson(k,n)}
        summaries.append(summary);allrows.extend(rows)
        print(name, 'valid',n,'median R',summary['median_inferred_ratio'],'coverage',summary['coverage']['fraction'],flush=True)
    out={'study':'EFMW-BH-AREA-003','seed':20261031,'kind':'synthetic injection/recovery, not LIGO data',
         'mass_detector_msun':68,'spin':.68,'frequency_hz':float(f),'damping_seconds':float(tau),
         'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'cases':summaries}
    (ROOT/'results/synthetic.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'results/injection_trials.csv').open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
    (ROOT/'results/waveform_examples.json').write_text(json.dumps(examples,separators=(',',':'))+'\n')
    print('elapsed',time.time()-started,flush=True)
if __name__=='__main__':main()
