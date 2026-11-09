import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FONT } from "../theme";

// Burned-in captions (from video07): one cue at a time, bottom centre, outside the camera rig so they never move.
// Cues come from the narration's own word timings (video07/work/captions.py): script spellings, digits for numbers,
// <= 42 chars a line, <= 2 lines. The word being spoken turns yellow; already-spoken words stay white.
export type CapWord = { w: string; s: number };
export type CapCue = { s: number; e: number; lines: CapWord[][] };

const YELLOW = "#ffd34d";

export const Captions: React.FC<{ cues: CapCue[]; bottom?: number; size?: number }> = ({ cues, bottom = 64, size = 50 }) => {
  const f = useCurrentFrame();
  const c = cues.find((q) => f >= q.s && f <= q.e);
  if (!c) return null;
  const words = c.lines.flat();
  const p = interpolate(f, [c.s, c.s + 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: bottom, pointerEvents: "none" }}>
      <div style={{ padding: "10px 26px 14px", borderRadius: 14, backgroundColor: "rgba(8,10,14,0.62)", opacity: p, translate: `0px ${8 * (1 - p)}px`,
        textAlign: "center", fontFamily: FONT, fontVariationSettings: "'wdth' 90, 'wght' 700", fontWeight: 700, fontSize: size, lineHeight: 1.18,
        color: "#ffffff", WebkitTextStroke: `${size * 0.08}px #000`, paintOrder: "stroke fill", textShadow: "0 3px 0 #000" }}>
        {c.lines.map((line, li) => (
          <div key={li} style={{ whiteSpace: "nowrap" }}>
            {line.map((w, wi) => {
              const k = words.indexOf(w);
              const next = words[k + 1]?.s ?? c.e;
              const now = f >= w.s && f < next;
              return <span key={wi} style={{ color: now ? YELLOW : "#ffffff" }}>{w.w}{wi < line.length - 1 ? " " : ""}</span>;
            })}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
