"""Side walk from her Grok reference video: sample one full cycle (two strides), cut her out, downscale to 48x60,
lock the head from the existing side idle frame (consistency with the other directions), quantise to the heroine palette."""
import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'; G='work/grok'
PICK=[int(v) for v in (sys.argv[1].split(',') if len(sys.argv)>1 else '11,14,17,20,23,26,29,32'.split(','))]
bg=np.array([38.,4.,12.]); FW,FH=48,60
meas=json.load(open(f'{G}/meas.json'))
H=np.median([m[6] for m in meas[1:]]); SCALE=(FH-2)/H; print('body px',H,'scale',round(SCALE,3))
def cut(i):
    a=np.array(Image.open(f'{G}/f_{i+1:03d}.png').convert('RGBA'))
    c=largest_blob(key(a,bg,thr=40,soft=30)); al=c[...,3]>0; ys,xs=np.nonzero(al)
    return c[ys.min():ys.max()+1, xs.min():xs.max()+1]
frames=[fit(cut(i),FW,FH,SCALE) for i in PICK]
idle=Image.open(f'{A}/heroine_idle_left.png')
pal=np.array(json.load(open('assets/sprites/48/heroine.json'))['palette'])
q,_=quantise(frames+[idle],48); q=q[:-1]
# head lock: paste the idle's rows above the neck over each frame, aligned on the head centroid
def head_c(im):
    a=np.array(im)[...,3]>0; h=int(a.shape[0]*0.45); ys,xs=np.nonzero(a[:h]); return xs.mean(), ys.mean()
def neck(im):
    a=np.array(im)[...,3]>0; w=[(np.nonzero(r)[0].max()-np.nonzero(r)[0].min()) if r.any() else 999 for r in a]
    lo,hi=int(len(w)*0.42),int(len(w)*0.62); return lo+int(np.argmin(w[lo:hi]))
ix,iy=head_c(idle); nk=neck(idle); ia=np.array(idle)
out=[]
for f in q:
    fx,fy=head_c(f); dx=int(round(ix-fx)); dy=int(round(iy-fy))
    a=np.array(f); s=np.zeros_like(a)
    ys=slice(max(0,dy),min(FH,FH+dy)); xs=slice(max(0,dx),min(FW,FW+dx))
    s[ys,xs]=a[max(0,-dy):max(0,-dy)+(ys.stop-ys.start), max(0,-dx):max(0,-dx)+(xs.stop-xs.start)]
    s[:nk]=ia[:nk]; out.append(Image.fromarray(s,'RGBA'))
for j in range(9):
    for d in ('left','right'):
        p=f'{A}/heroine_cycle_{d}_{j}.png'
        if os.path.exists(p): os.remove(p)
for j,f in enumerate(out):
    f.save(f'{A}/heroine_cycle_left_{j}.png'); f.transpose(Image.FLIP_LEFT_RIGHT).save(f'{A}/heroine_cycle_right_{j}.png')
cy=json.load(open(f'{A}/heroine_cycles.json')); cy['left']=cy['right']=len(out); json.dump(cy,open(f'{A}/heroine_cycles.json','w'))
sheet(out,8,5,bg=(40,4,12,255)).save(f'{W}/strip_side_video.png')
# reference strip at the same scale next to it
ref=[fit(cut(i),FW,FH,SCALE) for i in PICK]; sheet(ref,8,5,bg=(40,4,12,255)).save(f'{W}/strip_side_video_ref.png')
big=[f.resize((192,240),Image.NEAREST) for f in out]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
for b,g in zip(big,bgi): g.paste(b,(0,0),b)
bgi[0].save(f'{W}/heroine_cycle_left.gif',save_all=True,append_images=bgi[1:],duration=90,loop=0)
print('side frames',len(out),'neck',nk)
