"""Render independent, resumable 1080p scenes (PyAV/x264); samples use identical art."""
import argparse
import os
import time
import av
from PIL import Image
from director_open import *

def render(ids, samples=False):
    funcs={"s1":hook,"s2":data_scene,"s3":method,"cta1":subscribe,"s4":objective}
    if any(k not in funcs for k in ids):
        from director_close import charts, model_ticket, eye_ticket, caveats, outro
        funcs.update({k:lambda c,t,k=k:charts(c,t,k) for k in ["s5","s6","s7","s8"]})
        funcs.update(s9=model_ticket,s10=eye_ticket,s11=caveats,s12=outro)
    buf=np.empty((H,W,4),np.uint8)
    surface=sk.Surface.MakeRasterDirect(sk.ImageInfo.Make(W,H,sk.ColorType.kBGRA_8888_ColorType,sk.AlphaType.kOpaque_AlphaType),buf)
    c=surface.getCanvas();out=CUT/"picture";out.mkdir(exist_ok=True);checks=CUT/"stills";checks.mkdir(exist_ok=True)
    for sid in ids:
        frames=SC[sid]["frames"];dest=out/(sid+".mp4");start=time.monotonic()
        if not samples and dest.exists():print(sid,"cached",flush=True);continue
        if samples:
            sample_s={"s1":[.65,5.5,12.7],"s2":[4.1,13.8],"s3":[3.1,10.9,15,27.8,32,37.9],"cta1":[5.4],"s4":[11.8,17.7,25],"s5":[4,15],"s6":[6.8,17],"s7":[5,13],"s8":[6,18],"s9":[12.8,16.8,30,37],"s10":[8.4,20,29,36.7,43],"s11":[6,15],"s12":[5,15]}[sid]
            indices=[min(frames-1,round(s*30)) for s in sample_s]
        else:
            tmp=out/(sid+".working.mp4");container=av.open(str(tmp),"w")
            stream=container.add_stream("libx264",rate=30);stream.width=W;stream.height=H;stream.pix_fmt="yuv420p"
            stream.options={"crf":"17","preset":"veryfast","threads":"4","x264-params":"colorprim=bt709:transfer=bt709:colormatrix=bt709"}
            indices=range(frames)
        for f in indices:
            c.save();funcs[sid](c,f/30)
            if sid=="s12" and f>frames-18:rect(c,0,0,W,H,"#05090c",smooth((f-frames+18)/17))
            c.restore()
            if samples:
                Image.frombytes("RGB",(W,H),buf.tobytes(),"raw","BGRX").resize((960,540),Image.Resampling.LANCZOS).save(checks/f"{sid}-{f:04d}.jpg",quality=90)
            else:
                frame=av.VideoFrame.from_ndarray(buf,format="bgra").reformat(format="yuv420p",dst_colorspace="ITU709")
                for packet in stream.encode(frame):container.mux(packet)
        if not samples:
            for packet in stream.encode():container.mux(packet)
            container.close();os.replace(tmp,dest)
        print(sid,len(indices),"sampled" if samples else "encoded",round(time.monotonic()-start,1),"seconds",flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("ids",nargs="+");p.add_argument("--samples",action="store_true")
    a=p.parse_args();render(a.ids,a.samples)
