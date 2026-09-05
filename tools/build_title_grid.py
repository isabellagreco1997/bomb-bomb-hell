"""Keep the pixel background and publish the approved sprites at native detail.

The user restored the original detailed logo and characters after trying a
coarser shared grid. Their smaller display sizes and layout live in title.css;
no intermediate image downsampling should be reapplied to these animations.
"""
from pathlib import Path
import copy
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/title/sprites'
STAGE = (250, 200)


def build():
    source = json.loads((ASSETS / 'manifest.json').read_text())
    assert source['stage'] == [350, 280]
    result = {'stage': list(STAGE), 'fps': 24, 'sprites': {}}
    for key in ('heroine', 'ghost', 'logo'):
        track = copy.deepcopy(source['sprites'][key])
        track['stage'] = [350, 280]
        result['sprites'][key] = track
        print(key, track['file'], 'native detail retained')
    Image.open(ASSETS / 'skyline-base.png').resize(STAGE, Image.Resampling.NEAREST).save(ASSETS / 'skyline-grid250.png')
    for filename in ('manifest-grid250.json', 'manifest-grid250-source.json'):
        (ASSETS / filename).write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    build()
