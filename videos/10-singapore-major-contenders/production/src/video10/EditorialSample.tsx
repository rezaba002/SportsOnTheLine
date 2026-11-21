import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame } from "remotion";
import { FONT } from "../theme";
import { Logo } from "../cards/parts";

export const EDITORIAL_SAMPLE_FRAMES = 690;
const BG = "#080d13", WHITE = "#f1f4f5", RED = "#ff5862", GOLD = "#ffd34d", GREEN = "#a2e4a8";
const ramp = (f: number, a: number, b: number, x = 0, y = 1) => interpolate(f, [a, b], [x, y], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
const smooth = (x: number) => 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3);
const clip = (file: string) => staticFile(`video10/clips/${file}.mp4`);
// Moving images need local separation; plain-background display type does not.
const footageInk: React.CSSProperties = {fontWeight: 700, lineHeight: .92, letterSpacing: -5, color: WHITE, WebkitTextStroke: "2px #071019a0", paintOrder: "stroke fill", textShadow: "0 4px 0 #03080bc0, 0 10px 28px #000d"};
const displayInk: React.CSSProperties = {fontWeight: 700, lineHeight: .88, letterSpacing: -6, textShadow:'0 4px 0 #0008, 0 14px 30px #000b'};
const Stamp: React.FC<{text: string}> = ({text}) => <div style={{position: "absolute", left: 42, bottom: 32, fontSize: 23, padding: "7px 12px", background: "#060b12b0", color: "#d4dde4", letterSpacing: 1}}>{text}</div>;
const Film: React.FC<{file: string; style?: React.CSSProperties; playbackRate?: number}> = ({file, style, playbackRate = 1}) => <OffthreadVideo src={clip(file)} muted playbackRate={playbackRate} style={{width: "100%", height: "100%", objectFit: "cover", ...style}} />;

const Form: React.FC = () => {
  const f = useCurrentFrame();
  const reveal = smooth(ramp(f, 48, 88));
  const settle = spring({frame: Math.max(0, f - 62), fps: 30, config: {damping: 16, stiffness: 145, mass: .8}});
  return <AbsoluteFill style={{background: BG}}>
    <AbsoluteFill style={{clipPath: `polygon(0 0,${100 - reveal * 44}% 0,${100 - reveal * 50}% 100%,0 100%)`, transform: `scale(${1.035 - reveal * .035})`, transformOrigin: "30% 50%"}}>
      {f < 60 ? <Film file="mouz_action_v2" style={{transform: `translateX(${-reveal * 280}px)`}} /> : <Img src={staticFile("video10/editorial/mouz_freeze.jpg")} style={{width: "100%", height: "100%", objectFit: "cover", transform: `translateX(${-reveal * 280}px)`}} />}
      <AbsoluteFill style={{background: "linear-gradient(90deg,transparent 60%,#080d1350)"}} />
    </AbsoluteFill>
    <div style={{position: "absolute", left: 65, bottom: 130, width: 920, height: 330, background: "radial-gradient(ellipse at 30% 60%,#03080b9c,transparent 72%)", opacity: ramp(f, 4, 16) * ramp(f, 38, 54, 1, 0)}} />
    <div style={{...footageInk, position: "absolute", left: 90, top: 630, fontSize: 245, opacity: ramp(f, 4, 16) * ramp(f, 38, 54, 1, 0), transform: `translateY(${ramp(f, 4, 20, 65, 0)}px)`}}>FORM<span style={{color: RED}}>.</span></div>
    <div style={{position: "absolute", left: 1090, top: 145, width: 700, textAlign: "center", opacity: ramp(f, 62, 72), transform: `translateY(${(1 - settle) * 65}px) scale(${.85 + settle * .15})`}}>
      <div style={{display: "flex", justifyContent: "center"}}><Logo team="MOUZ" size={150} /></div>
      <div style={{...displayInk, fontSize: 390, color: RED}}>0</div>
      <div style={{...displayInk, fontSize: 105, letterSpacing: -3, marginTop: 24}}>MAPS<br />DROPPED</div>
      <div style={{fontSize: 29, color: "#b4c0ca", marginTop: 32, letterSpacing: 2}}>IEM BEIJING 2026</div>
    </div>
    <div style={{position: "absolute", left: `${100 - reveal * 47}%`, top: 0, width: 3, height: "100%", background: RED, opacity: reveal * .45, transform: "skewX(-6deg)"}} />
    <Stamp text={f < 60 ? "ESLCS · Beijing final" : "HELD FRAME · ESLCS · Beijing final"} />
  </AbsoluteFill>;
};

const Momentum: React.FC = () => {
  const f = useCurrentFrame(), reveal = smooth(ramp(f, 43, 67));
  return <AbsoluteFill style={{background: BG, clipPath: `inset(${ramp(f, 0, 14, 100, 0)}% 0 0 0)`}}>
    <AbsoluteFill style={{transform: `scale(${ramp(f, 0, 140, 1.07, 1.01)})`, transformOrigin: "65% 50%"}}>
      <Film file="yekindar_reaction_v2" />
    </AbsoluteFill>
    <AbsoluteFill style={{background: `linear-gradient(90deg,rgba(8,13,19,${reveal * .98}) 0%,rgba(8,13,19,${reveal * .9}) 27%,transparent 72%)`}} />
    <AbsoluteFill style={{background: "linear-gradient(0deg,#03080bce,transparent 55%)", opacity: ramp(f, 16, 27) * ramp(f, 49, 65, 1, 0)}} />
    <div style={{...footageInk, position: "absolute", left: 85, top: 715, fontSize: 208, letterSpacing: -7, opacity: ramp(f, 16, 27) * ramp(f, 49, 65, 1, 0), clipPath: `inset(0 0 ${ramp(f, 16, 35, 100, 0)}% 0)`}}>MOMENTUM<span style={{color: GREEN}}>.</span></div>
    <div style={{...footageInk, position: "absolute", left: 120, top: 225, width: 800, opacity: reveal, transform: `translateX(${(1 - reveal) * -90}px)`}}>
      <div style={{fontSize: 335, color: GREEN, lineHeight: .9}}>3</div>
      <div style={{fontSize: 118, letterSpacing: -4, marginTop: 8}}>TROPHIES</div>
      <div style={{marginTop: 25, fontSize: 74, letterSpacing: -1}}>IN 4 EVENTS</div>
    </div>
    <Stamp text="BLASTPremier · Hong Kong final · player reaction" />
  </AbsoluteFill>;
};

const Experience: React.FC<{tempo?:number}> = ({tempo=1}) => {
  const f = useCurrentFrame()*tempo, transition = smooth(ramp(f, 57, 90));
  return <AbsoluteFill style={{background: BG}}>
    {f < 90 && <AbsoluteFill style={{opacity: 1 - transition}}>
      <Film file="zywoo_archive" />
      <AbsoluteFill style={{background: "linear-gradient(0deg,#03080bea,transparent 75%)"}} />
      <div style={{...footageInk, position: "absolute", left: 85, bottom: 160, fontSize: 205, letterSpacing: -8, transform: `translateY(${ramp(f, 5, 25, 70, 0)}px)`, opacity: ramp(f, 5, 20)}}>EXPERIENCE<span style={{color: GOLD}}>.</span></div>
      <Stamp text="ARCHIVE · BLAST Rivals S1 2026 · BLASTPremier" />
    </AbsoluteFill>}
    <AbsoluteFill style={{opacity: transition, background: "radial-gradient(ellipse at 50% 35%,#ffd34d18,transparent 65%)"}}>
      <div style={{position: "absolute", top: 150, left: 130, transform: `scale(${.8 + transition * .2})`}}><Logo team="Vitality" size={170} /></div>
      <div style={{...displayInk, position: "absolute", left: 130, top: 395, width: 780, opacity: ramp(f, 78, 94)}}><div style={{fontSize: 123, letterSpacing: -4}}>THE FULL</div><div style={{fontSize: 292, color: GOLD, marginTop: 16}}>FIVE.</div></div>
      {["apEX", "ZywOo", "flameZ", "mezii", "ropz"].map((name, i) => {
        const p = spring({frame: Math.max(0, f - 99 - i * 8), fps: 30, config: {damping: 18, stiffness: 140}});
        return <div key={name} style={{position: "absolute", left: 1080, top: 235 + i * 115, width: 650, fontSize: 105, fontWeight: 700, letterSpacing: -3, lineHeight: 1, opacity: ramp(f, 99 + i * 8, 109 + i * 8), transform: `translateX(${(1 - p) * 90}px)`}}><span style={{display: "inline-block", width: 65, fontSize: 27, letterSpacing: 2, color: "#71818f", verticalAlign: "middle"}}>0{i + 1}</span>{name}</div>;
      })}
      <div style={{position: "absolute", top: 925, left: 130, fontSize: 29, color: "#b4c0ca", letterSpacing: 3, opacity: ramp(f, 140, 155)}}>EXPECTED SINGAPORE LINEUP</div>
    </AbsoluteFill>
  </AbsoluteFill>;
};

const Question: React.FC = () => {
  const f = useCurrentFrame(), dark = smooth(ramp(f, 120, 148));
  return <AbsoluteFill style={{background: BG}}>
    {f < 150 && ["MOUZ", "FURIA", "Vitality"].map((team, i) => <div key={team} style={{position: "absolute", left: i * 640, width: 640, height: "100%", overflow: "hidden", opacity: 1 - dark}}>
      <AbsoluteFill style={{transform: `translateY(${ramp(f, i * 4, 24 + i * 4, i % 2 ? -100 : 100, 0)}px)`}}>
      {i === 0 ? <Img src={staticFile("video10/editorial/mouz_freeze.jpg")} style={{width: "100%", height: "100%", objectFit: "cover"}} /> : <Film file={i === 1 ? "furia_hongkong_close" : "revision_opening_vitality_triptych"} />}
      <AbsoluteFill style={{background: "#080d1370", justifyContent: "center", alignItems: "center"}}><Logo team={team} size={210} /></AbsoluteFill>
      </AbsoluteFill>
      <div style={{position: "absolute", left: 22, bottom: 30, fontSize: 23, color: "#d4dde4", background: "#080d13b0", padding: "6px 10px"}}>{["HELD FRAME · ESLCS · Beijing", "BLASTPremier · Hong Kong", "ARCHIVE · BLAST Rivals S1 2026"][i]}</div>
    </div>)}
    <div style={{...displayInk, position: "absolute", top: 220, left: 210, width: 1500, textAlign: "center", transform: `scale(${ramp(f, 143, 184, .94, 1)})`}}>
      <div style={{fontSize: 110, letterSpacing: -2, opacity: ramp(f, 132, 148)}}>WHO HAS</div>
      <div style={{fontSize: 195, marginTop: 23, opacity: ramp(f, 136, 152)}}>WHAT IT</div>
      <div style={{fontSize: 264, marginTop: 16, opacity: ramp(f, 140, 156)}}>TAKES<span style={{color: GOLD}}>?</span></div>
    </div>
  </AbsoluteFill>;
};

export const Video10EditorialSample: React.FC = () => {
  const f = useCurrentFrame();
  const pause = f < 625 ? ramp(f, 615, 625, 1, 0) : f < 637 ? 0 : ramp(f, 637, 647);
  const music = ramp(f, 0, 18) * ramp(f, 648, 690, 1, 0) * pause * .25;
  return <AbsoluteFill style={{background: BG, color: WHITE, fontFamily: FONT, overflow: "hidden"}}>
    <Sequence durationInFrames={150}><Form /></Sequence>
    <Sequence from={150} durationInFrames={150}><Momentum /></Sequence>
    <Sequence from={300} durationInFrames={180}><Experience /></Sequence>
    <Sequence from={480} durationInFrames={210}><Question /></Sequence>
    <Audio src={staticFile("video10/editorial/music-tension-soft.mp3")} trimBefore={150} volume={music} />
    {[62, 225, 645].map(at => <Sequence key={at} from={at} durationInFrames={24}><Audio src={staticFile("video10/editorial/impact-soft-1.wav")} volume={.55} /></Sequence>)}
    {[150, 300].map(at => <Sequence key={at} from={at} durationInFrames={15}><Audio src={staticFile("video10/editorial/whoosh-short.wav")} volume={.6} /></Sequence>)}
  </AbsoluteFill>;
};

// Preserve the approved treatment and 16–20s triptych hold; align team handoffs to speech.
export const Video10OpeningFinal:React.FC<{furiaAt:number;vitalityAt:number;simulationAt:number}>=({furiaAt,vitalityAt,simulationAt})=>{
  const f=useCurrentFrame(),p=smooth(ramp(f,simulationAt,simulationAt+60));
  return <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,overflow:"hidden"}}>
    <Sequence durationInFrames={furiaAt}><Form/></Sequence>
    <Sequence from={furiaAt} durationInFrames={vitalityAt-furiaAt}><Momentum/></Sequence>
    <Sequence from={vitalityAt} durationInFrames={simulationAt-vitalityAt}><Experience tempo={1.3}/></Sequence>
    <Sequence from={simulationAt} durationInFrames={480-simulationAt}>
      <AbsoluteFill style={{background:BG}}>
        {["MOUZ","FURIA","Vitality"].map((team,i)=><div key={team} style={{position:"absolute",left:300+i*560,top:155+(1-p)*100,transform:`scale(${.85+.15*p})`}}><Logo team={team} size={200}/></div>)}
        <div style={{...displayInk,position:"absolute",left:140,top:490,fontSize:155,clipPath:`inset(0 ${100*(1-p)}% 0 0)`}}>WE SIMULATED<br/><span style={{color:GOLD}}>SINGAPORE.</span></div>
        <div style={{position:"absolute",left:150,top:905,width:1610,height:5,background:GOLD,transform:`scaleX(${p})`,transformOrigin:"left"}}/>
      </AbsoluteFill>
    </Sequence>
    <Sequence from={480} durationInFrames={210}><Question/></Sequence>
  </AbsoluteFill>;
};
