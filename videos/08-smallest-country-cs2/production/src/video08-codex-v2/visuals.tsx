import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, staticFile } from "remotion";
import { FONT } from "../theme";

export const Y = "#ffd34d",
  BLUE = "#5d9cec",
  GREEN = "#4cc878",
  RED = "#fa5462",
  WHITE = "#f5f6fa";
export const COLOR: Record<string, string> = {
  EST: "#399ee8",
  MNG: "#ff5668",
  DNK: "#58e39e",
  LVA: "#d75984",
  SWE: "#ffd34d",
  FIN: "#81bcff",
  RUS: "#fa5462",
  XKX: "#8c9dff",
  LTU: "#fed461",
};
export const FLAG: Record<string, string> = {
  EST: "ee",
  MNG: "mn",
  DNK: "dk",
  RUS: "ru",
  LVA: "lv",
  SWE: "se",
  FIN: "fi",
  LTU: "lt",
  XKX: "xk",
  MKD: "mk",
  BIH: "ba",
  USA: "us",
  BRA: "br",
  CHN: "cn",
};
export const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;
export const go = (f: number, at = 0, len = 9) =>
  interpolate(f, [at, at + len], [0, 1], {
    ...clamp,
    easing: Easing.bezier(0.12, 0.9, 0.19, 1),
  });
export const out = (f: number, at: number, len = 5) =>
  1 - interpolate(f, [at, at + len], [0, 1], clamp);
export const bodyFont: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 700,
  fontVariationSettings: "'wdth' 85, 'wght' 700",
};

export const Flag: React.FC<{ iso: string; h?: number }> = ({
  iso,
  h = 70,
}) => (
  <Img
    src={staticFile(`flags/${FLAG[iso] || iso.toLowerCase()}.svg`)}
    style={{
      height: h,
      width: (h * 4) / 3,
      objectFit: "cover",
      borderRadius: 5,
      boxShadow: "0 10px 30px #0005",
    }}
  />
);
export const Tag: React.FC<{
  children: React.ReactNode;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, color = Y, style }) => (
  <div
    style={{
      ...bodyFont,
      color,
      fontSize: 28,
      letterSpacing: 4,
      textTransform: "uppercase",
      ...style,
    }}
  >
    {children}
  </div>
);
export const Head: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, size = 96, color = WHITE, style }) => (
  <div
    style={{
      ...bodyFont,
      fontSize: size,
      lineHeight: 1.01,
      letterSpacing: -1,
      color,
      ...style,
    }}
  >
    {children}
  </div>
);
export const Center: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <AbsoluteFill
    style={{
      justifyContent: "center",
      alignItems: "center",
      paddingBottom: 120,
      ...style,
    }}
  >
    {children}
  </AbsoluteFill>
);
export const Stamp: React.FC<{
  children: React.ReactNode;
  f: number;
  at?: number;
  color?: string;
  size?: number;
}> = ({ children, f, at = 0, color = Y, size = 70 }) => {
  const p = go(f, at, 6);
  return (
    <div
      style={{
        ...bodyFont,
        opacity: f < at ? 0 : 1,
        color,
        fontSize: size,
        letterSpacing: 2,
        padding: "10px 28px",
        border: `5px solid ${color}`,
        transform: `scale(${2.1 - 1.1 * p}) rotate(${-9 + 5 * p}deg)`,
        background: "#10141bed",
        boxShadow: `0 0 35px ${color}24`,
      }}
    >
      {children}
    </div>
  );
};
export const Sticker: React.FC<{
  name: string;
  size?: number;
  f: number;
  at?: number;
}> = ({ name, size = 380, f, at = 0 }) => {
  const p = go(f, at, 10);
  return (
    <Img
      src={staticFile(`stickers08/${name}.png`)}
      style={{
        width: size,
        height: size,
        opacity: p,
        transform: `translateY(${40 * (1 - p)}px) scale(${0.75 + 0.25 * p}) rotate(${-13 * (1 - p)}deg)`,
        filter: "drop-shadow(0 20px 30px #0008)",
      }}
    />
  );
};

export type Row = {
  iso: string;
  name: string;
  rate: number;
  rank: number;
  count: number;
  pop: number;
};
export const Chart: React.FC<{
  rows: Row[];
  f: number;
  max: number;
  digits?: number;
  highlight?: string;
  raw?: boolean;
  title?: string;
}> = ({ rows, f, max, digits = 1, highlight, raw = false, title }) => (
  <div style={{ position: "absolute", left: 150, top: 130, width: 1620 }}>
    <Tag>
      {title ||
        (raw ? "RECORDED CS2 PRIZE EARNERS" : "PLAYERS PER MILLION CITIZENS")}
    </Tag>
    <div style={{ marginTop: 60 }}>
      {rows.map((r, i) => {
        const at = i * 4,
          p = go(f, at, 18),
          enter = go(f, at, 7),
          value = raw ? r.count : r.rate;
        const color = COLOR[r.iso] || BLUE;
        return (
          <div
            key={r.iso}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 22,
              height: rows.length > 3 ? 106 : 160,
              opacity: enter,
              transform: `translateX(${-80 * (1 - enter)}px)`,
            }}
          >
            <Flag iso={r.iso} h={rows.length > 3 ? 52 : 80} />
            <div
              style={{
                ...bodyFont,
                width: 330,
                fontSize: rows.length > 3 ? 45 : 60,
                color: highlight && r.iso !== highlight ? "#b2bac9" : WHITE,
              }}
            >
              {r.name === "North Macedonia" ? "N. Macedonia" : r.name}
            </div>
            <div
              style={{
                position: "relative",
                width: 850,
                height: rows.length > 3 ? 48 : 72,
                background: "#ffffff08",
                borderRadius: 5,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: Math.max(0, (value / max) * 850 * p),
                  height: "100%",
                  background: `linear-gradient(90deg, ${color}b0,${color})`,
                  borderRadius: 5,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  left: Math.max(0, (value / max) * 850 * p - 8),
                  width: 8,
                  height: "100%",
                  top: 0,
                  background: "#fff7",
                  opacity: f < at + 20 ? 1 : 0,
                }}
              />
            </div>
            <div
              style={{
                ...bodyFont,
                color,
                width: 180,
                fontSize: rows.length > 3 ? 63 : 96,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {raw ? Math.round(value * p) : (value * p).toFixed(digits)}
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

export const BigNumber: React.FC<{
  value: string;
  label?: string;
  color?: string;
  f: number;
  size?: number;
}> = ({ value, label, color = Y, f, size = 300 }) => (
  <Center>
    <Head
      size={size}
      color={color}
      style={{
        fontVariantNumeric: "tabular-nums",
        transform: `scale(${1.25 - 0.25 * go(f, 0, 9)})`,
        textShadow: `0 0 75px ${color}20`,
      }}
    >
      {value}
    </Head>
    {label && (
      <Tag color={WHITE} style={{ marginTop: 30, fontSize: 38 }}>
        {label}
      </Tag>
    )}
  </Center>
);

export const Split: React.FC<{
  left: React.ReactNode;
  right: React.ReactNode;
  versus?: string;
}> = ({ left, right, versus }) => (
  <Center style={{ flexDirection: "row", gap: 70 }}>
    <div
      style={{
        width: 700,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 24,
      }}
    >
      {left}
    </div>
    {versus && (
      <div style={{ ...bodyFont, fontSize: 70, color: "#ffffff40" }}>
        {versus}
      </div>
    )}
    <div
      style={{
        width: 700,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 24,
      }}
    >
      {right}
    </div>
  </Center>
);
