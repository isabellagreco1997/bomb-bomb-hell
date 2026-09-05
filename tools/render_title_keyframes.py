"""Render the stored, authored pixel rows. This does not design or deform frames."""
from pathlib import Path
import json
from PIL import Image

root=Path(__file__).resolve().parents[1]/'assets/title/sprites'
art=root/'keyframes'
records=json.loads((art/'pixel-art.json').read_text())
for name,record in records.items():
    source=Image.open(root/f'{name}-base.png').convert('RGBA')
    for index,patches in enumerate(record['keyframes']):
        frame=source.copy(); pixels=frame.load()
        for patch in patches:
            for dy,row in enumerate(patch['rows']):
                for dx,symbol in enumerate(row):
                    if symbol=='.': continue
                    x,y=patch['x']+dx,patch['y']+dy
                    if not (0<=x<frame.width and 0<=y<frame.height):
                        raise ValueError(f'{name} frame {index}: pixel outside canvas')
                    pixels[x,y]=(0,0,0,0) if symbol==' ' else tuple(record['palette'][symbol])+(255,)
        frame.save(art/f'{name}-{index:02d}.png')
print('Rendered stored pixel-map keyframes.')
