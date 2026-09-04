"""Bomb from bomb.mp4. The sphere is almost the background colour, so no colour key separates it cleanly.
Instead: BODY mask = frame 0 (background unlit) keyed tight, shadow removed (pixels darker than the background), holes filled;
per frame alpha = BODY mask (static) + SPARKS (bright warm pixels only). No shadow, no lit-background halo."""
import sys, os, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
from scipy import ndimage
A='assets/sprites/48/anim'; W='work'; FW,FH=96,96
fs=sorted(glob.glob('work/vid_bomb/f_*.png')); bg=np.array([28.,0.,7.])
f0=np.array(Image.open(fs[0]).convert('RGBA')).astype(float)
d=np.sqrt(((f0[...,:3]-bg)**2).sum(-1)); dark=(f0[...,:3].sum(-1)<bg.sum()-6)      # shadow: darker than the background
m=(d>10)&~dark
lab,n=ndimage.label(m); sizes=ndimage.sum(m,lab,range(1,n+1))
body=np.isin(lab,[i+1 for i,sz in enumerate(sizes) if sz>=200])            # sphere + cap + fuse (all sizeable parts), specks dropped
body=ndimage.binary_closing(body,iterations=2); body=ndimage.binary_fill_holes(body)
ys,xs=np.nonzero(body); print('body bbox',xs.min(),ys.min(),xs.max(),ys.max(),'px',int(body.sum()))
bright=(f0[...,:3].sum(-1)>600)                                              # only the white-hot sparkle at the fuse tip; the gold cap stays
core=body&~bright; core=ndimage.binary_fill_holes(core)
top=int(ys.min()+(ys.max()-ys.min())*0.45)
sph=core.copy(); sph[:top]=False                                              # sphere only, for width/centre (fuse and cap excluded)
above=core.copy(); above[top:]=False; above&=(d>40)                          # above the sphere keep only the fuse and cap, not frame 0's dim spark glow
core=sph|above
cys,cxs=np.nonzero(sph); body_w=cxs.max()-cxs.min(); body_bottom=cys.max(); cx=(cxs.min()+cxs.max())/2
SCALE=40/body_w; print('sphere width',body_w,'scale',round(SCALE,3))
def sparks(a):
    r,g,b=a[...,0],a[...,1],a[...,2]; return np.clip((r+g-330)/120,0,1)*np.clip((r-120)/80,0,1)
def frame(i):
    a=np.array(Image.open(fs[i]).convert('RGBA')).astype(float)
    alpha=np.maximum(core*255.0, sparks(a)*255.0); k=a.copy(); k[...,3]=alpha
    im=Image.fromarray(k.astype('uint8'),'RGBA')
    small=im.convert('RGBa').resize((round(im.width*SCALE),round(im.height*SCALE)),Image.LANCZOS).convert('RGBA')
    fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,(int(round(FW/2-cx*SCALE)),int(round((FH-3)-body_bottom*SCALE))),small); return fr
TICK=[0,15,30,45,60,75,90,105,114,120]
tick=[frame(i) for i in TICK]
q,pal=quantise(tick,40)
for p in glob.glob(f'{A}/bomb_tick_*.png'): os.remove(p)
for j,f in enumerate(q): f.save(f'{A}/bomb_tick_{j}.png')
sheet(q,10,2,bg=(78,12,26,255)).save(f'{W}/strip_bomb96.png'); print('bomb frames',len(q))
