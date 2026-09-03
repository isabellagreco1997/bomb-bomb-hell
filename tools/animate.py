"""Stabilise AI rows (align on head centroid), assemble 4-direction walks + candle loops, export gifs + strips."""
import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
D='assets/sprites/48'; W='work'
def load(prefix,n): return [Image.open(f'{D}/{prefix}_{i}.png') for i in range(n)]
def align_x(frames, top_frac=0.45):
    """shift each frame horizontally so the head centroid matches the row median (kills AI jitter)"""
    cs=[]
    for f in frames:
        a=np.array(f)[...,3]>0; h=int(a.shape[0]*top_frac); ys,xs=np.nonzero(a[:h]); cs.append(xs.mean())
    med=np.median(cs); out=[]
    for f,c in zip(frames,cs):
        dx=int(round(med-c)); g=Image.new('RGBA',f.size,(0,0,0,0)); g.paste(f,(dx,0),f); out.append(g)
    return out, [round(med-c,1) for c in cs]
hj=json.load(open(f'{D}/heroine.json'))['rows']
rows={n:load('heroine_'+n,hj[n]) for n in ('down','up','left','row4','row5')}
walk={'down':rows['row5'],'up':rows['row4'],'left':rows['left']}
idle={'down':rows['down'][0],'up':rows['up'][0],'left':rows['left'][0]}
for k in list(walk):
    walk[k],shifts=align_x(walk[k]); print('align',k,shifts)
walk['right']=[f.transpose(Image.FLIP_LEFT_RIGHT) for f in walk['left']]
idle['right']=idle['left'].transpose(Image.FLIP_LEFT_RIGHT)
os.makedirs(f'{D}/anim',exist_ok=True)
for k,fr in walk.items():
    for i,f in enumerate(fr): f.save(f'{D}/anim/heroine_walk_{k}_{i}.png')
    idle[k].save(f'{D}/anim/heroine_idle_{k}.png')
    big=[f.resize((f.width*4,f.height*4),Image.NEAREST) for f in fr]
    bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/heroine_walk_{k}.gif',save_all=True,append_images=bg[1:],duration=110,loop=0,disposal=2)
    sheet(fr,7,4,bg=(40,4,12,255)).save(f'{W}/strip_walk_{k}.png')
cj=json.load(open(f'{D}/candle.json'))['rows']
cand={n:load('candle_'+n,cj[n]) for n in cj}
for k in ('idle','move'):
    fr,shifts=align_x(cand[k],0.6); print('candle align',k,shifts)
    loop=fr+[fr[1]]                      # 0 1 2 1 ping-pong
    for i,f in enumerate(fr): f.save(f'{D}/anim/candle_{k}_{i}.png')
    big=[f.resize((f.width*4,f.height*4),Image.NEAREST) for f in loop]
    bg=[Image.new('RGB',b.size,(40,4,12)) for b in big]
    for b,g in zip(big,bg): g.paste(b,(0,0),b)
    bg[0].save(f'{W}/candle_{k}.gif',save_all=True,append_images=bg[1:],duration=140,loop=0,disposal=2)
for k in ('hurt','defeated'):
    for i,f in enumerate(cand[k]): f.save(f'{D}/anim/candle_{k}_{i}.png')
# frame-difference per row: does anything actually move?
for k,fr in walk.items():
    a=[np.array(f)[...,3]>0 for f in fr]; diffs=[int((a[i]^a[(i+1)%len(a)]).sum()) for i in range(len(a))]
    print('walk',k,'changed px between frames',diffs)
