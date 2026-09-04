"""Map tiles from the tiles sheet → 48x48: floor (cracked obsidian + lava), pillar (ornate black stone), wall (gilded stone segment),
two crates (velvet, skull) each with its broken version. One shared palette."""
import sys, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; T=48
im=Image.open('assets/src/tiles_sheet.png').convert('RGBA')
BOX={'floor':(314,41,458,201),'pillar':(428,261,608,463),'wall':(784,40,891,118),   # pillar = demon-face statue, wall = plain gilded stone segment
     'crate_0':(15,519,145,691),'crate_0_broken':(15,717,145,883),'crate_1':(486,521,620,691),'crate_1_broken':(486,719,619,882),'brazier':(865,504,939,611)}   # candelabra: the wall sconce
def tile(name,inset=0.06,keep_bg=True):
    x0,y0,x1,y1=BOX[name]; w,h=x1-x0,y1-y0
    if name=='brazier': inset=0.0
    c=im.crop((x0+int(w*inset),y0+int(h*inset),x1-int(w*inset),y1-int(h*inset)))
    # square crop from the centre, then downscale
    s=min(c.width,c.height); top=(name=='brazier')   # candelabra: keep the flames, crop the top square
    c=c.crop(((c.width-s)//2,0 if top else (c.height-s)//2,(c.width-s)//2+s,(0 if top else (c.height-s)//2)+s))
    out=c.convert('RGBa').resize((T,T),Image.LANCZOS).convert('RGBA'); a=np.array(out); a[...,3]=255; return Image.fromarray(a,'RGBA')
tiles={n:tile(n) for n in BOX}
# animation variants, painted from the tiles' own pixels
def lava_variant(t, gain):
    a=np.array(t).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]; lava=(r>120)&(r>g+40)&(r>b+40)      # the orange/red veins
    o=a.copy(); o[lava,:3]=np.clip(a[lava,:3]*gain+np.array([0,0,0]),0,255); return Image.fromarray(o.astype('uint8'),'RGBA')
def eyes_variant(t):
    a=np.array(t).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]; eye=(r>140)&(g<70)&(b<70)              # the statue's red eyes and gems
    o=a.copy(); o[eye,:3]=[255,90,60]; return Image.fromarray(o.astype('uint8'),'RGBA')
def flame_variant(t, k):
    a=np.array(t).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]; fl=(r>200)&(g>150)&(b<150)              # the candle flames
    o=a.copy(); ys,xs=np.nonzero(fl)
    if k==1: o[ys-1,xs]=a[ys,xs]                                                                     # flame licks 1 px up
    if k==2: o[fl,:3]=np.clip(a[fl,:3]+40,0,255)                                                     # flame flares
    return Image.fromarray(o.astype('uint8'),'RGBA')
tiles['floor_1']=lava_variant(tiles['floor'],0.75); tiles['floor_2']=lava_variant(tiles['floor'],1.3)
tiles['pillar_glow']=eyes_variant(tiles['pillar'])
tiles['brazier_1']=flame_variant(tiles['brazier'],1); tiles['brazier_2']=flame_variant(tiles['brazier'],2)
q,pal=quantise(list(tiles.values()),56)
for n,f in zip(tiles,q): f.save(f'{A}/tile_{n}.png')
# mock: a 7x5 patch of the map with walls, pillars, floor and crates, 4x
names=list(tiles); m=Image.new('RGBA',(T*7,T*5))
for y in range(5):
    for x in range(7):
        k='wall' if (x in (0,6) or y in (0,4)) else ('pillar' if x%2==0 and y%2==0 else 'floor')
        m.paste(q[names.index(k)],(x*T,y*T))
for (x,y,k) in ((1,2,'crate_0'),(3,1,'crate_1'),(4,3,'crate_0_broken'),(5,2,'crate_1_broken'),(2,0,'brazier'),(4,0,'brazier_2'),(1,1,'floor_2'),(5,1,'floor_1'),(2,2,'pillar_glow')): m.paste(q[names.index(k)],(x*T,y*T))
m.resize((m.width*3,m.height*3),Image.NEAREST).save('work/tiles_mock.png'); print('tiles',list(tiles))
