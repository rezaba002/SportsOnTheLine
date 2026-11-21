from collections import Counter
from datetime import date, timedelta
from functools import lru_cache
from director_art import *
from director_inputs import ROOT

TL=read(CUT/"edit.json"); DATA=TL["data"]
SC={s["id"]:s for s in TL["scenes"]}
FIELD=DATA["field"]
PROBS=DATA["probs"]

@lru_cache(None)
def cue(sid,word,n=0):
    norm=lambda s:''.join(ch for ch in s.casefold() if ch.isalnum())
    s=SC[sid];hits=[w for w in s["words"] if norm(w["w"])==norm(word)]
    if n>=len(hits):raise ValueError(f"Missing voice cue: {sid} / {word} / {n}")
    return hits[n]["s"]+s["leadFrames"]/30
def pct(v):return f"{100*v:.1f}%"
def archive(c,desc):
    rect(c,97,909, min(1200,54+font(23,"mono").measureText(desc)),47,INK,.87)
    text(c,desc,119,941,23,WHITE,"mono")
def mark(c,x,y,size,col=INK):
    path(c,[(x-size*.42,y),(x-size*.1,y+size*.32),(x+size*.45,y-size*.35)],col,1,max(3,size*.11))

def hook(c,t):
    if t<cue("s1","fails"):
        base(c)
        p=smooth((t-cue("s1","Ten")+.16)/.65)
        c.save();c.translate(1040+p*40,540);c.rotate(-7+p*4);c.scale(1+.012*t,1+.012*t)
        for i,team in enumerate(FIELD):
            row,col=divmod(i,4);pop=ease((t+.22-i*.028)/.38)
            x=150+col*193;y=-323+row*182
            rect(c,x-77,y-75+(1-pop)*42,154,148,"#2d4043",pop,6)
            line(c,x-72,y-71,x+70,y-71,ICE,.45*pop)
            logo(c,team,x,y+(1-pop)*42,94,pop)
        c.restore()
        slug(c,"SINGAPORE MAJOR   /   STAGE 1",104,214,ICE)
        if p<1:reveal(c,t+.12,100,600,["16 TEAMS."],179,WHITE)
        if p>0:
            rect(c,75,396,890,244,INK,p)
            reveal(c,t-cue("s1","Ten")+.14,100,600,["10 PICKS."],174,LIME)
            for i in range(10):rect(c,110+64*i,685,47,7,LIME,clamp((p*12-i)/2))
        return
    a=t-cue("s1","fails")
    if t<cue("s1","This"):
        base(c,True)
        c.save();c.rotate(-4,950,500)
        for i in range(3):
            x=345+i*610
            ticket(c,x,531+(1-ease((a+.08-i*.10)/.39))*360,.855,(i-1)*3,
                   "SIMULATED TICKET","PASS" if i==2 else "MISS","Illustrative 2-in-3 failure rate",
                   LIME if i==2 else CORAL,shine=clamp(a/2))
        c.restore()
        tag(c,"ABOUT 2 IN 3 FAIL",123,188,INK,WHITE)
        return
    b=t-cue("s1","This");photo(c,"sky",b,.66,.08)
    slug(c,"SINGAPORE   /   COUNTER-STRIKE 2",104,155,LIME)
    change=cue("s1","show")
    if t<change:
        reveal(c,b+.1,100,547,["STAGE 1","PICK’EM."],176)
    else:
        reveal(c,t-change+.18,100,505,["MODEL","VS. EYE TEST"],122)
        ticket(c,1374,536+12*math.sin(b*.46),1.11,-7+1.7*math.sin(b*.28),
               "MODEL  /  STAGE COMPLETION","31.9%","At least five correct",shine=clamp((t-change)/4))
    text(c,"RESULTS THROUGH 15 NOV 2026",107,946,27,WHITE,"mono")

@lru_cache(None)
def weeks():
    maps=read(ROOT/"video06/refresh_2026-11-16/dataset.json")["maps"];start=date(2026,5,3)
    counts=Counter((date.fromisoformat(m["date"])-start).days//7 for m in maps)
    assert sum(counts.values())==2619 and min(counts)>=0
    return [counts.get(i,0) for i in range(max(counts)+1)]
def data_scene(c,t):
    switch=cue("s2","paired")
    if t<switch:
        base(c,True);slug(c,"THE DATASET  /  INVITED-TEAM COHORT",104,146,INK)
        reveal(c,t+.2,99,495,[f"{round(2619*ease((t+.2)/2.2)):,}"],280,INK)
        text(c,"MATCH MAPS",111,606,86,INK,"display")
        vals=weeks();mx=max(vals)
        for i,v in enumerate(vals):
            p=ease((t-i*.055)/.60);h=224*v/mx*p
            rect(c,104+i*60.5,860-h,38,h,INK if i<24 else "#647432")
        line(c,99,862,1810,862,INK,.6)
        text(c,"03 MAY",104,916,29,INK,"mono");text(c,"MAPS PER WEEK",961,916,25,INK,"mono",align="center")
        text(c,"15 NOV",1812,916,29,INK,"mono",align="right")
        return
    b=t-switch;photo(c,"players",b,.63,.12)
    archive(c,"ARCHIVE  /  SK VS G2  ·  COLOGNE 2016")
    x=105
    if t<cue("s2","roster"):
        slug(c,"OFFICIAL STANDINGS",x,249,ICE);reveal(c,b+.13,x,571,["02 NOV"],170)
        text(c,"Valve ranking snapshot",x,678,54)
    else:
        slug(c,"EXPECTED FIVE  /  EXPERIENCE INPUT",x,230,ICE)
        reveal(c,t-cue("s2","roster")+.16,x,490,["432"],180)
        text(c,"career LAN maps per player, on average",x,567,43,WHITE,"reg")
        if t>=cue("s2","career")-.15:
            p=ease((t-cue("s2","career")+.15)/.55)
            text(c,"14",x,756+(1-p)*38,133,LIME,"display",p)
            text(c,"Major-title player credits",x+153,748,40,WHITE,"reg",p)

def method(c,t):
    base(c)
    if t<cue("s3","Each"):
        slug(c,"RECENCY  /  WEIGHT PER MAP",107,156,ICE)
        reveal(c,t+.23,101,482,["21 DAYS"],148)
        text(c,"Half the weight of a new result.",109,590,46,WHITE,"reg")
        x0,y0,x1,y1=910,794,1770,277
        line(c,x0,y0,x1,y0,GRAY,.8);line(c,x0,y0,x0,y1,GRAY,.8)
        for j in [0,21,42,63]:
            x=x0+(x1-x0)*j/63;text(c,f"{j}d",x,y0+48,27,GRAY,"mono",align="center")
        p=ease((t+.1)/2.5)
        pts=[(x0+(x1-x0)*i/126,y0-(y0-y1)*2**(-i/42)) for i in range(1+int(p*126))]
        path(c,pts,ICE,1,8)
        if t>cue("s3","half")-.14:
            xx=x0+(x1-x0)/3;yy=(y0+y1)/2;dot(c,xx,yy,13,LIME);text(c,"50%",xx+22,yy-24,49,LIME)
        return
    if t<cue("s3","Then"):
        loc=t-cue("s3","Each")
        slug(c,"RESULTS-ONLY MODEL",107,176,ICE)
        for i,(label,sub,word) in enumerate([("01","Valve prior","Each"),("02","Roster discount","Maps"),("03","Map-specific edge","map-specific")]):
            p=ease((t-cue("s3",word)+.08)/.50);x=108+i*583
            line(c,x,442,x+495*p,442,LIME,p,4)
            text(c,label,x,405,111,ICE,"display",p)
            text(c,sub,x,541+(1-p)*42,69,WHITE,"display",p,maxw=525)
        text(c,"A new roster inherits less of the old lineup’s evidence.",110,755,44,GRAY,"reg",ease((loc-3)/.5))
        return
    if t<cue("s3","twenty"):
        base(c,True);loc=t-cue("s3","Then");slug(c,"SIMULATING THE SWISS STAGE",110,159,INK)
        reveal(c,loc+.2,102,491,["THE VETO"],145,INK)
        for i,(x,txt,sub,word) in enumerate([(105,"BO1","Early matches","early"),(972,"BO3","Advance or go home","threes")]):
            p=ease((t-cue("s3",word)+.05)/.47);rect(c,x,574,805*p,7,INK)
            text(c,txt,x,787+(1-p)*34,137,INK,"display",p)
            text(c,sub,x,878,46,INK,"reg",p)
        return
    if t<cue("s3","tested"):
        b=t-cue("s3","twenty");slug(c,"HOLDOUT   /   NOV 09—15",105,147,ICE)
        x,y=489,528
        circle_meter(c,x,y,240,.70,ease((t-cue("s3","called")+.35)/.8),LIME)
        text(c,"14/20",x,y+28,125,WHITE,"display",ease((t-cue("s3","called")+.3)/.4),"center")
        text(c,"SERIES CORRECT",x,y+94,29,GRAY,"mono",align="center")
        for i,(label,val,word,col) in enumerate([("MODEL",.617,"log",ICE),("COIN FLIP",.693,"against",GRAY)]):
            p=ease((t-cue("s3",word)+.10)/.6);xx=912;yy=432+i*195
            text(c,label,xx,yy-20,34,WHITE,"mono",p);text(c,f"{val:.3f}",1760,yy-18,56,col,"bold",p,"right")
            rect(c,xx,yy+16,832,19,LINE,.72);rect(c,xx,yy+16,832*val/.75*p,19,col)
        text(c,"Log loss  /  lower is better",915,880,37,GRAY,"reg",ease((b-4)/.7))
        return
    loc=t-cue("s3","tested")
    movie=CUT/"photos/flusha"
    if loc<6.5 and (movie/"195.jpg").exists():
        im=raster(movie/f"{min(195,int(loc*30)+1):03}.jpg")
        sc=max(W/im.width(),H/im.height());img(c,im,(W-im.width()*sc)/2,(H-im.height()*sc)/2,im.width()*sc,im.height()*sc)
        grad(c,0,0,W,H,INK,INK,.87,.15);archive(c,"ARCHIVE  /  FLUSHA  ·  COLOGNE 2016")
    elif loc<6.5:
        photo(c,"arena",loc,.6,.15);archive(c,"ARCHIVE  /  IEM KATOWICE 2019")
    slug(c,"VALIDATION DECISION",108,211,ICE)
    if t<cue("s3","published"):
        reveal(c,loc+.08,104,498,["EXPERIENCE","ON TRIAL."],120)
    else:
        reveal(c,t-cue("s3","published")+.09,104,506,["BASELINE","RETAINED."],124,LIME)

def subscribe(c,t):
    photo(c,"crowd",t,.38,.12)
    archive(c,"ARCHIVE  /  IEM KATOWICE 2014")
    p=ease((t+.10)/.55);x=108
    slug(c,"SPORTS ON THE LINE   /   FIELD NOTES",x,146,LIME)
    reveal(c,t+.12,x,404,["FOLLOW THE","FORECAST."],124)
    rect(c,x,655,692*p,106,PAPER,r=4)
    if p>.7:
        img(c,raster(PUBLIC/"brand/logo.png"),x+12,666,83,83)
        text(c,"SportsOnTheLine",x+114,719,39,INK)
        clicked=t>=cue("cta1","subscribe")
        rect(c,x+431,679,235,59,LIME if clicked else INK,r=4)
        text(c,"SUBSCRIBED" if clicked else "SUBSCRIBE",x+548,719,27,INK if clicked else WHITE,"bold",align="center")
    if t>cue("cta1","Stage"):
        tag(c,"NEXT UP: STAGE 2",112,838,LIME)

def objective(c,t):
    base(c,True);s="s4";when=cue(s,"trap")
    if t<when:
        slug(c,"PICK’EM SCORING",104,151,INK)
        reveal(c,t+.15,100,388,["TEN SLOTS."],153,INK)
        for j,(n,lab,x,w,word,nn) in enumerate([(2,"SWEEP  /  3–0",110,360,"two",0),(2,"SWEPT  /  0–3",574,360,"two",1),(6,"ADVANCE  /  3–1 OR 3–2",1042,745,"six",0)]):
            p=ease((t-cue(s,word,nn)+.15)/.50)
            text(c,lab,x,551,32,INK,"mono",p)
            for k in range(n):
                xx=x+k*(w/n);r=clamp((p*1.4-k*.06))
                rect(c,xx,590+(1-r)*30,w/n-16,104,INK,r,3)
                if t>cue(s,"Five") and (j==0 or j==2 and k<3):mark(c,xx+(w/n-16)/2,641,43,LIME)
        if t>cue(s,"Five"):reveal(c,t-cue(s,"Five")+.12,108,887,["5 CORRECT TO PASS"],75,INK)
    elif t<cue(s,"So"):
        base(c);a=t-when;slug(c,"THE SCORING TRAP",105,172,CORAL)
        ticket(c,515+ease(a/.85)*115,546,1.22,-8+ease(a/.85)*5,"TEAM FINISH","3–0","Placed in an advance slot",CORAL)
        if t>=cue(s,"sitting"):
            reveal(c,t-cue(s,"sitting")+.13,1120,555,["0 PTS"],158,CORAL)
            text(c,"A sweep misses this slot.",1130,662,40,WHITE,"reg")
    else:
        slug(c,"THE SEARCH OBJECTIVE",106,179,INK)
        a=t-cue(s,"So");reveal(c,a+.1,104,490,["CHANCE OF"],131,INK)
        p=ease((t-cue(s,"chance")+.22)/.65)
        rect(c,97,557,1645*p,219,INK)
        text(c,"FIVE OR MORE CORRECT.",119,726,125,LIME,"display",p,maxw=1590)
        text(c,"One ticket. One pass threshold.",110,899,41,INK,"reg",ease((t-cue(s,"number"))/.45))
