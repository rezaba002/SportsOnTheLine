import React from "react";
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../theme";
import {Logo} from "../cards/parts";
import config from "../../public/video10/scenario-sample/config.json";

export const SCENARIO_SAMPLE_FRAMES = config.frames;
const BG = "#080d13", WHITE = "#f1f4f5", GOLD = "#ffd34d", PURPLE = "#dca2ff", MUTED = "#9eacb8";
const ramp = (f: number, a: number, b: number, x = 0, y = 1) => interpolate(f, [a, b], [x, y], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
const display: React.CSSProperties = {fontWeight: 700, letterSpacing: -5, lineHeight: .9};

export const VitalityScenarioSample: React.FC = () => {
  const f = useCurrentFrame(), {roster, experience, caveat} = config.cues;
  const phase = f < roster ? 0 : f < experience ? 1 : f < caveat ? 2 : 3;
  const start = [0, roster, experience, caveat][phase];
  const enter = ramp(f, start, start + 12);
  const value = config.values[Math.min(phase, 2)];
  const dip = f < experience ? ramp(f, experience - 15, experience - 5, 1, 0) : ramp(f, experience + 3, experience + 16);
  const music = ramp(f, 0, 20) * ramp(f, config.frames - 35, config.frames, 1, 0) * dip * (phase === 3 ? .075 : config.voice ? .10 : .22);
  return <AbsoluteFill style={{background: BG, color: WHITE, fontFamily: FONT}}>
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 22% 42%,${phase === 2 ? "#dca2ff13" : "#ffd34d0b"},transparent 68%)`}} />
    {phase < 3 ? <>
      <div style={{position: "absolute", left: 130, top: 110}}><Logo team="Vitality" size={135} /></div>
      <div style={{position: "absolute", left: 130, top: 300, transform: `translateY(${(1 - enter) * 24}px)`, opacity: enter}}>
        <div style={{...display, fontSize: 300, color: GOLD}}>{value.toFixed(1)}<span style={{fontSize: 165, letterSpacing: -10}}>%</span></div>
        <div style={{fontSize: 37, color: MUTED, letterSpacing: 4, marginTop: 38}}>TITLE PROBABILITY</div>
      </div>
      <div style={{...display, position: "absolute", left: 1140, top: 340, fontSize: 102, color: phase === 2 ? PURPLE : WHITE, letterSpacing: -2}}>
        {["RECENT", "ROSTER", "ASSUMED"][phase]}<br />{["FORM", "ADJUSTED", "EXPERIENCE"][phase]}
      </div>
      {phase === 2 && <div style={{position: "absolute", left: 1140, top: 595, fontSize: 35, color: PURPLE, letterSpacing: 2}}>SENSITIVITY SCENARIO</div>}
      <div style={{position: "absolute", left: 130, top: 805, width: 1650, height: 26, background: "#26313b"}}>
        <div style={{width: `${value}%`, height: "100%", background: phase === 2 ? PURPLE : GOLD}} />
        {[0, 25, 50, 75, 100].map(tick => <div key={tick} style={{position: "absolute", left: `${tick}%`, top: -10, width: 1, height: 46, background: "#8b99a580"}}><div style={{position: "absolute", top: 65, left: -30, width: 65, textAlign: "center", fontSize: 30, color: MUTED}}>{tick}%</div></div>)}
      </div>
      <div style={{position: "absolute", left: 130, top: 965, fontSize: 27, letterSpacing: 2, color: MUTED}}>{["RECENCY-WEIGHTED BASELINE", "STAND-IN RESULTS DISCOUNTED", "EXPERIENCE EFFECT ASSUMED"][phase]}</div>
    </> : <>
      <div style={{position: "absolute", left: 135, top: 130, color: PURPLE, fontSize: 37, letterSpacing: 3}}>33.2% · ASSUMED SCENARIO</div>
      <div style={{...display, position: "absolute", left: 130, top: 330, opacity: enter, transform: `translateY(${(1 - enter) * 25}px)`}}>
        <div style={{fontSize: 190, color: PURPLE}}>SCENARIO.</div>
        <div style={{fontSize: 190, marginTop: 22}}>NOT PROOF.</div>
      </div>
      <div style={{position: "absolute", left: 140, top: 845, maxWidth: 1630, fontSize: 46, color: MUTED, lineHeight: 1.3}}>Historical test found no reliable improvement.</div>
    </>}
    <Audio src={staticFile("video10/editorial/music-tension-soft.mp3")} trimBefore={450} volume={music} />
    {config.voice && <Sequence from={config.voiceAt}><Audio src={staticFile("video10/scenario-sample/brian_pilot.mp3")} volume={1} /></Sequence>}
    {[roster, experience].map(at => <Sequence key={at} from={at} durationInFrames={12}><Audio src={staticFile("video10/editorial/click-soft.wav")} volume={.3} /></Sequence>)}
  </AbsoluteFill>;
};
