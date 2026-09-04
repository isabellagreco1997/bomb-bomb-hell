"""Idle per direction from the standing frame: body never moves. Secondary motion only:
hair tips sway 1 px, sleeves settle 1 px, one blink per loop (front view, eyes taken from a blink frame of her video).
8 frames, meant for ~150 ms each."""
import sys, os, glob, json; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'
def is_hair(p): r,g,b,a=[int(v) for v in p]; return a>0 and r>170 and 90<g<185 and 90<b<175 and r-g>35 and r-b>25
def is_cream(p): r,g,b,a=[int(v) for v in p]; return a>0 and r>190 and g>170 and b>140 and (r-b)<70
def shift_px(base, mask, dx, dy):
    """move only the masked pixels by (dx,dy); vacated pixels keep the base underneath (no holes)"""
    out=base.copy(); H,Wd=mask.shape
    ys,xs=np.nonzero(mask)
    for y,x in zip(ys,xs):
        ny,nx=y+dy,x+dx
        if 0<=ny<H and 0<=nx<Wd: out[ny,nx]=base[y,x]
    return out
def masks(a):
    al=a[...,3]>0; H,Wd=al.shape; ys,xs=np.nonzero(al); top=ys.min(); body_h=ys.max()-top
    hair=np.zeros_like(al); cream=np.zeros_like(al)
    for y in range(H):
        for x in range(Wd):
            if al[y,x]:
                if is_hair(a[y,x]): hair[y,x]=True
                elif is_cream(a[y,x]): cream[y,x]=True
    # hair tips = hair pixels in the lower 35% of the hair mass
    hys=np.nonzero(hair.any(1))[0]; h0,h1=hys.min(),hys.max(); tips=hair.copy(); tips[:h0+int((h1-h0)*0.65)]=False
    # sleeves = cream pixels between 45% and 78% of the body height, in the outer 30% columns of the body width
    cx0,cx1=xs.min(),xs.max(); w=cx1-cx0; sleeves=cream.copy()
    sleeves[:top+int(body_h*0.45)]=False; sleeves[top+int(body_h*0.78):]=False
    sleeves[:, cx0+int(w*0.3):cx1-int(w*0.3)]=False
    return tips, sleeves
def blink_eyes(base, d):
    """front view only: lids = the top 2 rows of each eye replaced by the skin tone just above the eye. Lash row and iris below untouched."""
    if d!='down': return None
    a=base.copy(); al=a[...,3]>0; ys,xs=np.nonzero(al); top,H=ys.min(),ys.max()-ys.min()
    band=slice(top+int(H*0.30),top+int(H*0.5))
    dark=(a[band][...,:3].astype(int).sum(-1)<330)&al[band]
    from scipy import ndimage
    lab,n=ndimage.label(dark); sizes=ndimage.sum(dark,lab,range(1,n+1))
    eyes=[i+1 for i in np.argsort(sizes)[::-1][:2] if sizes[i]>=6]     # the two biggest dark blobs in the face band = the eyes
    out=a.copy()
    for e in eyes:
        m=(lab==e); rows=np.nonzero(m.any(1))[0]; r0=rows.min()
        for r in (r0, r0+1):
            cols=np.nonzero(m[r])[0]
            for c in cols:
                yy=band.start+r
                # skin sample: nearest non-dark opaque pixel above this column
                k=yy-1
                while k>0 and (a[k,c,3]==0 or a[k,c,:3].astype(int).sum()<330): k-=1
                out[yy,c]=a[k,c]
    print('blink: eyes found',len(eyes))
    return out
pal_frames=[]; result={}
for d in ('down','up','left'):
    base=np.array(Image.open(f'{A}/heroine_idle_{d}_0.png'))
    tips,sleeves=masks(base)
    hairR=shift_px(base,tips,1,0); hairL=shift_px(base,tips,-1,0)
    def arms(b): return shift_px(b,sleeves,0,1)
    blink=blink_eyes(base,d)
    frames=[base, hairR, arms(hairR), arms(base), base, hairL, arms(hairL), (blink if blink is not None else arms(base))]
    result[d]=[Image.fromarray(f,'RGBA') for f in frames]
    print(d,'hair tip px',int(tips.sum()),'sleeve px',int(sleeves.sum()))
result['right']=[f.transpose(Image.FLIP_LEFT_RIGHT) for f in result['left']]
for p in glob.glob(f'{A}/heroine_idle_*.png'): os.remove(p)
for d,fr in result.items():
    for j,f in enumerate(fr): f.save(f'{A}/heroine_idle_{d}_{j}.png')
    big=[f.resize((192,240),Image.NEAREST) for f in fr]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bgi): g.paste(b,(0,0),b)
    bgi[0].save(f'{W}/heroine_idle_{d}.gif',save_all=True,append_images=bgi[1:],duration=150,loop=0)
rows=[f for d in ('down','up','left') for f in result[d]]
sheet(rows,8,5,bg=(40,4,12,255)).save(f'{W}/strip_idle.png'); print('ok')
