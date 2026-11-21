import React from "react";
import {AbsoluteFill, Easing, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../theme";
import {framing, CameraKey} from "../video09/camera";
import config from "../../public/video10/scenario-sample/config.json";
import media from '../../public/video10/footage-revision.json';

export const SCENARIO_MOTION_FRAMES = config.frames;
const BG="#080e15", WHITE="#f2f5f7", GOLD="#ffd34d", PURPLE="#dca2ff", MUTED="#a5b7c2";
const BOTTOM=820, LEFT=160, WIDTH=1600, MAX=40;
const clamp={extrapolateLeft:"clamp",extrapolateRight:"clamp"} as const;
const ease=Easing.bezier(.18,.82,.22,1);
const tween=(f:number,a:number,b:number,x=0,y=1)=>interpolate(f,[a,b],[x,y],{...clamp,easing:ease});
const travel=(f:number,a:number,b:number,x=0,y=1)=>interpolate(f,[a,b],[x,y],clamp);
const pos=(value:number)=>LEFT+WIDTH*value/MAX;
const {roster,experience,caveat}=config.cues;
const NOT_PROVEN=557, HISTORY=637;
const cameraKeys:CameraKey[]=[
  {f:0,x:880,z:1.02,dur:85},{f:95,x:920,z:1,dur:70},
  {f:roster-8,x:955,z:1.02,dur:105},{f:experience-8,x:1010,z:1.035,dur:115},
  {f:experience+110,x:985,z:1,dur:95},{f:caveat,x:1010,z:1.02,dur:90},
  {f:HISTORY,x:950,z:.97,dur:100},{f:760,x:960,z:1,dur:95},
];
const ink:React.CSSProperties={fontWeight:700,lineHeight:.92,letterSpacing:-5,textShadow:"0 4px 18px #000c",WebkitTextStroke:"1px #06101b70",paintOrder:"stroke fill"};

const Shot:React.FC<{file:string;label:string;inset?:boolean}> = ({file,label,inset=false})=>{
  const f=useCurrentFrame(), duration=108;
  const visibility=Math.min(tween(f,0,8),tween(f,duration-8,duration,1,0));
  return <AbsoluteFill style={{opacity:visibility,overflow:"hidden",...(inset?{left:1160,top:105,width:670,height:415,bottom:"auto",right:"auto",borderRadius:18,transform:`translateX(${tween(f,0,22,140,0)}px) perspective(1200px) rotateY(${tween(f,0,75,-9,0)}deg)`,boxShadow:"0 30px 65px #0008"}:{})}}>
    <OffthreadVideo src={staticFile(`video10/clips/${file}`)} muted style={{width:"100%",height:"100%",objectFit:"cover",transform:`scale(${tween(f,0,duration,1.065,1.015)})`}} />
    {!inset&&<AbsoluteFill style={{background:"linear-gradient(0deg,#080e15f5 1%,#080e1560 55%,#080e1520)"}}/>}
    <div style={{position:"absolute",left:inset?18:45,bottom:inset?18:24,fontSize:inset?20:23,color:WHITE,padding:"7px 12px",background:"#06101bc9",letterSpacing:.5}}>{label}</div>
  </AbsoluteFill>;
};

const MapFlow:React.FC<{f:number}>=({f})=>{
  const local=f-roster, fade=tween(f,roster-18,roster)*tween(f,roster+100,roster+133,1,0);
  return <AbsoluteFill style={{opacity:fade}}>
    <div style={{...ink,position:"absolute",left:155,top:150,fontSize:76}}>30 <span style={{fontSize:43,letterSpacing:0}}>STAND-IN MAPS</span></div>
    {Array.from({length:30},(_,i)=>{
      const p=tween(local,i*1.8,i*1.8+53), sx=175+(i%10)*52,sy=285+Math.floor(i/10)*56;
      const x=sx+(pos(config.values[1])-sx)*p,y=sy+(BOTTOM-sy)*p-180*Math.sin(p*Math.PI);
      return <div key={i} style={{position:"absolute",left:x,top:y,width:24*(1-p*.65),height:30*(1-p*.65),background:GOLD,opacity:1-p*.8,transform:`rotate(${p*30}deg)`,boxShadow:p>.1?"0 0 16px #ffd34d70":"none"}}/>;
    })}
  </AbsoluteFill>;
};

export const VitalityScenarioMotion:React.FC=()=>{
  const f=useCurrentFrame(), phase=f<roster?0:f<experience?1:2;
  const baseline=config.values[0], adjusted=config.values[1], assumed=config.values[2];
  const first=travel(f,22,145,0,baseline);
  const rosterValue=travel(f,roster,experience-10,baseline,adjusted);
  const assumedValue=travel(f,experience,caveat-16,adjusted,assumed);
  const solid=f<roster?first:rosterValue;
  const extension=f<experience?adjusted:assumedValue;
  const labelValue=config.values[phase];
  const head=pos(phase<2?solid:extension);
  const camera=framing(cameraKeys,f);
  const graphVisible=tween(f,20,60);
  const historyFilm=tween(f,HISTORY,HISTORY+14)*tween(f,HISTORY+94,HISTORY+108,1,0);
  const withdraw=tween(f,caveat+20,caveat+125);
  const lineProgress=tween(f,roster-4,roster+105);
  const branchProgress=travel(f,experience,caveat);
  const smallValue=tween(f,caveat,caveat+70);
  const rulerOpacity=1-historyFilm*.48;
  const firstArc=`M ${pos(baseline)} ${BOTTOM-15} Q ${(pos(baseline)+pos(adjusted))/2} ${BOTTOM-150} ${pos(adjusted)} ${BOTTOM-15}`;
  const branch=`M ${pos(adjusted)} ${BOTTOM-8} C ${pos(adjusted)+120} ${BOTTOM-68}, ${pos(assumed)-160} ${BOTTOM-68}, ${pos(assumed)} ${BOTTOM-8}`;
  return <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,overflow:"hidden"}}>
    <AbsoluteFill style={{background:"radial-gradient(ellipse at 68% 35%,#25374a50,transparent 65%),linear-gradient(135deg,#0a1421,#070b10)"}}/>
    <Sequence durationInFrames={108}><Shot file={media.slots.vitality_scenario_intro.file+'.mp4'} label={media.slots.vitality_scenario_intro.label}/></Sequence>
    <Sequence from={roster} durationInFrames={108}><Shot file={media.slots.vitality_scenario_inset.file+'.mp4'} label={media.slots.vitality_scenario_inset.label} inset/></Sequence>
    <Sequence from={HISTORY} durationInFrames={108}><Shot file={media.slots.vitality_scenario_tail.file+'.mp4'} label={media.slots.vitality_scenario_tail.label}/></Sequence>

    <AbsoluteFill style={{opacity:graphVisible,transform:`translateX(${960-camera.x}px) scale(${camera.z})`,transformOrigin:"960px 540px"}}>
      <div style={{position:"absolute",left:LEFT,top:BOTTOM-57,fontSize:31,color:MUTED,letterSpacing:3,opacity:rulerOpacity}}>TITLE CHANCE</div>
      <svg width="1920" height="1080" style={{position:"absolute",overflow:"visible",opacity:rulerOpacity}}>
        <defs>
          <linearGradient id="motion-gold"><stop stopColor="#9a7625"/><stop offset=".6" stopColor={GOLD}/><stop offset="1" stopColor="#fff2ad"/></linearGradient>
          <linearGradient id="motion-purple"><stop stopColor="#bc79e0" stopOpacity=".2"/><stop offset="1" stopColor={PURPLE} stopOpacity=".8"/></linearGradient>
          <pattern id="assumed-hatch" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform={`translate(${f*.32} 0) rotate(-35)`}><rect width="4" height="24" fill={PURPLE} opacity=".3"/></pattern>
          <clipPath id="branch-reveal"><rect x={pos(adjusted)-30} y="0" width={(pos(assumed)-pos(adjusted)+60)*branchProgress} height="1080"/></clipPath>
        </defs>
        <line x1={LEFT} y1={BOTTOM+33} x2={pos(MAX)} y2={BOTTOM+33} stroke="#718393" strokeWidth="2"/>
        {[0,10,20,30,40].map(t=><g key={t}><line x1={pos(t)} y1={BOTTOM+20} x2={pos(t)} y2={BOTTOM+52} stroke="#8798a6" strokeWidth="2"/><text x={pos(t)} y={BOTTOM+102} fill={MUTED} fontSize="34" textAnchor="middle">{t}%</text></g>)}
        <rect x={LEFT} y={BOTTOM-18} width={pos(labelValue)-LEFT} height="36" rx="5" fill="none" stroke={phase===2?PURPLE:GOLD} strokeWidth="2" opacity=".2"/>
        <line x1={pos(labelValue)} x2={pos(labelValue)} y1={BOTTOM-42} y2={BOTTOM+22} stroke={phase===2?PURPLE:GOLD} strokeWidth="2" strokeDasharray="4 5" opacity=".45"/>
        <rect x={LEFT} y={BOTTOM-18} width={Math.max(0,pos(solid)-LEFT)} height="36" rx="5" fill="url(#motion-gold)"/>
        {f>=roster&&<line x1={pos(baseline)} x2={pos(baseline)} y1={BOTTOM-32} y2={BOTTOM+18} stroke={WHITE} strokeWidth="2" opacity=".5"/>}
        {f>=experience&&<>
          <rect x={pos(adjusted)} y={BOTTOM-18} width={Math.max(0,pos(extension)-pos(adjusted))} height="36" fill="url(#assumed-hatch)" opacity={1-withdraw*.8}/>
          <rect x={pos(adjusted)} y={BOTTOM-18} width={Math.max(0,pos(extension)-pos(adjusted))} height="36" rx="3" fill="none" stroke={PURPLE} strokeWidth="3" strokeDasharray="12 8" strokeDashoffset={-f*.45}/>
        </>}
        {Array.from({length:9},(_,i)=>{
          const length=Math.max(0,pos(solid)-LEFT-16), x=LEFT+((f*2.2+i*91)%Math.max(1,length));
          return <line key={i} x1={x} x2={x+10} y1={BOTTOM-10} y2={BOTTOM-10} stroke="#fff8c9" strokeWidth="3" opacity=".4"/>;
        })}
        <path d={firstArc} fill="none" stroke={GOLD} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-lineProgress} opacity={tween(f,roster-8,roster+8)}/>
        <path d={branch} fill="none" stroke={PURPLE} strokeWidth="4" pathLength="1" strokeDasharray=".015 .012" strokeDashoffset={-f*.0005} opacity={branchProgress} clipPath="url(#branch-reveal)"/>
        <circle cx={head} cy={BOTTOM} r={12+Math.sin(f/12)*2} fill={phase===2?PURPLE:GOLD}/>
        <circle cx={head} cy={BOTTOM} r={22+Math.sin(f/17)*5} fill="none" stroke={phase===2?PURPLE:GOLD} strokeWidth="2" opacity=".3"/>
      </svg>

      <div style={{...ink,position:"absolute",left:pos(labelValue)-320,top:BOTTOM-320-smallValue*10,width:640,textAlign:"center",fontSize:205-smallValue*57,color:phase===2?PURPLE:GOLD,opacity:1-historyFilm*.45}}>{labelValue.toFixed(1)}<span style={{fontSize:110-smallValue*25}}>%</span>
        <div style={{fontSize:46,letterSpacing:1,marginTop:18,color:phase===2?PURPLE:WHITE}}>{["RECENT FORM","ROSTER ADJUSTED","ASSUMED EXPERIENCE"][phase]}</div>
      </div>
      <MapFlow f={f}/>
    </AbsoluteFill>

    {f>=caveat&&<div style={{position:"absolute",left:125,top:200,transform:`translateX(${tween(f,caveat,caveat+50,-55,0)}px)`,opacity:tween(f,caveat,caveat+28)*(1-tween(f,790,830))}}>
      <div style={{fontSize:43,letterSpacing:4,color:PURPLE,opacity:1-tween(f,NOT_PROVEN-8,NOT_PROVEN+12)}}>A SCENARIO</div>
      <div style={{...ink,fontSize:167,marginTop:14,clipPath:`inset(0 ${100-tween(f,NOT_PROVEN-8,NOT_PROVEN+30)*100}% 0 0)`}}>NOT<br/>PROVEN<span style={{color:PURPLE}}>.</span></div>
      <div style={{fontSize:37,color:WHITE,letterSpacing:2,marginTop:28,opacity:tween(f,HISTORY+25,HISTORY+60)}}>BY THE HISTORICAL TEST</div>
      <div style={{width:tween(f,690,750,0,520),height:6,marginTop:25,background:PURPLE}}/>
    </div>}
  </AbsoluteFill>;
};
