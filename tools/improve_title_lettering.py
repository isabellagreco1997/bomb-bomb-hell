"""Assemble the authored three-color lettering with the original animated bomb."""
from pathlib import Path
import json
import math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/title/sprites'


def improve():
    manifest_path = ASSETS / 'manifest-grid250.json'
    manifest = json.loads(manifest_path.read_text())
    source_manifest = json.loads((ASSETS / 'manifest-grid250-source.json').read_text())
    source_track = source_manifest['sprites']['logo']
    source = Image.open(ASSETS / 'logo-grid250-atlas.png').convert('RGBA')
    w, h = source_track['size']
    ox, oy = source_track['origin']
    master = np.array(Image.open(ASSETS / 'logo-flat-lettering.png').convert('RGBA'))
    lettering = np.array(Image.open(ASSETS / 'logo-lettering-region.png')) > 0
    expected = {(216, 38, 51), (234, 184, 85), (32, 7, 14)}
    assert set(map(tuple, master[master[:, :, 3] > 0, :3])) == expected
    frames = []
    for i in range(source_track['frames']):
        sx, sy = i % source_track['columns'] * w, i // source_track['columns'] * h
        frame = Image.new('RGBA', (250, 200))
        frame.alpha_composite(source.crop((sx, sy, sx + w, sy + h)), (ox, oy))
        before = np.array(frame)
        after = before.copy()
        after[lettering] = master[lettering]
        assert np.array_equal(before[~lettering], after[~lettering])
        assert set(np.unique(after[:, :, 3])) <= {0, 255}
        frames.append(Image.fromarray(after))
    union = np.logical_or.reduce([np.array(frame)[:, :, 3] > 0 for frame in frames])
    yy, xx = np.where(union)
    box = (int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1)
    w, h = box[2] - box[0], box[3] - box[1]
    cols = source_track['columns']
    result = Image.new('RGBA', (cols * w, math.ceil(len(frames) / cols) * h))
    for i, frame in enumerate(frames):
        result.alpha_composite(frame.crop(box), (i % cols * w, i // cols * h))
    track = manifest['sprites']['logo']
    track.update(file='logo-flat-grid250-atlas.png', size=[w, h], origin=list(box[:2]),
                 lettering='Authored solid red faces, one gold outline color, dark separation')
    result.save(ASSETS / track['file'], optimize=True)
    frames[0].save(ASSETS / 'logo-flat-grid250-idle.png')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Flat lettering:', len(frames), 'frames; exact three-color text palette; bomb/fuse unchanged')
    return track


if __name__ == '__main__':
    improve()
