"""Consistent 4-direction walks from the sheet's OWN drawn frames.
At source resolution: align frames on the head centroid, lock head+hair from frame 0 over every frame (kills AI redraw jitter),
measure the feet, sort frames into cycle order by phase angle, then downscale + quantise with the character palette."""
import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
SRC='assets/src/heroine_sheet.png'; D='assets/sprites/48'; A=f'{D}/anim'; W='work'
her=np.array(Image.open(SRC).convert('RGBA')); HBG=np.array([33.8,1.4,8.4]); boxes=json.load(open('work/heroine_boxes.json'))
FW,FH=48,60; SCALE=(FH-2)/134
ROWS={'down':range(32,39),'up':range(24,31),'left':range(15,22)}
def cell(i):
    b=boxes[i]; c=largest_blob(key(her[b[1]:b[3],b[0]:b[2]],HBG))
    # pad every cell to a common canvas, feet on the bottom
    canvas=np.zeros((150,110,4)); h,w=c.shape[:2]; canvas[150-h:, (110-w)//2:(110-w)//2+w]=c; return canvas
def head_cx(c):
    a=c[...,3]>40; h=int(a.shape[0]*0.45); ys,xs=np.nonzero(a[:h]); return xs.mean(), ys.mean()
def shift(c,dx,dy):
    out=np.zeros_like(c); H,Wd=c.shape[:2]
    ys=slice(max(0,dy),min(H,H+dy)); xs=slice(max(0,dx),min(Wd,Wd+dx))
    out[ys,xs]=c[max(0,-dy):max(0,-dy)+(ys.stop-ys.start), max(0,-dx):max(0,-dx)+(xs.stop-xs.start)]; return out
def neck_row(c):
    a=c[...,3]>40; H=a.shape[0]; w=[(np.nonzero(r)[0].max()-np.nonzero(r)[0].min()) if r.any() else 999 for r in a]
    lo,hi=int(H*0.42),int(H*0.62); return lo+int(np.argmin(w[lo:hi]))
def foot_metrics(c, side):
    a=c[...,3]>40; H=a.shape[0]; legs=a[int(H*0.80):]; ys,xs=np.nonzero(legs)
    hx,_=head_cx(c)
    if side:   # profile: front foot = leftmost boot pixel (she faces left), back foot = rightmost; phase from their x offsets to the head
        return xs.min()-hx, xs.max()-hx
    left=legs[:, :int(hx)]; right=legs[:, int(hx):]
    bl=np.nonzero(left.any(1))[0].max() if left.any() else 0; br=np.nonzero(right.any(1))[0].max() if right.any() else 0
    return bl-br, (xs.max()-xs.min())
out={}
for d,idx in ROWS.items():
    cells=[cell(i) for i in idx]
    cx0,cy0=head_cx(cells[0]); al=[]
    for c in cells:
        cx,cy=head_cx(c); al.append(shift(c,int(round(cx0-cx)),int(round(cy0-cy))))
    base=al[0]; nk=neck_row(base)
    locked=[]
    for c in al:
        m=c.copy(); m[:nk]=base[:nk]; locked.append(m)       # head + hair pixel-identical across the cycle
    met=np.array([foot_metrics(c, d=='left') for c in locked],float)
    z=(met-met.mean(0))/(met.std(0)+1e-6); ang=np.arctan2(z[:,1],z[:,0])
    order=list(np.argsort(ang)); print(d,'neck',nk,'metrics',met.round(1).tolist(),'order',order)
    out[d]=[fit(locked[i],FW,FH,SCALE) for i in order]
pal=np.array(json.load(open(f'{D}/heroine.json'))['palette'])
allf=[f for v in out.values() for f in v]+[Image.open(f'{A}/heroine_idle_{d}.png') for d in ('down','up','left')]
q,_=quantise(allf,48)
k=0
for d in list(out):
    fr=q[k:k+len(out[d])]; k+=len(out[d]); out[d]=fr
out['right']=[f.transpose(Image.FLIP_LEFT_RIGHT) for f in out['left']]
for d,fr in out.items():
    for j,f in enumerate(fr): f.save(f'{A}/heroine_cycle_{d}_{j}.png')
    for j in range(len(fr),7):
        p=f'{A}/heroine_cycle_{d}_{j}.png'
        if os.path.exists(p): os.remove(p)
    big=[f.resize((f.width*4,f.height*4),Image.NEAREST) for f in fr]; bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/heroine_cycle_{d}.gif',save_all=True,append_images=bg[1:],duration=100,loop=0)
    sheet(fr,7,5,bg=(40,4,12,255)).save(f'{W}/strip_cycle_{d}.png')
json.dump({d:len(fr) for d,fr in out.items()},open(f'{A}/heroine_cycles.json','w'))
print('done')
