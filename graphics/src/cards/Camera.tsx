import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// Virtual camera, After-Effects style: a NULL object parents the whole picture, and the CAMERA is synced to the null
// (its point of interest follows the null's anchor), so a move of the null reads as one camera move, never as the
// picture sliding on its own. No cuts: the camera glides from one framing (shot) to the next and drifts in between.
//
// Shot values are kept small on purpose (the owner asked not to overdo position):
//   z  zoom of the null (1 = full frame)        x, y  null position offset in px
//   ry / rx  camera orbit in degrees (yaw / pitch)  ay  anchor height (px from top) the zoom is centred on
export type Shot = { z: number; x: number; y: number; ry: number; rx: number; ay: number };
export type CamKey = { f: number; glide: number; shot: Shot };

export const SHOTS = {
  wide: { z: 1, x: 0, y: 0, ry: 0, rx: 0, ay: 540 },
  push: { z: 1.035, x: 0, y: 0, ry: 0, rx: 0.4, ay: 540 },
  left: { z: 1.03, x: 14, y: 0, ry: 2, rx: 0.5, ay: 540 },
  right: { z: 1.03, x: -14, y: 0, ry: -2, rx: 0.5, ay: 540 },
  high: { z: 1.025, x: 0, y: 10, ry: 0, rx: 1.4, ay: 540 },
} satisfies Record<string, Shot>;
// close on a height of the picture (the Major line): zoom centred on it so the line stays where it was
export const lineShot = (ay: number, side: -1 | 0 | 1 = 0): Shot => ({ z: 1.05, x: side * -8, y: 0, ry: side * 1.2, rx: 0.3, ay });

const EASE = Easing.bezier(0.45, 0, 0.55, 1);   // slow in, slow out, like a dolly
const KEYS: (keyof Shot)[] = ["z", "x", "y", "ry", "rx", "ay"];
const PERSPECTIVE = 2600;   // ≈ a 50 mm lens on a 1920 frame

const shotAt = (keys: CamKey[], f: number): Shot => {
  let cur: Shot = keys[0]?.shot ?? SHOTS.wide;
  for (const k of keys) {
    if (f < k.f) break;
    const p = interpolate(f, [k.f, k.f + Math.max(1, k.glide)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: EASE });
    const from = cur;
    cur = Object.fromEntries(KEYS.map((n) => [n, from[n] + (k.shot[n] - from[n]) * p])) as Shot;
  }
  return cur;
};

export const CameraRig: React.FC<{ keys: CamKey[]; background: string; children: React.ReactNode }> = ({ keys, background, children }) => {
  const f = useCurrentFrame();
  const { width } = useVideoConfig();      // works for 16:9 and 9:16 (Shorts)
  const cx = width / 2;
  const s = shotAt(keys, f);
  // handheld-slow drift so the picture is never fully still (a few px, a fraction of a degree)
  const dx = 3 * Math.sin(f / 97), dy = 2 * Math.sin(f / 131 + 1), dr = 0.12 * Math.sin(f / 173 + 2);
  const nx = s.x + dx, ny = s.y + dy;
  return (
    // CAMERA: perspective, its point of interest locked to the null's anchor (sync)
    <AbsoluteFill style={{ backgroundColor: background, overflow: "hidden", perspective: PERSPECTIVE, perspectiveOrigin: `${cx + nx}px ${s.ay + ny}px` }}>
      {/* NULL: the whole picture is its child */}
      <AbsoluteFill style={{ transformOrigin: `${cx}px ${s.ay}px`, transform: `translate3d(${nx}px, ${ny}px, 0) rotateX(${s.rx}deg) rotateY(${s.ry + dr}deg) scale(${s.z})`, backgroundColor: background }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
