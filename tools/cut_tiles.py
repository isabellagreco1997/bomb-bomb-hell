"""Map tiles from the tiles sheet → 48x48: floor (cracked obsidian + lava), pillar (ornate black stone), wall (gilded stone segment),
two crates (velvet, skull) each with its broken version. One shared palette."""
import sys, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; T=48
im=Image.open('assets/src/tiles_sheet.png').convert('RGBA')
BOX={'floor':(314,41,458,201),'pillar':(428,261,608,463),'wall':(784,40,891,118),   # pillar = demon-face statue, wall = plain gilded stone segment
     'crate_0':(15,519,145,691),'crate_0_broken':(15,717,145,883),'crate_1':(486,521,620,691),'crate_1_broken':(486,719,619,882)}
def tile(name,inset=0.06,keep_bg=True):
    x0,y0,x1,y1=BOX[name]; w,h=x1-x0,y1-y0; c=im.crop((x0+int(w*inset),y0+int(h*inset),x1-int(w*inset),y1-int(h*inset)))
    # square crop from the centre, then downscale
    s=min(c.width,c.height); c=c.crop(((c.width-s)//2,(c.height-s)//2,(c.width-s)//2+s,(c.height-s)//2+s))
    out=c.convert('RGBa').resize((T,T),Image.LANCZOS).convert('RGBA'); a=np.array(out); a[...,3]=255; return Image.fromarray(a,'RGBA')
tiles={n:tile(n) for n in BOX}
q,pal=quantise(list(tiles.values()),48)
for n,f in zip(tiles,q): f.save(f'{A}/tile_{n}.png')
# mock: a 7x5 patch of the map with walls, pillars, floor and crates, 4x
names=list(tiles); m=Image.new('RGBA',(T*7,T*5))
for y in range(5):
    for x in range(7):
        k='wall' if (x in (0,6) or y in (0,4)) else ('pillar' if x%2==0 and y%2==0 else 'floor')
        m.paste(q[names.index(k)],(x*T,y*T))
for (x,y,k) in ((1,2,'crate_0'),(3,1,'crate_1'),(4,3,'crate_0_broken'),(5,2,'crate_1_broken')): m.paste(q[names.index(k)],(x*T,y*T))
m.resize((m.width*3,m.height*3),Image.NEAREST).save('work/tiles_mock.png'); print('tiles',list(tiles))
