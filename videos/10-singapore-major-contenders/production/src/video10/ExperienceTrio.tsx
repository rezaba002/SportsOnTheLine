import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Logo} from '../cards/parts';
import {FONT} from '../theme';
import data from '../../public/video10/revision-data.json';

type ExperienceScene={frames:number;words:Array<{w:string;s:number;e:number}>};
const TEAMS=['Vitality','FURIA','MOUZ'] as const;
const COLORS={Vitality:'#ffd34d',FURIA:'#a2e4a8',MOUZ:'#ff5e64'};
const WHITE='#f2f5f7',MUTED='#a5b5c3';
const t=(f:number,a:number,b:number,x=0,y=1)=>{const p=interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});return x+(y-x)*p*p*(3-2*p);};
const display:React.CSSProperties={fontWeight:700,letterSpacing:-4,lineHeight:.96,textShadow:'0 3px 0 #0009, 0 12px 28px #000a'};

export const ExperienceTrio:React.FC<{scene:ExperienceScene}>=({scene})=>{
  const f=useCurrentFrame();
  const cue=(word:string,fallback:number,after=0)=>{
    const w=scene.words.find(w=>w.s>=after&&w.w.toLowerCase().replace(/[^a-z]/g,'')===word.toLowerCase());
    return w?Math.round(w.s*30)+24:scene.frames*fallback;
  };
  const starts=[20,cue('Furia',.16),cue('Mouse',.25)];
  const notTeam=cue('These',.33),lan=cue('snapshot',.46);
  const lanStarts=[cue('thousand',.55,10)-20,cue('Furia',.65,10)-15,cue('Mouse',.74,10)-15];
  const end=Math.max(cue('ordering',.83),lanStarts[2]+120);
  const creditsOpacity=1-t(f,lan-30,lan+5),lanOpacity=t(f,lan+10,lan+40)*(1-t(f,end,end+45));
  return <AbsoluteFill style={{background:'#080e15',color:WHITE,fontFamily:FONT,overflow:'hidden'}}>
    <AbsoluteFill style={{background:'radial-gradient(ellipse at 40% 40%,#ffd34d0f,transparent 65%)'}}/>
    <AbsoluteFill style={{opacity:creditsOpacity}}>
      <div style={{position:'absolute',left:145,top:280,fontSize:43,letterSpacing:3,opacity:t(f,20,45)}}>PLAYER MAJOR-TITLE CREDITS</div>
      {TEAMS.map((team,column)=>{
        const x=150+column*620,col=COLORS[team],value=data.teams[team].credits,start=starts[column];
        return <div key={team} style={{position:'absolute',left:x,top:0,opacity:t(f,start,start+30),transform:`translateY(${t(f,start,start+50,65,0)}px)`}}>
          <div style={{position:'absolute',top:110}}><Logo team={team} size={140}/></div>
          {Array.from({length:value},(_,i)=>{
            const p=t(f,start+i*5,start+55+i*5);
            return <div key={i} style={{position:'absolute',left:i%7*75,top:410+Math.floor(i/7)*115,width:57,height:82,border:`2px solid ${col}`,background:`linear-gradient(140deg,${col}ce,${col}22)`,opacity:p,transform:`perspective(500px) rotateY(${(1-p)*80}deg) translateY(${(1-p)*65}px)`}}/>;
          })}
          <div style={{...display,position:'absolute',top:665,fontSize:170,color:col}}>{value}</div>
          {column>0&&<div style={{position:'absolute',top:855,fontSize:33,color:MUTED}}>{column===1?'FalleN':'Spinx'}</div>}
        </div>;
      })}
      <div style={{position:'absolute',left:150,top:955,fontSize:33,color:'#dca2ff',opacity:t(f,notTeam,notTeam+25)}}>PLAYER TITLES ≠ DISTINCT TEAM CHAMPIONSHIPS</div>
    </AbsoluteFill>
    <AbsoluteFill style={{opacity:lanOpacity}}>
      <div style={{...display,position:'absolute',left:145,top:110,fontSize:110}}>EXPERIENCE<br/>OF THE FIVE.</div>
      {TEAMS.map((team,i)=>{
        const value=data.teams[team].lan,p=t(f,lanStarts[i],lanStarts[i]+60);
        return <div key={team} style={{position:'absolute',left:145,top:430+i*190}}>
          <div style={{fontSize:47,color:COLORS[team],lineHeight:1.1}}>{team}</div>
          <div style={{position:'absolute',left:285,top:0,height:64,width:1140*value/1200*p,background:COLORS[team]}}/>
          <div style={{...display,position:'absolute',left:1500,top:-5,fontSize:80}}>{Math.round(value).toLocaleString('en-US')}</div>
        </div>;
      })}
      {[0,600,1200].map(value=><div key={value} style={{position:'absolute',left:430+1140*value/1200,top:925,fontSize:25,color:MUTED}}>{value.toLocaleString('en-US')}</div>)}
      <div style={{position:'absolute',left:145,top:985,fontSize:27,color:MUTED}}>AVG CAREER LAN MAPS · {data.snapshot} SNAPSHOT · SHARED 0–1,200 SCALE</div>
    </AbsoluteFill>
    <AbsoluteFill style={{opacity:t(f,end+35,end+65)}}>
      <div style={{...display,position:'absolute',left:145,top:150,fontSize:145}}>THE FIVE.<br/><span style={{color:COLORS.Vitality}}>NOT THE BADGE.</span></div>
      {TEAMS.map((team,i)=><div key={team} style={{position:'absolute',left:200+i*550,top:625,transform:`translateY(${t(f,end+35+i*10,end+85+i*10,80,0)}px)`}}><Logo team={team} size={245}/></div>)}
    </AbsoluteFill>
  </AbsoluteFill>;
};
