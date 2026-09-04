"""Bomb from bomb.mp4: tick frames (fuse building) + burst frames (flash and explosion centre). 48x64 frames, bomb body ~40 px, bottom anchored."""
import sys, os, glob; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'; W='work'; FW,FH=48,64
fs=sorted(glob.glob('work/vid_bomb/f_*.png')); bg=np.array([28.,0.,7.])
THR=int(sys.argv[1]) if len(sys.argv)>1 else 10; SOFT=8
def cutf(i, keep_all=False, thr=None):
    a=np.array(Image.open(fs[i]).convert('RGBA'))
    if thr:   # burst: keep only the bright fire (flash + sparks), the lit background and the bomb body drop out
        r,g,b=a[...,0].astype(float),a[...,1].astype(float),a[...,2].astype(float); heat=np.clip((r+g-330)/120,0,1)*np.clip((r-120)/80,0,1)
        k=a.astype(float).copy(); k[...,3]=heat*255; return k
    k=key(a,bg,thr=THR,soft=SOFT)
    return k if keep_all else largest_blob(k)
# bomb body width from frame 0 (largest blob = the bomb)
c0=largest_blob(cutf(0,True)); al=c0[...,3]>0; ys,xs=np.nonzero(al); body_w=xs.max()-xs.min(); body_bottom=ys.max()
SCALE=40/body_w; print('bomb body width',body_w,'scale',round(SCALE,3),'bottom',body_bottom)
def frame(i, keep_all, thr=None):
    c=cutf(i,keep_all,thr); im=Image.fromarray(c.astype('uint8'),'RGBA')
    # anchor: the bomb bottom row lands on FH-3, horizontally centred on the body's centre from frame 0
    cx=(xs.min()+xs.max())/2
    small=im.convert('RGBa').resize((round(im.width*SCALE),round(im.height*SCALE)),Image.LANCZOS).convert('RGBA')
    fr=Image.new('RGBA',(FW,FH),(0,0,0,0)); fr.paste(small,(int(round(FW/2-cx*SCALE)),int(round((FH-3)-body_bottom*SCALE))),small); return fr
TICK=[0,15,30,45,60,75,90,105,114,120]        # fuse building over 5 s
BURST=[123,125,127,129,132,135]               # flash, peak, fade
tick=[frame(i,True) for i in TICK]; burst=[frame(i,True,thr=90) for i in BURST]   # burst: only the bright fire, not the lit background
q,pal=quantise(tick+burst,40); tick,burst=q[:len(tick)],q[len(tick):]
for p in glob.glob(f'{A}/bomb_*.png'): os.remove(p)
for j,f in enumerate(tick): f.save(f'{A}/bomb_tick_{j}.png')
for j,f in enumerate(burst): f.save(f'{A}/bomb_burst_{j}.png')
sheet(tick+burst,8,4,bg=(40,4,12,255)).save(f'{W}/strip_bomb.png'); print('bomb frames',len(tick),len(burst))
