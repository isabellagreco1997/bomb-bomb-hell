"""Build consistent title art and authored local-motion sprite frames from original PNGs.
The original inputs are never overwritten. Run from the game project root.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/title'
OUT=SRC/'sprites'
WORK=ROOT/'work/title-animation'
OUT.mkdir(exist_ok=True); WORK.mkdir(parents=True,exist_ok=True)
GRID=4
STAGE=(350,280)
N=60
FPS=12

def clean(name,colors,hero=False,opaque=False):
    a=np.array(Image.open(SRC/name).convert('RGBA'))
    if not opaque:
        mask=a[:,:,3]>=128
        lab,n=nd.label(mask)
        sizes=np.bincount(lab.ravel());sizes[0]=0
        if hero:
            mask=lab==sizes.argmax()
            # The dark outlined sprite has no intentionally white silhouette edge.
            # Remove pale matte remnants touching the outside, not interior highlights.
            rgb=a[:,:,:3].astype(int)
            pale=(rgb.min(2)>175)&((rgb.max(2)-rgb.min(2))<38)
            edge=mask & nd.binary_dilation(~mask)
            mask &= ~(pale & edge)
        else:
            mask &= sizes[lab]>=24
        a[:,:,3]=np.where(mask,255,0)
        a[~mask,:3]=0
    im=Image.fromarray(a).resize(STAGE,Image.Resampling.BOX)
    a=np.array(im); mask=a[:,:,3]>=160 if not opaque else np.ones(a.shape[:2],bool)
    a[:,:,3]=np.where(mask,255,0);a[~mask,:3]=0
    # Palette reduction without dithering: solid color clusters, no generated noise.
    rgba=Image.fromarray(a)
    q=rgba.quantize(colors=colors,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).convert('RGBA')
    a=np.array(q);a[:,:,3]=np.where(mask,255,0);a[~mask,:3]=0
    return Image.fromarray(a)

base={
 'heroine':clean('heroine-bomb-falling-original-horns.png',64,hero=True),
 'ghost':clean('candle-ghost.png',32),
 'logo':clean('title-logo.png',80),
 'skyline':clean('background-skyline.png',64,opaque=True),
 'menu':clean('hud-frame.png',48),
}
for key,im in base.items(): im.save(OUT/f'{key}-base.png')

# Preview uses the same transforms as the live title composition.
def composition(art):
    stage=art['skyline'].copy()
    stage.alpha_composite(art['heroine'],(-10,3))
    stage.alpha_composite(art['ghost'])
    logo=art['logo'].resize((294,235),Image.Resampling.NEAREST)
    stage.alpha_composite(logo,(52,3))
    stage.alpha_composite(art['menu'])
    return stage
composition(base).resize((1050,840),Image.Resampling.NEAREST).save(WORK/'consistent-art.png')
# Inspection crops are nearest-neighbor enlargements, with a dark matte for edge QA.
for key,box in [('heroine',(15,102,150,266)),('ghost',(270,104,326,178))]:
    tile=base[key].crop(box)
    bg=Image.new('RGBA',tile.size,'#210712');bg.alpha_composite(tile)
    bg.resize((tile.width*5,tile.height*5),Image.Resampling.NEAREST).save(WORK/f'{key}-detail.png')
print('Clean 4px-grid bases saved; originals preserved.')


# Only assembly happens here. The artwork is stored in individually authored PNGs
# and explicit palette-indexed pixel maps in sprites/keyframes/pixel-art.json.
ART=OUT/'keyframes'
hero_order=([0]*8 + [1,1,2,2,3,3,4,4,5,5,2,2]*4 + [6,7,6,2])
ghost_cycle=[0,1,2,3,4,3,2,1]
ghost_order=[ghost_cycle[(i//2)%len(ghost_cycle)] for i in range(N)]
ghost_order[39]=5
logo_cycle=[0,1,2,3,2,1]
orders={'heroine':hero_order,'ghost':ghost_order,'logo':[logo_cycle[(i//2)%len(logo_cycle)] for i in range(N)]}

def positioned(key,im):
    layer=Image.new('RGBA',STAGE)
    if key=='heroine':layer.alpha_composite(im,(-10,3))
    elif key=='logo':layer.alpha_composite(im.resize((294,235),Image.Resampling.NEAREST),(52,3))
    else:layer.alpha_composite(im)
    return layer

manifest={'stage':list(STAGE),'fps':FPS,'sourcePixelGrid':GRID,'sprites':{}}
all_tracks={}
for key,order in orders.items():
    assert len(order)==N
    keyframes={i:Image.open(ART/f'{key}-{i:02d}.png').convert('RGBA') for i in set(order)}
    frames=[positioned(key,keyframes[i]) for i in order];all_tracks[key]=frames
    union=np.logical_or.reduce([np.array(f)[:,:,3]>0 for f in frames])
    ys,xs=np.where(union);box=(max(0,int(xs.min())-1),max(0,int(ys.min())-1),min(350,int(xs.max())+2),min(280,int(ys.max())+2))
    tiles=[f.crop(box) for f in frames];w,h=tiles[0].size;cols=10
    sheet=Image.new('RGBA',(w*cols,h*((N+cols-1)//cols)))
    for i,f in enumerate(tiles):sheet.alpha_composite(f,((i%cols)*w,(i//cols)*h))
    sheet.save(OUT/f'{key}-atlas.png',optimize=True)
    frames[0].save(OUT/f'{key}-idle.png')
    manifest['sprites'][key]={'file':f'{key}-atlas.png','frames':N,'fps':FPS,'columns':cols,'size':[w,h],'origin':list(box[:2]),'uniqueFrames':len({f.tobytes() for f in tiles}),'authoredKeyframes':len(keyframes),'sequence':order}
    gif=[]
    for tile in tiles:
        bg=Image.new('RGBA',tile.size,'#210712');bg.alpha_composite(tile)
        gif.append(bg.convert('RGB').resize((w*4,h*4),Image.Resampling.NEAREST))
    gif[0].save(WORK/f'{key}-motion.gif',save_all=True,append_images=gif[1:],duration=83,loop=0,disposal=2)
video_track = OUT/'heroine-video-track.json'
if video_track.exists():
    manifest['sprites']['heroine'] = json.loads(video_track.read_text())
ghost_video_track = OUT/'ghost-video-track.json'
if ghost_video_track.exists():
    manifest['sprites']['ghost'] = json.loads(ghost_video_track.read_text())
logo_video_track = OUT/'logo-video-track.json'
if logo_video_track.exists():
    manifest['sprites']['logo'] = json.loads(logo_video_track.read_text())
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Complete scene loop for visual QA, at the same pixel scale across every asset.
scene_frames=[]
for t in range(N):
    scene=base['skyline'].copy()
    for key in ['heroine','ghost','logo']:scene.alpha_composite(all_tracks[key][t])
    scene.alpha_composite(base['menu'])
    scene_frames.append(scene.convert('RGB').resize((700,560),Image.Resampling.NEAREST))
scene_frames[0].save(WORK/'authored-scene.gif',save_all=True,append_images=scene_frames[1:],duration=83,loop=0,disposal=2)
print('Assembled authored keyframes:',{k:v['authoredKeyframes'] for k,v in manifest['sprites'].items()})
