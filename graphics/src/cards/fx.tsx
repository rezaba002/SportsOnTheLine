import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// Motion helpers for the cards. Frames are relative to the card's own <Sequence>.

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const OUT_EASE = Easing.bezier(0.16, 1, 0.3, 1);

// Card entrance + exit: slide, scale and de-blur in; quick fade and drift out before `exitAt`.
export const Appear: React.FC<{
  children: React.ReactNode;
  delay?: number;
  exitAt?: number;
  from?: "right" | "zoom" | "up";
}> = ({ children, delay = 0, exitAt, from = "right" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inEnd = delay + 0.55 * fps;
  const outStart = exitAt === undefined ? Infinity : exitAt - 0.35 * fps;
  const outEnd = exitAt ?? Infinity;
  const shift = from === "right" ? ["160px 0px", "0px 0px"] : from === "up" ? ["0px 90px", "0px 0px"] : ["0px 0px", "0px 0px"];
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity:
          interpolate(frame, [delay, delay + 0.25 * fps], [0, 1], clamp) *
          (exitAt === undefined ? 1 : interpolate(frame, [outStart, outEnd], [1, 0], clamp)),
        translate: frame < outStart
          ? interpolate(frame, [delay, inEnd], shift, { ...clamp, easing: OUT_EASE })
          : interpolate(frame, [outStart, outEnd], ["0px 0px", from === "right" ? "80px 0px" : "0px 40px"], clamp),
        scale: interpolate(frame, [delay, inEnd], [from === "zoom" ? 0.82 : 0.96, 1], { ...clamp, easing: Easing.spring({ damping: 14 }), output: "perceptual-scale" }),
        filter: `blur(${interpolate(frame, [delay, delay + 0.3 * fps], [14, 0], clamp)}px)`,
      }}
    >
      {children}
    </div>
  );
};

// A number that counts up from `from` to `value`, starting at `delay`.
export const CountUp: React.FC<{ value: number; from?: number; delay?: number; seconds?: number; format?: (n: number) => string }> = ({
  value,
  from = 0,
  delay = 0,
  seconds = 0.7,
  format = (n) => String(Math.round(n)),
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return <>{format(interpolate(frame, [delay, delay + seconds * fps], [from, value], { ...clamp, easing: OUT_EASE }))}</>;
};

// Fade + rise for small pieces inside a card (impact rows, chips), staggered by `delay`.
export const Rise: React.FC<{ children: React.ReactNode; delay: number; style?: React.CSSProperties }> = ({ children, delay, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        opacity: interpolate(frame, [delay, delay + 0.25 * fps], [0, 1], clamp),
        translate: interpolate(frame, [delay, delay + 0.35 * fps], ["0px 18px", "0px 0px"], { ...clamp, easing: OUT_EASE }),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

// A one-off pulse: 0 before `at`, peaks right after, back to 0 over `seconds`.
export const usePulse = (at: number, seconds = 0.6) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return interpolate(frame, [at, at + 0.08 * fps, at + seconds * fps], [0, 1, 0], clamp);
};

// Soft coloured light behind a logo.
export const Halo: React.FC<{ color: string; size: number; strength?: number }> = ({ color, size, strength = 1 }) => (
  <div
    style={{
      position: "absolute",
      width: size,
      height: size,
      borderRadius: "50%",
      background: `radial-gradient(circle, ${color}${Math.round(0x55 * strength).toString(16).padStart(2, "0")} 0%, ${color}00 68%)`,
      pointerEvents: "none",
    }}
  />
);
