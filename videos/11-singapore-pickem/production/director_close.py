from director_open import *

OPTS={"s5":("3-0","THE CEILING",LIME),"s6":("3-1","THE ENGINE ROOM",ICE),
      "s7":("3-2","THE NARROW BAND",PURPLE),"s8":("0-3","THE FLOOR",CORAL)}
MODEL=DATA["tickets"]["model"];EYE=DATA["tickets"]["eye"]

def charts(c,t,sid):
    record,name,col=OPTS[sid];rows=sorted([(team,ps[record]) for team,ps in PROBS.items()],key=lambda el:-el[1])
    top,v=rows[0];light=sid=="s6";base(c,light)
    fg=INK if light else WHITE;mut="#46575a" if light else GRAY
    accent="#24686d" if light else col
    at=lambda w:cue(sid,w)
    tag(c,"EXACT FINISH   /   "+record.replace("-","–"),95,140,INK if light else col,WHITE if light else INK)
    if sid=="s5":split=at("After");hero,sub=pct(v),top;closing="8 TEAMS";caption="below a 10% sweep chance"
    elif sid=="s6":split=at("band");hero,sub=pct(v),top;closing="20.5–26.5%";caption="FaZe through PARIVISION"
    elif sid=="s7":split=at("bottom");hero,sub="4.3 PTS","between first and tenth";closing="6.9–17.9%";caption="the bottom six teams"
    else:split=at("notice");hero,sub=pct(v),top;closing=pct(1-v);caption="Chinggis avoid the sweep"
    # A portrait first; pull back to the ranking when the narration widens.
    portrait=ease((t+.1)/.6);fall=smooth((t-split)/.7)
    text(c,name,99,249,47,mut,"display",portrait)
    if sid!="s7":
        logo(c,top,299,415,174*(1-fall*.23),portrait)
    else:
        for j in range(4):
            p=ease((t-j*.090)/.5);logo(c,rows[j][0],156+j*99,419+(1-p)*33,75,p)
    text(c,hero,94,630,142 if len(hero)<8 else 110,fg,"display",1-fall,maxw=530)
    text(c,sub,104,708,39,mut,"reg",1-fall,maxw=515)
    text(c,closing,94,630+(1-fall)*32,105 if len(closing)>7 else 137,accent,"display",fall,maxw=540)
    text(c,caption,104,704,38,fg,"reg",fall,maxw=525)
    if sid=="s5" and t>at("Imperial"):text(c,"Only two are below 5%.",105,785,34,mut,"reg",ease((t-at("Imperial"))/.5))
    if sid=="s8":
        rect(c,105,764,460*fall,15,LINE);rect(c,105,764,460*v*fall,15,CORAL)
    # Indexed score strip: endpoints use one 0–40% scale across every outcome.
    x0=1082;scale=1480;y0=176;dy=46
    muted_grid=INK if light else GRAY
    for j in range(5):
        x=x0+j*.1*scale;line(c,x,y0-33,x,y0+15*dy+22,muted_grid,.17)
        text(c,str(j*10)+"%",x,y0+15*dy+64,23,mut,"mono",align="center")
    if sid=="s7" and t>at("between"):
        p=ease((t-at("between"))/.6);left=x0+rows[9][1]*scale;right=x0+v*scale
        rect(c,left,y0-21,(right-left)*p,dy*9+39,PURPLE,.14);line(c,right,y0-21,right,y0+9*dy+16,PURPLE,p*.67)
    if sid=="s6" and t>split:
        rect(c,x0+rows[6][1]*scale,y0+2*dy-19,(rows[2][1]-rows[6][1])*scale*fall,dy*4+36,accent,.15)
    for i,(team,prob) in enumerate(rows):
        if sid=="s5":start=([at("One"),at("Ninjas"),at("Heroic")]+[at("follow")+.08*k for k in range(5)]+[split+.078*k for k in range(8)])[i]
        elif sid=="s6":start=([at("strong"),at("Ninjas")]+[at("band")+.11*k for k in range(14)])[i]
        elif sid=="s7":start=(at("look")+.08*i if i<10 else split+.1*(i-10))
        else:start=([at("floor"),at("Imperial"),at("Lynn")]+[at("These")+.085*k for k in range(13)])[i]
        p=ease((t-start+.09)/.47);y=y0+i*dy
        if p<=0:continue
        text(c,f"{i+1:02d}",686,y+8,22,mut,"mono",p)
        logo(c,team,760,y,34,p);text(c,SHORT.get(team,team),796,y+11,31,fg,"bold",p,maxw=266)
        rect(c,x0,y-7,scale*prob*p,14,accent if i<(10 if sid=="s7" else 3) else mut, p*(1 if i<3 else .71),2)
        text(c,pct(prob),x0+scale*prob+14,y+10,27,fg,"bold",p)
    text(c,"MODEL ESTIMATE   /   100,000 SIMULATED STAGES",686,989,24,mut,"mono")

def board(c,t,eye=False):
    base(c);sid="s10" if eye else "s9";accent=ICE if eye else LIME
    slug(c,"PICK’EM   /   STAGE 1",97,116,accent)
    text(c,"THE EYE TEST" if eye else "THE MODEL’S TICKET",93,245,111,WHITE,"display")
    groups=["3-0","0-3","advance"]
    basepos={}
    for j,g in enumerate(groups):
        y=[356,540,749][j];lab=["SWEEP","SWEPT","ADVANCE"][j]
        text(c,lab,100,y+43,46,accent,"display");text(c,["3–0","0–3","3–1 / 3–2"][j],101,y+88,29,GRAY,"mono")
        for i,team in enumerate(MODEL["picks"][g]):
            x=425+i*235
            basepos[team]=(x,y,g)
            rect(c,x-8,y-19,216,136,"#1c2a30",1,4);line(c,x+1,y+120,x+199,y+120,accent,.28)
    # Actual team motion: NiP and HEROIC cross arcs, then 9z replaces DENDELE.
    sw=smooth((t-cue(sid,"Ninjas"))/1.1) if eye else 0
    rep=smooth((t-cue(sid,"out"))/.9) if eye else 0
    spoken=["one","Heroic","Ching-giss","Imperial","Paree-vision","Eternal","Ninjas","Liquid","Den-deh-leh","Faze"]
    for idx,(team,(x,y,g)) in enumerate(basepos.items()):
        a=1 if eye else ease((t-cue(sid,spoken[idx])+.14)/.37)
        if not a:continue
        if eye and team in ["Ninjas in Pyjamas","HEROIC"]:
            other="HEROIC" if team=="Ninjas in Pyjamas" else "Ninjas in Pyjamas"
            xx,yy,ng=basepos[other];x=mix(x,xx,sw);y=mix(y,yy,sw)+(1 if team=="HEROIC" else -1)*67*math.sin(sw*math.pi)
            if sw>.5:g=ng
        if eye and team=="DENDELE" and rep:
            if rep<.5:a=1-rep*2;y-=rep*68
            else:team="9z";a=(rep-.5)*2;y+=36*(1-a)
        y+=(1-a)*35
        p=PROBS[team];prob=p[g] if g!="advance" else p["3-1"]+p["3-2"]
        logo(c,team,x+45,y+40,64,a);text(c,pct(prob),x+91,y+52,33,accent,"bold",a)
        text(c,SHORT.get(team,team),x+4,y+100,29,WHITE,"bold",a,maxw=191)
    text(c,"Percentages are the chance of scoring that exact slot.",101,991,30,GRAY,"reg")
    if eye and t>cue(sid,"higher"):
        tag(c,"NiP TO SWEEP   /   HEROIC TO ADVANCE",1031,233,ICE)
    elif not eye and t>cue(sid,"data"):tag(c,"10 PICKS   /   5 NEEDED",1230,224,LIME)

def model_ticket(c,t):
    sid="s9";at=lambda w:cue(sid,w)
    if t<at("Run"):board(c,t);return
    if t<at("lazy"):
        base(c,True);a=t-at("Run");tag(c,"EVALUATION   /   70,000 HELD-OUT DRAWS",102,156,INK,PAPER)
        ticket(c,565,540,1.22,-7+2*ease(a/3),"MODEL TICKET","5+ PICKS","Stage-completion threshold",LIME,teams=["100 Thieves","HEROIC"],shine=clamp(a/4))
        p=ease((t-at("five"))/.55);text(c,"31.9%",1060,584+(1-p)*45,179,INK,"display",p)
        text(c,"chance of completion",1070,676,47,INK,"reg",p)
        text(c,"95% MC interval: 31.5–32.2%",1070,760,31,INK,"mono",p)
    else:
        base(c);a=t-at("lazy");slug(c,"ONE MODEL   /   SAME 70,000 DRAWS",105,176,LIME)
        reveal(c,a+.1,102,398,["HOW MUCH DID THE SEARCH ADD?"],94)
        old=at("November");ev=MODEL["evaluation"];rows=[("SEARCHED TICKET",ev,LIME,0),("FAVORITE PER SLOT",MODEL["naive"],ICE,at("favorite")-at("lazy")),("NOV 5 TICKET",MODEL["nov5"],GRAY,old-at("lazy"))]
        for i,(label,e,col,start) in enumerate(rows):
            y=523+i*119;p=ease((a-start+.12)/.72);v=e["p_5_or_more"]
            text(c,label,109,y+11,32,col,"mono",p)
            rect(c,570,y-14,950*v/.40*p,27,col,p,2)
            text(c,pct(v),570+950*v/.4+25,y+17,43,WHITE,"bold",p)
        text(c,"Stage completion probability   /   not real-world accuracy",107,956,32,GRAY,"reg")

def eye_ticket(c,t):
    sid="s10";at=lambda w:cue(sid,w)
    if t<at("swings"):board(c,t,True);return
    if t<at("What"):
        base(c,True);slug(c,"THE ONE REPLACEMENT",102,147,INK)
        for i,(team,op,col,ser) in enumerate([("DENDELE","PARIVISION",CORAL,"OUT"),("9z","Lynn Vision",LIME,"IN")]):
            x=495+i*925;begin=0 if i==0 else cue("s10","Nine",2)
            p=ease((t-begin+.14)/.5)
            if p<=0:continue
            ticket(c,x,470+(1-p)*390,1.18,-4+i*7,ser+"   /   OPENING MATCH",team,"vs "+op,col,teams=[team,op],shine=clamp((t-at("swings"))/5))
            text(c,"48.9–57.3% to advance" if i==0 else "Lynn Vision: seed 16",x,816,46,INK,"bold",p,"center")
            text(c,"ACROSS MODEL SETTINGS" if i==0 else "OPENING OPPONENT",x,872,25,INK,"mono",p,"center")
    elif t<at("Lock"):
        base(c);a=t-at("What");slug(c,"PRICE OF THE EYE TEST   /   P(5+)",104,181,ICE)
        for i,(label,v,ci,col,p) in enumerate([("MODEL",MODEL["evaluation"]["p_5_or_more"],"31.5–32.2%",LIME,1),("MY TICKET",EYE["evaluation"]["p_5_or_more"],"28.5–29.2%",ICE,ease((t-at("becomes"))/.6))]):
            x=107+i*911;text(c,label,x,368,46,col,"mono",p)
            text(c,pct(v),x,621+(1-p)*45,193,WHITE,"display",p)
            text(c,"95% MC interval: "+ci,x,715,35,GRAY,"reg",p)
        if t>=at("About"):tag(c,"ABOUT 3 PERCENTAGE POINTS",108,892,ICE)
    else:
        base(c,True);a=t-at("Lock");tag(c,"COMMENT BELOW",105,191,INK,PAPER)
        reveal(c,a+.15,102,475,["LOCK YOUR","TEN PICKS."],150,INK)
        ticket(c,1400,529+(1-ease(a/.75))*340,1.1,8,"YOUR TICKET","YOUR 10","2 sweep  /  2 swept  /  6 advance",LIME,shine=clamp(a/3))
        text(c,"We’ll grade them after Stage 1.",108,814,53,INK,"reg")

def caveats(c,t):
    at=lambda w:cue("s11",w);base(c)
    if t<at("Keep"):
        slug(c,"FORECAST FREEZE",107,194,ICE)
        for i,(lab,val,start) in enumerate([("VALVE STANDINGS","02 NOV",0),("LAST MAP RESULT","15 NOV",at("Results"))]):
            a=ease((t-start+.13)/.6);x=107+i*904
            text(c,lab,x,364,34,ICE,"mono",a);text(c,val,x,620+(1-a)*50,163,WHITE,"display",a)
            line(c,x,730,x+699*a,730,ICE,a,4)
        return
    slug(c,"SAME TICKET   /   DIFFERENT RECENCY SETTINGS",103,161,ICE)
    reveal(c,t-at("Keep")+.18,102,351,["31.9–41.0%"],132)
    vals=DATA["sensitivity"];days=sorted(map(int,vals));x0=170;y0=818
    for i,day in enumerate(days):
        val=vals[str(day)];x=x0+i*305;a=ease((t-at("Keep")-i*.18)/.70);h=val/50*320*a
        rect(c,x,y0-h,145,h,LIME if day==21 else "#739da3",a)
        text(c,f"{val:.1f}%",x+73,y0-h-19,36,WHITE,"bold",a,"center")
        text(c,f"{day}d",x+73,y0+49,31,GRAY,"mono",a,"center")
    text(c,"Recency half-life   /   model sensitivity, not a confidence interval",106,981,32,GRAY,"reg")

def outro(c,t):
    photo(c,"bay",t,.46,.20)
    grad(c,0,0,W,H,INK,INK,.25,.12)
    slug(c,"SPORTS ON THE LINE   /   NEXT EPISODE",104,177,LIME)
    reveal(c,t+.12,100,447,["STAGE 2","PICK’EM."],144)
    text(c,"Updated results. Your tickets graded.",108,731,43,WHITE,"reg",ease((t-4.8)/.7))
    if t>cue("s12","Like")-.28:
        p=ease((t-cue("s12","Like")+.28)/.48)
        rect(c,103,798,388*p,84,LIME,r=3)
        text(c,"SUBSCRIBE",286,855,42,INK,"display",p,"center")
    # Clear right half for the YouTube end-screen video link.
