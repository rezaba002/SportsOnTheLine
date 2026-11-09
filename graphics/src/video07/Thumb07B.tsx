import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, FONT } from "../theme";
import { teamLogo } from "../teams";

// Video 07 thumbnail v2 (1280x720): the season's best move (PR -> MOUZ, +16) and the super-sub (jL).
// Player cut-outs (owner's photos, rembg) get a white stroke + coloured glow + drop shadow.
const GREEN = "#4cc878", YELLOW = "#ffd34d";
const COND: React.CSSProperties = { fontVariationSettings: "'wdth' 75, 'wght' 700", fontWeight: 700 };

// stroke = 8 hard drop-shadows around the cut-out; then a coloured glow and a dark shadow for depth
const stroke = (w: number, col: string) =>
  [[w, 0], [-w, 0], [0, w], [0, -w], [w * 0.7, w * 0.7], [-w * 0.7, w * 0.7], [w * 0.7, -w * 0.7], [-w * 0.7, -w * 0.7]]
    .map(([x, y]) => `drop-shadow(${x}px ${y}px 0 ${col})`).join(" ");
const playerFx = (glow: string) => `${stroke(5, "#ffffff")} drop-shadow(0 0 22px ${glow}) drop-shadow(0 0 48px ${glow}aa) drop-shadow(0 18px 24px rgba(0,0,0,0.75))`;

export const Thumb07B: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden", backgroundColor: "#0d0f13" }}>
    {/* background: green left, gold right, light rays, grain */}
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 18% 60%, ${GREEN}55 0%, transparent 45%), radial-gradient(ellipse at 85% 55%, ${YELLOW}4d 0%, transparent 45%), linear-gradient(180deg, #161a22 0%, #0b0d11 100%)` }} />
    <AbsoluteFill style={{ background: "repeating-linear-gradient(115deg, rgba(255,255,255,0.035) 0 2px, transparent 2px 46px)" }} />
    <AbsoluteFill style={{ opacity: 0.16, backgroundImage: "repeating-radial-gradient(circle at 40% 40%, rgba(255,255,255,0.08) 0 1px, transparent 1px 3px)" }} />
    {/* soft dark column behind the headline, so the words read over the photos */}
    <AbsoluteFill style={{ background: "radial-gradient(ellipse 22% 55% at 50% 38%, rgba(8,10,14,0.85) 0%, rgba(8,10,14,0) 100%)" }} />
    {/* PR (left) */}
    <Img src={staticFile("thumb/pr_cut.png")} style={{ position: "absolute", left: -40, bottom: -10, height: 590, filter: playerFx(GREEN) }} />
    {/* jL (right) */}
    <Img src={staticFile("thumb/jl_cut.png")} style={{ position: "absolute", right: -70, bottom: -10, height: 600, filter: playerFx(YELLOW) }} />
    {/* center headline */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 36, textAlign: "center", transform: "skewX(-8deg)", ...COND, fontSize: 130, lineHeight: 0.86, letterSpacing: 1,
      textShadow: "0 8px 0 #000, 0 0 40px rgba(0,0,0,0.8)" }}>
      WHICH<br />MOVES<br /><span style={{ color: YELLOW }}>WORKED?</span>
    </div>
    {/* PR badge */}
    <div style={{ position: "absolute", left: 290, bottom: 40, display: "flex", alignItems: "center", gap: 14, padding: "6px 22px 6px 14px", borderRadius: 16, backgroundColor: "rgba(10,14,12,0.88)",
      border: `4px solid ${GREEN}`, boxShadow: `0 0 34px ${GREEN}88`, rotate: "-4deg" }}>
      <Img src={teamLogo("MOUZ") ?? ""} style={{ width: 110, height: 60, objectFit: "contain" }} />
      <span style={{ ...COND, fontSize: 96, lineHeight: 1, color: GREEN, textShadow: `0 0 24px ${GREEN}` }}>+16</span>
    </div>
    {/* jL badge */}
    <div style={{ position: "absolute", right: 280, bottom: 54, padding: "8px 24px", borderRadius: 14, backgroundColor: "rgba(16,14,8,0.9)", border: `4px solid ${YELLOW}`,
      boxShadow: `0 0 34px ${YELLOW}88`, rotate: "4deg", ...COND, fontSize: 62, lineHeight: 1, color: YELLOW }}>SUPER-SUB</div>
  </AbsoluteFill>
);
