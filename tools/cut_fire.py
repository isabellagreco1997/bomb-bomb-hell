"""Fire tiles from the effects sheet (painted gradient bg, so key by fire brightness, not bg distance).
Horizontal arm tiles from the 3 horizontal strips, vertical from the 2 vertical strips, centre from the cross. All 48x48."""
import sys, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
from scipy import ndimage
A='assets/sprites/48/anim'; W='work'; T=48
sheet_im=np.array(Image.open('assets/src/effects_sheet.png').convert('RGBA')).astype(float)
BOX={'h0':(26,362,129,396),'h1':(170,338,309,399),'h2':(345,347,516,393),'v0':(1155,293,1196,420),'v1':(1289,312,1324,415),'c0':(1118,179,1233,255),'c1':(1259,172,1369,263)}
def fire_key(cell, pad=6):
    r,g,b=cell[...,0],cell[...,1],cell[...,2]; heat=np.clip((r+g-260)/120,0,1)*np.clip((r-90)/80,0,1)    # bright + warm = fire
    a=cell.copy(); a[...,3]=heat*255; return a
def tile(name, thick):
    """scale so the strip's thin dimension = thick px, then CROP the long dimension to the tile (never stretch)"""
    x0,y0,x1,y1=BOX[name]; c=fire_key(sheet_im[y0-4:y1+4, x0-4:x1+4])
    im=Image.fromarray(c.astype('uint8'),'RGBA'); horizontal=im.width>=im.height
    s=thick/(im.height if horizontal else im.width)
    small=im.convert('RGBa').resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS).convert('RGBA')
    fr=Image.new('RGBA',(T,T),(0,0,0,0)); fr.paste(small,((T-small.width)//2,(T-small.height)//2),small); return fr
# ONE master: the vertical beam strips. Horizontal = the same beam turned 90 degrees, centre = both overlaid (brighter core). One style for the whole cross.
v=[tile('v0',38),tile('v1',38),tile('v0',38).transpose(Image.FLIP_TOP_BOTTOM)]
h=[t.transpose(Image.ROTATE_90) for t in v]
def overlay(a,b):
    A=np.array(a).astype(int); B=np.array(b).astype(int); out=A.copy()
    m=B[...,3]>A[...,3]; out[m]=B[m]
    both=(A[...,3]>128)&(B[...,3]>128); out[both,:3]=np.clip(np.maximum(A[both,:3],B[both,:3])+30,0,255)   # hotter where the beams cross
    return Image.fromarray(out.astype('uint8'),'RGBA')
c=[overlay(v[i],h[i]) for i in range(3)]
allf=h+v+c
q,pal=quantise(allf,32)
names=[f'fire_h_{i}' for i in range(3)]+[f'fire_v_{i}' for i in range(3)]+[f'fire_c_{i}' for i in range(3)]
for n,f in zip(names,q): f.save(f'{A}/{n}.png')
sheet(q,9,4,bg=(90,20,30,255)).save(f'{W}/strip_fire.png'); print('fire tiles',len(q))
