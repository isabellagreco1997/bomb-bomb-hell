"""Front/back walk for a top-down chibi: the AI rows don't step, so build the step ourselves.
One clean base frame per direction; legs (below the hem) split at the body centre; the stepping leg drops 2 px
(forward = lower on screen), the other lifts 1 px; body bobs 1 px on the pass frames. Hem stays put. 4 beats: L, pass, R, pass."""
import sys, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
D='assets/sprites/48/anim'; W='work'
def hem_row(a):
    """find the skirt hem: lowest row where the opaque width is still wide (skirt), legs below are narrow"""
    widths=[(np.nonzero(r)[0].max()-np.nonzero(r)[0].min()) if r.any() else 0 for r in a]
    H=len(widths); wmax=max(widths[int(H*0.5):])
    for y in range(H-1,int(H*0.5),-1):
        if widths[y]>=wmax*0.75: return y
    return int(H*0.8)
def shift_cols(img, x0, x1, y0, dy):
    """shift the block (rows y0.., cols x0..x1) by dy vertically; vacated rows filled from the row above (dy>0) or cleared"""
    a=np.array(img); H=a.shape[0]; out=a.copy()
    blk=a[y0:,x0:x1].copy(); out[y0:,x0:x1]=0
    if dy>=0:
        out[y0+dy:H, x0:x1]=blk[:H-y0-dy]
        for y in range(y0,y0+dy): out[y,x0:x1]=a[y0-1,x0:x1]*(a[y0-1,x0:x1,3:4]>0)  # stretch the hem row down to cover the gap
    else:
        out[y0:H+dy, x0:x1]=blk[-dy:]
    return Image.fromarray(out,'RGBA')
def bob(img, dy):
    g=Image.new('RGBA',img.size,(0,0,0,0)); g.paste(img,(0,dy),img); return g
for k in ('down','up'):
    base=Image.open(f'{D}/heroine_idle_{k}.png'); a=np.array(base)[...,3]>0
    hem=hem_row(a)+1; ys,xs=np.nonzero(a[hem:]); cx=int(round((xs.min()+xs.max())/2))
    print(k,'hem row',hem,'leg cols',xs.min(),xs.max(),'centre',cx)
    L=shift_cols(shift_cols(base,xs.min(),cx,hem,2),cx,xs.max()+1,hem,-1)   # left leg forward (lower), right lifted
    R=shift_cols(shift_cols(base,cx,xs.max()+1,hem,2),xs.min(),cx,hem,-1)
    P=bob(base,-1)                                                               # pass: feet together, body up 1
    cyc=[L,P,R,P]
    for j,f in enumerate(cyc): f.save(f'{D}/heroine_cycle_{k}_{j}.png')
    big=[f.resize((f.width*4,f.height*4),Image.NEAREST) for f in cyc]
    bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/heroine_cycle_{k}.gif',save_all=True,append_images=bg[1:],duration=130,loop=0)
    sheet(cyc,4,5,bg=(40,4,12,255)).save(f'{W}/strip_cycle_{k}.png')
