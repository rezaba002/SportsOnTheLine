import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { C, FONT } from "../theme";
import { teamColor } from "../teams";
import { Logo } from "../cards/parts";
import { Halo } from "../cards/fx";

// Video-05 thumbnails, 1280×720. Promise: HOW the invites were decided (the race to the line); the drops are the twist.
// A (chosen direction): CS2 look — dusty map tones, CT-blue / T-orange glow, scoreboard-style rows, the Major line as a
// red bomb-plant line with a C4. All drawn here, no game assets. B: the field split by the line.
const RED = "#e44c4c";
const GREEN = "#4cc878";
const YELLOW = "#ffd34d";
const CT = "#5d9cec";
const TT = "#ec963c";
const COND: React.CSSProperties = { fontVariationSettings: "'wdth' 75, 'wght' 700", fontWeight: 700 };

// a simple, original C4 drawing: block, wires, keypad, LED
const C4: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size * 0.62} viewBox="0 0 100 62">
    <rect x="2" y="10" width="96" height="48" rx="6" fill="#3a3f2a" stroke="#1d2016" strokeWidth="3" />
    <rect x="10" y="18" width="22" height="32" rx="2" fill="#6b6f4a" />
    <rect x="38" y="18" width="22" height="32" rx="2" fill="#6b6f4a" />
    <rect x="66" y="16" width="26" height="22" rx="3" fill="#15181c" />
    {[0, 1, 2].map((r) => [0, 1, 2].map((c) => <rect key={`${r}${c}`} x={69 + c * 7.5} y={19 + r * 5.6} width="5" height="3.6" rx="1" fill="#9aa3ad" />))}
    <circle cx="79" cy="46" r="5" fill={RED} />
    <path d="M14 10 C 20 -2, 40 -2, 46 10" stroke={RED} strokeWidth="3" fill="none" />
    <path d="M44 10 C 52 0, 66 0, 72 14" stroke={YELLOW} strokeWidth="3" fill="none" />
  </svg>
);

const ROWS_A = [
  { team: "Natus Vincere", w: 0.84, state: "up", rank: 10 },
  { team: "100 Thieves", w: 0.76, state: "up", rank: 18 },
  { team: "HOTU", w: 0.68, state: "down", rank: 19 },
  { team: "fnatic", w: 0.68, state: "down", rank: 20 },
] as const;

export const ThumbA: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden",
    background: `radial-gradient(ellipse at 18% 0%, #8a6a3e 0%, #3a2c1d 38%, #121419 75%)` }}>
    {/* grain + CT / T edge glow */}
    <AbsoluteFill style={{ opacity: 0.18, backgroundImage: "repeating-radial-gradient(circle at 30% 40%, rgba(255,255,255,0.08) 0 1px, transparent 1px 3px)" }} />
    <AbsoluteFill style={{ background: `linear-gradient(90deg, ${CT}44 0%, transparent 18%, transparent 82%, ${TT}44 100%)` }} />
    {/* title */}
    <div style={{ position: "absolute", left: 34, top: 14, transform: "skewX(-8deg)", ...COND, fontSize: 150, lineHeight: 0.95, letterSpacing: 2,
      textShadow: "0 6px 0 #000, 0 0 40px rgba(0,0,0,0.6)" }}>
      THE <span style={{ color: YELLOW }}>MAJOR</span> RACE
    </div>
    <div style={{ position: "absolute", left: 40, top: 160, ...COND, fontSize: 40, letterSpacing: 5, color: "#e7d8bd", textShadow: "0 3px 0 #000" }}>HOW THEY GOT INTO THE SINGAPORE MAJOR</div>
    {/* scoreboard rows */}
    {ROWS_A.map((r, i) => {
      const top = 236 + i * 112 + (i >= 2 ? 34 : 0);
      const col = r.state === "up" ? GREEN : RED;
      return (
        <div key={r.team} style={{ position: "absolute", left: 30, top, height: 96, width: 850 }}>
          <div style={{ position: "absolute", inset: 0, clipPath: "polygon(0 0, 100% 0, 97% 100%, 0 100%)", background: "linear-gradient(90deg, rgba(10,12,16,0.88), rgba(10,12,16,0.55))",
            borderLeft: `10px solid ${teamColor(r.team)}` }} />
          <div style={{ position: "absolute", left: 22, top: 18, width: 60, height: 60, ...COND, fontSize: 40, color: C.muted, textAlign: "center", lineHeight: "60px" }}>{r.rank}</div>
          <div style={{ position: "absolute", left: 90, top: 4, width: 88, height: 88, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Halo color={teamColor(r.team)} size={150} strength={0.9} />
            <Logo team={r.team} size={84} />
          </div>
          <div style={{ position: "absolute", left: 196, top: 22, height: 52, width: 520 * r.w, borderRadius: 4, backgroundColor: col, boxShadow: `0 0 28px ${col}99`,
            clipPath: "polygon(0 0, 100% 0, calc(100% - 14px) 100%, 0 100%)" }} />
          <div style={{ position: "absolute", left: 196 + 520 * r.w + 18, top: 2, ...COND, fontSize: 84, lineHeight: 1, color: col, textShadow: `0 0 24px ${col}` }}>{r.state === "up" ? "▲" : "▼"}</div>
        </div>
      );
    })}
    {/* the Major line: red bomb-plant line with a C4 */}
    <div style={{ position: "absolute", left: 0, right: 0, top: 236 + 2 * 112 + 4, borderTop: `9px dashed ${RED}`, boxShadow: `0 0 34px 8px ${RED}66` }} />
    <div style={{ position: "absolute", left: 760, top: 236 + 2 * 112 - 40 }}><C4 size={120} /></div>
    <div style={{ position: "absolute", left: 30, top: 236 + 2 * 112 + 14, ...COND, fontSize: 30, color: "#ffb1b1", letterSpacing: 3, textShadow: "0 2px 0 #000", display: "none" }}>MAJOR LINE</div>
    {/* s1mple in the BC.Game jersey (photo: HLTV.org, used at the owner's request) */}
    <div style={{ position: "absolute", right: -10, bottom: 0, width: 470, height: 490 }}>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 55%, ${teamColor("BC.Game")}55 0%, transparent 62%)` }} />
      <Img src={staticFile("thumb/s1mple_bcgame.png")} style={{ position: "absolute", bottom: 0, width: 470, filter: "drop-shadow(0 0 24px rgba(0,0,0,0.8)) contrast(1.06)" }} />
    </div>
    <div style={{ position: "absolute", right: 30, top: 214, padding: "8px 18px", borderRadius: 10, backgroundColor: "rgba(10,12,16,0.88)", border: `3px solid ${YELLOW}`,
      boxShadow: `0 0 30px ${YELLOW}66`, rotate: "4deg", ...COND, fontSize: 46, color: YELLOW, lineHeight: 1 }}>
      S1MPLE IS BACK
    </div>
  </AbsoluteFill>
);

// B: the field split by the line
export const ThumbB: React.FC = () => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, #13261c 0%, ${C.bg} 48%, ${C.bg} 52%, #2a1416 100%)`, fontFamily: FONT, color: C.white }}>
    <div style={{ position: "absolute", left: 40, top: 30, fontSize: 92, fontWeight: 700, color: GREEN, lineHeight: 1 }}>WHO GOT IN</div>
    <div style={{ position: "absolute", right: 40, top: 40, display: "flex", gap: 20 }}>
      {["Vitality", "Natus Vincere", "FaZe", "100 Thieves"].map((t) => (
        <div key={t} style={{ width: 120, height: 120, borderRadius: 18, backgroundColor: C.panel, border: `2px solid ${GREEN}88`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 26px ${GREEN}44` }}>
          <Logo team={t} size={96} />
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 290, textAlign: "center", fontSize: 72, fontWeight: 700, letterSpacing: 4 }}>
      HOW THE <span style={{ color: YELLOW }}>MAJOR</span> WAS DECIDED
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 390, borderTop: `8px dashed ${YELLOW}`, boxShadow: `0 0 30px 6px ${YELLOW}55` }} />
    <div style={{ position: "absolute", left: 40, bottom: 40, fontSize: 92, fontWeight: 700, color: RED, lineHeight: 1 }}>WHO DROPPED</div>
    <div style={{ position: "absolute", right: 40, bottom: 34, display: "flex", gap: 20 }}>
      {["fnatic", "B8", "TYLOO", "NRG"].map((t, i) => (
        <div key={t} style={{ width: 120, height: 120, borderRadius: 18, backgroundColor: C.panel, border: `2px solid ${RED}88`, display: "flex", alignItems: "center", justifyContent: "center",
          translate: `0px ${i % 2 ? 14 : 0}px`, rotate: `${i % 2 ? 4 : -3}deg`, boxShadow: `0 0 26px ${RED}44` }}>
          <Logo team={t} size={96} style={{ filter: "grayscale(0.5)" }} />
        </div>
      ))}
    </div>
  </AbsoluteFill>
);
