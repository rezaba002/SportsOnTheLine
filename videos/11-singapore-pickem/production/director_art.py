"""Local Skia art department. Coordinates are authored at 1920x1080."""
import math
import random
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageEnhance
from director_inputs import CUT, PUBLIC, WORK, read

sys.path.insert(0, str(WORK/"render-tools"))
import skia as sk

W,H=1920,1080
INK="#10191f"; PAPER="#ecebdc"; WHITE="#f9f7ed"; LIME="#e3fb51"; ICE="#86e4ea"
CORAL="#ff8a77"; GRAY="#a9b9bb"; LINE="#40545a"; PURPLE="#d3b9f0"
TEAMS=read(PUBLIC/"logos/logos.json")
SHORT={"Ninjas in Pyjamas":"NiP","Chinggis Warriors":"Chinggis","100 Thieves":"100 Thieves"}


def clamp(v): return max(0.,min(1.,v))
def ease(v): return 1-(1-clamp(v))**3
def smooth(v):
    v=clamp(v);return v*v*(3-2*v)
def mix(a,b,t):return a+(b-a)*t
def color(col,a=1):
    return (round(255*clamp(a))<<24)|int(col.lstrip("#"),16)
def pen(col,a=1,w=0):
    p=sk.Paint(Color=color(col,a),AntiAlias=True)
    if w:p.setStyle(sk.Paint.kStroke_Style);p.setStrokeWidth(w)
    return p
def rect(c,x,y,w,h,col,a=1,r=0,stroke=0):
    if w<=0 or h<=0 or a<=0:return
    b=sk.Rect.MakeXYWH(x,y,w,h);p=pen(col,a,stroke)
    if r:c.drawRoundRect(b,r,r,p)
    else:c.drawRect(b,p)
def line(c,x,y,xx,yy,col,a=1,w=2):c.drawLine(x,y,xx,yy,pen(col,a,w))
def dot(c,x,y,r,col,a=1,stroke=0):
    if r>0:c.drawCircle(x,y,r,pen(col,a,stroke))
def path(c,pts,col,a=1,w=0,close=False):
    if not pts:return
    p=sk.Path();p.moveTo(*pts[0])
    for q in pts[1:]:p.lineTo(*q)
    if close:p.close()
    c.drawPath(p,pen(col,a,w))
def grad(c,x,y,w,h,col1,col2,a1=1,a2=1,vertical=False):
    p=sk.Paint();p.setShader(sk.GradientShader.MakeLinear([(x,y),(x if vertical else x+w,y+h if vertical else y)], [color(col1,a1),color(col2,a2)]))
    c.drawRect(sk.Rect.MakeXYWH(x,y,w,h),p)

@lru_cache(None)
def face(style):
    if style=="mono":return sk.Typeface.MakeFromName("Consolas",sk.FontStyle.Normal())
    return sk.Typeface.MakeFromName("Bahnschrift",sk.FontStyle.Bold() if style!="reg" else sk.FontStyle.Normal())
@lru_cache(512)
def font(size,style):
    f=sk.Font(face(style),size);f.setSubpixel(True)
    f.setScaleX(.79 if style=="display" else .92 if style=="bold" else 1)
    return f
def text(c,s,x,y,size,col=WHITE,style="bold",a=1,align="left",maxw=0):
    if a<=0:return
    f=font(size,style);s=str(s);width=f.measureText(s)
    scale=min(1,maxw/max(1,width)) if maxw else 1
    c.save();c.translate(x,y);c.scale(scale,1)
    c.drawString(s,-width/2 if align=="center" else -width if align=="right" else 0,0,f,pen(col,a));c.restore()
def tag(c,s,x,y,col=LIME,ink=INK):
    w=font(24,"mono").measureText(s)+38
    rect(c,x,y-32,w,43,col,r=2);text(c,s,x+19,y-2,24,ink,"mono")
def slug(c,s,x,y,col=GRAY):
    line(c,x,y-8,x+40,y-8,col,1,3);text(c,s,x+55,y,26,col,"mono")

SAM=sk.SamplingOptions(sk.FilterMode.kLinear)
def img(c,im,x,y,w,h,a=1):
    if a>0:c.drawImageRect(im,sk.Rect.MakeXYWH(x,y,w,h),SAM,pen(WHITE,a))
def as_image(arr):
    return sk.Image.fromarray(np.ascontiguousarray(arr),colorType=sk.ColorType.kRGBA_8888_ColorType,copy=True)
@lru_cache(45)
def raster(p):
    return as_image(np.array(Image.open(p).convert("RGBA")))
@lru_cache(20)
def logo_im(team):
    p=PUBLIC/TEAMS[team]["file"]
    im=Image.open(p).convert("RGBA"); b=im.getbbox()
    if b:im=im.crop(b)
    return as_image(np.asarray(im))
def logo(c,team,x,y,size,a=1):
    im=logo_im(team);r=min(size/im.width(),size/im.height())
    img(c,im,x-im.width()*r/2,y-im.height()*r/2,im.width()*r,im.height()*r,a)
@lru_cache(12)
def texture(kind):
    y,x=np.mgrid[0:H,0:W];rng=np.random.default_rng(111)
    noise=rng.normal(0,1.35,(H,W))
    if kind=="paper":
        v=1-.072*(x/W)-.043*(y/H)
        base=np.array([244,242,224]);arr=v[:,:,None]*base+noise[:,:,None]
    else:
        val=18*np.exp(-((x-1350)/860)**2-((y-330)/670)**2)+6*np.exp(-((x-230)/820)**2-((y-630)/540)**2)
        arr=np.array([7,13,17])+val[:,:,None]*np.array([.53,.85,.94])+noise[:,:,None]*.78
    return as_image(np.dstack([np.clip(arr,0,255).astype('uint8'),np.full((H,W),255,np.uint8)]))
def base(c,paper=False):
    c.drawImage(texture("paper" if paper else "dark"),0,0)
@lru_cache(16)
def photo_image(key):
    im=Image.open(CUT/"photos"/(key+".jpg")).convert("RGB")
    # Retain recognisable event lighting while controlling saturation and contrast.
    im=ImageEnhance.Color(im).enhance(.76)
    im=ImageEnhance.Contrast(im).enhance(1.12)
    return as_image(np.asarray(im.convert("RGBA")))
def photo(c,key,t,pan=.5,shade=.38,box=(0,0,W,H)):
    im=photo_image(key);x,y,w,h=box
    c.save();c.clipRect(sk.Rect.MakeXYWH(x,y,w,h))
    zoom=1.055+.005*min(t,14);sc=max(w/im.width(),h/im.height())*zoom
    wi,hi=im.width()*sc,im.height()*sc
    img(c,im,x-(wi-w)*(pan+.035*math.sin(t*.18)),y-(hi-h)*.47,wi,hi)
    grad(c,x,y,w,h,"#050b10","#071218",.85,shade)
    grad(c,x,y+h*.60,w,h*.40,"#071017","#071017",0,.66,True)
    c.restore()
def barcode(c,x,y,w,h,ink=INK):
    rng=random.Random(267);pos=0
    while pos<w:
        b=rng.choice([2,3,4,6,9]);rect(c,x+pos,y,min(w-pos,b),h,ink);pos+=b+rng.choice([2,3,6])
def rule(c,x,y,w,col):
    for i in range(0,int(w),18):line(c,x+i,y,x+min(i+8,w),y,col,.55,2)

def ticket(c,x,y,scale,rot,label,value,sub,accent=LIME,serial="SGP / 001",teams=(),shine=0):
    """A physical match ticket: die-cut shoulders, serial stub, foil security lines."""
    c.save();c.translate(x,y);c.rotate(rot);c.scale(scale,scale)
    w,h=680,366
    # Offset stepped shadow is deliberate print depth, not a soft UI card.
    rect(c,-w/2+11,-h/2+17,w,h,"#03090b",.66,9)
    p=sk.Path();p.addRoundRect(sk.Rect.MakeXYWH(-340,-183,680,366),8,8)
    for yy in [-183,183]:
        hole=sk.Path();hole.addCircle(192,yy,18);p=sk.Op(p,hole,sk.PathOp.kDifference_PathOp)
    c.save();c.clipPath(p,True)
    img(c,texture("paper"),-340,-183,680,366);rect(c,192,-183,148,366,accent)
    for i in range(25):
        c.drawOval(sk.Rect.MakeXYWH(-452+i*6,-292+i*3,750,650),pen("#62716e",.13,1))
    grad(c,-380+shine*860,-183,110,366,WHITE,WHITE,0,.24)
    text(c,label,-303,-114,25,INK,"mono",maxw=458)
    text(c,value,-306,30,100 if len(value)<8 else 76,INK,"display",maxw=462)
    line(c,-302,65,155,65,INK,.52)
    text(c,sub,-301,116,27,INK,"bold",maxw=450)
    if teams:
        for i,team in enumerate(teams[:3]):logo(c,team,252,(-83+i*83),65)
    else:
        c.save();c.translate(266,83);c.rotate(-90);barcode(c,0,-30,188,59);c.restore()
    c.save();c.translate(312,147);c.rotate(-90);text(c,serial,0,0,19,INK,"mono");c.restore()
    for k in range(-159,162,19):line(c,192,k,192,k+7,INK,.6,2)
    c.restore();c.drawPath(p,pen(WHITE,.65,1.6));c.restore()

def reveal(c,age,x,y,lines,size=125,col=WHITE,step=.12):
    for i,s in enumerate(lines):
        p=ease((age-i*step)/.51)
        c.save();c.clipRect(sk.Rect.MakeXYWH(x-8,y+i*size*.94-size,1770,size*1.11))
        text(c,s,x,y+i*size*.94+(1-p)*size,size,col,"display",p)
        c.restore()
def circle_meter(c,x,y,r,p,animate,col):
    c.drawArc(sk.Rect.MakeXYWH(x-r,y-r,2*r,2*r),-90,359.95,False,pen(LINE,.6,17))
    c.drawArc(sk.Rect.MakeXYWH(x-r,y-r,2*r,2*r),-90,360*p*animate,False,pen(col,1,17))
    for i in range(60):
        a=i*math.tau/60-math.pi/2
        line(c,x+math.cos(a)*(r+17),y+math.sin(a)*(r+17),x+math.cos(a)*(r+(34 if i%5==0 else 24)),y+math.sin(a)*(r+(34 if i%5==0 else 24)),GRAY,.65,2)
