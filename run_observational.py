"""Reproduce released area products; no new strain likelihood is evaluated."""
import ast,hashlib,json,re
from pathlib import Path
import h5py
import numpy as np
from model import area,RSUN_KM

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/upstream/data'
def zscore(post,pre):
    return float((post.mean()-pre.mean())/np.sqrt(post.var()+pre.var()))
def main():
    with h5py.File(DATA/'area_law_inspiral_data.hdf5') as f:
        times=f['times'][:];pres=[f[f'area_insp_{i}'][:] for i in range(len(times))]
    idx=int(np.flatnonzero(np.isclose(times,-40,rtol=0,atol=.5))[0]);pre=pres[idx]
    with h5py.File(DATA/'ringdown_areas/220_10.5M_final_mass_spin_area.hdf5') as f:
        post_r=f['Area_f'][:];mass=f['M_f'][:];spin=f['chi_f'][:]
    post_p=np.load(DATA/'remnant_area_pyring_reweighted.npy')
    rng=np.random.default_rng(250114);n=min(len(post_r),len(post_p))
    pooled=np.concatenate([rng.choice(post_r,n,replace=False),rng.choice(post_p,n,replace=False)])
    assert np.all(pre>0) and np.all(pooled>0)
    # Compute the exact empirical product distribution, not independent-trial p-values.
    ratios=(pooled[:,None]/pre[None,:]).ravel()
    q=np.quantile(ratios,np.linspace(0,1,1001))
    prob=float(np.mean(ratios>1));qs=np.quantile(ratios,[.05,.5,.95])
    reference={'pre_cut_total_mass_times':float(times[idx]),'post_start_remnant_mass_times':10.5,
       'pre_samples':len(pre),'post_samples':len(pooled),'post_each_code':n,'pair_count':int(ratios.size),
       'z':zscore(pooled,pre),'ratio_median':float(qs[1]),'ratio90':qs[[0,2]].tolist(),
       'fractional_growth_median':float(qs[1]-1),'fractional_growth90':(qs[[0,2]]-1).tolist(),
       'empirical_positive_fraction':prob,'negative_pairs':int(np.sum(ratios<1)),
       'initial_area_median_km2':float(np.median(pre)*RSUN_KM**2),'final_area_median_km2':float(np.median(pooled)*RSUN_KM**2),
       'eta_median_crossing':float(1/qs[1]),'eta_positive90_threshold':float(1/qs[0]),
       'eta_negative90_threshold':float(1/qs[2]),'pooling_seed':250114}
    del ratios
    scans=[{'pre_cut':float(t),'z':zscore(pooled,a),'samples':len(a)} for t,a in zip(times,pres)]
    rings=[]
    for path in sorted((DATA/'ringdown_areas').glob('*.hdf5')):
        match=re.match(r'(.+)_([\d.]+)M_final',path.name)
        with h5py.File(path) as f: a=f['Area_f'][:]
        rings.append({'model':match[1],'start':float(match[2]),'samples':len(a),'z':zscore(a,pre)})
    code_z={'ringdown_only':zscore(post_r,pre),'pyring_only':zscore(post_p,pre),'pooled':zscore(pooled,pre)}
    # Evaluate just the released statistic function; do not execute unrelated upstream code.
    src=(ROOT/'data/upstream/scripts/significance_estimate_variance.py').read_text()
    tree=ast.parse(src);func=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='get_gaussian_significance')
    namespace={'np':np};exec(compile(ast.Module(body=[func],type_ignores=[]),'<upstream statistic>','exec'),namespace)
    upstream=float(namespace['get_gaussian_significance'](pooled,pre))
    err=float(np.max(np.abs(area(mass,spin)/(RSUN_KM**2)/post_r-1)))
    obs={'event':'GW250114','source_doi':'10.5281/zenodo.16877102','reference':reference,
         'ratio_quantiles':q.tolist(),'premerger_scan':scans,'ringdown_scan':rings,'code_comparison':code_z,
         'upstream_statistic':upstream,'upstream_difference':abs(upstream-reference['z']),
         'released_kerr_area_max_relative_error':err,
         'statistical_note':'Empirical pairs reuse finite, possibly correlated posterior samples; no binomial confidence or Gaussian-tail detection probability is inferred.'}
    (ROOT/'results/observational.json').write_text(json.dumps(obs,indent=2)+'\n')
    # Compact, lossless input cache for offline reproductions of all used summaries.
    arrays={'times':times,'post_ringdown':post_r,'post_pyring':post_p,'post_pooled':pooled,'mass':mass,'spin':spin}
    arrays.update({f'pre_{i}':a for i,a in enumerate(pres)})
    for row in rings:
        with h5py.File(DATA/f"ringdown_areas/{row['model']}_{row['start']:g}M_final_mass_spin_area.hdf5") as f:
            arrays[f"ring_{row['model']}_{row['start']:g}"]=f['Area_f'][:]
    np.savez_compressed(ROOT/'data/area_inputs.npz',**arrays)
    (ROOT/'results/observational-summary.txt').write_text(json.dumps(reference,indent=2)+'\n')
    print(json.dumps(reference,indent=2));print('codes',code_z,'area closure',err)
if __name__=='__main__':main()
