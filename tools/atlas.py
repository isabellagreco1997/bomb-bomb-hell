"""Pack phase-1 frames into atlas.png + atlas.json (name -> x,y,w,h)."""
import json, os
from PIL import Image
D='assets/sprites/48/anim'; OUT='assets'
names=[]
for d in ('down','up','left','right'):
    names+=[f'heroine_idle_{d}_{j}' for j in range(24)]
    names+= [f'heroine_cycle_{d}_{j}' for j in range(json.load(open(f'{D}/heroine_cycles.json'))[d])]
for k,n in (('idle',3),('move',3),('hurt',3),('defeated',2),('flicker',10)): names+=[f'candle_{k}_{i}' for i in range(n)]
names+=[f'bomb_tick_{j}' for j in range(10)]
names+=[f'fire_{k}_{j}' for k in ('h','v','c') for j in range(3)]
names+=['hud_heart_full','hud_heart_half','hud_heart_empty','heroine_dizzy_0','heroine_defeated_0']
names+=['tile_floor','tile_floor_1','tile_floor_2','tile_pillar','tile_pillar_glow','tile_wall','tile_crate_0','tile_crate_0_broken','tile_crate_1','tile_crate_1_broken','tile_brazier','tile_brazier_1','tile_brazier_2']
names+=['tile_exit','pw_bomb','pw_fire','pw_speed']
NS=json.load(open(f'{D}/heroine_start.json'))['n']; names+=[f'heroine_start_{j}' for j in range(NS)]
ND=json.load(open(f'{D}/heroine_death.json'))['n']; names+=[f'heroine_death_{j}' for j in range(ND)]
NW=json.load(open(f'{D}/heroine_win.json'))['n']; names+=[f'heroine_win_{j}' for j in range(NW)]
ims=[Image.open(f'{D}/{n}.png') for n in names]
# shelf packer: frames of mixed sizes, rows of equal height, atlas width 512
AW=512; meta={'frames':{},'anims':{}}; order=sorted(range(len(ims)),key=lambda i:(-ims[i].height,-ims[i].width))
x=y=rowh=0; pos={}
for i in order:
    im=ims[i]
    if x+im.width>AW: x=0; y+=rowh; rowh=0
    pos[i]=(x,y); x+=im.width; rowh=max(rowh,im.height)
AH=y+rowh; atlas=Image.new('RGBA',(AW,AH),(0,0,0,0))
for i,(px,py) in pos.items():
    im=ims[i]; atlas.paste(im,(px,py)); meta['frames'][names[i]]=[px,py,im.width,im.height]
for d in ('down','up','left','right'):
    meta['anims'][f'heroine_walk_{d}']=[f'heroine_cycle_{d}_{j}' for j in range(json.load(open(f'{D}/heroine_cycles.json'))[d])]
    meta['anims'][f'heroine_idle_{d}']=[f'heroine_idle_{d}_{j}' for j in range(24)]
meta['anims']['candle_idle']=['candle_idle_0','candle_idle_1','candle_idle_2','candle_idle_1']
meta['anims']['candle_move']=['candle_move_0','candle_move_1','candle_move_2','candle_move_1']
meta['anims']['candle_hurt']=['candle_hurt_0','candle_hurt_1','candle_hurt_2']
meta['anims']['candle_flicker']=[f'candle_flicker_{j}' for j in range(10)]
meta['anims']['heroine_win']=[f'heroine_win_{j}' for j in range(NW)]
meta['anims']['heroine_death']=[f'heroine_death_{j}' for j in range(ND)]
meta['anims']['heroine_start']=[f'heroine_start_{j}' for j in range(NS)]
meta['anims']['bomb_tick']=[f'bomb_tick_{j}' for j in range(10)]
for k in ('h','v','c'): meta['anims'][f'fire_{k}']=[f'fire_{k}_{j}' for j in range(3)]
meta['anims']['candle_defeated']=['candle_defeated_0','candle_defeated_1']
atlas.save(f'{OUT}/atlas.png'); json.dump(meta,open(f'{OUT}/atlas.json','w'),indent=1)
atlas.resize((atlas.width*3,atlas.height*3),Image.NEAREST).save('work/atlas_3x.png')
print('atlas',atlas.size,len(names),'frames')
