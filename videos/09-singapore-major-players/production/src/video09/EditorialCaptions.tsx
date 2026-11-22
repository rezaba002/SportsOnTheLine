import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { FONT } from "../theme";
import { CapCue } from "../cards/Captions";
import moments from "../../public/data/video09_emphasis.json";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const smooth = Easing.bezier(.22, .7, .25, 1);
const show = (f: number, at: number, duration: number) => interpolate(f, [at, at + duration], [0, 1], { ...clamp, easing: smooth });
const names = new Set(["donk", "sh1ro", "zywoo", "m0nesy", "zont1x", "nilo", "martinezsa", "brollan", "susp", "jame", "910", "niko", "kyousuke", "karrigan", "awp"]);
export const isEmphasisFrame = (f: number) => moments.some(m => f >= m.from && f < m.from + m.dur);

export const EditorialCaptions: React.FC<{ cues: CapCue[] }> = ({ cues }) => {
  const f = useCurrentFrame();
  if (isEmphasisFrame(f)) return null;
  const cue = cues.find(c => f >= c.s && f <= c.e);
  if (!cue) return null;
  const p = show(f, cue.s, 6);
  return <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 35, pointerEvents: "none", zIndex: 30 }}>
    <div style={{ maxWidth: 1440, padding: "8px 25px 10px", borderLeft: "4px solid #edff35", background: "linear-gradient(90deg,#080f14c0,#080f1420)", opacity: p, transform: `translateY(${(1 - p) * 7}px)`, textAlign: "left", fontFamily: FONT, fontWeight: 700, fontVariationSettings: "'wdth' 90, 'wght' 700", fontSize: 44, lineHeight: 1.18, letterSpacing: .4, color: "#f6f7f0", textShadow: "0 2px 5px #000, 0 1px 2px #000" }}>
      {cue.lines.map((line, i) => <div key={i} style={{ whiteSpace: "nowrap" }}>
        {line.map((w, j) => <span key={j} style={{ color: names.has(w.w.toLowerCase().replace(/'s\b/g, "").replace(/[^a-z0-9]/g, "")) ? "#edff35" : "#f6f7f0" }}>{w.w}{j < line.length - 1 ? " " : ""}</span>)}
      </div>)}
    </div>
  </AbsoluteFill>;
};

export const EmphasisMoments: React.FC = () => {
  const f = useCurrentFrame(), moment = moments.find(m => f >= m.from && f < m.from + m.dur);
  if (!moment) return null;
  const local = f - moment.from, fade = show(local, 0, 6) * (1 - show(local, moment.dur - 6, 6));
  return <AbsoluteFill style={{ backgroundColor: "#080f14", opacity: fade, fontFamily: FONT, overflow: "hidden", zIndex: 20 }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(#29404a33 1px,transparent 1px),linear-gradient(90deg,#29404a33 1px,transparent 1px)", backgroundSize: "96px 96px" }} />
    <div style={{ position: "absolute", left: 90, top: 75, color: "#a0b4b5", fontSize: 24, letterSpacing: 5 }}>SPORTS ON THE LINE</div>
    <div style={{ position: "absolute", left: 90, top: 215, color: "#73cbff", fontSize: 29, letterSpacing: 5, opacity: show(local, 3, 10) }}>{moment.tag}</div>
    <div style={{ position: "absolute", left: 110, right: 110, top: 320 }}>
      {moment.lines.map((line, i) => {
        const p = show(local, i * 5, 15), size = Math.min(line === "+1" ? 210 : 174, 1550 / Math.max(1, line.length * .5));
        return <div key={i} style={{ fontSize: size, fontWeight: 800, fontVariationSettings: "'wdth' 90, 'wght' 800", letterSpacing: -2, lineHeight: 1.08, color: i ? "#edff35" : "#f6f7f0", opacity: p, transform: `translateY(${(1 - p) * 28}px)` }}>{line}</div>;
      })}
      <div style={{ height: 6, width: 1100, backgroundColor: "#edff35", marginTop: 28, transformOrigin: "left", transform: `scaleX(${show(local, 6, 18)})` }} />
      {moment.note && <div style={{ fontSize: 29, letterSpacing: 3, marginTop: 30, color: "#a0b4b5", opacity: show(local, 15, 12) }}>{moment.note}</div>}
    </div>
    <div style={{ position: "absolute", right: 95, bottom: 75, width: 90, height: 90, borderTop: "3px solid #73cbff", borderRight: "3px solid #73cbff" }} />
  </AbsoluteFill>;
};
