"""Pack phase-1 frames into atlas.png + atlas.json (name -> x,y,w,h)."""
import json, os
from PIL import Image
D='assets/sprites/48/anim'; OUT='assets'
names=[]
for d in ('down','up','left','right'):
    names+=[f'heroine_idle_{d}_{j}' for j in range(24)]
    names+= [f'heroine_cycle_{d}_{j}' for j in range(json.load(open(f'{D}/heroine_cycles.json'))[d])]
for k,n in (('idle',3),('move',3),('hurt',3),('defeated',2),('flicker',10)): names+=[f'candle_{k}_{i}' for i in range(n)]
ims=[Image.open(f'{D}/{n}.png') for n in names]
FW,FH=48,60; cols=10; rows=(len(ims)+cols-1)//cols
atlas=Image.new('RGBA',(FW*cols,FH*rows),(0,0,0,0)); meta={'frame':[FW,FH],'frames':{},'anims':{}}
for i,(n,im) in enumerate(zip(names,ims)):
    x,y=(i%cols)*FW,(i//cols)*FH; atlas.paste(im,(x,y)); meta['frames'][n]=[x,y,FW,FH]
for d in ('down','up','left','right'):
    meta['anims'][f'heroine_walk_{d}']=[f'heroine_cycle_{d}_{j}' for j in range(json.load(open(f'{D}/heroine_cycles.json'))[d])]
    meta['anims'][f'heroine_idle_{d}']=[f'heroine_idle_{d}_{j}' for j in range(24)]
meta['anims']['candle_idle']=['candle_idle_0','candle_idle_1','candle_idle_2','candle_idle_1']
meta['anims']['candle_move']=['candle_move_0','candle_move_1','candle_move_2','candle_move_1']
meta['anims']['candle_hurt']=['candle_hurt_0','candle_hurt_1','candle_hurt_2']
meta['anims']['candle_flicker']=[f'candle_flicker_{j}' for j in range(10)]
meta['anims']['candle_defeated']=['candle_defeated_0','candle_defeated_1']
atlas.save(f'{OUT}/atlas.png'); json.dump(meta,open(f'{OUT}/atlas.json','w'),indent=1)
atlas.resize((atlas.width*3,atlas.height*3),Image.NEAREST).save('work/atlas_3x.png')
print('atlas',atlas.size,len(names),'frames')
