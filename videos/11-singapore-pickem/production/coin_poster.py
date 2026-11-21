"""Cinematic Coin or Bust artwork. Keep the first thumbnail untouched."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from coin_thumbnail import ART, EP, HF

W,H=1600,900
Y,X=np.mgrid[0:H,0:W].astype("float32")
SIZE=(W,H)


def halo(cx,cy,sx,sy):
    return np.exp(-((X-cx)/sx)**2-((Y-cy)/sy)**2)


def alpha(a):
    return Image.fromarray(np.uint8(255*np.clip(a,0,1)))


def light(canvas,tint,mask):
    lay=Image.new("RGB",SIZE,tint)
    canvas.paste(lay,(0,0),alpha(mask) if isinstance(mask,np.ndarray) else mask)


def type_art(s,width,height):
    f=ImageFont.truetype("C:/Windows/Fonts/impact.ttf",230)
    box=f.getbbox(s);w=box[2]-box[0];h=box[3]-box[1]
    a=Image.new("L",(w+6,h+6))
    ImageDraw.Draw(a).text((3-box[0],3-box[1]),s,font=f,fill=255)
    a=a.transform((w+50,h+6),Image.Transform.AFFINE,(1,.23,-.23*h,0,1,0),Image.Resampling.BICUBIC)
    return a.crop(a.getbbox()).resize((width,height),HF)


def title(canvas,s,x,y,w,h,c1,c2):
    a=type_art(s,w,h)
    mask=Image.new("L",SIZE);mask.paste(a,(x,y+13))
    light(canvas,"#010305",mask.filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.GaussianBlur(7)))
    mask=Image.new("L",SIZE);mask.paste(a,(x,y))
    light(canvas,"#070907",mask.filter(ImageFilter.MaxFilter(9)))
    ramp=np.uint8(np.asarray(c1)[None,:]+np.linspace(0.,1.,h)[:,None]*(np.asarray(c2)-np.asarray(c1)))
    ink=np.broadcast_to(ramp[:,None,:],(h,w,3)).copy()
    canvas.paste(Image.fromarray(ink),(x,y),a)


def artwork():
    rng=np.random.default_rng(219)
    warm=halo(1249,336,521,397)
    cyan=halo(418,282,490,418)
    rake=np.clip(.50+.27*np.sin((X+Y*1.14)*.009)+.11*np.cos((X+Y*1.7)*.041),0,1)
    fog=(.33+.40*rake+.23*np.sin(X*.007+Y*.011))*np.maximum(warm,cyan)
    noise=rng.normal(0,1.55,SIZE[::-1])
    image=np.dstack([6+warm*66+fog*15+noise,11+warm*30+cyan*54+fog*28+noise,18+warm*11+cyan*77+fog*20+noise])
    canvas=Image.fromarray(image.clip(0,255).astype("uint8"))
    skyline=ImageOps.fit(Image.open(ART/"photos/bay.jpg"),SIZE).convert("L").filter(ImageFilter.GaussianBlur(3.5))
    skyline=ImageOps.colorize(skyline,"#0a1016","#b08447")
    canvas.paste(skyline,(0,0),alpha(.31*halo(1120,554,665,260)))
    # Diagonal light spill and particulate; keep the face and the metal clean.
    light(canvas,"#ffba52",.17*np.exp(-((X+Y*1.38-1692)/41)**2)*warm)
    light(canvas,"#ffa936",.14*np.exp(-((X+Y*1.38-1780)/98)**2)*warm)
    light(canvas,"#6ce6ff",.29*np.exp(-((X+Y*.93-740)/44)**2)*cyan)
    d=ImageDraw.Draw(canvas)
    for _ in range(116):
        x=int(rng.uniform(85,1510)); y=int(rng.uniform(18,710))
        if rng.uniform()>warm[y,x]*.47+cyan[y,x]*.28:
            continue
        r=rng.uniform(.55,2.8);base=canvas.getpixel((x,y))
        k=rng.uniform(.24,.81); tint=(254,167,76) if x>760 else (127,229,225)
        fill=tuple(int(v+(c-v)*k) for v,c in zip(base,tint))
        if r>2.2:d.line((x-r*2.5,y+r*.75,x+r*2.5,y-r*.75),fill=fill,width=2)
        else:d.ellipse((x-r,y-r,x+r,y+r),fill=fill)

    agent=Image.open(ART/"phoenix-agent.png").convert("RGBA")
    agent=agent.crop(agent.getbbox()).resize((1039,1144),HF).rotate(8,Image.Resampling.BICUBIC,expand=True)
    agent=agent.crop(agent.getbbox())
    at=(-42,-50)
    matte=Image.new("L",SIZE);matte.paste(agent.getchannel("A"),at)
    # Directional rims blend with the two surrounding light sources.
    rim=np.asarray(matte.filter(ImageFilter.MaxFilter(13)),dtype=np.float32)/255
    light(canvas,"#79e5fa",rim*(.18+.28*halo(254,306,315,470)))
    light(canvas,"#ffd077",rim*.62*halo(730,250,345,470))
    source=Image.new("RGB",SIZE);source.paste(agent.convert("RGB"),at)
    v=np.asarray(source,dtype=np.float32)/255.
    teal=halo(238,314,381,617);amber=halo(739,306,280,490);key=halo(484,272,280,288)
    v=(v-.32)*1.19+.31
    v=v*np.dstack([.90+.30*amber+.17*key,.96+.22*teal+.10*key,.92+.27*teal+.07*key])
    v+=np.dstack([.15*amber+.055*key,.067*amber+.034*teal+.029*key,.053*teal+.012*key])
    canvas.paste(Image.fromarray(np.uint8(np.clip(v,0,1)*255)),(0,0),matte)

    light(canvas,"#ffad42",.28*halo(1212,364,415,375))
    # Exact Valve asset: no rotation, redrawing, relighting, or re-engraving.
    emblem=Image.open(ART/"singapore-2026-gold.png").convert("RGBA")
    emblem=emblem.crop(emblem.getbbox()).resize((599,599),HF)
    at=(876,33)
    shade=Image.new("L",SIZE);shade.paste(emblem.getchannel("A"),(at[0]-11,at[1]+31))
    light(canvas,"#160902",shade.filter(ImageFilter.GaussianBlur(17)).point(lambda v:int(v*.73)))
    # A glint behind the asset warms its silhouette without crossing the engraving.
    light(canvas,"#ffdb80",.72*halo(1408,137,84,31)+.22*halo(1408,137,15,74))

    # Roll off the detail behind the editorial headline, not behind the hero subjects.
    floor=np.clip((Y-562)/339,0,1)**1.28
    light(canvas,"#060808",.96*floor)
    canvas.paste(emblem,at,emblem)
    # Keep the simulation claim visually subordinate and make COIN the hook.
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((122,522,849,601),7,fill="#10171d",outline="#6f989e",width=2)
    d.rectangle((122,522,130,601),fill="#ffdc43")
    stat=ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf",42)
    stat.set_variation_by_axes([700,94])
    d.text((154,563),"STAGE 1 SIMULATED 100,000 TIMES",font=stat,fill="#fcf4db",anchor="lm")
    title(canvas,"COIN",120,632,880,208,(255,250,145),(255,189,21))
    title(canvas,"OR BUST",1027,711,449,103,(255,254,243),(216,221,208))

    output=EP/"final/thumbnail_E_singapore_coin.jpg"
    canvas.resize((1280,720),HF).save(output,quality=95,subsampling=0,optimize=True)
    canvas.resize((320,180),HF).save(ART/"singapore_coin_wording_mobile.jpg",quality=96)
    print(output)


if __name__=="__main__":
    artwork()
