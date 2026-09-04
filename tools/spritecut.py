"""shared helpers: key, premultiplied downscale, shared-palette quantise, sheets"""
from PIL import Image
import numpy as np
from scipy import ndimage

def key(cell, bg, thr=30, soft=25):
    rgb=cell[...,:3].astype(float); d=np.sqrt(((rgb-bg)**2).sum(-1))
    a=np.clip((d-thr)/soft,0,1)*255
    out=cell.copy().astype(float); out[...,3]=np.minimum(out[...,3],a)
    return out

def largest_blob(cell_rgba, keep_inside=True):
    """keep the biggest opaque component (+ components inside its bbox), drop stray sparkles"""
    a=cell_rgba[...,3]>40
    lab,n=ndimage.label(ndimage.binary_closing(a,iterations=2))
    if n<=1:
        out=cell_rgba.copy(); filled=ndimage.binary_fill_holes(a); holes=filled&~a
        out[holes,:3]=cell_rgba[holes,:3]; out[holes,3]=255; return out
    sizes=ndimage.sum(a,lab,range(1,n+1)); big=int(np.argmax(sizes))+1
    sl=ndimage.find_objects(lab)[big-1]
    keep=(lab==big)
    if keep_inside:
        box=np.zeros_like(keep); box[sl]=True
        keep|=(lab>0)&box
    out=cell_rgba.copy(); out[~keep,3]=0
    # enclosed holes (dark eyes, sockets keyed out because they match the background) get their original pixels back
    filled=ndimage.binary_fill_holes(keep); holes=filled&~keep
    out[holes,:3]=cell_rgba[holes,:3]; out[holes,3]=255
    return out

def fit(cell, fw, fh, scale, anchor='bottom', dy=0):
    im=Image.fromarray(cell.astype('uint8'),'RGBA')
    w=max(1,round(im.width*scale)); h=max(1,round(im.height*scale))
    small=im.convert('RGBa').resize((w,h),Image.LANCZOS).convert('RGBA')   # premultiplied: no bg bleed
    frame=Image.new('RGBA',(fw,fh),(0,0,0,0))
    x=(fw-w)//2; y=(fh-h+dy) if anchor=='bottom' else (fh-h)//2
    frame.paste(small,(x,y),small)
    return frame

def quantise(frames, ncol):
    arrs=[np.array(f) for f in frames]
    pix=np.concatenate([a[a[...,3]>=128][:,:3] for a in arrs])
    side=int(np.ceil(np.sqrt(len(pix)))); pad=np.zeros((side*side,3),'uint8'); pad[:len(pix)]=pix; pad[len(pix):]=pix[:side*side-len(pix)]
    pal_img=Image.fromarray(pad.reshape(side,side,3)).quantize(colors=ncol,method=Image.MEDIANCUT,dither=Image.NONE)
    pal=np.array(pal_img.getpalette()[:ncol*3]).reshape(-1,3)
    out=[]
    for a in arrs:
        m=a[...,3]>=128; rgb=a[...,:3].astype(int)
        idx=((rgb[...,None,:]-pal[None,None,:,:])**2).sum(-1).argmin(-1)
        q=np.zeros_like(a); q[...,:3]=pal[idx]; q[...,3]=np.where(m,255,0); q[~m,:3]=0
        out.append(Image.fromarray(q.astype('uint8'),'RGBA'))
    return out, pal

def sheet(frames, cols, scale=1, bg=(0,0,0,0)):
    fw=max(f.width for f in frames); fh=max(f.height for f in frames); rows=(len(frames)+cols-1)//cols
    s=Image.new('RGBA',(fw*cols,fh*rows),bg)
    for i,f in enumerate(frames): s.paste(f,((i%cols)*fw,(i//cols)*fh),f)
    if scale>1: s=s.resize((s.width*scale,s.height*scale),Image.NEAREST)
    return s
