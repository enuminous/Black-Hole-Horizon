"""Fetch the pinned LVK archive; extract only the area-law inputs and scripts."""
import hashlib,json,tarfile,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
URL='https://zenodo.org/records/16877102/files/GW250114_data_release.tar.gz?download=1'
MD5='58c00488e66bc87d588b642cbdf33e2d'

def main():
    cache=ROOT/'data/GW250114_data_release.tar.gz'
    cache.parent.mkdir(exist_ok=True)
    if not cache.exists():
        tmp=cache.with_suffix('.partial')
        with urllib.request.urlopen(URL,timeout=120) as r,tmp.open('wb') as f:
            while b:=r.read(1024*1024):f.write(b)
        tmp.rename(cache)
    digest=hashlib.md5(cache.read_bytes()).hexdigest()
    if digest!=MD5:raise RuntimeError('Archive checksum mismatch; do not analyze')
    entries=[]
    with tarfile.open(cache) as tar:
        for item in tar.getmembers():
            if not item.isfile():continue
            # Never extract filesystem paths or links directly from an archive.
            parts=Path(item.name).parts
            if '..' in parts or Path(item.name).is_absolute():raise ValueError('Unsafe member')
            if not (any(s in item.name.lower() for s in ('area','readme','license')) or item.name in ('scripts/significance_estimate_variance.py','scripts/data_sources.py')):continue
            raw=tar.extractfile(item).read();target=ROOT/'data/upstream'/item.name
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            entries.append({'path':item.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    manifest={'url':URL,'doi':'10.5281/zenodo.16877102','released':'2025-09-10','license':'CC-BY-4.0',
              'authors':'LIGO Scientific Collaboration, Virgo Collaboration and KAGRA Collaboration',
              'archive_bytes':cache.stat().st_size,'md5':digest,'sha256':hashlib.sha256(cache.read_bytes()).hexdigest(),'members':entries}
    (ROOT/'sources/data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Verified archive; extracted {len(entries)} members')
if __name__=='__main__':main()
