import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { C, FONT } from "../theme";
import { teamLogo } from "../teams";
import { Halo } from "../cards/fx";

// Video 07 thumbnail (1280x720): the best move vs standing still. Left MOUZ +16 (PR in), right Spirit -10 (no change).
const GREEN = "#4cc878", RED = "#e44c4c", YELLOW = "#ffd34d";
const COND: React.CSSProperties = { fontVariationSettings: "'wdth' 75, 'wght' 700", fontWeight: 700 };
const Big: React.FC<{ team: string; w: number; h: number; style?: React.CSSProperties }> = ({ team, w, h, style }) => (
  <Img src={teamLogo(team) ?? ""} style={{ width: w, height: h, objectFit: "contain", position: "relative", ...style }} />
);

export const Thumb07: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden", backgroundColor: "#121419" }}>
    <AbsoluteFill style={{ background: `linear-gradient(105deg, #12301f 0%, #12301f 49.6%, #3a1416 50.4%, #3a1416 100%)` }} />
    <AbsoluteFill style={{ opacity: 0.15, backgroundImage: "repeating-radial-gradient(circle at 50% 50%, rgba(255,255,255,0.08) 0 1px, transparent 1px 3px)" }} />
    {/* left: the best move */}
    <div style={{ position: "absolute", left: 40, top: 150, width: 560, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Halo color={RED} size={560} strength={0.9} /><Big team="MOUZ" w={500} h={200} />
    </div>
    <div style={{ position: "absolute", left: 70, top: 410, ...COND, fontSize: 64, color: GREEN, textShadow: "0 4px 0 #000" }}>+PR</div>
    <div style={{ position: "absolute", left: 300, top: 380, ...COND, fontSize: 210, lineHeight: 1, color: GREEN, textShadow: `0 6px 0 #000, 0 0 40px ${GREEN}88` }}>+16</div>
    {/* right: standing still */}
    <div style={{ position: "absolute", right: 50, top: 140, width: 520, height: 300, display: "flex", alignItems: "center", justifyContent: "center", filter: "grayscale(0.5)" }}>
      <Halo color="#ffffff" size={520} strength={0.6} /><Big team="Spirit" w={480} h={210} />
    </div>
    <div style={{ position: "absolute", right: 300, top: 380, ...COND, fontSize: 210, lineHeight: 1, color: RED, textShadow: `0 6px 0 #000, 0 0 40px ${RED}88` }}>−10</div>
    <div style={{ position: "absolute", right: 40, top: 430, padding: "6px 18px", border: `6px solid ${RED}`, borderRadius: 12, color: RED, ...COND, fontSize: 52, rotate: "-7deg",
      backgroundColor: "rgba(14,17,23,0.85)" }}>NO CHANGE</div>
    {/* question */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 18, textAlign: "center", transform: "skewX(-8deg)", ...COND, fontSize: 118, lineHeight: 1, textShadow: "0 7px 0 #000" }}>
      WHICH MOVES <span style={{ color: YELLOW }}>WORKED?</span>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 26, textAlign: "center", ...COND, fontSize: 44, color: "#e7d8bd", letterSpacing: 4, textShadow: "0 3px 0 #000" }}>
      EVERY CS2 ROSTER CHANGE SINCE COLOGNE
    </div>
  </AbsoluteFill>
);
