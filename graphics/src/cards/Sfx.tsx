import React from "react";
import { Audio } from "@remotion/media";
import { Sequence, staticFile, useVideoConfig } from "remotion";

// One sound effect at a frame. CC0 sounds from the editing-videos library (all measured at about -22 LUFS).
// Volumes are set for review without narration; the final mix puts effects 12–24 dB under the voice.
export const SFX = {
  whooshCard: "sfx/whoosh-short.wav",
  whooshBig: "sfx/whoosh-soft.wav",
  stamp: "sfx/dry-thud.wav",
  stampIn: "sfx/check-mark.wav",
  stampOut: "sfx/error-3.wav",
  riser: "sfx/riser-short-2s.wav",
  impact: "sfx/impact-soft-1.wav",
  // video 05 v2: a richer palette
  tick: "sfx/clock-tick.wav",
  tickSoft: "sfx/tick-soft.wav",
  whooshMed: "sfx/whoosh-medium-1s.wav",
  whooshLong: "sfx/whoosh-long-2s.wav",
  impact2: "sfx/impact-soft-2.wav",
  impact3: "sfx/impact-soft-3.wav",
  knock: "sfx/impact-wood-light.wav",
  win: "sfx/success-2.wav",
  lose: "sfx/error-buzz-soft.wav",
  hit: "sfx/stinger-hit-short.wav",
  energetic: "sfx/stinger-energetic-hit.wav",
  pop1: "sfx/pop-1.wav",
  pop2: "sfx/pop-2.wav",
  up: "sfx/send-whoosh-up.wav",
  chime: "sfx/success-chime.wav",
  bell: "sfx/bell-ding.wav",
  // video 05 v4: clicks (levelled to one loudness by video05/work/sfx_variants.py) and slides
  tap: "sfx/tap.wav",
  clickSoft: "sfx/click-soft.wav",
  clickSharp: "sfx/click-sharp.wav",
  select: "sfx/select-1.wav",
  toggle: "sfx/toggle.wav",
  hover: "sfx/hover-2.wav",
  slide1: "sfx/slide-1.wav",
  slide2: "sfx/slide-2.wav",
  sweep: "sfx/sweep-long.wav",
  // video 07: longer build-ups
  riserLong: "sfx/riser-medium-4s.wav",
  swell: "sfx/swell-soft-3s.wav",
} as const;

// Pools: one name, several sounds; a play takes one of them, so a series never repeats the same sample.
export const POOLS = {
  click: ["tap", "clickSoft", "clickSharp", "select", "toggle", "hover"],
  swoosh: ["whooshCard", "whooshBig", "slide1", "slide2", "whooshMed"],
  pop: ["pop1", "pop2"],
  tickAny: ["tick", "tickSoft"],
  bigWhoosh: ["whooshLong", "sweep"],
  camWhoosh: ["whooshCard", "slide1", "whooshBig", "slide2", "whooshMed", "sweep"],   // camera angle changes
} as const satisfies Record<string, readonly (keyof typeof SFX)[]>;

type Name = keyof typeof SFX | keyof typeof POOLS;

// Variation (video 05 v4) is switched on by <SfxSeed>: each play picks a pitch variant (public/sfx/v/<file>_<p>.wav,
// -3..+3 semitones) and a volume within ±2 dB. The pick is a hash of the absolute frame, so a render is repeatable.
// Seeds nest: a <SfxSeed offset> inside a Sequence adds that Sequence's start, so the hash sees the absolute frame.
const SeedCtx = React.createContext<{ on: boolean; base: number }>({ on: false, base: 0 });
export const SfxSeed: React.FC<{ offset: number; children: React.ReactNode }> = ({ offset, children }) => {
  const parent = React.useContext(SeedCtx);
  return <SeedCtx.Provider value={{ on: true, base: parent.base + offset }}>{children}</SeedCtx.Provider>;
};

const hash = (n: number) => {
  let h = (n * 2654435761) >>> 0;
  h ^= h >>> 15;
  h = Math.imul(h, 2246822519) >>> 0;
  return (h ^ (h >>> 13)) >>> 0;
};
const PITCH_CYCLE = [0, 2, -1, 1, -2, 3, -3];
const nameSeed = (s: string) => [...s].reduce((a, c) => a * 31 + c.charCodeAt(0), 7);

// `lead` frames before `at`, so the transient lands with the picture (sound effects lead the visual by 2–4 frames).
// `n`: index in a series (rows of a card…): rotates the pool member and the pitch so neighbours always differ.
// `pitch`: fixed semitones (-3..3), e.g. day ticks that climb towards the deadline.
export const Sfx: React.FC<{ at: number; sound: Name; volume?: number; lead?: number; n?: number; pitch?: number }> = ({ at, sound, volume = 0.7, lead = 2, n, pitch }) => {
  const { fps } = useVideoConfig();
  const seed = React.useContext(SeedCtx);
  const h = hash(seed.base + at + nameSeed(sound));
  const hs = hash(seed.base + nameSeed(sound));   // one offset per series, so neighbours (n, n+1) always differ
  const pool = (POOLS as Record<string, readonly (keyof typeof SFX)[]>)[sound];
  const member = pool ? pool[(n !== undefined ? n + hs : h) % pool.length] : (sound as keyof typeof SFX);
  let src: string = SFX[member];
  let vol = volume;
  if (seed.on) {
    const p = pitch ?? (n !== undefined ? PITCH_CYCLE[(n + hs) % 7] : (h % 5) - 2);
    src = src.replace(/^sfx\/(.+)\.wav$/, `sfx/v/$1_${Math.max(-3, Math.min(3, Math.round(p)))}.wav`);
    vol = volume * Math.pow(10, ((h >>> 8) % 5 - 2) / 20);
  }
  return (
    <Sequence from={Math.max(0, Math.round(at - lead))} durationInFrames={3 * fps} layout="none">
      <Audio src={staticFile(src)} volume={Math.min(1, vol)} />
    </Sequence>
  );
};
