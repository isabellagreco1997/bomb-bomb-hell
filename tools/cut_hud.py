"""HUD hearts from the enemies/UI sheet: full, half, empty. 24 px icons, keyed by distance from the panel background."""
import sys, os, shutil; sys.path.insert(0,'tools')
from spritecut import *
from PIL import Image
import numpy as np
A='assets/sprites/48/anim'
sheet_im=np.array(Image.open('assets/src/enemies_sheet.png').convert('RGBA')).astype(float)
BOX={'full':(1008,77,1042,108),'half':(1075,77,1110,108),'empty':(1108,77,1143,108)}
bg=np.median(sheet_im[60:70,1000:1150,:3].reshape(-1,3),axis=0); print('panel bg',bg)
out=[]
for n,(x0,y0,x1,y1) in BOX.items():
    c=largest_blob(key(sheet_im[y0:y1,x0:x1],bg,thr=35,soft=25)); im=Image.fromarray(c.astype('uint8'),'RGBA')
    s=24/im.width; small=im.convert('RGBa').resize((24,max(1,round(im.height*s))),Image.LANCZOS).convert('RGBA')
    fr=Image.new('RGBA',(24,24),(0,0,0,0)); fr.paste(small,(0,(24-small.height)//2),small); out.append(fr)
q,_=quantise(out,24)
for n,f in zip(BOX,q): f.save(f'{A}/hud_heart_{n}.png')
for n in ('dizzy','defeated'): shutil.copy(f'assets/sprites/48/heroine_{n}_0.png',f'{A}/heroine_{n}_0.png')
sheet(q,3,6,bg=(40,4,12,255)).save('work/strip_hearts.png'); print('hearts ok')
