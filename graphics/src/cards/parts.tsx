import React from "react";
import { Img } from "remotion";
import { C, FONT } from "../theme";
import { teamLogo } from "../teams";

// Small building blocks shared by every card.

export const DARK_LOGOS = ["Voca", "Nemesis"];

export const Logo: React.FC<{ team: string; size: number; style?: React.CSSProperties }> = ({ team, size, style }) => {
  const src = teamLogo(team);
  if (!src) {
    return (
      <div style={{ width: size, height: size, borderRadius: size / 5, backgroundColor: C.line, color: C.white, fontFamily: FONT, fontWeight: 700, fontSize: size * 0.4, display: "flex", alignItems: "center", justifyContent: "center", ...style }}>
        {team.slice(0, 2).toUpperCase()}
      </div>
    );
  }
  return (
    <div style={{ width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center", ...style }}>
      <Img src={src} style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain", backgroundColor: DARK_LOGOS.includes(team) ? "rgba(238,240,245,0.92)" : undefined, borderRadius: 6 }} />
    </div>
  );
};

export const Delta: React.FC<{ value: number; size: number }> = ({ value, size }) => (
  <span style={{ color: value >= 0 ? C.win : C.loss, fontWeight: 700, fontSize: size, fontVariantNumeric: "tabular-nums" }}>
    {value >= 0 ? "+" : "−"}
    {Math.abs(value)}
  </span>
);

export const ordinal = (n: number) => {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
};

export const RankMove: React.FC<{ from: number; to: number; spots: number; size: number }> = ({ from, to, spots, size }) => {
  const col = (r: number) => (r <= spots ? C.white : C.loss);
  return (
    <span style={{ fontSize: size, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>
      <span style={{ color: col(from) }}>{ordinal(from)}</span>
      <span style={{ color: C.dim }}> → </span>
      <span style={{ color: col(to) }}>{ordinal(to)}</span>
    </span>
  );
};

export const SampleTag: React.FC = () => (
  <div style={{ position: "absolute", right: 14, top: 10, fontFamily: FONT, fontSize: 18, fontWeight: 700, letterSpacing: 2, color: C.t, opacity: 0.9 }}>
    SAMPLE DATA
  </div>
);

// Card shell: dark panel, deep drop shadow plus a soft glow in the card's accent colour (hex).
export const cardStyle = (accent = "#5d9cec", glow = 1): React.CSSProperties => ({
  position: "absolute",
  background: `linear-gradient(160deg, rgb(30, 36, 47) 0%, rgb(22, 26, 35) 60%, rgb(19, 23, 31) 100%)`,
  border: `1px solid ${C.line}`,
  borderRadius: 18,
  boxShadow: `0 30px 90px rgba(0,0,0,0.65), 0 0 ${Math.round(70 * glow)}px ${accent}${Math.round(0x40 * glow).toString(16).padStart(2, "0")}`,
  fontFamily: FONT,
  color: C.white,
  overflow: "hidden",
});
export const cardBox = cardStyle();

// Thin colour bar along the top of a card: one colour, or a gradient between two teams.
export const AccentBar: React.FC<{ colors: string[]; height?: number }> = ({ colors, height = 6 }) => (
  <div style={{ position: "absolute", left: 0, top: 0, right: 0, height, background: colors.length > 1 ? `linear-gradient(90deg, ${colors.join(", ")})` : colors[0] }} />
);
