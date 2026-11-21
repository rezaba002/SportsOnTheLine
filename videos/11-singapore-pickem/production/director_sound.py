"""Word-cued foley, three ducked score beds and two-pass delivery mastering."""
import json
import math
import shutil
import subprocess as sp
from pathlib import Path
import numpy as np
from scipy.io.wavfile import write as wav
from director_inputs import CUT, read, write

LIB=Path.home()/".claude/skills/editing-videos/library"
LIBRARY={r["id"]:r for r in read(LIB/"catalog.json")["sounds"]}
TL=read(CUT/"edit.json");SC={s["id"]:s for s in TL["scenes"]};RATE=48000
N=TL["frames"]*1600;MIX=np.zeros((N,2),np.float32);events=[];used={};duck=np.ones(N//480+1,np.float32)

def clip(path,af="anull"):
    b=sp.check_output(["ffmpeg","-v","error","-i",str(path),"-af",af,"-ar",str(RATE),"-ac","2","-f","f32le","pipe:1"])
    return np.frombuffer(b,np.float32).reshape(-1,2)
def place(data,start,gain=1,fade=.012,pan=0,env=None):
    start=max(0,round(start*RATE));ln=min(len(data),N-start)
    if ln<=0:return
    x=data[:ln].copy()*gain
    if env is not None:x*=env[:ln,None]
    n=min(ln//2,int(RATE*fade))
    if n:
        v=np.linspace(0,1,n,dtype=np.float32);x[:n]*=v[:,None];x[-n:]*=v[::-1,None]
    x[:,0]*=min(1,1-pan);x[:,1]*=min(1,1+pan)
    MIX[start:start+ln]+=x
def sec(sid):return SC[sid]["fromFrame"]/30
def cue(sid,word):
    s=SC[sid];return s["audioStart"]/30+next(w["s"] for w in s["words"] if w["w"].casefold()==word.casefold())
def asset(name):
    row=LIBRARY[name];assert row["license"]=="CC0 1.0"
    dest=CUT/"sounds"/row["file"];dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copyfile(LIB/row["file"],dest)
    used[name]=row;return dest
def measure(p):
    proc=sp.run(["ffmpeg","-nostats","-hide_banner","-i",str(p),"-map","0:a:0","-af","loudnorm=I=-14:TP=-1.9:LRA=10:print_format=json","-f","null","-"],capture_output=True,text=True,check=True)
    return json.JSONDecoder().raw_decode(proc.stderr[proc.stderr.rfind("{"):])[0]
def run():
    for s in SC.values():
        at=s["audioStart"]/30
        voice=clip(s["file"],"highpass=f=65,loudnorm=I=-16:TP=-2.8:LRA=9")
        place(voice,at,fade=.005)
        for w in s["words"]:
            a=max(0,int((at+w["s"]-.16)*100));b=min(len(duck),int((at+w["e"]+.24)*100))
            duck[a:b]=.51
        events.append({"kind":"voice","id":s["id"],"start":at,"end":at+len(voice)/RATE})
    state=1
    for i,v in enumerate(duck):
        state+=(v-state)*(.16 if v<state else .045);duck[i]=state
    for name,s,e in [("music-tension-soft","s1","s3"),("music-contemplation","s3","s5"),("music-tension-soft","s5","s9"),
                     ("music-tension-22s","s9","s10"),("music-contemplation","s10","s12"),("music-inspiring-orchestral","s12",None)]:
        a=sec(s);b=sec(e) if e else N/RATE;ln=round((b-a)*RATE);v=clip(asset(name),"equalizer=f=2300:t=q:w=1:g=-3")
        d=v.copy()
        while len(d)<ln:
            k=min(len(v)//3,RATE);r=np.linspace(0,1,k,dtype=np.float32)[:,None]
            d=np.concatenate((d[:-k],d[-k:]*(1-r)+v[:k]*r,v[k:]))
        env=np.interp(np.arange(ln)/480+a*100,np.arange(len(duck)),duck).astype(np.float32)
        place(d[:ln],a,.21,1.1,env=env);events.append(dict(kind="score",id=name,start=a,end=b))
    for sid,word,name,shift,gain,pan in [
      ("s1","Ten","click-soft",-.07,.25,-.18),("s1","fails","dry-thud",-.11,.36,0),("s1","Singapore","swell-soft-3s",-1.55,.17,.12),
      ("s2","maps","tick-soft",-.10,.23,-.10),("s3","half","select-1",-.09,.21,.12),("s3","vetoes","page-turn",-.20,.24,-.10),
      ("s3","fourteen","impact-soft-1",-.09,.30,0),("cta1","subscribe","click-mouse",-.055,.31,.12),
      ("s4","slots","slide-1",-.15,.25,-.20),("s4","Five","check-mark",-.08,.25,0),("s4","nothing","stamp-thud",-.11,.31,0),
      ("s5","After","switch-1",-.08,.22,.10),("s6","band","panel-expand",-.13,.23,.12),("s7","bottom","slide-2",-.12,.22,-.17),
      ("s8","notice","toggle",-.06,.23,0),("s9","locks","drop-item",-.10,.27,0),("s9","Heroic","select-2",-.07,.19,.12),
      ("s9","Run","page-turn",-.18,.25,-.2),("s9","thirty-one","impact-soft-2",-.09,.28,0),("s10","Ninjas","drag-item",-.10,.24,-.18),
      ("s10","out","back-nav",-.07,.21,.15),("s10","becomes","downlifter-2s",-.24,.18,0),
      ("s10","Lock","stamp-thud",-.12,.28,.04),("s11","Keep","slide-1",-.15,.21,-.10),("s12","subscribe","click-soft-2",-.075,.24,.15)]:
        a=cue(sid,word)+shift;place(clip(asset(name)),a,gain,pan=pan);events.append(dict(kind="effect",id=name,scene=sid,word=word,start=a,gain=gain))
    wav(CUT/"premaster.wav",RATE,MIX)
    write(CUT/"mix_cues.json",dict(cues=events,sources=used))
    master()

def master():
    first=measure(CUT/"premaster.wav")
    af=("loudnorm=I=-14:TP=-1.9:LRA=10:linear=true:"+":".join(k+"="+first[v] for k,v in
        [("measured_I","input_i"),("measured_TP","input_tp"),("measured_LRA","input_lra"),("measured_thresh","input_thresh"),("offset","target_offset")]))
    sp.run(["ffmpeg","-v","error","-y","-i",str(CUT/"premaster.wav"),"-af",af,"-ar",str(RATE),"-c:a","aac","-b:a","320k",str(CUT/"sound.m4a")],check=True)
    result=measure(CUT/"sound.m4a");write(CUT/"sound_receipt.json",dict(measured=result,**read(CUT/"mix_cues.json")))
    print("AAC measured:",result,flush=True)

if __name__=="__main__":run()
