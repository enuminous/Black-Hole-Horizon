"""Build an offline SXS horizon trajectory subset from the pinned CC BY 4.0 release."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
import h5py
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://zenodo.org/api/records/13182440/files/Lev5:'
MD5 = {'Horizons.h5':'d1e13bc439f3bc71a912cce697783ba6','metadata.json':'0d573928205effecc3c13d576774c83e'}

def build(cache):
    cache.mkdir(exist_ok=True, parents=True)
    for name, expected in MD5.items():
        file = cache / name
        if not file.exists():
            with urlopen(SOURCE + name + '/content', timeout=90) as response:
                file.write_bytes(response.read())
        if hashlib.md5(file.read_bytes()).hexdigest() != expected:
            raise ValueError('Source checksum mismatch: ' + name)
    metadata = json.loads((cache / 'metadata.json').read_text())
    tracks = {}
    with h5py.File(cache / 'Horizons.h5') as source:
        for group, symbol in zip(('AhA.dir','AhB.dir','AhC.dir'),'ABC'):
            g = source[group]
            xyz = g['CoordCenterInertial.dat'][()]
            times = xyz[:,0]
            t0 = source['AhC.dir/CoordCenterInertial.dat'][0,0]
            # Keep half-M cadence in the last 280M and postmerger, 2M elsewhere.
            sel = [0]
            for i in range(1,len(times)-1):
                if times[i]-times[sel[-1]] >= (.49 if times[i]>=t0-280 else 1.99):
                    sel.append(i)
            sel.append(len(times)-1)
            t = times[sel]
            props = []
            for col in ('ArealMass.dat','ChristodoulouMass.dat','chiMagInertial.dat'):
                tab = g[col][()]
                assert tab[0,0] <= t[0] and tab[-1,0] >= t[-1]
                props.append(np.interp(t,tab[:,0],tab[:,1]))
            tracks[symbol] = np.column_stack([t-t0,xyz[sel,1:],*props]).round(8).tolist()
    result = dict(source='SXS:BBH:0305',level=5,epoch=float(t0),q=metadata['reference_mass_ratio'],
                  orbits=metadata['number_of_orbits'],columns=['t-t_common','x','y','z','M_irr','M_Ch','spin'],
                  tracks=tracks)
    (ROOT/'orbits.js').write_text('window.BHOrbit='+json.dumps(result,separators=(',',':'))+';\n')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('cache',type=Path);build(ap.parse_args().cache)
