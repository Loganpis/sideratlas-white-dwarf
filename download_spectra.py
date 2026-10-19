"""Re-fetch the exact published DA spectra, checking their saved hashes."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parent


def main():
    provenance=json.loads((ROOT/'data/spectra-provenance.json').read_text())
    for record in provenance['records']:
        path=(ROOT/record['file']).resolve()
        if not path.is_relative_to(ROOT/'data'):raise ValueError('Input path outside data directory')
        if not path.exists():
            with urllib.request.urlopen(record['url'],timeout=30) as response:data=response.read()
            if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Remote input changed; review before adopting a new model version')
            path.write_bytes(data)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise ValueError(f'Modified input: {path.name}')
    print('Verified all 10 original Koester spectra')


if __name__=='__main__':main()
