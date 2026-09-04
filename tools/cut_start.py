"""Start-pose sequence from game start poses.mp4 (same framing as the front walk video).
Scale from this video's standing frame 0, placed on the front idle's anchor (torso x, head y), held frames removed, evenly sampled to N frames."""
import sys, json, os, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'; FW,FH=48,60; BODY=56; N=int(sys.argv[1]) if len(sys.argv)>1 else 32
fs=sorted(glob.glob('work/vid_start/f_*.png'))
a0=np.array(Image.open(fs[0]).convert('RGB')).astype(int); bg=np.median(np.concatenate([a0[:6].reshape(-1,3),a0[-6:].reshape(-1,3),a0[:,:6].reshape(-1,3),a0[:,-6:].reshape(-1,3)]),0); print('bg',bg)
def cut(p):
    a=np.array(Image.open(p).convert('RGBA')); c=largest_blob(key(a,bg,thr=45,soft=30)); al=c[...,3]>0; ys,xs=np.nonzero(al); return c[ys.min():ys.max()+1, xs.min():xs.max()+1]
def anchor(c):
    al=c[...,3]>0; ys,xs=np.nonzero(al); top,H=ys.min(),ys.max()-ys.min()
    hy,hx=np.nonzero(al[top:top+int(H*0.4)]); ty,tx=np.nonzero(al[top+int(H*0.45):top+int(H*0.8)]); return tx.mean(), top+hy.mean()
raw=[cut(f) for f in fs]
def pad(c,H=620,Wd=520):
    o=np.zeros((H,Wd,4)); h,w=c.shape[:2]; o[H-h:, (Wd-w)//2:(Wd-w)//2+w]=c[:H,:Wd]; return o
cells=[raw[0]]; last=pad(raw[0])
for c in raw[1:]:
    p=pad(c)
    if np.abs(p-last).mean()>1.5: cells.append(c); last=p
print('unique frames',len(cells),'of',len(raw))
scale=BODY/cells[0].shape[0]; print('standing height',cells[0].shape[0],'scale',round(scale,3))
idle=np.array(Image.open(f'{A}/heroine_idle_down_0.png')); hx,hy=anchor(idle)
def place(c):
    im=Image.fromarray(c.astype('uint8'),'RGBA'); w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.convert('RGBa').resize((w,h),Image.LANCZOS).convert('RGBA'); sa=np.array(small); cx,cy=anchor(sa)
    fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,(int(round(hx-cx)),int(round(hy-cy))),small); return fr
picks=[int(round(i*(len(cells)-1)/(N-1))) for i in range(N)]
frames=[place(cells[i]) for i in picks]
q,_=quantise(frames+[Image.fromarray(idle,'RGBA')],48); q=q[:-1]
for p in glob.glob(f'{A}/heroine_start_*.png'): os.remove(p)
for j,f in enumerate(q): f.save(f'{A}/heroine_start_{j}.png')
json.dump({'n':len(q)},open(f'{A}/heroine_start.json','w'))
sheet(q[::4],8,4,bg=(40,4,12,255)).save(f'{W}/strip_start.png')
big=[f.resize((192,240),Image.NEAREST) for f in q]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
for b,g in zip(big,bgi): g.paste(b,(0,0),b)
bgi[0].save(f'{W}/heroine_start.gif',save_all=True,append_images=bgi[1:],duration=150,loop=0); print('start frames',len(q))
