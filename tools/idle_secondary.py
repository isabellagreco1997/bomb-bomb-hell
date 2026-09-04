"""Breathing idle, 24 frames (~100 ms each), body design untouched:
 - breath: everything above the boots rises 1 px for half the loop (the stocking row above the boot repeats, feet stay planted)  [period 24]
 - hair: the lower part of the hair sways 1 px left / right on its own tempo                                                      [period 12]
 - sleeves settle 1 px on the exhale; front view blinks once (2-row lids) near the end of the loop."""
import sys, os, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
from scipy import ndimage
A='assets/sprites/48/anim'; W='work'; N=24
def is_hair(p): r,g,b,a=[int(v) for v in p]; return a>0 and r>170 and 90<g<185 and 90<b<175 and r-g>35 and r-b>25
def is_cream(p): r,g,b,a=[int(v) for v in p]; return a>0 and r>190 and g>170 and b>140 and (r-b)<70
def masks(a):
    al=a[...,3]>0; H,Wd=al.shape; ys,xs=np.nonzero(al); top=ys.min(); body_h=ys.max()-top
    hair=np.array([[is_hair(p) for p in row] for row in a]); cream=np.array([[is_cream(p) for p in row] for row in a])
    hys=np.nonzero(hair.any(1))[0]; h0,h1=hys.min(),hys.max(); tips=hair.copy(); tips[:h0+int((h1-h0)*0.6)]=False
    cx0,cx1=xs.min(),xs.max(); w=cx1-cx0; sleeves=cream.copy()
    sleeves[:top+int(body_h*0.45)]=False; sleeves[top+int(body_h*0.78):]=False; sleeves[:, cx0+int(w*0.3):cx1-int(w*0.3)]=False
    return tips, sleeves
def boot_top(a):
    """first row of the boots = lowest 4 rows of the silhouette"""
    al=a[...,3]>0; ys=np.nonzero(al.any(1))[0]; return ys.max()-3
def shift_px(base, mask, dx, dy):
    out=base.copy(); H,Wd=mask.shape; ys,xs=np.nonzero(mask)
    for y,x in zip(ys,xs):
        ny,nx=y+dy,x+dx
        if 0<=ny<H and 0<=nx<Wd: out[ny,nx]=base[y,x]
    return out
def inhale(a, bt):
    """rise 1 px: rows above the boot top move up one; the vacated row (stocking above the boot) is a copy of itself"""
    out=a.copy(); out[:bt-1]=a[1:bt]; out[bt-1]=a[bt-1]; return out
def blink(a):
    al=a[...,3]>0; ys,xs=np.nonzero(al); top,H=ys.min(),ys.max()-ys.min()
    band=slice(top+int(H*0.30),top+int(H*0.5)); dark=(a[band][...,:3].astype(int).sum(-1)<330)&al[band]
    lab,n=ndimage.label(dark); sizes=ndimage.sum(dark,lab,range(1,n+1))
    eyes=[i+1 for i in np.argsort(sizes)[::-1][:2] if sizes[i]>=6]; out=a.copy()
    for e in eyes:
        m=(lab==e); rows=np.nonzero(m.any(1))[0]; r0=rows.min()
        for r in (r0,r0+1):
            for c in np.nonzero(m[r])[0]:
                yy=band.start+r; k=yy-1
                while k>0 and (a[k,c,3]==0 or a[k,c,:3].astype(int).sum()<330): k-=1
                out[yy,c]=a[k,c]
    return out
result={}
for d in ('down','up','left'):
    base=np.array(Image.open(f'{A}/heroine_idle_{d}_0.png')); tips,sleeves=masks(base); bt=boot_top(base)
    frames=[]
    for t in range(N):
        f=base.copy()
        hair_dx=[1,1,1,1,0,0,-1,-1,-1,-1,0,0][t%12]           # hair tempo: 12
        if hair_dx: f=shift_px(f,tips,hair_dx,0)
        if 6<=t<18: f=inhale(f,bt)                            # breath tempo: 24, in for 12 frames
        if 18<=t<24: f=shift_px(f,sleeves,0,1)                # sleeves settle on the exhale
        if d=='down' and t in (20,21): f=blink(f)
        frames.append(f)
    result[d]=[Image.fromarray(f,'RGBA') for f in frames]
result['right']=[f.transpose(Image.FLIP_LEFT_RIGHT) for f in result['left']]
for d,fr in result.items():
    for p in glob.glob(f'{A}/heroine_idle_{d}_*.png'):
        if not p.endswith('_0.png'): os.remove(p)
    for j,f in enumerate(fr): f.save(f'{A}/heroine_idle_{d}_{j}.png')
    big=[f.resize((192,240),Image.NEAREST) for f in fr]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bgi): g.paste(b,(0,0),b)
    bgi[0].save(f'{W}/heroine_idle_{d}.gif',save_all=True,append_images=bgi[1:],duration=100,loop=0)
rows=[result[d][t] for d in ('down','up','left') for t in (0,4,8,12,16,20)]
sheet(rows,6,5,bg=(40,4,12,255)).save(f'{W}/strip_idle.png'); print('idle ok', N, 'frames per direction')
