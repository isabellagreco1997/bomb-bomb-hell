"""Pick real key frames out of the AI's 7-frame rows by measuring the feet, build 4-beat walk cycles."""
import sys, os, json; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
D='assets/sprites/48/anim'; W='work'
def frames(k): return [Image.open(f'{D}/heroine_walk_{k}_{i}.png') for i in range(7)]
def measure(f, facing):
    a=np.array(f)[...,3]>0; H,Wd=a.shape
    head=a[:int(H*0.45)]; hy,hx=np.nonzero(head); cx=hx.mean()
    legs=a[int(H*0.72):]                                   # bottom 28% = legs + boots
    ly,lx=np.nonzero(legs)
    spread=lx.max()-lx.min() if len(lx) else 0
    if facing in ('down','up'):
        left=legs[:, :int(cx)]; right=legs[:, int(cx):]
        bl=np.nonzero(left.any(1))[0].max() if left.any() else 0
        br=np.nonzero(right.any(1))[0].max() if right.any() else 0
        return dict(spread=int(spread), step=int(bl-br))    # +ve: screen-left foot lower (forward)
    else:
        return dict(spread=int(spread), step=round(lx.mean()-cx,1))  # leg mass ahead(-) / behind(+) the head, facing left
cycles={}
for k in ('down','up','left'):
    fr=frames(k); m=[measure(f,k) for f in fr]
    print(k,[ (i,d['spread'],d['step']) for i,d in enumerate(m)])
    steps=np.array([d['step'] for d in m]); spreads=np.array([d['spread'] for d in m])
    a=int(steps.argmax()); b=int(steps.argmin())
    rest=[i for i in range(7) if i not in (a,b)]
    # pass frames = the two with the smallest spread among the rest (feet together)
    p=sorted(rest,key=lambda i:spreads[i])[:2]
    cyc=[a,p[0],b,p[1] if len(p)>1 else p[0]]
    cycles[k]=cyc; print('  cycle',cyc)
cycles['right']=cycles['left']
json.dump(cycles,open(f'{D}/heroine_cycles.json','w'))
for k,cyc in cycles.items():
    fr=[Image.open(f'{D}/heroine_walk_{k}_{i}.png') for i in cyc]
    for j,f in enumerate(fr): f.save(f'{D}/heroine_cycle_{k}_{j}.png')
    big=[f.resize((f.width*4,f.height*4),Image.NEAREST) for f in fr]
    bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/heroine_cycle_{k}.gif',save_all=True,append_images=bg[1:],duration=130,loop=0)
    sheet(fr,4,5,bg=(40,4,12,255)).save(f'{W}/strip_cycle_{k}.png')
