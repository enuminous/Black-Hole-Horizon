"""Offline checks of published results, cached inputs and independent identities."""
import ast,hashlib,json,unittest
from pathlib import Path
import numpy as np
from model import area,RSUN_KM
ROOT=Path(__file__).resolve().parent
def main():
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    gates=[{'name':'Numerical identity and noiseless recovery tests','status':'PASS' if result.wasSuccessful() else 'FAIL','detail':f'{result.testsRun-len(result.failures)-len(result.errors)}/{result.testsRun} checks'}]
    def check(name,passed,detail):gates.append({'name':name,'status':'PASS' if passed else 'FAIL','detail':detail})
    raw=ROOT/'PROTOCOL.md';expected=(ROOT/'PROTOCOL.sha256').read_text().split()[0]
    check('Frozen protocol hash',hashlib.sha256(raw.read_bytes()).hexdigest()==expected,expected)
    o=json.loads((ROOT/'results/observational.json').read_text());s=json.loads((ROOT/'results/synthetic.json').read_text())
    cache=np.load(ROOT/'data/area_inputs.npz');pre=cache[f"pre_{int(np.where(cache['times']==-40)[0][0])}"];post=cache['post_pooled']
    z=(post.mean()-pre.mean())/np.sqrt(post.var()+pre.var())
    check('Published 4.4 reference reproduced',abs(z-4.4)<.15,f'z={z:.12f}; frozen tolerance 0.15')
    check('Cached inputs reproduce stored statistic',abs(z-o['reference']['z'])<1e-12,'Independent cache read; same statistic, not independent astrophysical evidence')
    check('Released mass/spin/area consistency',np.max(abs(area(cache['mass'],cache['spin'])/RSUN_KM**2/cache['post_ringdown']-1))<1e-12,'Kerr formula matches supplied area values')
    # Equivalent pair count via order statistics avoids the all-pairs array.
    neg=int(np.searchsorted(np.sort(post),pre,side='left').sum())
    check('Exact empirical pair count',neg==o['reference']['negative_pairs'],f'{neg} negative pairs; pairs reuse samples')
    check('Trial accounting',sum(c['trials'] for c in s['cases'])==3200 and all(c['valid']+c['invalid']==c['trials'] for c in s['cases']),'16 cases × 200; invalid fits retained')
    for c in s['cases']:
        if c['case'] in ('scale_R1.5_s1','scale_R1.02_s1','overtone_two_t0ms'):
            lo,hi=c['coverage']['wilson95'];check('90% coverage: '+c['case'],lo<=.9<=hi,f"{c['coverage']['count']}/{c['valid']}; Wilson95 [{lo:.4f},{hi:.4f}]")
    gates.append({'name':'EFMW-specific waveform and observational bound','status':'UNRESOLVED','detail':'No regular C1 black-hole solution, perturbation spectrum or likelihood mapping supplied'})
    (ROOT/'results/gates.json').write_text(json.dumps(gates,indent=2)+'\n')
    print(json.dumps(gates,indent=2))
    # Expected scientific calibration FAIL is a result, not a software test failure.
    hard=[g for g in gates if not g['name'].startswith('90% coverage:') and g['status']=='FAIL']
    if hard:raise SystemExit(1)
if __name__=='__main__':main()
