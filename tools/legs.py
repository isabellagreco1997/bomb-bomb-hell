"""Draw the legs per frame (contact / pass) from the idle frame's own boot + stocking pixels. No offset seams:
a forward leg is EXTENDED by repeating a shin row above the boot, a trailing leg is CONTRACTED by dropping one; the hem sits over the join.
Upper body (rows above the hem) comes from the sheet's drawn walk frames, head locked (see build_walks.py)."""
import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'
def arr(p): return np.array(Image.open(p))
def hem_row(a):
    """first row (scanning down from 70% height) where the centre column band is transparent = the legs have separated below the hem"""
    al=a[...,3]>0; H,Wd=al.shape; ys,xs=np.nonzero(al); cx=int((xs.min()+xs.max())/2)
    for y in range(int(H*0.7),H):
        if not al[y,cx-1:cx+2].any() and al[y].any(): return y
    return int(H*0.83)
def leg_blobs(a,hem):
    """split the rows below the hem into left/right blobs by the gap between the legs (or at the centre if they touch)"""
    al=a[hem:,:,3]>0; cols=al.any(0); xs=np.nonzero(cols)[0]
    gaps=[x for x in range(xs.min(),xs.max()) if not cols[x]]
    cx=int(np.median(gaps)) if gaps else int((xs.min()+xs.max())/2)
    return cx
def repose_leg(a,hem,x0,x1,extend):
    """return the leg block (rows hem.., cols x0..x1) re-drawn with `extend` extra shin rows (negative = shorter)"""
    blk=a[hem:,x0:x1].copy(); H=blk.shape[0]
    rows=np.nonzero(blk[...,3].any(1))[0]
    if len(rows)==0: return blk
    top,bot=rows.min(),rows.max()
    # boot = darkest 4 rows at the bottom; shin row = the row just above the boot
    boot_top=max(top+1,bot-3); shin=blk[boot_top-1:boot_top]
    body=blk[top:boot_top]; boot=blk[boot_top:bot+1]
    if extend>0: body=np.concatenate([body]+[shin]*extend)
    elif extend<0: body=body[:max(1,len(body)+extend)]
    new=np.concatenate([body,boot]); out=np.zeros_like(blk)
    # anchor: the leg top stays at the hem (top row), so the boot moves down when extended
    n=min(len(new),H-top); out[top:top+n]=new[:n]
    return out
def compose(upper_src, legs_src, hem, poses, bob=0):
    """legs from legs_src re-posed, then the upper body of upper_src pasted over (skirt covers the join). poses = (extendL, extendR)"""
    a=legs_src.copy(); cx=leg_blobs(a,hem); xs=np.nonzero((a[hem:,:,3]>0).any(0))[0]
    L=repose_leg(a,hem,xs.min(),cx,poses[0]); R=repose_leg(a,hem,cx,xs.max()+1,poses[1])
    out=np.zeros_like(a); out[hem:,xs.min():cx]=L; out[hem:,cx:xs.max()+1]=R
    up=upper_src.copy(); up[hem:]=0
    m=up[...,3]>0; out[m]=up[m]
    if bob: 
        o=np.zeros_like(out); o[:bob if bob<0 else None]=out[-bob:] if bob<0 else out[:]
        if bob<0: o=np.zeros_like(out); o[:out.shape[0]+bob]=out[-bob:]
        out=o
    return out
def gif(frames,name,ms=110):
    big=[Image.fromarray(f,'RGBA').resize((f.shape[1]*4,f.shape[0]*4),Image.NEAREST) for f in frames]; bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/{name}.gif',save_all=True,append_images=bg[1:],duration=ms,loop=0)
cycles={}
# ---- front / back: contact L, pass, contact R, pass ----
for d,upper_idx in (('down',[0,3,5,2]),('up',[0,3,5,2])):
    base=arr(f'{A}/heroine_idle_{d}.png'); hem=hem_row(base)
    ups=[arr(f'{A}/heroine_cycle_{d}_{i}.png') for i in upper_idx]      # head-locked drawn frames from build_walks
    fr=[compose(ups[0],base,hem,(2,-2)), compose(ups[1],base,hem,(0,0),bob=-1), compose(ups[2],base,hem,(-2,2)), compose(ups[3],base,hem,(0,0),bob=-1)]
    cycles[d]=fr; print(d,'hem',hem)
# ---- side: stride, recoil (legs closer), pass (legs under the hip, body up), recoil ----
base=arr(f'{A}/heroine_idle_left.png'); hem=hem_row(base)
al=base[hem:,:,3]>0; xs=np.nonzero(al.any(0))[0]; cx=leg_blobs(base,hem)
def side_frame(upper, pull, bob=0, vertical=False, swap=False):
    a=base.copy(); out=np.zeros_like(a)
    front=a[hem:,xs.min():cx]; back=a[hem:,cx:xs.max()+1]
    if vertical:
        # both legs under the hip: take each leg's boot (bottom 4 rows) and draw a straight stocking column above it in the leg's own colours
        hip=int((xs.min()+xs.max())/2)
        for blk,dx in ((back,+1),(front,-1)):
            rows=np.nonzero(blk[...,3].any(1))[0]; top,bot=rows.min(),rows.max(); boot=blk[bot-3:bot+1]
            bc=np.nonzero(boot[-1,:,3])[0]; bw=bc.max()-bc.min()+1; boot=boot[:,bc.min():bc.max()+1]
            stock=blk[top:bot-3]; sc=[r[r[:,3]>0][:,:3] for r in stock if (r[:,3]>0).any()]
            col=np.median(np.concatenate(sc),0).astype('uint8') if sc else np.array([240,220,200],'uint8')
            x0=hip+dx*2-bw//2; H=bot-top+1-2      # slightly shorter than the stride leg (foot under the body, higher)
            for y in range(H-4):
                out[hem+top+2+y, x0+1:x0+bw-1]=[*col,255]
            out[hem+top+2+H-4:hem+top+2+H, x0:x0+bw]=boot
    else:
        def sh(blk,dx):
            o=np.zeros_like(blk); Wd=blk.shape[1]
            if dx>=0: o[:,dx:]=blk[:,:Wd-dx]
            else: o[:,:Wd+dx]=blk[:,-dx:]
            return o
        f=sh(front,pull); b=sh(back,-pull)
        if swap:
            # the other leg leads: same geometry as stride A, but the shading of the two legs is exchanged
            # (front blob takes the far leg's darker tones and vice versa), so the eye reads the far leg stepping forward
            def tones(blk):
                px=blk[blk[...,3]>0][:,:3]; u=np.unique(px,axis=0); return u[np.argsort(u.sum(1))]
            def remap(blk, src_t, dst_t):
                o=blk.copy(); m=blk[...,3]>0; px=blk[m][:,:3]
                idx=np.array([np.where((src_t==p).all(1))[0][0] for p in px]); q=(idx/(max(1,len(src_t)-1))*(len(dst_t)-1)).round().astype(int)
                o[m,:3]=dst_t[q]; return o
            tf,tb=tones(front),tones(back)
            f=remap(f,tf,tb); b=remap(b,tb,tf)
            out[hem:,xs.min():cx]=f; out[hem:,cx:xs.max()+1]=np.where(b[...,3:4]>0,b,out[hem:,cx:xs.max()+1])
        else:
            out[hem:,xs.min():cx]=f; out[hem:,cx:xs.max()+1]=np.where(b[...,3:4]>0,b,out[hem:,cx:xs.max()+1])
    up=upper.copy(); up[hem:]=0; m=up[...,3]>0; out[m]=up[m]
    if bob<0: o=np.zeros_like(out); o[:out.shape[0]+bob]=out[-bob:]; out=o
    return out
ups=[arr(f'{A}/heroine_cycle_left_{i}.png') for i in (0,2,3,4,5,6,1,2)]
cycles['left']=[side_frame(ups[0],0), side_frame(ups[1],3), side_frame(ups[2],6,bob=-1), side_frame(ups[3],3,swap=True),
                side_frame(ups[4],0,swap=True), side_frame(ups[5],3,swap=True), side_frame(ups[6],6,bob=-1), side_frame(ups[7],3)]   # stride A, recoil, pass, recoil, stride B (other leg leads), recoil, pass, recoil
cycles['right']=[np.ascontiguousarray(f[:,::-1]) for f in cycles['left']]
for d,fr in cycles.items():
    for j in range(9):
        p=f'{A}/heroine_cycle_{d}_{j}.png'
        if os.path.exists(p): os.remove(p)
    for j,f in enumerate(fr): Image.fromarray(f,'RGBA').save(f'{A}/heroine_cycle_{d}_{j}.png')
    gif(fr,f'heroine_cycle_{d}')
json.dump({d:len(fr) for d,fr in cycles.items()},open(f'{A}/heroine_cycles.json','w'))
rows=[Image.fromarray(f,'RGBA') for d in ('down','up','left','right') for f in cycles[d]]
sheet(rows,4,5,bg=(40,4,12,255)).save(f'{W}/strip_legs_all.png'); print('ok')
