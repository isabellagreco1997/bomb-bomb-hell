"""All heroine frames from her two reference videos. Views: down = walk front.mp4; up/left = bands 2/3 of back and side.mp4; right = mirror of left.
Idle = frame 0 of each view (standing, feet on the floor). One scale per view from the STANDING height, so size never changes.
Every frame is placed by aligning its head centroid to the idle's, so the body stays put and the feet lift naturally.
Walk cycle = 8 frames sampled over one full cycle (two steps) found by autocorrelating the leg spread."""
import sys, json, os, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'; FW,FH=48,60; BODY=56
meta=json.load(open('work/vid_meta.json')); bands=meta['bands']
mids=[(bands[0][1]+bands[1][0])//2,(bands[1][1]+bands[2][0])//2]
VIEWS={'down':('work/vid_front',None,meta['front_bg']),'up':('work/vid_stack',(mids[0],mids[1]),meta['stack_bg']),'left':('work/vid_stack',(mids[1],992),meta['stack_bg'])}
def cut(path,band,bg):
    a=np.array(Image.open(path).convert('RGBA'))
    if band: a=a[band[0]:band[1]]
    c=largest_blob(key(a,np.array(bg,float),thr=45,soft=30)); al=c[...,3]>0; ys,xs=np.nonzero(al)
    return c[ys.min():ys.max()+1, xs.min():xs.max()+1]
def head_c(c):
    """anchor: x = torso centroid (rows 45..80% of the body, the part that must stay put), y = head centroid (stable height)"""
    al=c[...,3]>0; ys,xs=np.nonzero(al); top,H=ys.min(),ys.max()-ys.min()
    hy,hx=np.nonzero(al[top:top+int(H*0.4)]); ty,tx=np.nonzero(al[top+int(H*0.45):top+int(H*0.8)])
    return tx.mean(), top+hy.mean()
def spread(c):
    al=c[...,3]>0; legs=al[int(al.shape[0]*0.82):]; xs=np.nonzero(legs.any(0))[0]; return xs.max()-xs.min()
def footdiff(c):
    """front/back views: lower foot = the forward one. left-half bottom minus right-half bottom; cycles once per full walk"""
    al=c[...,3]>0; H=al.shape[0]; legs=al[int(H*0.82):]; hx,_=head_c(c); hx=int(hx)
    L=legs[:,:hx]; R=legs[:,hx:]
    bl=np.nonzero(L.any(1))[0].max() if L.any() else 0; br=np.nonzero(R.any(1))[0].max() if R.any() else 0
    return bl-br
def place(c,scale,hx,hy):
    """downscale c and paste so its head centroid lands at (hx,hy) in the 48x60 frame"""
    im=Image.fromarray(c.astype('uint8'),'RGBA'); w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.convert('RGBa').resize((w,h),Image.LANCZOS).convert('RGBA'); sa=np.array(small)
    cx,cy=head_c(sa); fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,(int(round(hx-cx)),int(round(hy-cy))),small); return fr
allframes={}; report={}
for d,(folder,band,bg) in VIEWS.items():
    fs=sorted(glob.glob(f'{folder}/f_*.png'))
    cells=[cut(f,band,bg) for f in fs]
    idle=cells[0]; scale=BODY/idle.shape[0]
    # idle placement: feet on row 58 (1 px margin), centred; record its head position
    im=Image.fromarray(idle.astype('uint8'),'RGBA').convert('RGBa').resize((round(idle.shape[1]*scale),BODY),Image.LANCZOS).convert('RGBA')
    ia=np.array(im); cx,cy=head_c(ia); x0=(FW-im.width)//2; y0=FH-2-BODY; hx,hy=x0+cx,y0+cy
    if d=='left':
        sp=np.array([spread(c) for c in cells],float); s=sp-sp.mean(); ac=[np.dot(s[:-k],s[k:])/np.dot(s,s) for k in range(1,80)]
        P=int(np.argmax(ac[5:20]))+6; cyc=2*P                             # spread peaks once per step: full cycle 2P
    else:
        sp=np.array([footdiff(c) for c in cells],float); s=sp-sp.mean(); ac=[np.dot(s[:-k],s[k:])/np.dot(s,s) for k in range(1,80)]
        P=int(np.argmax(ac[9:40]))+10; cyc=P                               # foot difference cycles once per full walk
    start=12+int(np.argmax(sp[12:12+cyc])); picks=[start+round(k*cyc/8) for k in range(8)]
    report[d]=dict(idle_h=int(idle.shape[0]),scale=round(scale,4),step_period=P,picks=picks,spread=[int(v) for v in sp[:60]])
    print(d,'idle h',idle.shape[0],'scale',round(scale,3),'step period',P,'frames',picks)
    walk=[place(cells[i],scale,hx,hy) for i in picks]
    idle_fr=place(idle,scale,hx,hy)
    # idle breath: 4 frames, whole body down 1 px on frames 2-3 (feet stay planted: the 1 px is absorbed visually by the boots)
    bob=Image.new('RGBA',(FW,FH),(0,0,0,0)); bob.paste(idle_fr,(0,1),idle_fr)
    allframes[d]={'idle':[idle_fr],'walk':walk}
json.dump(report,open(f'{W}/vid_report.json','w'),indent=1)
flat=[f for d in allframes for k in ('idle','walk') for f in allframes[d][k]]
q,pal=quantise(flat,48); it=iter(q)
for d in allframes:
    for k in ('idle','walk'): allframes[d][k]=[next(it) for _ in allframes[d][k]]
allframes['right']={k:[f.transpose(Image.FLIP_LEFT_RIGHT) for f in v] for k,v in allframes['left'].items()}
for p in glob.glob(f'{A}/heroine_cycle_*.png')+glob.glob(f'{A}/heroine_idle_*.png'): os.remove(p)
for d,v in allframes.items():
    for j,f in enumerate(v['walk']): f.save(f'{A}/heroine_cycle_{d}_{j}.png')
    for j,f in enumerate(v['idle']): f.save(f'{A}/heroine_idle_{d}_{j}.png')
json.dump({d:8 for d in allframes},open(f'{A}/heroine_cycles.json','w'))
json.dump({'palette':pal.tolist()},open('assets/sprites/48/heroine_video_palette.json','w'))
rows=[f for d in ('down','up','left','right') for f in allframes[d]['idle'][:1]+allframes[d]['walk']]
sheet(rows,9,4,bg=(40,4,12,255)).save(f'{W}/strip_video_all.png')
for d in ('down','up','left'):
    fr=allframes[d]['walk']; big=[f.resize((192,240),Image.NEAREST) for f in fr]; bgi=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bgi): g.paste(b,(0,0),b)
    bgi[0].save(f'{W}/heroine_cycle_{d}.gif',save_all=True,append_images=bgi[1:],duration=100,loop=0)
print('done')
