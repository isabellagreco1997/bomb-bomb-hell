"""Check alpha, atlas dimensions, local motion, and static body preservation."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]/'assets/title/sprites'
m=json.loads((root/'manifest.json').read_text())
for name,d in m['sprites'].items():
    atlas=np.array(Image.open(root/d['file']))
    w,h=d['size'];cols=d['columns']
    assert atlas.shape==(h*((d['frames']+cols-1)//cols),w*cols,4),name
    assert set(np.unique(atlas[:,:,3])).issubset({0,255}),name+' has soft/dirty alpha'
    assert np.any(atlas[:,:,3]==0),name+' has no transparency'
    frames=[atlas[(i//cols)*h:(i//cols+1)*h,(i%cols)*w:(i%cols+1)*w] for i in range(d['frames'])]
    assert len({f.tobytes() for f in frames})>=4,name+' is not animated'
    changed=np.logical_or.reduce([np.any(f!=frames[0],axis=2) for f in frames])
    if name=='heroine':
        # Below the hair/face/fuse, clothing and limbs must remain pixel-identical.
        static_start=196-d['origin'][1]
        assert not changed[static_start:].any(),'Heroine body moves between frames'
    if name=='ghost':
        # The central wax body between the crown and eyes remains anchored.
        y0,y1=138-d['origin'][1],146-d['origin'][1]
        assert not changed[y0:y1].any(),'Ghost body moves between frames'
    print(name,':',len(frames),'frames;',round(float(changed.mean())*100,1),'percent of atlas cell changes; binary transparency PASS')
print('Sprite checks passed.')
