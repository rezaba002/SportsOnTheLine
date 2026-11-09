import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { FONT } from "../theme";

// Video 07 thumbnail round 3 (after a 1.3% early CTR): bigger players, no boxes, huge outlined text low across the
// jerseys (never on faces). A "BEST TRANSFER?", B "WORTH IT?" + big +16, C "TRANSFER MVP" with CS2's MVP star.
type V = "A" | "B" | "C";
const GREEN = "#3ee07a", YELLOW = "#ffd23a", WHITE = "#ffffff";
const COND: React.CSSProperties = { fontFamily: FONT, fontVariationSettings: "'wdth' 75, 'wght' 700", fontWeight: 700 };
const stroke = (w: number, col: string) =>
  [[w, 0], [-w, 0], [0, w], [0, -w], [w * 0.7, w * 0.7], [-w * 0.7, w * 0.7], [w * 0.7, -w * 0.7], [-w * 0.7, -w * 0.7]].map(([x, y]) => `drop-shadow(${x}px ${y}px 0 ${col})`).join(" ");
const playerFx = (glow: string) => `${stroke(6, WHITE)} drop-shadow(0 0 26px ${glow}) drop-shadow(0 0 60px ${glow}99)`;
const fade = "linear-gradient(to bottom, black 70%, transparent 98%)";
// heavy outlined text: thick black outline (text-stroke drawn behind the fill) + hard drop shadow
const Shout: React.FC<{ children: React.ReactNode; size: number; color: string; style?: React.CSSProperties }> = ({ children, size, color, style }) => (
  <div style={{ ...COND, fontSize: size, lineHeight: 0.9, color, WebkitTextStroke: `${size * 0.11}px #000`, paintOrder: "stroke fill",
    filter: `drop-shadow(0 ${size * 0.07}px 0 #000) drop-shadow(0 0 ${size * 0.25}px rgba(0,0,0,0.6))`, letterSpacing: size * 0.01, whiteSpace: "nowrap", ...style }}>{children}</div>
);
const Star: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ filter: `drop-shadow(0 0 18px ${YELLOW}) drop-shadow(0 6px 0 #000)` }}>
    <path d="M50 4 L62 37 L97 38 L69 59 L79 93 L50 73 L21 93 L31 59 L3 38 L38 37 Z" fill={YELLOW} stroke="#000" strokeWidth="5" strokeLinejoin="round" />
  </svg>
);

export const Thumb07W: React.FC<{ v: V }> = ({ v }) => (
  <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#07090c" }}>
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 22% 40%, ${GREEN}66 0%, transparent 50%), radial-gradient(ellipse at 80% 38%, ${YELLOW}55 0%, transparent 50%), linear-gradient(180deg, #11151c 0%, #050608 100%)` }} />
    <AbsoluteFill style={{ background: "repeating-linear-gradient(115deg, rgba(255,255,255,0.04) 0 3px, transparent 3px 52px)" }} />
    {/* players: bigger, faces in the top 2/3, bodies fade out at the bottom */}
    <Img src={staticFile("thumb/pr_cut.png")} style={{ position: "absolute", left: -40, top: 8, height: 640, filter: playerFx(GREEN), WebkitMaskImage: fade, maskImage: fade }} />
    <Img src={staticFile("thumb/jl_cut.png")} style={{ position: "absolute", right: -60, top: 20, height: 620, filter: playerFx(YELLOW), WebkitMaskImage: fade, maskImage: fade }} />
    {v === "A" ? (
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 26, display: "flex", justifyContent: "center", transform: "rotate(-3deg)" }}>
        <Shout size={190} color={WHITE}>BEST <span style={{ color: GREEN }}>TRANSFER?</span></Shout>
      </div>
    ) : null}
    {v === "B" ? (
      <>
        <div style={{ position: "absolute", left: 535, top: 105, transform: "rotate(-6deg)" }}><Shout size={200} color={GREEN}>+16</Shout></div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 24, display: "flex", justifyContent: "center", transform: "rotate(-3deg)" }}>
          <Shout size={210} color={YELLOW}>WORTH IT?</Shout>
        </div>
      </>
    ) : null}
    {v === "C" ? (
      <>
        <div style={{ position: "absolute", left: 590, top: 70, transform: "rotate(-8deg)" }}><Star size={190} /></div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 26, display: "flex", justifyContent: "center", transform: "rotate(-3deg)" }}>
          <Shout size={190} color={WHITE}>TRANSFER <span style={{ color: YELLOW }}>MVP</span></Shout>
        </div>
      </>
    ) : null}
  </AbsoluteFill>
);
