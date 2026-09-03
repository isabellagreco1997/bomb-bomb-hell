"""Side walk hybrid: head + torso + skirt from the sheet's side idle (locked), legs from the Grok reference frames,
video leg tones remapped onto the sheet's stocking/boot tones so the outfit matches front and back."""
import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'; FW,FH=48,60
video=[np.array(Image.open(f'{A}/heroine_cycle_left_{j}.png')) for j in range(8)]   # from side_from_video.py (full body, head locked)
idle=np.array(Image.open(f'{A}/heroine_idle_left.png'))
al=idle[...,3]>0
def hem_side(a):
    """side view: hem = the lowest row whose opaque width is still >= 70% of the skirt's widest row"""
    w=[(np.nonzero(r)[0].max()-np.nonzero(r)[0].min()) if r.any() else 0 for r in a]; H=len(w); wmax=max(w[int(H*0.55):])
    for y in range(H-1,int(H*0.55),-1):
        if w[y]>=wmax*0.7: return y+1
hem=int(sys.argv[1]) if len(sys.argv)>1 else 48; print('side hem row',hem)
def tones(blk):
    px=blk[blk[...,3]>0][:,:3]; u=np.unique(px,axis=0); return u[np.argsort(u.sum(1))]
def remap(blk,src_t,dst_t):
    o=blk.copy(); m=blk[...,3]>0; px=blk[m][:,:3]
    idx=np.array([np.where((src_t==p).all(1))[0][0] for p in px]); q=(idx/(max(1,len(src_t)-1))*(len(dst_t)-1)).round().astype(int)
    o[m,:3]=dst_t[q]; return o
sheet_legs=tones(idle[hem:]); out=[]
for j,v in enumerate(video):
    legs=v[hem:].copy(); legs=remap(legs,tones(legs),sheet_legs)
    f=np.zeros_like(idle); f[hem:]=legs
    up=idle.copy(); up[hem:]=0; m=up[...,3]>0; f[m]=up[m]
    # body bob: rows where the video body was lifted are lost by locking the torso; add a 1px lift on the two pass frames (smallest leg spread)
    out.append(f)
sp=[(np.nonzero((f[hem:,:,3]>0).any(0))[0]).max()-np.nonzero((f[hem:,:,3]>0).any(0))[0].min() for f in out]; print('leg spread per frame',sp)
order=np.argsort(sp)[:2]
for j in order:
    o=np.zeros_like(out[j]); o[:-1]=out[j][1:]; out[j]=o
os.makedirs(f'{W}/hybrid',exist_ok=True)
ims=[Image.fromarray(f,'RGBA') for f in out]
for j,im in enumerate(ims): im.save(f'{W}/hybrid/left_{j}.png')
sheet(ims,8,5,bg=(40,4,12,255)).save(f'{W}/strip_side_hybrid.png')
big=[im.resize((192,240),Image.NEAREST) for im in ims]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
for b,g in zip(big,bgi): g.paste(b,(0,0),b)
bgi[0].save(f'{W}/heroine_cycle_left_hybrid.gif',save_all=True,append_images=bgi[1:],duration=90,loop=0); print('ok')
