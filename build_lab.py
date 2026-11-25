"""Build a dependency-free HTML lab and static scientific figure from executed outputs."""
import json
import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def collision_home(area_html):
    folder = ROOT / 'collision'
    html = (folder / 'index.html').read_text()
    # Keep links to the evidence CSV, protocol and ZIP valid from the root.
    html = html.replace('<head>', '<head><base href="./collision/">', 1)
    old_ids = set(re.findall(r'\bid="([^"]+)"', area_html))
    current_ids = set(re.findall(r'\bid="([^"]+)"', html))
    anchors = json.dumps(sorted(old_ids - current_ids))
    legacy_links = (
        f'<script>function openAreaAnchor() {{if ({anchors}.includes(location.hash.slice(1))) {{'
        "const area = new URL('area.html', location.href);"
        "area.search = location.search; area.hash = location.hash;"
        "location.replace(area.href);}}"
        "addEventListener('hashchange',openAreaAnchor);openAreaAnchor();</script>"
    )
    html = html.replace('</head>', legacy_links + '</head>', 1)
    css = (folder / 'lab.css').read_text()
    html = html.replace('<link rel="stylesheet" href="lab.css">', f'<style>{css}</style>')
    scripts = []
    for name in ('orbits.js', 'fields.js', 'bhns-data.js', 'bhns.js', 'lab.js'):
        tag = f'<script defer src="{name}"></script>'
        if html.count(tag) != 1:
            raise ValueError(f'Missing or duplicate player asset: {name}')
        html = html.replace(tag, '')
        scripts.append('<script>' + (folder / name).read_text() + '</script>')
    return html.replace('</body>', ''.join(scripts) + '</body>')

def main():
    data={k:json.loads((ROOT/'results'/f).read_text()) for k,f in [('observational','observational.json'),('synthetic','synthetic.json'),('examples','waveform_examples.json'),('gates','gates.json')]}
    raw=json.dumps(data,separators=(',',':')).replace('</','<\\/')
    area_html = (ROOT/'lab.template.html').read_text().replace('__STUDY_DATA__',raw)
    (ROOT/'area.html').write_text(area_html)
    (ROOT/'index.html').write_text(collision_home(area_html))
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'EFMW-BH-AREA-003'})
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    o=data['observational'];q=np.asarray(o['ratio_quantiles']);p=np.linspace(0,1,len(q))
    axes[0].plot(q-1,p,color='#167d86');axes[0].axvline(0,color='#b85d35',ls='--');axes[0].set(xlabel='Fractional Kerr area growth',ylabel='Empirical cumulative fraction',title='GW250114 released posterior products')
    for r,col in [(1.5,'#167d86'),(1.02,'#b85d35')]:
        cases=[c for c in data['synthetic']['cases'] if c['case'].startswith('scale') and c['true_ratio']==r]
        xs=np.asarray([c['scale'] for c in cases]);ys=[c['median_inferred_ratio'] for c in cases]
        axes[1].plot(xs,r/xs**2,color=col,ls='--');axes[1].scatter(xs,ys,color=col,label=f'true R={r}')
    axes[1].axhline(1,color='gray',lw=1);axes[1].legend();axes[1].set(xlabel='Injected frequency scale s',ylabel='Recovered Af/Ai',title='Synthetic: exact mass degeneracy')
    selected=[c for c in data['synthetic']['cases'] if c['case'] in ('scale_R1.5_s1','overtone_single_t0ms','overtone_single_t5ms','overtone_single_t10ms','overtone_two_t0ms')]
    labels=['Pure 220','Omit 221\n0 ms','Omit 221\n5 ms','Omit 221\n10 ms','Fit both\n0 ms']
    for i,c in enumerate(selected):
        f=c['coverage']['fraction'];lo,hi=c['coverage']['wilson95'];axes[2].errorbar(i,f,yerr=[[f-lo],[hi-f]],fmt='o',color='#167d86',capsize=4)
        axes[2].annotate(f"{c['valid']}/200",(i,.05),ha='center',fontsize=8)
    axes[2].axhline(.9,color='#b85d35',ls='--');axes[2].set_xticks(range(5),labels);axes[2].set(ylim=(0,1.05),ylabel='Coverage among valid fits',title='Approximate 90% interval calibration')
    fig.savefig(ROOT/'results/summary.svg',metadata={'Date':None});plt.close(fig)
    from model import area,qnm
    golden=[{'m':m,'s':s,'area':float(area(m,s)),'qnm':[float(x) for x in qnm(m,s)]} for m,s in [(20,.05),(68,.68),(100,.95)]]
    (ROOT/'tests/physics-golden.json').write_text(json.dumps(golden,indent=2)+'\n')
    print('Built standalone collision index.html, area.html and results/summary.svg')
if __name__=='__main__':main()
