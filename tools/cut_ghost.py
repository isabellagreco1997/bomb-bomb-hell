"""Ghost from ghost.mp4: loop frames [S,E), deduped, sampled to N, scaled so the body matches the current candle sprite, bottom-anchored."""
import sys, os, glob, json; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
S,E,N=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); OUT=sys.argv[4] if len(sys.argv)>4 else 'work'
A='assets/sprites/48/anim'; FW,FH=48,60
fs=sorted(glob.glob('work/vid_ghost/f_*.png'))
a0=np.array(Image.open(fs[S]).convert('RGB')).astype(int); bg=np.median(np.concatenate([a0[:6].reshape(-1,3),a0[-6:].reshape(-1,3),a0[:,:6].reshape(-1,3),a0[:,-6:].reshape(-1,3)]),0)
def cut(p):
    a=np.array(Image.open(p).convert('RGBA')); c=largest_blob(key(a,bg,thr=40,soft=30)); al=c[...,3]>0; ys,xs=np.nonzero(al); return c[ys.min():ys.max()+1, xs.min():xs.max()+1]
raw=[cut(fs[i]) for i in range(S,E)]
def pad(c,H=620,Wd=500):
    o=np.zeros((H,Wd,4)); h,w=c.shape[:2]; o[H-h:, (Wd-w)//2:(Wd-w)//2+w]=c[:H,:Wd]; return o
cells=[raw[0]]; last=pad(raw[0])
for c in raw[1:]:
    p=pad(c)
    if np.abs(p-last).mean()>1.0: cells.append(c); last=p
# current in-game candle: body height (opaque rows) for the scale
cur=np.array(Image.open(f'{A}/candle_flicker_0.png')); rows=np.nonzero((cur[...,3]>0).any(1))[0]; target_h=rows.max()-rows.min()+1
med_h=np.median([c.shape[0] for c in cells]); scale=target_h/med_h
print('unique',len(cells),'of',len(raw),'| target height',target_h,'median src height',med_h,'scale',round(scale,3))
picks=[int(round(i*(len(cells)-1)/(N-1))) for i in range(N)]
frames=[]
for i in picks:
    c=cells[i]; im=Image.fromarray(c.astype('uint8'),'RGBA'); w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.convert('RGBa').resize((w,h),Image.LANCZOS).convert('RGBA'); fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,((FW-w)//2,FH-2-h),small); frames.append(fr)
q,pal=quantise(frames,32)
os.makedirs(OUT,exist_ok=True)
for j,f in enumerate(q): f.save(f'{OUT}/ghost_loop_{j}.png')
big=[f.resize((192,240),Image.NEAREST) for f in q]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
for b,g in zip(big,bgi): g.paste(b,(0,0),b)
bgi[0].save(f'{OUT}/ghost_loop.gif',save_all=True,append_images=bgi[1:],duration=int(1000*(E-S)/24/N),loop=0)
old=Image.open(f'{A}/candle_flicker_0.png').resize((192,240),Image.NEAREST); cmp=Image.new('RGB',(192*2+20,240),(40,4,12)); cmp.paste(old,(0,0),old); cmp.paste(big[0],(212,0),big[0]); cmp.save(f'{OUT}/ghost_compare.png')
sheet(q,N,4,bg=(40,4,12,255)).save(f'{OUT}/ghost_strip.png'); print('gif frames',len(q),'ms/frame',int(1000*(E-S)/24/N))
