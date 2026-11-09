import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";

// Frames from a stamp's `at` to the moment it hits the row: sound, line flash and shake are all keyed to this.
export const STAMP_LAND = 5;

// IN / OUT marker on a race row when a team crosses the Major line (S1 rubber stamp approved 2026-11-01; pill kept as an option).
// With `at` (a frame of the race), the stamp drops in big, lands with a shockwave ring, then settles at its tilt.
export const Stamp: React.FC<{ kind: "in" | "out"; variant: "rubber" | "pill"; left: number; rowH: number; at?: number }> = ({
  kind,
  variant,
  left,
  rowH,
  at,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = kind === "in" ? "#4cc878" : "#e44c4c"; // C.win / C.loss as hex, so alpha suffixes work
  const h = Math.max(rowH * (variant === "rubber" ? 1.05 : 0.95), 32);
  const t0 = at ?? -1000;
  const land = t0 + STAMP_LAND;
  const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
  const shown = frame >= t0;
  const ring = interpolate(frame, [land, land + 0.5 * fps], [0, 1], clamp);

  if (variant === "rubber") {
    return (
      <div style={{ position: "absolute", left, top: (rowH - h) / 2, height: h, opacity: shown ? 1 : 0 }}>
        {at !== undefined && ring > 0 && ring < 1 ? (
          <div
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: h * 3 * ring + h,
              height: h * 3 * ring + h,
              translate: "-50% -50%",
              borderRadius: "50%",
              border: `${4 * (1 - ring) + 1}px solid ${color}`,
              opacity: 1 - ring,
            }}
          />
        ) : null}
        <div
          style={{
            height: h,
            padding: "0 18px",
            border: `5px solid ${color}`,
            borderRadius: 8,
            color,
            fontFamily: FONT,
            fontWeight: 700,
            fontSize: h * 0.62,
            lineHeight: `${h - 10}px`,
            letterSpacing: 4,
            whiteSpace: "nowrap",
            backgroundColor: "rgba(14, 17, 23, 0.6)",
            rotate: `${interpolate(frame, [t0, land], [-24, -8], clamp)}deg`,
            scale: String(interpolate(frame, [t0, land, land + 3, land + 7], [2.8, 0.92, 1.06, 1], { ...clamp, easing: Easing.in(Easing.quad) })),
            boxShadow: `0 0 ${18 + 30 * (1 - ring)}px ${color}${at !== undefined && ring < 1 ? "aa" : "55"}, inset 0 0 10px ${color}44`,
          }}
        >
          {kind === "in" ? "IN" : "OUT"}
        </div>
      </div>
    );
  }
  return (
    <div
      style={{
        position: "absolute",
        left,
        top: (rowH - h) / 2,
        height: h,
        padding: "0 20px 0 14px",
        borderRadius: h / 2,
        backgroundColor: color,
        color: C.bg,
        fontFamily: FONT,
        fontWeight: 700,
        fontSize: h * 0.46,
        lineHeight: `${h}px`,
        letterSpacing: 1,
        whiteSpace: "nowrap",
        boxShadow: `0 0 24px ${color}88`,
        opacity: shown ? 1 : 0,
      }}
    >
      {kind === "in" ? "▲ INTO THE MAJOR" : "▼ OUT OF THE MAJOR"}
    </div>
  );
};
