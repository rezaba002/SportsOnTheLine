import React from "react";
import {AbsoluteFill, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../theme";
import {teamLogo} from "../teams";
import {pct as formatPercent} from "./MotionScene";
import {Logo} from "../cards/parts";
import {ExperienceTrio} from './ExperienceTrio';
import media from '../../public/video10/footage-revision.json';
import timeline from "../../public/video10/final-timeline.json";
import {MouzMapMotion, MouzOddsMotion} from "./MouzMotionSamples";
import {VitalityScenarioMotion} from "./VitalityScenarioMotion";
import {Video10OpeningFinal} from "./EditorialSample";

export const FINAL_FILM_FRAMES=timeline.frames;
type Scene=typeof timeline.scenes[number];
const BG="#080e15", W="#f2f5f7", M="#a5b5c3", R="#ff5e64", G="#ffd34d", F="#a2e4a8", C="#56d7e1", P="#dca2ff";
const colors:Record<string,string>={MOUZ:R,Vitality:G,FURIA:F,Falcons:"#4cd4a0",Spirit:C};
const clamp={extrapolateLeft:"clamp",extrapolateRight:"clamp"} as const;
const t=(f:number,a:number,b:number,x=0,y=1)=>{const p=interpolate(f,[a,b],[0,1],clamp);return x+(y-x)*(p*p*(3-2*p));};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const ink:React.CSSProperties={fontWeight:700,letterSpacing:-5,lineHeight:.94,textShadow:'0 3px 0 #0009, 0 12px 28px #000a'};
const cue=(s:Scene,word:string,fallback:number,after=0)=>{
  const mark=s.words.find(w=>w.s>=after&&w.w.toLowerCase().replace(/[^a-z0-9]/g,"")===word.toLowerCase());
  return mark?Math.round(mark.s*30)+24:fallback*s.frames;
};
const Copy:React.FC<{f:number;at:number;until?:number;x?:number;y?:number;size?:number;color?:string;children:React.ReactNode}>=({f,at,until=1e6,x=130,y=135,size=140,color=W,children})=>{
  const p=t(f,at,at+24),out=t(f,until-20,until);
  return <div style={{...ink,position:"absolute",left:x,top:y,fontSize:size,color,opacity:p*(1-out),transform:`translateY(${(1-p)*45-out*25}px)`,clipPath:`inset(0 0 ${(1-p)*100}% 0)`}}>{children}</div>;
};
const Note:React.FC<{children:React.ReactNode;x?:number;y?:number;color?:string}>=({children,x=135,y=925,color=M})=><div style={{position:"absolute",left:x,top:y,fontSize:28,letterSpacing:1.5,color,lineHeight:1.3}}>{children}</div>;
const Plane:React.FC<{children:React.ReactNode;color?:string}>=({children,color=C})=><AbsoluteFill style={{background:BG,color:W,fontFamily:FONT,overflow:"hidden"}}>
  <AbsoluteFill style={{background:`radial-gradient(ellipse at 72% 38%,${color}10,transparent 64%)`}}/>{children}
</AbsoluteFill>;

const Film:React.FC<{file:string;label:string;box?:boolean;right?:boolean;cut?:boolean}>=({file,label,box=false,right=false,cut=false})=>{
  const f=useCurrentFrame(),p=t(f,0,22),q=t(f,88,108,1,0);
  return <AbsoluteFill style={{overflow:"hidden",opacity:Math.min(p,q),...(box?{left:right?1040:95,top:440,width:780,height:440,right:"auto",bottom:"auto",transform:`perspective(1800px) rotateY(${t(f,0,90,right?-7:7,0)}deg) translateY(${(1-p)*90}px)`,boxShadow:"0 30px 70px #0009"}:{}),clipPath:cut?`polygon(${mix(100,45,p)}% 0,100% 0,100% 100%,${mix(100,35,p)}% 100%)`:undefined}}>
    <OffthreadVideo src={staticFile(`video10/clips/${file}.mp4`)} muted style={{width:"100%",height:"100%",objectFit:"cover",transform:`scale(${t(f,0,108,1.045,1)})`}}/>
    {!box&&<AbsoluteFill style={{background:"linear-gradient(0deg,#080e15e8,transparent 65%)"}}/>}
    <div style={{position:"absolute",left:box?14:42,bottom:box?16:28,fontSize:box?21:24,background:"#06101bc9",padding:"6px 12px",color:W}}>{label}</div>
  </AbsoluteFill>;
};
const Clip:React.FC<{at:number;file:string;label:string;box?:boolean;right?:boolean;cut?:boolean}>=({at,...props})=><Sequence from={Math.round(at)} durationInFrames={108}><Film {...props}/></Sequence>;
const RevisionClip:React.FC<{at:number;slot:keyof typeof media.slots;box?:boolean;right?:boolean}>=({slot,...props})=>{
  const clip=media.slots[slot];return <Clip {...props} file={clip.file} label={clip.label}/>;
};
const CaseLogo:React.FC<{team:string}>=({team})=>{
  const f=useCurrentFrame(),appear=t(f,0,9),leave=t(f,30,48),scale=t(f,0,17,.63,1)+leave*.11;
  return <Plane color={colors[team]}><AbsoluteFill style={{justifyContent:'center',alignItems:'center',opacity:appear*(1-leave),transform:`scale(${scale})`,filter:`drop-shadow(0 18px 35px #000a)`}}><Img src={teamLogo(team)!} style={{width:700,height:700,objectFit:"contain"}}/></AbsoluteFill></Plane>;
};

const Method:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),recent=cue(s,"Recent",.27),sim=cue(s,"simulation",.4),assume=cue(s,"Then",.61);
  const fold=t(f,sim,sim+95),p=t(f,recent,recent+150);
  const path=Array.from({length:91},(_,i)=>`${200+i*16},${790-500*Math.pow(.5,(90-i)/21)}`).join(" ");
  return <Plane>
    <Copy f={f} at={5} until={sim+60} size={210}>2,619<span style={{fontSize:70,color:C}}> MAPS</span></Copy>
    <div style={{position:"absolute",left:140,top:365,fontSize:31,color:M,opacity:1-fold}}>RESULTS THROUGH 15 NOV 2026</div>
    <svg width="1920" height="1080" style={{position:"absolute",opacity:1-fold,transform:`translateY(${-fold*100}px)`}}>
      <line x1="200" y1="800" x2="1650" y2="800" stroke={M} strokeWidth="2"/>
      <polyline points={path} fill="none" stroke={C} strokeWidth="7" strokeDasharray="2100" strokeDashoffset={2100*(1-p)}/>
      {Array.from({length:75},(_,i)=>{const age=90-i*1.2,w=Math.pow(.5,age/21),appear=t(f,20+i*1.2,55+i*1.2);return <circle key={i} cx={200+i*19.2} cy={790-500*w} r={mix(10,4+11*w,p)} fill={C} opacity={appear*mix(1,.2+.8*w,p)}/>;})}
      <text x="195" y="855" fontSize="30" fill={M}>90 DAYS AGO</text><text x="1510" y="855" fontSize="30" fill={W}>LATEST</text>
    </svg>
    <Copy f={f} at={recent} until={sim+40} x={850} y={160} size={90} color={C}>21-DAY<br/>HALF-LIFE</Copy>
    {['STAGES','MAP VETOES','TITLE'].map((label,i)=>{
      const a=t(f,sim+i*25,sim+75+i*25),drift=t(f,assume,assume+90);
      return <div key={label} style={{position:"absolute",left:130+i*600,top:mix(510,270,drift),opacity:a,transform:`translateX(${(1-a)*140}px) scale(${mix(.8,1,a)})`}}><div style={{color:C,fontSize:38,letterSpacing:3}}>0{i+1}</div><div style={{...ink,fontSize:72,marginTop:25}}>{label}</div><div style={{width:490,height:6,background:C,marginTop:45,transform:`scaleX(${t(f,sim+40+i*30,sim+130+i*30)})`,transformOrigin:"left"}}/></div>;
    })}
    <Copy f={f} at={assume+35} y={565} size={128} color={P}>TEST THE<br/>ASSUMPTIONS.</Copy>
    <div style={{position:"absolute",left:130,top:890,width:1600,display:"flex",justifyContent:"space-between",opacity:t(f,assume+65,assume+100),color:M,fontSize:32}}><span>OBSERVED RESULTS</span><span>MODEL FORECAST</span><span style={{color:P}}>ASSUMED EFFECTS</span></div>
  </Plane>;
};

const Threats:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),sp=cue(s,"Spirit",.48),last=cue(s,"Their",.8),p=t(f,sp-20,sp+45);
  return <Plane color={C}>
    <div style={{position:"absolute",inset:0,transform:`translateX(${-p*1920}px)`}}>
      <RevisionClip at={0} slot="field_falcons"/>
      <div style={{position:"absolute",left:130,top:180,opacity:t(f,55,95)}}><Logo team="Falcons" size={220}/></div>
      <Copy f={f} at={30} y={580} size={146}>THE REIGNING<br/><span style={{color:colors.Falcons}}>CHAMPIONS.</span></Copy>
      <Img src={staticFile("video09-v4/players/m0NESY.webp")} style={{position:"absolute",height:950,right:70,bottom:-10,filter:"drop-shadow(-25px 10px 35px #0009)",transform:`translateY(${t(f,110,sp,50,0)}px)`,opacity:t(f,80,115)}}/>
      <Note>FALCONS 3–0 FURIA · COLOGNE FINAL</Note>
    </div>
    <div style={{position:"absolute",inset:0,transform:`translateX(${(1-p)*1920}px)`}}>
      <RevisionClip at={sp+30} slot="field_spirit"/>
      <Img src={staticFile("video09-v4/players/donk.webp")} style={{position:"absolute",height:970,left:60,bottom:0,filter:"drop-shadow(30px 0 40px #000b)",transform:`scale(${t(f,sp,sp+190,1.03,1)})`}}/>
      <div style={{position:"absolute",left:1000,top:100}}><Logo team="Spirit" size={120}/></div>
      <Copy f={f} at={sp} x={920} y={260} size={150} color={C}>DONK.</Copy>
      <Copy f={f} at={sp+65} until={last} x={930} y={640} size={65}>sh1ro. The whole team.</Copy>
      <div style={{position:"absolute",left:920,top:790,color:W,fontSize:55,opacity:t(f,sp+100,sp+125)*(1-t(f,last-25,last))}}>2–0 vs MOUZ <span style={{fontSize:25,color:M}}>HK SEMIFINAL</span></div>
      <RevisionClip at={last} slot="field_final" box right/>
    </div>
  </Plane>;
};

const Result:React.FC<{s:Scene;furia?:boolean}>=({s,furia=false})=>{
  const f=useCurrentFrame(),team=furia?"FURIA":"MOUZ",col=colors[team];
  const detail=Math.min(cue(s,"That",.43),s.frames*.24),test=cue(s,furia?"Their":"The",.7,furia?13:10);
  const a=t(f,detail,detail+80),exit=t(f,test,test+75);
  const scores=furia?[["ANCIENT",13,11],["DUST2",13,5],["MIRAGE",13,8]]:[["MIRAGE",13,5],["DUST2",13,6],["INFERNO",13,4]];
  return <Plane color={col}>
    <RevisionClip at={0} slot={furia?'furia_form':'mouz_form'}/>
    <Copy f={f} at={30} until={detail+65} y={430} size={260} color={col}>3–0</Copy>
    <Copy f={f} at={50} until={detail+65} y={730} size={62}>{furia?"HONG KONG FINAL":"BEIJING · NO MAPS DROPPED"}</Copy>
    <div style={{position:"absolute",inset:0,opacity:a*(1-exit),transform:`translateX(${(1-a)*160-exit*200}px)`}}>
      {scores.map(([map,w,l],i)=>{const show=t(f,detail+i*35,detail+110+i*35);return <div key={map} style={{position:"absolute",left:150,top:190+i*230,width:1580}}><div style={{...ink,fontSize:76,color:col}}>{map}</div><div style={{position:"absolute",left:600,top:-8,...ink,fontSize:100}}>{w}–{l}</div><div style={{position:"absolute",left:1050,top:10,width:500,height:26,background:"#273543"}}><div style={{height:26,width:500*Number(w)/13*show,background:col}}/><div style={{height:12,width:500*Number(l)/13*show,background:M,marginTop:10}}/></div></div>;})}
      <Note>{furia?"FURIA / SPIRIT":"MOUZ / THE MONGOLZ"} · FINAL MAP SCORES · BAR SCALE 0–13 ROUNDS</Note>
    </div>
    <RevisionClip at={Math.round(s.frames*.53)} slot={furia?'furia_form_inset':'mouz_form_inset'} box right/>
    <Copy f={f} at={test+80} x={130} y={160} size={furia?155:145} color={col}>{furia?<>THREE TROPHIES.<br/>FOUR EVENTS.</>:<>A WHOLE<br/>TOURNAMENT.</>}</Copy>
    <div style={{position:"absolute",left:160,top:620,display:"flex",gap:70,opacity:exit}}>{Array.from({length:furia?4:3},(_,i)=><div key={i} style={{width:furia?210:390,height:130,border:`2px solid ${furia&&i===3?M:col}`,background:furia&&i===3?"transparent":`${col}20`,transform:`translateY(${t(f,test+i*14,test+80+i*14,70,0)}px)`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:64,color:col}}>{furia?(i<3?"W":"—"):`${scores[i][1]}–${scores[i][2]}`}</div>)}</div>
    <div style={{opacity:exit}}><Note>{furia?"3 TITLES IN 4 EVENTS · UNORDERED TALLY":"BEIJING FINAL · MIRAGE / DUST2 / INFERNO"}</Note></div>
  </Plane>;
};

const Network:React.FC<{f:number;at:number;team:string;names:string[];broken?:boolean}>=({f,at,team,names,broken=false})=>{
  const col=colors[team], p=t(f,at,at+150),shift=t(f,at+160,at+310),points=names.map((_,i)=>team==='Vitality'?[960+Math.cos(-Math.PI/2+i*Math.PI*.4)*345,575+Math.sin(-Math.PI/2+i*Math.PI*.4)*260]:team==='FURIA'?[290,285+i*150]:[270+i*340,540+(i%2?90:-40)]);
  return <><svg width="1920" height="1080" style={{position:"absolute"}}>
    {(team==='MOUZ'?points.slice(1):points).map(([x,y],i)=>{const [px,py]=points[Math.max(0,i)];const path=team==='Vitality'?`M ${x} ${y} Q ${mix(x,960,.5)} ${y+shift*45} 960 575`:team==='FURIA'?`M ${x+70} ${y} C 720 ${y},720 570,1000 570`:`M ${px} ${py} Q ${(x+px)/2} ${y-180-shift*60} ${x} ${y}`;return <path key={i} d={path} fill="none" stroke={col} strokeWidth="5" pathLength="1" strokeDasharray={broken&&i===1?".03 .02":"1"} strokeDashoffset={1-t(f,at+i*24,at+150+i*24)} opacity={.25+.65*p}/>;})}
    {team==='Vitality'&&<g opacity={p}><circle cx="960" cy="575" r="90" fill={BG} stroke={G} strokeWidth="3"/><text x="960" y="585" fontSize="28" fill={G} textAnchor="middle">COORDINATE</text></g>}
    {team==='FURIA'&&<g opacity={p}><path d="M1000 570 C1200 570,1300 570,1580 570" fill="none" stroke={F} strokeWidth="16" pathLength="1" strokeDasharray="1" strokeDashoffset={1-t(f,at+100,at+300)}/><circle cx="1640" cy="570" r="75" fill={BG} stroke={F} strokeWidth="3"/><text x="1640" y="580" fontSize="32" fill={F} textAnchor="middle">FINISH</text></g>}
    {points.map(([x,y],i)=><g key={i} opacity={t(f,at+i*12,at+50+i*12)}><circle cx={x} cy={y} r={68} fill="#0c1b25" stroke={col} strokeWidth="3"/><circle cx={x} cy={y} r={team==='FURIA'?72:80+22*t(f,at+70+i*30,at+170+i*30)} fill="none" stroke={col} opacity={.15}/><text x={x} y={y+10} textAnchor="middle" fill={W} fontSize="29">{names[i]}</text></g>)}
  </svg><Note y={team==='FURIA'?1005:925}>ILLUSTRATIVE TEAMPLAY · NO POSITION OR CALLING METRIC</Note></>;
};

const Test:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),team=s.chapter,col=colors[team],vit=team==="Vitality",furia=team==="FURIA";
  const first=cue(s,vit?"There":"PR",.22),next=cue(s,vit?"So":furia?"In":"That",.43),network=cue(s,vit?"The":furia?"whether":"Watch",.68,vit?15:furia?13:15);
  const names=vit?["apEX","ZywOo","flameZ","mezii","ropz"]:furia?["FalleN","KSCERATO","yuurih","YEKINDAR","molodoy"]:["xertioN","Spinx","torzsi","PR","xelex"];
  return <Plane color={col}>
    <RevisionClip at={0} slot={vit?'vitality_test':furia?'furia_test':'mouz_test'}/>
    <Copy f={f} at={30} until={next+30} y={220} size={130} color={col}>{vit?<>FULL FIVE.<br/>CURRENT PROBLEMS.</>:furia?<>THE FINAL<br/>IS STILL THE TEST.</>:<>BEIJING IS<br/>THE STANDARD.</>}</Copy>
    <Copy f={f} at={first} until={next+45} y={650} size={vit?155:105}>{vit?"3–4":furia?"FALCONS 3–0 FURIA":"SPIRIT 2–0 MOUZ"}</Copy>
    <div style={{position:"absolute",left:140,top:855,fontSize:31,color:M,opacity:t(f,first,first+30)*(1-t(f,next,next+30))}}>{vit?"HONG KONG · FULL ROSTER MAP RECORD":furia?"COLOGNE MAJOR FINAL":"HONG KONG SEMIFINAL"}</div>
    <div style={{position:"absolute",inset:0,opacity:t(f,first,first+20)*(1-t(f,next,next+35))}}>
      {Array.from({length:vit?7:furia?3:2},(_,i)=>{
        const show=t(f,first+i*14,first+70+i*14),win=vit&&i<3;
        const x=vit?1080+i%4*170:furia?1270+i*190:1030+i*230,y=vit?530+Math.floor(i/4)*150:620;
        return <div key={i} style={{position:'absolute',left:x,top:y,width:vit?115:155,height:115,color:win?G:R,border:`2px solid ${win?G:R}`,background:`linear-gradient(140deg,${win?G:R}28,transparent)`,transform:`perspective(700px) rotateY(${(1-show)*80}deg) translateY(${(1-show)*110}px)`,opacity:show,display:'flex',alignItems:'center',justifyContent:'center',fontSize:65,fontWeight:700}}>{win?'W':'L'}</div>;
      })}
      <div style={{position:'absolute',left:1080,top:vit?855:795,fontSize:25,color:M}}>{vit?'7 MAPS · UNORDERED W–L TALLY':furia?'THREE MAP LOSSES · COLOGNE FINAL':'TWO MAP LOSSES · HONG KONG SEMIFINAL'}</div>
    </div>
    <Copy f={f} at={next+20} until={network} y={140} size={150}>{vit?<>HISTORY HAS TO<br/><span style={{color:col}}>PLAY TODAY.</span></>:furia?<>CONTEND.<br/><span style={{color:col}}>THEN COMPLETE.</span></>:<>FIND THE<br/><span style={{color:col}}>NEXT ANSWER.</span></>}</Copy>
    {!vit&&<svg width="1920" height="1080" style={{position:'absolute',opacity:t(f,next+25,next+55)*(1-t(f,network-15,network+10))}}>
      {furia?<>
        {[380,1410].map((x,i)=><g key={x}><path d={`M${x-100} 835 L${x-100} 575 L${x+100} 550 L${x+100} 810`} fill="none" stroke={F} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1-t(f,next+i*30,next+110+i*30)}/><text x={x} y="510" textAnchor="middle" fill={W} fontSize="42">{i?'TITLE':'FINAL'}</text></g>)}
        <path d="M165 735 C620 735,1040 735,1650 735" fill="none" stroke={F} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1-t(f,next+40,network-5)}/>
        <circle cx={mix(165,1650,t(f,next+40,network-5))} cy="735" r="15" fill={W}/>
      </>:<>
        <path d="M180 710 L740 710" fill="none" stroke={R} strokeWidth="6" pathLength="1" strokeDasharray="1" strokeDashoffset={1-t(f,next+20,next+100)}/>
        {[530,820].map((y,i)=><g key={y}><path d={`M740 710 C980 710,1080 ${y},1570 ${y}`} fill="none" stroke={i?M:R} strokeWidth="5" pathLength="1" strokeDasharray={i?'.015 .012':'1'} strokeDashoffset={1-t(f,next+80+i*20,network-5)}/><text x="1580" y={y+10} fontSize="34" fill={W}>{i?'REPEAT':'ADAPT'}</text></g>)}
        <text x="180" y="640" fontSize="38" fill={W}>FIRST PLAN</text>
        <path d="M714 674 L770 746 M770 674 L714 746" stroke={R} strokeWidth="7" pathLength="1" strokeDasharray="1" strokeDashoffset={1-t(f,next+95,next+145)}/>
      </>}
      <text x="150" y="950" fontSize="27" fill={M}>ILLUSTRATIVE CHAMPIONSHIP ROUTE · NO ESTIMATED CAUSAL EFFECT</text>
    </svg>}
    <div style={{opacity:t(f,network,network+45)}}><Network f={f} at={network} team={team} names={names} broken={!vit}/></div>
    <Copy f={f} at={network+20} y={130} size={90} color={col}>{vit?"CALLING. COORDINATION.":furia?"COLLECTIVE EXECUTION.":"KEEP THE FIVE INVOLVED."}</Copy>
  </Plane>;
};

const Roster:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),split=cue(s,"fourteen",.25),restore=cue(s,"PGL",.42),rule=cue(s,"We",.7,10);
  const p=t(f,split,restore),q=t(f,restore,restore+130),r=t(f,rule,rule+90);
  return <Plane color={G}>
    <Copy f={f} at={10} until={restore+30} size={160} color={G}>30 <span style={{fontSize:75,color:W}}>STAND-IN MAPS</span></Copy>
    {Array.from({length:30},(_,i)=>{
      const first=i<14,j=first?i:i-14,x0=140+i%15*105,y0=430+Math.floor(i/15)*100,x1=140+j%8*82+(first?0:920),y1=440+Math.floor(j/8)*90;
      const x=mix(mix(x0,x1,p),210+i%5*335,q),y=mix(mix(y0,y1,p),595,q),show=t(f,25+i*1.5,60+i*1.5);
      return <div key={i} style={{position:"absolute",left:x,top:y,width:57,height:66,background:G,opacity:show*(1-q*.97),transform:`perspective(500px) rotateY(${q*90}deg)`}}/>;
    })}
    {[['PORTO','14 MAPS','mezii'],['BUCHAREST','16 MAPS','apEX']].map(([event,n,name],i)=><div key={event} style={{position:"absolute",left:140+i*920,top:690,opacity:p*(1-q),transform:`translateY(${(1-p)*80}px)`}}><div style={{fontSize:58,color:G,...ink}}>{event}</div><div style={{fontSize:45,marginTop:20}}>{n} · jL FOR {name}</div></div>)}
    <Copy f={f} at={restore} until={rule+20} y={135} size={145}>RESTORE<br/><span style={{color:G}}>THE FIVE.</span></Copy>
    {['apEX','ZywOo','flameZ','mezii','ropz'].map((name,i)=>{
      const show=t(f,restore+i*14,restore+65+i*14);
      return <div key={name} style={{position:"absolute",left:135+i*335,top:570-q*45-r*95,opacity:show,transform:`perspective(1400px) rotateX(${(1-show)*65}deg) translateY(${(1-show)*150}px)`}}><div style={{width:275,height:155,borderTop:`4px solid ${G}`,background:"linear-gradient(180deg,#ffd34d19,transparent)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:60,fontWeight:700}}>{name}</div><div style={{width:275,height:3,background:G,opacity:.4}}/></div>;
    })}
    <Copy f={f} at={rule} y={135} size={110} color={G}>SAME RULE.<br/>WINS AND LOSSES.</Copy>
    <svg width="1920" height="1080" style={{position:"absolute",opacity:r}}><path d="M 350 760 L 1570 760" stroke={G} strokeWidth="5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-r}/><text x="350" y="835" fontSize="38" fill={W}>WINS × 0.5</text><text x="1300" y="835" fontSize="38" fill={W}>LOSSES × 0.5</text></svg>
    <Note>{f<restore?"PORTO + BUCHAREST · LINEUP AUDIT":"EXPECTED MAJOR LINEUP · apEX RETURN CONFIRMED BY PGL"}</Note>
  </Plane>;
};

const History:React.FC<{s:Scene}>=({s})=><ExperienceTrio scene={s}/>;

const FuriaOdds:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),change=cue(s,"moderate",.18),conditional=cue(s,"If",.5),caution=cue(s,"Their",.74),p=t(f,change,change+140),q=t(f,conditional,conditional+100);
  const baseline=timeline.baseline.FURIA.title*100,moderate=timeline.moderate.FURIA.title*100,value=baseline/timeline.baseline.FURIA.advance_s3;
  return <Plane color={F}>
    <Copy f={f} at={5} until={conditional+40} size={170} color={F}>STILL IN<br/>THE RACE.</Copy>
    <svg width="1920" height="1080" style={{position:"absolute",opacity:1-q}}>
      {[0,10,20,30,40].map(x=><g key={x}><line x1={190+x*38} y1="520" x2={190+x*38} y2="840" stroke={M} opacity=".18"/><text x={190+x*38} y="905" fill={M} fontSize="27">{x}%</text></g>)}
      <rect x="190" y="560" height="75" width={38*baseline*t(f,20,150)} fill={F}/><rect x="190" y="745" height="75" width={38*moderate*p} fill={P}/>
      <text x="190" y="530" fill={W} fontSize="32">RECENT-FORM BASELINE</text><text x="190" y="720" fill={P} fontSize="32">ASSUMED EXPERIENCE SCENARIO</text>
      <text x={210+38*baseline} y="618" fill={F} fontSize="66">{baseline.toFixed(1)}%</text><text x={210+38*moderate} y="803" fill={P} fontSize="66" opacity={p}>{moderate.toFixed(1)}%</text>
    </svg>
    <div style={{opacity:q}}><Copy f={f} at={conditional} x={135} y={130} size={190} color={F}>{value.toFixed(1)}%</Copy><Copy f={f} at={conditional+20} x={145} y={350} size={55}>TITLE · IF PLAYOFFS</Copy>
      <svg width="1920" height="1080" style={{position:"absolute"}}>{Array.from({length:9},(_,i)=>{const pth=t(f,conditional+i*9,conditional+140+i*9);return <path key={i} d={`M 175 690 C 600 ${450+i*45}, 1150 ${450+i*45}, 1740 690`} stroke={i<2?F:"#364955"} strokeWidth={i<2?5:2} fill="none" pathLength="1" strokeDasharray="1" strokeDashoffset={1-pth}/>;})}<circle cx="1740" cy="690" r="55" stroke={F} strokeWidth="4" fill={BG}/><text x="1740" y="700" textAnchor="middle" fill={F} fontSize="29">TITLE</text></svg>
      <Note>ILLUSTRATIVE ROUTES · CONDITIONAL MODEL ESTIMATE · NO NAMED OPPONENT</Note>
    </div>
    <Copy f={f} at={caution} x={950} y={170} size={87}>RESILIENT CASE.<br/><span style={{color:F}}>NO GUARANTEE.</span></Copy>
  </Plane>;
};

const Farewell:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),prof=cue(s,"Professor",.35),story=cue(s,"His",.62,12),human=cue(s,"Here",.75),p=t(f,prof,prof+130);
  return <Plane color={F}>
    <RevisionClip at={0} slot="fallen"/>
    <Copy f={f} at={30} until={prof+45} x={125} y={590} size={205}>FalleN<span style={{color:F}}>.</span></Copy>
    <div style={{position:"absolute",left:100,top:120,width:1700,height:750,overflow:"hidden",opacity:p,clipPath:`inset(0 ${100*(1-p)}% 0 0)`}}>
      <div style={{position:"absolute",left:0,top:55,color:F,fontSize:72,letterSpacing:6}}>THE PROFESSOR</div>
      <div style={{...ink,position:"absolute",left:0,top:240,fontSize:220,transform:`translateX(${t(f,prof,story,80,0)}px)`}}>ONE LAST<br/>MAJOR.</div>
      <div style={{position:"absolute",left:0,top:690,color:M,fontSize:30}}>SCHEDULED FINAL MAJOR · RETIREMENT PLANNED FOR END 2026</div>
    </div>
    <div style={{position:"absolute",left:1410,top:110,opacity:p,transform:`perspective(1400px) rotateY(${(1-p)*-30}deg)`}}><Logo team="FURIA" size={340}/></div>
    <div style={{position:"absolute",left:145,top:945,color:F,fontSize:31,opacity:t(f,story,story+30)*(1-t(f,human,human+35))}}>THE GODFATHER OF BRAZILIAN COUNTER-STRIKE</div>
    <div style={{position:"absolute",left:150,top:945,fontSize:32,color:W,opacity:t(f,human,human+35)}}>THE HUMAN STAKE GOES BEYOND A PERCENTAGE.</div>
  </Plane>;
};

const Comparison:React.FC<{s:Scene}>=({s})=>{
  const f=useCurrentFrame(),experience=cue(s,"Vitality",.19),breakers=cue(s,"Falcons",.53),publish=cue(s,"We",.67,14),question=cue(s,"The",.8,20);
  const p=t(f,experience,experience+105),assumed=f>=experience,withdraw=t(f,publish,publish+80),end=t(f,question,question+55);
  return <Plane color={G}>
    {['MOUZ','FURIA','Vitality'].map((team,i)=>{
      const b=timeline.baseline[team as 'MOUZ'].title*100,m=timeline.moderate[team as 'MOUZ'].title*100;
      const bar=mix(b,m,p),endpoint=assumed?m:b,top=290+i*205;
      return <div key={team} style={{position:"absolute",left:140-withdraw*1900,top,opacity:t(f,i*22,50+i*22)}}><Logo team={team} size={100}/>{assumed&&p<1&&<div style={{position:'absolute',left:185,top:8,width:endpoint*32,height:65,border:`2px dashed ${colors[team]}`,opacity:.3,boxSizing:'border-box'}}/>}<div style={{position:"absolute",left:185,top:8,width:bar*32,height:65,background:colors[team]}}/><div style={{position:"absolute",left:1450,top:0,fontSize:75,...ink,color:colors[team]}}>{formatPercent(endpoint/100)}</div></div>;
    })}
    <Copy f={f} at={0} until={publish+40} y={110} size={70} color={assumed?P:W}>{assumed?"ASSUMED EXPERIENCE SCENARIO":"RECENT-FORM BASELINE"}</Copy>
    <div style={{position:"absolute",left:145,top:940,fontSize:29,color:M,opacity:1-withdraw}}>TITLE PROBABILITIES · SHARED 0–40% SCALE · VALUES AT VERIFIED ENDPOINTS</div>
    <div style={{position:"absolute",left:1450,top:180,display:"flex",gap:45,opacity:t(f,breakers,breakers+35)*(1-withdraw)}}><Logo team="Falcons" size={110}/><Logo team="Spirit" size={110}/></div>
    <div style={{position:"absolute",inset:0,opacity:withdraw*(1-end)}}>
      <Copy f={f} at={publish} y={230} size={160}>DATED.<br/><span style={{color:G}}>TESTABLE.</span></Copy>
      <div style={{position:"absolute",left:145,top:700,fontSize:44,color:M}}>Forecast cutoff: 15 November 2026</div>
      <div style={{position:"absolute",left:145,top:790,width:1450,height:6,background:G,transform:`scaleX(${t(f,publish+30,question)})`,transformOrigin:"left"}}/>
    </div>
    <div style={{position:"absolute",inset:0,opacity:end}}>
      {['MOUZ','FURIA','Vitality'].map((team,i)=><div key={team} style={{position:"absolute",left:190+i*595,top:100,transform:`translateY(${(1-end)*100}px)`}}><Logo team={team} size={210}/></div>)}
      <Copy f={f} at={question} x={180} y={430} size={180}>WHICH CASE<br/>HOLDS<span style={{color:G}}>?</span></Copy>
    </div>
  </Plane>;
};

const Editorial:React.FC<{s:Scene}>=({s})=>{
  switch(s.id){
    case 'hook':return <Video10OpeningFinal furiaAt={cue(s,'Furia',.16)} vitalityAt={cue(s,'Vitality',.29)} simulationAt={cue(s,'We',.5)}/>;
    case 'method':return <Method s={s}/>;
    case 'field':return <Threats s={s}/>;
    case 'mouz_form':return <Result s={s}/>;
    case 'mouz_maps':return <MouzMapMotion/>;
    case 'mouz_odds':return <MouzOddsMotion/>;
    case 'mouz_test':return <Test s={s}/>;
    case 'vitality_roster':return <Roster s={s}/>;
    case 'vitality_history':return <History s={s}/>;
    case 'vitality_scenario':return <VitalityScenarioMotion/>;
    case 'vitality_test':return <Test s={s}/>;
    case 'furia_form':return <Result s={s} furia/>;
    case 'furia_odds':return <FuriaOdds s={s}/>;
    case 'furia_test':return <Test s={s}/>;
    case 'fallen':return <Farewell s={s}/>;
    case 'comparison':return <Comparison s={s}/>;
    default:return null;
  }
};

export const Video10FinalFilm:React.FC=()=> <AbsoluteFill style={{background:BG}}>
  {timeline.caseOpeners.map(o=><Sequence key={o.id} from={o.fromFrame} durationInFrames={o.frames}><CaseLogo team={o.team}/></Sequence>)}
  {timeline.scenes.map(s=><Sequence key={s.id} from={s.fromFrame} durationInFrames={s.frames}><Editorial s={s}/></Sequence>)}
  <Sequence from={timeline.introFrom} durationInFrames={228}><OffthreadVideo src={staticFile('video09-v4/intro.mp4')} muted/></Sequence>
  <Sequence from={timeline.frames-150} durationInFrames={150}><Plane color={G}><div style={{position:'absolute',left:130,top:270,...ink,fontSize:105}}>SPORTS ON THE LINE<span style={{color:G}}>.</span></div><div style={{position:'absolute',left:135,top:470,fontSize:45,color:M}}>The numbers. The context. The game.</div><div style={{position:'absolute',left:135,top:790,fontSize:29,color:M}}>MODEL / SCENARIOS THROUGH 15 NOV 2026 · SOURCES & CREDITS IN DESCRIPTION</div></Plane></Sequence>
</AbsoluteFill>;
