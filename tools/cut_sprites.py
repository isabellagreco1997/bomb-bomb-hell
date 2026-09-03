"""Cut the heroine + floating candle spirit out of the Codex concept sheets into game frames.
Heroine frames: 32x40 (feet on bottom row). Candle frames: 32x32. Shared palette per character, no dither."""
from PIL import Image, ImageDraw
import numpy as np, json, os
from scipy import ndimage
SRC='assets/src'; OUT='assets/sprites'; WORK='work'
os.makedirs(OUT,exist_ok=True)

def components(rgb, bg, thr=30, minarea=400, gap=6):
    d=np.sqrt(((rgb.astype(int)-bg)**2).sum(-1)); mask=ndimage.binary_closing(d>thr,iterations=3)
    lab,n=ndimage.label(mask); boxes=[]
    for sl in ndimage.find_objects(lab):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        if h*w>=minarea: boxes.append((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
    changed=True
    while changed:
        changed=False; out=[]
        while boxes:
            a=boxes.pop(); ax0,ay0,ax1,ay1=a
            for j,b in enumerate(boxes):
                bx0,by0,bx1,by1=b
                if ax0-gap<bx1 and bx0-gap<ax1 and ay0-gap<by1 and by0-gap<ay1:
                    boxes[j]=(min(ax0,bx0),min(ay0,by0),max(ax1,bx1),max(ay1,by1)); a=None; changed=True; break
            if a: out.append(a)
        boxes=out
    return boxes

def key(rgba_cell, bg, thr=30, soft=25):
    """hard-key background: alpha = 0 within thr of bg, ramp to 255 over soft px of distance (then thresholded later)"""
    rgb=rgba_cell[...,:3].astype(float); d=np.sqrt(((rgb-bg)**2).sum(-1))
    a=np.clip((d-thr)/soft,0,1)*255
    # remove the small dark drop-shadow ellipse: pixels close to bg in hue but darker -> already near bg distance
    out=rgba_cell.copy().astype(float); out[...,3]=np.minimum(out[...,3],a)
    return out

def fit(cell, fw, fh, scale, anchor='bottom'):
    """downscale a keyed RGBA float cell by scale, place into fw x fh frame."""
    im=Image.fromarray(cell.astype('uint8'),'RGBA')
    # premultiply-safe downscale: composite on transparent, LANCZOS
    w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.resize((w,h),Image.LANCZOS)
    frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
    x=(fw-w)//2; y=(fh-h) if anchor=='bottom' else (fh-h)//2
    frame.paste(small,(x,y),small)
    return frame

def quantise(frames, ncol):
    """shared palette across frames: quantise opaque pixels, alpha thresholded at 128."""
    arrs=[np.array(f) for f in frames]
    pix=np.concatenate([a[a[...,3]>=128][:,:3] for a in arrs])
    pal_img=Image.fromarray(pix.reshape(1,-1,3).astype('uint8')).quantize(colors=ncol,method=Image.MEDIANCUT,dither=Image.NONE)
    pal=np.array(pal_img.getpalette()[:ncol*3]).reshape(-1,3)
    out=[]
    for a in arrs:
        m=a[...,3]>=128; rgb=a[...,:3].astype(int)
        idx=((rgb[...,None,:]-pal[None,None,:,:])**2).sum(-1).argmin(-1)
        q=np.zeros_like(a); q[...,:3]=pal[idx]; q[...,3]=np.where(m,255,0); q[~m,:3]=0
        out.append(Image.fromarray(q.astype('uint8'),'RGBA'))
    return out, pal

def sheet(frames, cols, scale=1):
    fw,fh=frames[0].size; rows=(len(frames)+cols-1)//cols
    s=Image.new('RGBA',(fw*cols,fh*rows),(0,0,0,0))
    for i,f in enumerate(frames): s.paste(f,((i%cols)*fw,(i//cols)*fh))
    if scale>1: s=s.resize((s.width*scale,s.height*scale),Image.NEAREST)
    return s

# ---------- HEROINE ----------
her=np.array(Image.open(f'{SRC}/heroine_sheet.png').convert('RGBA'))
HBG=np.array([33.8,1.4,8.4])
boxes=json.load(open(f'{WORK}/heroine_boxes.json'))
FW,FH=32,40
# body height ~134 px in row 1 -> 38 px
SCALE=38/134
rows={'down':range(1,8),'up':range(8,15),'left':range(15,22),'row4':range(24,31),'row5':range(32,39)}
poses={'bomb_a':22,'bomb_b':23,'bomb_item':31,'victory':39,'hurt':41,'dizzy':43,'defeated':45}
raw={}
for name,idx in rows.items():
    raw[name]=[fit(key(her[b[1]:b[3],b[0]:b[2]],HBG),FW,FH,SCALE) for b in (boxes[i] for i in idx)]
for name,i in poses.items():
    b=boxes[i]; cell=key(her[b[1]:b[3],b[0]:b[2]],HBG)
    fw=FW if name!='victory' and name!='defeated' and name!='dizzy' else 48
    raw[name]=[fit(cell,fw,FH,SCALE)]
allf=[f for v in raw.values() for f in v]
q,pal=quantise(allf,32)
k=0; her_out={}
for name,v in raw.items():
    her_out[name]=q[k:k+len(v)]; k+=len(v)
    for j,f in enumerate(her_out[name]): f.save(f'{OUT}/heroine_{name}_{j}.png')
json.dump({'palette':pal.tolist(),'frame':[FW,FH],'rows':{n:len(v) for n,v in her_out.items()}},open(f'{OUT}/heroine.json','w'),indent=1)
prev=sheet([f for v in her_out.values() for f in v if f.width==FW],7,6); prev.save(f'{WORK}/heroine_preview_6x.png')
print('heroine frames',sum(len(v) for v in her_out.values()),'palette',len(pal))

# ---------- CANDLE ----------
en=np.array(Image.open(f'{SRC}/enemies_sheet.png').convert('RGBA'))
px,py,px1,py1=294+8,10+36,515-8,351-6   # inside the panel border, under the label
panel=en[py:py1,px:px1].copy()
# flatten soft alpha onto its own mean bg colour
CBG=np.median(panel[...,:3].reshape(-1,3),axis=0).astype(float); print('candle bg',CBG)
cb=components(panel[...,:3],CBG,thr=45,minarea=300,gap=10)
cb.sort(key=lambda b:(b[1]//60,b[0]))
vis=Image.fromarray(panel[...,:3]); dr=ImageDraw.Draw(vis)
for i,b in enumerate(cb): dr.rectangle(b,outline=(0,255,0)); dr.text((b[0],b[1]),str(i),fill=(0,255,0)); print('candle box',i,b,'w',b[2]-b[0],'h',b[3]-b[1])
vis.resize((vis.width*3,vis.height*3),Image.NEAREST).save(f'{WORK}/candle_boxes_3x.png')
json.dump(cb,open(f'{WORK}/candle_boxes.json','w'))
