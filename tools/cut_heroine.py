import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
TILE=int(sys.argv[1]) if len(sys.argv)>1 else 48
FW,FH=TILE,int(TILE*1.25)                # 48x60 or 32x40
BODY=134; SCALE=(FH-2)/BODY
OUT=f'assets/sprites/{TILE}'; os.makedirs(OUT,exist_ok=True)
her=np.array(Image.open('assets/src/heroine_sheet.png').convert('RGBA'))
HBG=np.array([33.8,1.4,8.4]); boxes=json.load(open('work/heroine_boxes.json'))
rows={'down':range(1,8),'up':range(8,15),'left':range(15,22),'row4':range(24,31),'row5':range(32,39)}
poses={'bomb_a':22,'bomb_b':23,'victory':39,'hurt':41,'dizzy':43,'defeated':45}
raw={}
for name,idx in rows.items():
    raw[name]=[fit(largest_blob(key(her[b[1]:b[3],b[0]:b[2]],HBG)),FW,FH,SCALE) for b in (boxes[i] for i in idx)]
for name,i in poses.items():
    b=boxes[i]; cell=largest_blob(key(her[b[1]:b[3],b[0]:b[2]],HBG), keep_inside=True)
    w=max(FW,int(np.ceil((b[2]-b[0])*SCALE/8)*8)); raw[name]=[fit(cell,w,FH,SCALE)]
allf=[f for v in raw.values() for f in v]
q,pal=quantise(allf,48)
k=0; out={}
for name,v in raw.items():
    out[name]=q[k:k+len(v)]; k+=len(v)
    for j,f in enumerate(out[name]): f.save(f'{OUT}/heroine_{name}_{j}.png')
json.dump({'tile':TILE,'frame':[FW,FH],'scale':SCALE,'palette':pal.tolist(),'rows':{n:len(v) for n,v in out.items()}},open(f'{OUT}/heroine.json','w'),indent=1)
walk=[f for n in ('down','up','left','row4','row5') for f in out[n]]
sheet(walk,7,max(1,288//FW),bg=(40,4,12,255)).save(f'work/heroine_{TILE}_walk_preview.png')
sheet([out[n][0] for n in poses],6,max(1,288//FW),bg=(40,4,12,255)).save(f'work/heroine_{TILE}_poses_preview.png')
print(TILE,'frames',len(allf),'scale',round(SCALE,3))
