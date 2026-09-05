"""Candle spirit: ONE body (idle frame 0) + the flame from each of the 6 idle/move frames = 6 flicker frames, no body jitter.
Floating is done in-game (sine dy), direction needs no mirror."""
import sys, os, json; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'
fr=[np.array(Image.open(f'{A}/ghost_{k}_{i}.png')) for k in ('idle','move') for i in range(3)]
base=fr[0]
# body top = first row where a wide, light (wax) run appears below the flame: find the flame/body boundary by colour: wax is bright & unsaturated
def is_wax(p): r,g,b=p[:3].astype(int); return p[3]>0 and min(r,g,b)>150 and (max(r,g,b)-min(r,g,b))<70
rows=[sum(is_wax(p) for p in row) for row in base]
body_top=next(y for y,c in enumerate(rows) if c>=2)-1; print('body top row',body_top)
# align each frame's body to the base by the wax centroid, then swap only the rows above body_top (flame)
def wax_cx(a):
    m=np.array([[is_wax(p) for p in row] for row in a]); ys,xs=np.nonzero(m); return xs.mean()
cx0=wax_cx(base); out=[]
for a in fr:
    dx=int(round(cx0-wax_cx(a))); s=np.roll(a,dx,axis=1)
    f=base.copy(); f[:body_top]=s[:body_top]; out.append(f)
# ping-pong through the 6 flames for a smooth flicker
order=[0,1,2,3,4,5,4,3,2,1]
for j,i in enumerate(order): Image.fromarray(out[i],'RGBA').save(f'{A}/ghost_flicker_{j}.png')
big=[Image.fromarray(out[i],'RGBA').resize((192,240),Image.NEAREST) for i in order]; bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
for b,g in zip(big,bg): g.paste(b,(0,0),b)
bg[0].save(f'{W}/ghost_flicker.gif',save_all=True,append_images=bg[1:],duration=90,loop=0)
sheet([Image.fromarray(o,'RGBA') for o in out],6,4,bg=(40,4,12,255)).save(f'{W}/strip_ghost_flicker.png'); print('ok',len(order))
