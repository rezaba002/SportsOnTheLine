import React from "react";
import {AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../theme";
import media from '../../public/video10/footage-revision.json';
import {framing,CameraKey} from "../video09/camera";
import settings from "../../public/video10/mouz-samples/config.json";

const MAP=settings.mouz_maps, ODDS=settings.mouz_odds;
export const MOUZ_MAP_FRAMES=MAP.frames, MOUZ_ODDS_FRAMES=ODDS.frames;
const BG="#080f17", WHITE="#f0f4f6", RED="#ff5e64", GOLD="#ffd34d", MUTED="#98aebd";
const clamp={extrapolateLeft:"clamp",extrapolateRight:"clamp"} as const;
const ease=Easing.bezier(.2,.78,.24,1);
const t=(f:number,a:number,b:number,x=0,y=1)=>interpolate(f,[a,b],[x,y],{...clamp,easing:ease});
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const ink:React.CSSProperties={fontWeight:700,lineHeight:.93,letterSpacing:-4,textShadow:"0 3px 0 #0009, 0 12px 28px #000c"};

const Footage:React.FC<{file:string;label:string;inset?:boolean}>=({file,label,inset=false})=>{
  const f=useCurrentFrame(),opacity=Math.min(t(f,0,8),t(f,100,108,1,0));
  return <AbsoluteFill style={{opacity,overflow:"hidden",...(inset?{left:1320,top:90,width:535,height:325,bottom:"auto",right:"auto",borderRadius:16,transform:`translateX(${t(f,0,24,110,0)}px)`}:{})}}>
    <OffthreadVideo src={staticFile(`video10/clips/${file}.mp4`)} muted style={{width:"100%",height:"100%",objectFit:"cover",transform:`scale(${t(f,0,108,1.06,1)})`}}/>
    {!inset&&<AbsoluteFill style={{background:"linear-gradient(0deg,#080f17e8,transparent 85%)"}}/>}
    <div style={{position:"absolute",left:inset?12:42,bottom:inset?12:26,fontSize:inset?19:23,padding:"6px 10px",background:"#06101bd0",color:WHITE}}>{label}</div>
  </AbsoluteFill>;
};

const Bed:React.FC<{frames:number;voice:string;events:number[]}>=({frames,voice,events})=>{
  const f=useCurrentFrame();
  return <>
    <Audio src={staticFile("video10/editorial/music-tension-soft.mp3")} trimBefore={650} volume={t(f,0,20)*t(f,frames-50,frames,1,0)*.085}/>
    <Sequence from={24}><Audio src={staticFile(`video10/mouz-samples/${voice}.mp3`)}/></Sequence>
    {events.map(at=><Sequence key={at} from={at} durationInFrames={12}><Audio src={staticFile("video10/editorial/click-soft.wav")} volume={.25}/></Sequence>)}
  </>;
};

const MapActor:React.FC<{index:number;f:number;columns:number}>=({index,f,columns})=>{
  const map=MAP.maps[index],c=MAP.cues;
  const at=[c.mirage-45,c.nuke-18,c.cache-18][index];
  const reveal=t(f,at,at+22),ban=index===0?t(f,c.remove,c.remove+27):0;
  const x=mix(130,130+index*620,columns),y=mix(320+index*370,365,columns);
  const metricX=mix(660,0,columns),metricY=mix(0,135,columns);
  const chipY=mix(210,345,columns),step=mix(46,32,columns),size=mix(34,24,columns);
  return <div style={{position:"absolute",left:x,top:y,opacity:reveal*(1-ban*.62),transform:`translateX(${(1-reveal)*150}px) perspective(1400px) rotateY(${(1-reveal)*14}deg)`}}>
    <div style={{...ink,color:RED,fontSize:mix(180,105,columns)}}>{map.name.toUpperCase()}</div>
    <div style={{...ink,position:"absolute",left:metricX,top:metricY,fontSize:mix(156,140,columns),whiteSpace:"nowrap"}}>{map.wins}<span style={{color:MUTED}}>–</span>{map.losses}</div>
    <div style={{position:"absolute",left:metricX,top:mix(155,285,columns),fontSize:mix(38,32,columns),letterSpacing:2,whiteSpace:"nowrap",color:index===2?GOLD:MUTED}}>{index===2?"ONLY ":""}{map.wins+map.losses} MAPS · W–L</div>
    {Array.from({length:map.wins+map.losses},(_,i)=>{
      const draw=t(f,[c.mirage,c.nuke,c.cache][index]+i*1.5,[c.mirage,c.nuke,c.cache][index]+i*1.5+18);
      const win=i<map.wins;
      return <div key={i} style={{position:"absolute",left:metricX+i*step+(1-draw)*90,top:chipY+(1-draw)*-65,width:size,height:size,opacity:draw,background:win?WHITE:"#74323c",border:win?"none":`2px solid ${RED}`,transform:`rotate(${(1-draw)*35}deg)`}}>{!win&&<svg width="100%" height="100%" viewBox="0 0 30 30"><path d="M7 7L23 23M23 7L7 23" stroke={RED} strokeWidth="3"/></svg>}</div>;
    })}
    {index===0&&<svg width="480" height="140" style={{position:"absolute",left:-5,top:-5,overflow:"visible"}}><path d="M0 0L450 122M450 0L0 122" pathLength="1" stroke={RED} strokeWidth="15" fill="none" strokeDasharray="1" strokeDashoffset={1-ban}/></svg>}
  </div>;
};

export const MouzMapMotion:React.FC=()=>{
  const f=useCurrentFrame(),c=MAP.cues,columns=t(f,c.veto,c.veto+100);
  const keys:CameraKey[]=[{f:0,x:500,z:.82,dur:60},{f:c.mirage-40,x:600,z:.8,dur:60},{f:c.nuke-10,x:745,z:.78,dur:60},{f:c.cache-12,x:895,z:.76,dur:55},{f:c.raw,x:760,z:.67,dur:85},{f:c.veto,x:540,z:1,dur:95}];
  const camera=framing(keys,f),raw=t(f,c.raw,c.raw+25)*(1-t(f,c.veto-35,c.veto));
  const remaining=t(f,c.remove,c.remove+55),safe=t(f,c.safe,c.safe+20)*(1-t(f,c.veto-20,c.veto+4));
  return <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,overflow:"hidden"}}>
    <AbsoluteFill style={{background:"radial-gradient(ellipse at 35% 38%,#63202a38,transparent 66%)"}}/>
    <Sequence durationInFrames={108}><Footage file={media.slots.mouz_maps.file} label={media.slots.mouz_maps.label}/></Sequence>
    <Sequence from={c.raw} durationInFrames={108}><Footage file={media.slots.mouz_maps_inset.file} label={media.slots.mouz_maps_inset.label} inset/></Sequence>
    <div style={{...ink,position:"absolute",left:120,top:600,fontSize:170,opacity:t(f,5,24)*(1-t(f,88,112)),transform:`translateY(${t(f,5,30,70,0)}px)`}}>THE VETO<span style={{color:RED}}>.</span></div>
    <div style={{position:"absolute",left:130,top:100,fontSize:54,letterSpacing:3,opacity:t(f,c.date,c.date+20)*(1-t(f,c.mirage-10,c.mirage+5))}}>16 OCT — 15 NOV 2026</div>
    <AbsoluteFill style={{transform:`translateY(${540-camera.x}px) scale(${camera.z})`,transformOrigin:"960px 540px"}}>
      {[0,1,2].map(i=><MapActor key={i} index={i} f={f} columns={columns}/>)}
    </AbsoluteFill>
    <div style={{...ink,position:"absolute",left:1370,top:620,fontSize:70,opacity:raw,transform:`translateY(${(1-raw)*45}px)`}}>RAW<br/>RESULTS<div style={{fontSize:30,color:MUTED,letterSpacing:1,marginTop:25}}>DIFFERENT<br/>OPPONENTS</div></div>
    <div style={{...ink,position:"absolute",left:1280,top:520,width:550,fontSize:91,opacity:safe,transform:`translateX(${(1-safe)*110}px)`}}>NO SAFE<br/>MAP<div style={{height:6,width:t(f,c.safe+12,c.safe+60,0,420),background:RED,marginTop:25}}/></div>
    <div style={{position:"absolute",left:130,top:95,opacity:t(f,c.veto+35,c.veto+65)}}><div style={{fontSize:31,letterSpacing:3,color:MUTED}}>ILLUSTRATIVE VETO</div><div style={{...ink,fontSize:90,marginTop:15}}>IF MIRAGE IS REMOVED…</div></div>
    <svg width="1920" height="1080" style={{position:"absolute",opacity:remaining}}>
      <path d="M760 810 L760 855 L1750 855 L1750 810" fill="none" stroke={GOLD} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1-remaining}/>
      <text x="1255" y="930" textAnchor="middle" fill={WHITE} fontSize="38">REMAINING OPTIONS SHOWN</text>
      <text x="1255" y="985" textAnchor="middle" fill={MUTED} fontSize="27">SCHEMATIC VETO · NO MATCHUP ODDS</text>
    </svg>
    <Bed frames={MAP.frames} voice="mouz_maps" events={[c.mirage,c.nuke,c.cache,c.remove]}/>
  </AbsoluteFill>;
};

const DOTS=1000,WINS=Math.round(ODDS.title*DOTS),QUALIFIED=Math.round(ODDS.playoffs*DOTS);
const grid=(i:number)=>({x:235+i%50*28,y:400+Math.floor(i/50)*25});
const split=(i:number)=>i<WINS?({x:170+i%17*27,y:420+Math.floor(i/17)*27}):({x:810+(i-WINS)%29*27,y:400+Math.floor((i-WINS)/29)*18});
const qualified=(i:number)=>({x:180+i%37*25,y:350+Math.floor(i/37)*24});

export const MouzOddsMotion:React.FC=()=>{
  const f=useCurrentFrame(),c=ODDS.cues,divide=t(f,c.field,c.playoffs-5),repack=t(f,c.playoffs,c.calculated+45),filter=t(f,c.playoffs+20,c.playoffs+100);
  const conditional=t(f,c.conditional,c.conditional+55),unknown=t(f,c.unknown,c.unknown+70);
  return <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,overflow:"hidden"}}>
    <AbsoluteFill style={{background:"radial-gradient(ellipse at 25% 50%,#72253225,transparent 68%)"}}/>
    <svg width="1920" height="1080" style={{position:"absolute"}}>
      {Array.from({length:DOTS},(_,i)=>{
        const original=grid(i),spread=split(i),retained=qualified(i),keep=i<QUALIFIED;
        const initial=t(f,(i%50)*.4+Math.floor(i/50)*1.1,(i%50)*.4+Math.floor(i/50)*1.1+25);
        let x=mix(original.x,spread.x,divide),y=mix(original.y,spread.y,divide);
        x=mix(x,keep?retained.x:spread.x+Math.sin(i)*150,repack);
        y=mix(y,keep?retained.y:1200+(i%13)*25,repack);
        return <circle key={i} cx={x+(1-initial)*110} cy={y-(1-initial)*80} r={5.8} fill={i<WINS?RED:"#8fa8ba"} opacity={initial*(keep?1:1-filter)*(i<WINS?1:.62)}/>;
      })}
      {Array.from({length:3},(_,i)=>{
        const y=505+i*155,p=t(f,c.unknown+i*14,c.unknown+i*14+50);
        return <g key={i} opacity={p}><line x1="1255" y1={y} x2="1405" y2={y} stroke={WHITE} strokeWidth="3" strokeDasharray="8 9" strokeDashoffset={-f*.8}/><circle cx="1490" cy={y} r="57" fill="#10202d" stroke={RED} strokeWidth="3"/><text x="1490" y={y+22} textAnchor="middle" fill={WHITE} fontSize="69">?</text><text x="1585" y={y+10} fill={MUTED} fontSize="31">{["QF","SF","FINAL"][i]}</text></g>;
      })}
    </svg>
    <div style={{...ink,position:"absolute",left:230-t(f,c.playoffs,c.calculated,70),top:105,fontSize:mix(160,85,repack),color:RED,opacity:t(f,15,50)*(1-t(f,c.calculated-15,c.calculated+10))}}>{(ODDS.title*100).toFixed(1)}%<div style={{fontSize:34,letterSpacing:2,marginTop:15,color:WHITE}}>TITLE · BASELINE</div></div>
    <div style={{...ink,position:"absolute",left:1080,top:105,fontSize:122,opacity:divide*(1-t(f,c.playoffs,c.playoffs+35))}}> {(100-ODDS.title*100).toFixed(1)}%<div style={{fontSize:34,letterSpacing:2,marginTop:15,color:MUTED}}>REST OF THE FIELD</div></div>
    <div style={{...ink,position:"absolute",left:1240,top:150,width:560,opacity:conditional,transform:`translateX(${(1-conditional)*100}px)`}}><div style={{fontSize:184,color:RED}}>{(ODDS.conditional*100).toFixed(1)}<span style={{fontSize:105}}>%</span></div><div style={{fontSize:42,letterSpacing:1,marginTop:26}}>TITLE · IF PLAYOFFS</div></div>
    <div style={{position:"absolute",left:175,top:940,fontSize:29,letterSpacing:2,color:MUTED,opacity:t(f,50,80)*(1-t(f,c.playoffs,c.playoffs+45))}}>ILLUSTRATIVE PROBABILITY SPLIT · 1 CHIP ≈ 0.1%</div>
    <div style={{position:"absolute",left:175,top:940,fontSize:35,letterSpacing:1,color:WHITE,opacity:t(f,c.playoffs+60,c.calculated)}}>ONLY PLAYOFF-QUALIFIED PATHS REMAIN</div>
    <div style={{position:"absolute",left:1260,top:400,fontSize:31,letterSpacing:2,color:MUTED,opacity:unknown}}>OPPONENTS STILL UNKNOWN</div>
    <div style={{...ink,position:"absolute",left:180,top:115,fontSize:60,opacity:t(f,c.calculated,c.calculated+35)*(1-unknown)}}>SAME WINS.<br/>SMALLER POOL.</div>
    <Bed frames={ODDS.frames} voice="mouz_odds" events={[c.field,c.playoffs,c.conditional]}/>
  </AbsoluteFill>;
};
