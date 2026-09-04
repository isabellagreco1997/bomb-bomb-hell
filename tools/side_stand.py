"""Side idle from her own video: the frame where the feet are closest together (the pass), placed like every other frame,
then the lifted boot is brought down to the floor row (its leg blob shifts down; the gap under the hem is filled by repeating the blob's top row).
Everything above the hem is untouched."""
import sys, json, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
from scipy import ndimage
A='assets/sprites/48/anim'; FW,FH=48,60; BODY=56
meta=json.load(open('work/vid_meta.json')); b=meta['bands']; band=((b[1][1]+b[2][0])//2, 992); bg=np.array(meta['stack_bg'],float)
fs=sorted(glob.glob('work/vid_stack/f_*.png'))
def cut(p):
    a=np.array(Image.open(p).convert('RGBA'))[band[0]:band[1]]; c=largest_blob(key(a,bg,thr=45,soft=30)); al=c[...,3]>0; ys,xs=np.nonzero(al); return c[ys.min():ys.max()+1, xs.min():xs.max()+1]
def spread(c):
    al=c[...,3]>0; legs=al[int(al.shape[0]*0.82):]; xs=np.nonzero(legs.any(0))[0]; return xs.max()-xs.min()
cells=[cut(f) for f in fs[:120]]
sp=np.array([spread(c) for c in cells])
# candidate pass frames = local minima of the leg spread; pick the one whose body colours match the walk frames best
cands=[i for i in range(6,len(sp)-1) if sp[i]<=sp[i-1] and sp[i]<=sp[i+1] and sp[i]<np.percentile(sp,25)]
walk=np.array(Image.open(f'{A}/heroine_cycle_left_0.png')); wm=walk[...,3]>0; wcol=walk[wm][:,:3].mean(0)
def body_col(c):
    al=c[...,3]>0; ys=np.nonzero(al.any(1))[0]; body=c[int(ys.min()+(ys.max()-ys.min())*0.45):]; m=body[...,3]>0; return body[m][:,:3].mean(0)
scores=[(float(np.abs(body_col(cells[i])-wcol).sum()),i) for i in cands]; scores.sort(); k=scores[0][1]
print('pass candidates',cands); print('best colour match frame',k,'spread',sp[k],'score',round(scores[0][0],1))
idle=cells[0]; scale=BODY/idle.shape[0]
def anchor(c):
    al=c[...,3]>0; ys,xs=np.nonzero(al); top,H=ys.min(),ys.max()-ys.min()
    hy,hx=np.nonzero(al[top:top+int(H*0.4)]); ty,tx=np.nonzero(al[top+int(H*0.45):top+int(H*0.8)]); return tx.mean(), top+hy.mean()
def place(c,hx,hy):
    im=Image.fromarray(c.astype('uint8'),'RGBA'); w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.convert('RGBa').resize((w,h),Image.LANCZOS).convert('RGBA'); sa=np.array(small); cx,cy=anchor(sa)
    fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,(int(round(hx-cx)),int(round(hy-cy))),small); return np.array(fr)
im=Image.fromarray(idle.astype('uint8'),'RGBA').convert('RGBa').resize((round(idle.shape[1]*scale),BODY),Image.LANCZOS).convert('RGBA')
cx,cy=anchor(np.array(im)); x0=(FW-im.width)//2; y0=FH-2-BODY; hx,hy=x0+cx,y0+cy
cur=np.array(Image.open(f'{A}/heroine_idle_left_0.png'))     # current idle (from from_videos) gives the floor row
floor=np.nonzero((cur[...,3]>0).any(1))[0].max()
f=place(cells[k],hx,hy); al=f[...,3]>0
# hem = first row (from 70%) where the legs form 2 runs with a central gap
def runs(row): xs=np.nonzero(row)[0]; return (1+int((np.diff(xs)>1).sum())) if len(xs) else 0
hem=next((y for y in range(int(FH*0.75),FH) if runs(al[y])>=2), int(FH*0.8))
lab,n=ndimage.label(al[hem:]); print('hem',hem,'leg blobs',n,'floor',floor)
out=f.copy()
for i in range(1,n+1):
    m=(lab==i); ys,xs=np.nonzero(m); bottom=hem+ys.max(); dy=floor-bottom
    if m.sum()<6 or dy<=0: continue
    blk=np.zeros_like(f[hem:]); blk[m]=f[hem:][m]
    out[hem:][m]=0
    top=ys.min(); shifted=np.zeros_like(blk); shifted[dy:]=blk[:-dy]
    for y in range(top, top+dy): shifted[y]=blk[top]*(blk[top][...,3:4]>0)      # fill the gap with the blob's top row
    mm=shifted[...,3]>0; out[hem:][mm]=shifted[mm]
    print(' blob',i,'grounded by',dy,'px')
out[:hem]=f[:hem]
Image.fromarray(out,'RGBA').save(f'{A}/heroine_idle_left_0.png'); Image.fromarray(out,'RGBA').transpose(Image.FLIP_LEFT_RIGHT).save(f'{A}/heroine_idle_right_0.png'); print('side stance ok')
