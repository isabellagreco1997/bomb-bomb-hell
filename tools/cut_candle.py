import sys, json, os; sys.path.insert(0,'tools')
from spritecut import *
TILE=int(sys.argv[1]) if len(sys.argv)>1 else 48
FW,FH=TILE,int(TILE*1.25); SCALE=(FH-14)/68      # candle body ~68 px on the sheet -> ~46 px, player-sized like real Bomberman enemies
OUT=f'assets/sprites/{TILE}'; os.makedirs(OUT,exist_ok=True)
en=np.array(Image.open('assets/src/enemies_sheet.png').convert('RGBA'))
panel=en[46:345,302:507].copy(); CBG=np.array([47.,10.,20.])
cols=[(5,65),(72,135),(142,202)]; rows=[(0,70),(72,150),(151,229)]
names=['idle','move','hurt']
out={}
raw={}
for r,(y0,y1) in enumerate(rows):
    raw[names[r]]=[]
    for (x0,x1) in cols:
        cell=key(panel[y0:y1,x0:x1],CBG,thr=45,soft=30); cell=largest_blob(cell)
        raw[names[r]].append(fit(cell,FW,FH,SCALE))
dcols=[(2,100),(100,202)]; raw['defeated']=[]
for (x0,x1) in dcols:
    cell=largest_blob(key(panel[231:297,x0:x1],CBG,thr=45,soft=30)); raw['defeated'].append(fit(cell,FW,FH,SCALE))
allf=[f for v in raw.values() for f in v]
q,pal=quantise(allf,32)
k=0
for name,v in raw.items():
    out[name]=q[k:k+len(v)]; k+=len(v)
    for j,f in enumerate(out[name]): f.save(f'{OUT}/candle_{name}_{j}.png')
json.dump({'tile':TILE,'frame':[FW,FH],'scale':SCALE,'palette':pal.tolist(),'rows':{n:len(v) for n,v in out.items()}},open(f'{OUT}/candle.json','w'),indent=1)
sheet(allf,3,max(1,288//FW),bg=(40,4,12,255)).save(f'work/candle_{TILE}_raw_preview.png')
sheet([f for v in out.values() for f in v],3,max(1,288//FW),bg=(40,4,12,255)).save(f'work/candle_{TILE}_preview.png')
# also the raw grid cells at 3x for a sanity check of the cut
cells=[Image.fromarray(panel[y0:y1,x0:x1]) for (y0,y1) in rows for (x0,x1) in cols]
sheet(cells,3,3).save('work/candle_cells_3x.png')
print(TILE,'candle frames',len(allf))
