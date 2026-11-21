"""Compose the Coin or Bust thumbnail from a Valve agent render and original coin art."""
from pathlib import Path
import math

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

EP = Path(__file__).resolve().parents[1]
ART = EP / "work/director"
SIZE = (1920, 1080)
FONT = Path("C:/Windows/Fonts/bahnschrift.ttf")
LIME = "#e3fb51"
PAPER = "#fcf7e7"
HF = Image.Resampling.LANCZOS


def font(size, bold=True, narrow=False):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_axes([700 if bold else 550, 80 if narrow else 100])
    return f


def headline(canvas, word, x, y, width, height, fill):
    f = font(260, narrow=True)
    b = f.getbbox(word, stroke_width=0)
    g = Image.new("L", (b[2]-b[0], b[3]-b[1]))
    ImageDraw.Draw(g).text((-b[0],-b[1]),word,font=f,fill=255)
    g = g.resize((width,height), HF)
    mask = Image.new("L", SIZE); mask.paste(g,(x,y))
    outline = mask.filter(ImageFilter.MaxFilter(13))
    canvas.paste("#080e16",(0,0),outline)
    canvas.paste(fill,(0,0),mask)


def coin():
    s=664; center=332
    gy,gx = np.mgrid[0:s,0:s]
    dx=(gx-center)/294; dy=(gy-center)/294
    angle=np.arctan2(dy,dx); r=np.hypot(dx,dy)
    gold=0.55+.2*np.cos(angle+1.7)+.16*np.cos(dx*7+dy*9)+.05*np.cos(r*155)
    gold+=np.random.default_rng(11).normal(0,.008,(s,s))
    rgb=np.stack([133+gold*137,73+gold*156,27+gold*150],2).clip(0,255).astype("uint8")
    alpha=np.uint8(np.clip((1.001-r)*294,0,1)*255)
    im=Image.fromarray(np.dstack([rgb,alpha])); d=ImageDraw.Draw(im)
    for rad, color, w in [(288,"#f8dc8f",4),(277,"#56320c",8),(266,"#f4c779",3),(232,"#7b4a18",4),(226,"#ffde88",2)]:
        d.ellipse((center-rad,center-rad,center+rad,center+rad),outline=color,width=w)
    for i in range(112):
        a=i*math.tau/112
        pts=[(center+math.cos(a)*k,center+math.sin(a)*k) for k in (243 if i%7 else 235,260)]
        d.line(pts,fill="#724718" if i%3 else "#ffdf94",width=3 if i%7 else 5)
    def stamp(s,y,n):
        f=font(n,narrow=True)
        d.text((center,y+2),s,font=f,anchor="mm",fill="#fbe2a0")
        d.text((center,y),s,font=f,anchor="mm",fill="#603812")
    stamp("PICK’EM",204,81)
    for i in range(5):
        x=242+i*45; y=288+abs(i-2)*7
        d.ellipse((x-8,y-8,x+8,y+8),fill="#815322",outline="#fce2a6",width=2)
    points=[(233,361),(305,427),(438,321)]
    d.line([(x,y+4) for x,y in points],fill="#ffdf8f",width=33,joint="curve")
    d.line(points,fill="#764619",width=28,joint="curve")
    stamp("MAJOR",488,40)
    lean=im.resize((572,664),HF).rotate(-17,Image.Resampling.BICUBIC,expand=True)
    a=lean.getchannel("A")
    rs=Image.new("RGBA",(lean.width+23,lean.height+20))
    for i in range(23,0,-1):
        tone=(round(122+47*(i%4)/3),round(73+35*(i%4)/3),28,255)
        rs.paste(tone,(i,i//2),a)
    rs.alpha_composite(lean)
    return rs.crop(rs.getbbox())


def create():
    w,h=SIZE; y,x=np.mgrid[0:h,0:w]
    glow=np.exp(-(((x-1530)/630)**2+((y-503)/480)**2))
    warm=np.exp(-(((x-1060)/260)**2+((y-650)/310)**2))
    grains=np.random.default_rng(88).normal(0,1.2,SIZE[::-1])
    bg=np.stack([9+12*glow+18*warm,16+45*glow+12*warm,28+47*glow+4*warm],2)+grains[:,:,None]
    canvas=Image.fromarray(bg.clip(0,255).astype("uint8")).convert("RGBA")
    photo=ImageOps.fit(Image.open(ART/"photos/bay.jpg"),SIZE).convert("L").filter(ImageFilter.GaussianBlur(4))
    city=ImageOps.colorize(photo,"#08101c","#28616d").convert("RGBA")
    city.putalpha(Image.fromarray((np.clip((x-670)/1100,0,1)*110).astype("uint8")))
    canvas.alpha_composite(city)
    design=ImageDraw.Draw(canvas)
    design.rounded_rectangle((101,143,651,217),radius=5,fill="#152a36",outline="#39606c",width=2)
    design.rectangle((101,143,112,217),fill=LIME)
    design.text((133,177),"SINGAPORE  /  STAGE 1",font=font(36,narrow=True),anchor="lm",fill="#ceebed")
    agent=Image.open(ART/"phoenix-agent.png").convert("RGBA")
    agent=agent.crop(agent.getbbox()).resize((900,991),HF)
    aa=agent.getchannel("A")
    graded=ImageEnhance.Contrast(agent.convert("RGB")).enhance(1.13)
    graded=ImageEnhance.Color(graded).enhance(.77)
    tone=Image.new("RGB",agent.size,"#459792")
    tone=Image.blend(graded,tone,.14).convert("RGBA");tone.putalpha(aa)
    at=(1127,91)
    edge=Image.new("L",SIZE);edge.paste(aa,(at[0]-3,at[1]-2))
    canvas.paste("#5ae3dd",(0,0),edge.filter(ImageFilter.GaussianBlur(29)).point(lambda i:int(i*.39)))
    canvas.paste("#7deade",(0,0),edge.filter(ImageFilter.MaxFilter(9)).point(lambda i:int(i*.58)))
    canvas.alpha_composite(tone,at)
    art=coin().resize((473,489),HF)
    coin_at=(895,512)
    shadow=Image.new("L",SIZE);shadow.paste(art.getchannel("A"),(coin_at[0]+13,coin_at[1]+22))
    canvas.paste("#04080e",(0,0),shadow.filter(ImageFilter.GaussianBlur(26)).point(lambda i:int(i*.68)))
    canvas.alpha_composite(art,coin_at)
    feet=Image.new("RGBA",SIZE);feet.putalpha(Image.fromarray(np.uint8(np.clip((y-984)/96,0,1)*150)))
    canvas.alpha_composite(feet)
    headline(canvas,"COIN OR",94,302,842,177,PAPER)
    headline(canvas,"BUST",90,521,791,263,LIME)
    dst=EP/"final/thumbnail_B_coin.jpg"
    canvas.convert("RGB").resize((1280,720),HF).save(dst,quality=94,subsampling=0,optimize=True)
    canvas.convert("RGB").resize((320,180),HF).save(ART/"coin_mobile.jpg",quality=94)
    print(dst)


if __name__ == "__main__":
    create()
