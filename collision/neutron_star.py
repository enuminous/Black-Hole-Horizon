"""Build the NS–BH replay from the CC BY 4.0 Einstein Toolkit BHNS dataset."""
import argparse
import base64
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tarfile
import h5py
import numpy as np
from matplotlib import colormaps
from PIL import Image

ROOT = Path(__file__).resolve().parent
ARCHIVE_MD5 = '302d6a1ca637298839b8cd9aaddecdce'
MEMBERS = ('rho.xy.h5', 'puncturetracker-pt_loc..asc', 'quasilocalmeasures-qlm_scalars..asc')
# G=c=M_sun=1. Solar mass parameter from IAU 2015 B3, c in SI, CODATA 2018 G.
GM_SUN = 1.3271244e20
C = 299792458.
G = 6.67430e-11
KM = GM_SUN / C**2 / 1000.
MS = GM_SUN / C**3 * 1000.
CGS = C**6 / (G*GM_SUN**2) / 1000.
HALF_KM, N, COLS = 60., 201, 8
LOG_MIN, LOG_MAX = 8., 15.
KEY = re.compile(r'HYDROBASE::rho it=(\d+) tl=0 rl=(\d+) c=(\d+)')
BOX = re.compile(r'/\[(-?\d+),(-?\d+)\]:\[(-?\d+),(-?\d+)\]/')
AXIS = (np.arange(N)+.5)*(2*HALF_KM/N)/KM-HALF_KM/KM

def extract(source, cache):
    with source.open('rb') as raw:
        if hashlib.file_digest(raw,'md5').hexdigest()!=ARCHIVE_MD5:
            raise ValueError('Upstream archive checksum differs')
    cache.mkdir(exist_ok=True,parents=True)
    seen=set()
    with tarfile.open(source,'r|gz') as tar:
        for member in tar:
            name=member.name.removeprefix('bhns_gw230529/')
            if name in MEMBERS and member.isfile():
                if name in seen: raise ValueError('Repeated archive member')
                with (cache/name).open('wb') as target:
                    shutil.copyfileobj(tar.extractfile(member),target)
                seen.add(name)
            if seen==set(MEMBERS): break
    if seen!=set(MEMBERS): raise ValueError('Missing input')

def table(file, *wanted):
    with file.open() as f:
        for line in f:
            if line.startswith('# data columns:'): break
        else: raise ValueError('No column definitions in '+str(file))
    ids={name:int(i)-1 for i,name in re.findall(r'(\d+):([^\s]+)',line)}
    rows=np.loadtxt(file,usecols=[8,*[ids[name] for name in wanted]])
    assert np.isfinite(rows).all() and np.all(np.diff(rows[:,0])>0)
    return rows

def sample_slice(h5, entries):
    # Paint valid nearest cells coarse to fine. Empty and inactive AMR boxes never win.
    pixels=np.full((N,N),np.nan)
    for level,component,key in sorted(entries):
        d=h5[key]; origin=d.attrs['origin']; delta=d.attrs['delta']
        ix=np.floor((AXIS-origin[0])/delta[0]+.5).astype(int)
        iy=np.floor((AXIS-origin[1])/delta[1]+.5).astype(int)
        if ix[-1]<0 or iy[-1]<0 or ix[0]>=d.shape[1] or iy[0]>=d.shape[0]:continue
        ox,oy=d.attrs['iorigin']
        active=d.attrs['active'].decode()
        boxes=BOX.findall(active)
        if not boxes and '{}' not in active:raise ValueError(active)
        for box in boxes:
            x0,y0,x1,y1=map(int,box)
            assert 0<=x0-ox<=x1-ox<d.shape[1] and 0<=y0-oy<=y1-oy<d.shape[0]
            a=np.flatnonzero((ix>=x0-ox)&(ix<=x1-ox))
            b=np.flatnonzero((iy>=y0-oy)&(iy<=y1-oy))
            if a.size and b.size:
                pixels[np.ix_(b,a)]=d[()][np.ix_(iy[b],ix[a])]
    if not np.isfinite(pixels).all() or np.min(pixels)<0:raise ValueError('Incomplete or invalid density slice')
    return pixels

def build(cache):
    punct=table(cache/MEMBERS[1],'pt_loc_x[0]','pt_loc_y[0]')
    masses=table(cache/MEMBERS[2],'qlm_mass[1]')
    if not np.all((masses[:,1]>3)&(masses[:,1]<6)):raise ValueError('Invalid horizon mass channel')
    series=np.column_stack([masses[:,0]*MS,masses[:,1]])
    frames=[]; pics=[]
    with h5py.File(cache/MEMBERS[0]) as f:
        by_it=defaultdict(list)
        for key in f:
            match=KEY.fullmatch(key)
            if match:
                it,level,comp=map(int,match.groups());by_it[it].append((level,comp,key))
        for it,entries in sorted(by_it.items()):
            time=float(f[entries[0][-1]].attrs['time'])
            assert punct[0,0]<=time<=punct[-1,0] and masses[0,0]<=time<=masses[-1,0]
            rho=sample_slice(f,entries)*CGS
            pos=[float(np.interp(time,punct[:,0],punct[:,col])*KM) for col in (1,2)]
            # Store the true pre-quantization slice peak as well as the display.
            frames.append([time*MS,*pos,float(rho.max())])
            log=np.log10(np.maximum(rho,10.**LOG_MIN))
            pics.append(np.rint(255*np.clip((log-LOG_MIN)/(LOG_MAX-LOG_MIN),0,1)).astype('uint8')[::-1])
    assert len(frames)==50 and frames[0][0]==0 and np.all(np.diff(np.array(frames)[:,0])>0)
    img=Image.new('P',(COLS*N,((len(frames)+COLS-1)//COLS)*N))
    palette=np.rint(colormaps['inferno'](np.linspace(0,1,256))[:,:3]*255).astype('uint8')
    img.putpalette(palette.tobytes())
    atlas=np.zeros((img.height,img.width),dtype='uint8')
    for i,pic in enumerate(pics):
        y=(i//COLS)*N;x=(i%COLS)*N;atlas[y:y+N,x:x+N]=pic
    img.putdata(atlas.ravel())
    buff=io.BytesIO();img.save(buff,format='PNG',optimize=True)
    # Use only the common density time span for the mass overlay and marker.
    end=frames[-1][0]
    curve=series[series[:,0]<=end+1e-10].copy()
    if end-curve[-1,0]>1e-9:
        curve=np.vstack([curve,[end,np.interp(end,series[:,0],series[:,1])]])
    mid=(curve[0,1]+curve[-1,1])/2
    j=np.flatnonzero(curve[:,1]>=mid)[0]
    marker=np.interp(mid,curve[j-1:j+1,1],curve[j-1:j+1,0])
    obj=dict(n=N,cols=COLS,halfKm=HALF_KM,logRange=[LOG_MIN,LOG_MAX],
             frames=np.round(frames,8).tolist(),mass=np.round(curve,8).tolist(),
             midpointMs=round(float(marker),8),png=base64.b64encode(buff.getvalue()).decode())
    (ROOT/'bhns-data.js').write_text('window.BHNSData='+json.dumps(obj,separators=(',',':'))+';\n')
    np.savetxt(ROOT/'bhns-horizon-mass.csv',curve,delimiter=',',header='time_ms,horizon_mass_Msun',fmt='%.10g',comments='')
    print(f'{len(frames)} slices through {end:.5f} ms, mass {curve[0,1]:.5f} to {curve[-1,1]:.5f}, midpoint {marker:.5f} ms')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('archive',type=Path)
    parser.add_argument('cache',type=Path)
    args=parser.parse_args()
    extract(args.archive,args.cache)
    build(args.cache)
