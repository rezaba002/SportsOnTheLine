import React from "react";
import { AbsoluteFill, Img } from "remotion";
import { C, FONT } from "../theme";
import { teamLogo } from "../teams";
import { Halo } from "../cards/fx";

// New thumbnails for video 02 ("Every CS2 Major So Far", CTR 2.6% with the old one). Three variants for YouTube's
// thumbnail test. Hook from the video: FaZe reached 3 Major finals (Copenhagen, Shanghai, Budapest) and lost all 3.
// No player photos; the trophy is an original drawing (not the real Major trophy). 1280x720.
const RED = "#e44c4c", YELLOW = "#ffd34d", GOLD = "#e8b84a";
const COND: React.CSSProperties = { fontVariationSettings: "'wdth' 75, 'wght' 700", fontWeight: 700 };

const Trophy: React.FC<{ size: number; color?: string; dim?: boolean }> = ({ size, color = GOLD, dim }) => (
  <svg width={size} height={size * 1.2} viewBox="0 0 100 120" style={{ opacity: dim ? 0.45 : 1, filter: dim ? "grayscale(1)" : `drop-shadow(0 0 ${size / 8}px ${color}88)` }}>
    <path d="M22 8 H78 V30 C78 52 66 64 50 66 C34 64 22 52 22 30 Z" fill={color} />
    <path d="M22 14 H8 C8 34 16 42 26 44" stroke={color} strokeWidth="6" fill="none" />
    <path d="M78 14 H92 C92 34 84 42 74 44" stroke={color} strokeWidth="6" fill="none" />
    <rect x="44" y="64" width="12" height="22" fill={color} />
    <rect x="30" y="86" width="40" height="10" rx="2" fill={color} />
    <rect x="22" y="96" width="56" height="14" rx="3" fill={color} />
    <path d="M34 16 C34 40 40 52 50 56" stroke="rgba(255,255,255,0.35)" strokeWidth="5" fill="none" />
  </svg>
);
const Cross: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ position: "absolute", filter: `drop-shadow(0 0 10px ${RED})` }}>
    <path d="M14 14 L86 86 M86 14 L14 86" stroke={RED} strokeWidth="14" strokeLinecap="round" />
  </svg>
);
// logos fit inside a box (width x height), so tall logos (FaZe) don't overflow
const BigLogo: React.FC<{ team: string; width: number; height?: number; style?: React.CSSProperties }> = ({ team, width, height = width, style }) => (
  <Img src={teamLogo(team) ?? ""} style={{ width, height, objectFit: "contain", ...style }} />
);
const Bg: React.FC<{ tint?: string }> = ({ tint = "#3a1416" }) => (
  <>
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 30% 40%, ${tint} 0%, #121419 70%)` }} />
    <AbsoluteFill style={{ opacity: 0.16, backgroundImage: "repeating-radial-gradient(circle at 30% 40%, rgba(255,255,255,0.08) 0 1px, transparent 1px 3px)" }} />
  </>
);

// A — "THE CURSE": FaZe, three crossed trophies, 0 FOR 3
export const Thumb02A: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden" }}>
    <Bg />
    <div style={{ position: "absolute", left: 40, top: 30, width: 560, height: 430, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Halo color={RED} size={680} strength={1.3} />
      <BigLogo team="FaZe" width={520} height={410} style={{ position: "relative", filter: "drop-shadow(0 8px 0 #000)" }} />
    </div>
    <div style={{ position: "absolute", left: 80, bottom: 28, display: "flex", gap: 40 }}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Trophy size={130} dim />
          <Cross size={120} />
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", right: 50, top: 60, textAlign: "right", transform: "skewX(-8deg)" }}>
      <div style={{ ...COND, fontSize: 70, color: C.muted, letterSpacing: 2 }}>MAJOR FINALS</div>
      <div style={{ ...COND, fontSize: 300, lineHeight: 0.9, color: YELLOW, textShadow: "0 8px 0 #000, 0 0 50px rgba(255,211,77,0.35)" }}>0</div>
      <div style={{ ...COND, fontSize: 130, lineHeight: 0.9, textShadow: "0 6px 0 #000" }}>FOR 3</div>
    </div>
    <div style={{ position: "absolute", right: 50, bottom: 56, padding: "10px 22px", border: `5px solid ${RED}`, borderRadius: 10, color: RED, ...COND, fontSize: 54, letterSpacing: 3, rotate: "-5deg",
      backgroundColor: "rgba(14,17,23,0.85)", boxShadow: `0 0 26px ${RED}66` }}>CURSED?</div>
  </AbsoluteFill>
);

// B — "5 · 4 · 1": the five finals as trophies; FaZe in red three times
const FINALS = [
  { y: "2024", champ: "Natus Vincere", lost: "FaZe" }, { y: "2024", champ: "Spirit", lost: "FaZe" }, { y: "2025", champ: "Vitality", lost: "The MongolZ" },
  { y: "2025", champ: "Vitality", lost: "FaZe" }, { y: "2026", champ: "Falcons", lost: "FURIA" },
];
export const Thumb02B: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden" }}>
    <Bg tint="#2b2416" />
    <div style={{ position: "absolute", left: 0, right: 0, top: 26, textAlign: "center", ...COND, fontSize: 92, letterSpacing: 2, textShadow: "0 6px 0 #000" }}>
      5 MAJORS · <span style={{ color: YELLOW }}>4 CHAMPS</span> · <span style={{ color: RED }}>1 CURSE</span>
    </div>
    <div style={{ position: "absolute", left: 40, right: 40, top: 170, display: "flex", justifyContent: "space-between" }}>
      {FINALS.map((f, i) => (
        <div key={i} style={{ width: 228, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <Trophy size={92} />
          <div style={{ height: 100, display: "flex", alignItems: "center" }}><BigLogo team={f.champ} width={190} height={92} /></div>
          <div style={{ ...COND, fontSize: 30, color: C.muted }}>{f.y} FINAL · LOST BY</div>
          <div style={{ position: "relative", width: 210, height: 130, borderRadius: 14, display: "flex", alignItems: "center", justifyContent: "center",
            backgroundColor: f.lost === "FaZe" ? `${RED}30` : "rgba(255,255,255,0.05)", border: `4px solid ${f.lost === "FaZe" ? RED : "rgba(255,255,255,0.12)"}`,
            boxShadow: f.lost === "FaZe" ? `0 0 26px ${RED}77` : "none" }}>
            <BigLogo team={f.lost} width={180} height={f.lost === "FaZe" ? 112 : 90} style={{ opacity: f.lost === "FaZe" ? 1 : 0.4, filter: f.lost === "FaZe" ? "none" : "grayscale(1)" }} />
          </div>
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

// C — "WHO'S #6?": the five champions + a glowing empty slot for Singapore
export const Thumb02C: React.FC = () => (
  <AbsoluteFill style={{ fontFamily: FONT, color: C.white, overflow: "hidden" }}>
    <Bg tint="#1d2a3d" />
    <div style={{ position: "absolute", left: 50, top: 40, transform: "skewX(-8deg)", ...COND, fontSize: 150, lineHeight: 0.95, textShadow: "0 7px 0 #000" }}>
      WHO WINS<br /><span style={{ color: YELLOW }}>MAJOR #6?</span>
    </div>
    <div style={{ position: "absolute", left: 50, bottom: 50, display: "flex", gap: 14 }}>
      {FINALS.map((f, i) => (
        <div key={i} style={{ width: 132, height: 170, borderRadius: 16, backgroundColor: "rgba(255,255,255,0.06)", border: `3px solid ${GOLD}66`, display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center", gap: 6 }}>
          <BigLogo team={f.champ} width={112} height={90} />
          <div style={{ ...COND, fontSize: 28, color: GOLD }}>#{i + 1}</div>
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", right: 60, top: 150, width: 380, height: 470, borderRadius: 26, border: `6px dashed ${YELLOW}`, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", backgroundColor: "rgba(255,211,77,0.08)", boxShadow: `0 0 60px ${YELLOW}55` }}>
      <Trophy size={150} color={YELLOW} />
      <div style={{ ...COND, fontSize: 210, lineHeight: 0.9, color: YELLOW, textShadow: "0 0 40px rgba(255,211,77,0.6)" }}>?</div>
      <div style={{ ...COND, fontSize: 44, letterSpacing: 3 }}>SINGAPORE</div>
    </div>
  </AbsoluteFill>
);
