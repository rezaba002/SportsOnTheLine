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


type Variant = "A" | "B" | "C";
const Headline: React.FC<{ v: Variant }> = ({ v }) => {
  if (v === "A") return (   // CS2 round-win banner style
    <div style={{ position: "absolute", left: 0, right: 0, top: 46, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ width: 760, height: 10, background: `linear-gradient(90deg, transparent, ${YELLOW}, transparent)` }} />
      <div style={{ width: 760, padding: "14px 0 18px", textAlign: "center", background: "linear-gradient(90deg, rgba(10,12,16,0) 0%, rgba(10,12,16,0.92) 18%, rgba(10,12,16,0.92) 82%, rgba(10,12,16,0) 100%)" }}>
        <div style={{ ...COND, fontSize: 64, letterSpacing: 6, color: C.white, lineHeight: 1 }}>WHO WON</div>
        <div style={{ ...COND, fontSize: 132, letterSpacing: 2, color: YELLOW, lineHeight: 0.95, textShadow: `0 0 30px ${YELLOW}66` }}>ROSTER MANIA?</div>
      </div>
      <div style={{ width: 760, height: 10, background: `linear-gradient(90deg, transparent, ${YELLOW}, transparent)` }} />
    </div>
  );
  if (v === "B") return (   // fits the clear column between the two heads (x ~480-860), on a dark plate
    <div style={{ position: "absolute", left: 468, width: 400, top: 30, textAlign: "center", ...COND, lineHeight: 0.9 }}>
      <div style={{ position: "absolute", inset: "-14px -18px -18px -18px", borderRadius: 18, background: "radial-gradient(ellipse at 50% 45%, rgba(8,10,14,0.92) 0%, rgba(8,10,14,0.75) 60%, rgba(8,10,14,0) 100%)" }} />
      <div style={{ position: "relative", transform: "skewX(-8deg)", textShadow: "0 7px 0 #000" }}>
        <div style={{ fontSize: 108 }}>BEST</div>
        <div style={{ fontSize: 112, color: GREEN, textShadow: `0 7px 0 #000, 0 0 26px ${GREEN}66` }}>TRANSFER</div>
        <div style={{ fontSize: 50, letterSpacing: 2, marginTop: 10, whiteSpace: "nowrap" }}>OF THE <span style={{ color: YELLOW, textShadow: `0 5px 0 #000, 0 0 22px ${YELLOW}88` }}>CS2</span> SEASON</div>
      </div>
    </div>
  );
  return (   // C: a CS2 kill-feed line
    <div style={{ position: "absolute", left: 0, right: 0, top: 60, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, padding: "12px 26px", borderRadius: 8, backgroundColor: "rgba(0,0,0,0.78)", border: "3px solid #c0392b" }}>
        <span style={{ ...COND, fontSize: 78, color: "#8fb8ff" }}>PR</span>
        <svg width="110" height="44" viewBox="0 0 110 44"><path d="M4 26 L64 18 L70 12 L96 12 L96 20 L106 20 L106 26 L72 28 L60 40 L48 40 L54 30 L4 32 Z" fill="#fff" /></svg>
        <svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="16" fill="none" stroke="#fff" strokeWidth="4" /><circle cx="20" cy="20" r="5" fill="#fff" /></svg>
        <span style={{ ...COND, fontSize: 78, color: "#f5c96a" }}>MOUZ #1</span>
      </div>
      <div style={{ ...COND, fontSize: 70, letterSpacing: 4, textShadow: "0 6px 0 #000" }}>ROSTER MOVES <span style={{ color: YELLOW }}>RANKED</span></div>
    </div>
  );
};

export const Thumb07V: React.FC<{ v: Variant }> = ({ v }) => (
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
    <Headline v={v} />
    {/* PR badge */}
    <div style={{ position: "absolute", left: 290, bottom: 40, display: "flex", alignItems: "center", gap: 14, padding: "6px 22px 6px 14px", borderRadius: 16, backgroundColor: "rgba(10,14,12,0.88)",
      border: `4px solid ${GREEN}`, boxShadow: `0 0 34px ${GREEN}88`, rotate: "-4deg" }}>
      <Img src={teamLogo("MOUZ") ?? ""} style={{ width: 110, height: 60, objectFit: "contain" }} />
      <span style={{ ...COND, fontSize: 96, lineHeight: 1, color: GREEN, textShadow: `0 0 24px ${GREEN}` }}>+16</span>
    </div>
    {/* jL badge */}
    <div style={{ position: "absolute", right: v === "B" ? 300 : 280, bottom: 44, padding: "8px 22px", borderRadius: 14, backgroundColor: "rgba(16,14,8,0.9)", border: `4px solid ${YELLOW}`,
      boxShadow: `0 0 34px ${YELLOW}88`, rotate: "4deg", ...COND, fontSize: v === "B" ? 56 : 62, lineHeight: 1, color: YELLOW }}>{v === "B" ? "BEST STAND-IN" : "SUPER-SUB"}</div>
  </AbsoluteFill>
);
