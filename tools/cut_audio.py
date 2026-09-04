"""Split a voice-line file into single clips on silence, then speed + pitch up (tape-style: asetrate), trim, normalise.
usage: cut_audio.py <src.mp3> <name> [rate=1.3] [noise_db=-35] [min_sil=0.25]"""
import sys, subprocess, re, os, json
src=sys.argv[1]; name=sys.argv[2]; rate=float(sys.argv[3]) if len(sys.argv)>3 else 1.3
noise=sys.argv[4] if len(sys.argv)>4 else '-35dB'; minsil=sys.argv[5] if len(sys.argv)>5 else '0.25'
out=subprocess.run(['ffmpeg','-i',src,'-af',f'silencedetect=noise={noise}:d={minsil}','-f','null','-'],capture_output=True,text=True).stderr
dur=float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',out).groups()[2])+60*float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',out).groups()[1])
starts=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)]; ends=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
# sound segments = between silence_end[i] and silence_start[i+1]
bounds=[]; cur=0.0 if (not starts or starts[0]>0.05) else None
if cur is not None: bounds.append([0.0,None])
for s,e in zip(starts,ends+[dur]):
    if bounds and bounds[-1][1] is None: bounds[-1][1]=s
    bounds.append([e,None])
if bounds and bounds[-1][1] is None: bounds[-1][1]=dur
segs=[(a,b) for a,b in bounds if b-a>0.12]
os.makedirs('assets/audio',exist_ok=True); made=[]
for i,(a,b) in enumerate(segs):
    a0=max(0,a-0.04); b0=min(dur,b+0.06); o=f'assets/audio/{name}_{i}.mp3'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{a0:.3f}','-to',f'{b0:.3f}','-i',src,'-af',f'asetrate=44100*{rate},aresample=44100,loudnorm=I=-16:TP=-1.5:LRA=11','-ar','44100','-b:a','96k',o],check=True)
    made.append(o); print(f'{o}: {a0:.2f}-{b0:.2f}s ({(b0-a0)/rate:.2f}s after speed-up)')
json.dump(made,open(f'assets/audio/{name}.json','w')); print(len(made),'clips')
