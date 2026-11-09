import React from "react";
import { AbsoluteFill, Sequence, Series, interpolate, useCurrentFrame } from "remotion";
import { RankingRace } from "../RankingRace";
import { C, FONT } from "../theme";
import { MatchCard, type Match } from "./MatchCard";
import { NoPlayCard, RosterCard, VerdictCard } from "./OtherCards";
import { checkStamps, crossings } from "./crossings";
import { STAMP_LAND } from "./Stamp";
import { Sfx } from "./Sfx";

// Review clips of the approved card designs, each played as a full "moment" on the real race (2026-11-01).
// Ranks and points are real (HLTV daily Valve ranking); match event/maps are SAMPLE until the real results are pulled.
// A moment: race held on the day before (card up) -> the day plays in slow motion -> the race STOPS on the day ->
// only then the IN/OUT stamps land, one after another, each with its sound, a line flash and a small shake.

type RaceProps = React.ComponentProps<typeof RankingRace>;
type Base = Omit<RaceProps, "secondsPerStep" | "holdSeconds" | "freezeDay">;

// The race held on one day.
const Frozen: React.FC<Base & { day: number }> = ({ day, ...p }) => <RankingRace {...p} secondsPerStep={0.6} holdSeconds={3} freezeDay={day} />;

// The race moving from day-1 to day in slow motion. Lasts MOVE frames: the move itself (85 % of 2 s) plus the
// row smoothing, so by the last frame every bar has stopped and the next part can hold the day exactly.
const SLOW = 2;
export const MOVE = SLOW * 30 + 6;
const SlowStep: React.FC<Base & { day: number }> = ({ day, ...p }) => (
  <Sequence from={-(day - 1) * SLOW * 30}>
    <RankingRace {...p} secondsPerStep={SLOW} holdSeconds={3} />
  </Sequence>
);

// Small camera shake right after each impact frame (deterministic, so every render is the same).
const Shake: React.FC<{ at: number[]; children: React.ReactNode }> = ({ at, children }) => {
  const frame = useCurrentFrame();
  const k = Math.max(0, ...at.map((a) => (frame >= a ? interpolate(frame, [a, a + 9], [1, 0], { extrapolateRight: "clamp" }) : 0)));
  return <AbsoluteFill style={{ translate: `${Math.sin(frame * 2.7) * 10 * k}px ${Math.cos(frame * 3.3) * 8 * k}px` }}>{children}</AbsoluteFill>;
};

// The race stopped on `day`, then the stamps of that day land (from the data, checked), 12 frames apart.
export const STAMP_GAP = 12;
const StampHold: React.FC<Base & { day: number; first?: number }> = ({ day, first = 8, ...p }) => {
  const list = checkStamps(p.dataset, day, crossings(p.dataset, day));
  const stamps = list.map((c, i) => ({ team: c.team, kind: c.kind, style: "rubber" as const, at: first + i * STAMP_GAP }));
  const lands = stamps.map((s) => s.at + STAMP_LAND);
  return (
    <AbsoluteFill>
      <Shake at={lands}>
        <Frozen {...p} day={day} stamps={stamps} pulseAt={lands} focusAt={-60} /> {/* already dimmed: continues the move */}
      </Shake>
      {stamps.map((s, i) => (
        <React.Fragment key={s.team}>
          <Sfx at={lands[i]} sound="stamp" volume={0.9} />
          <Sfx at={lands[i]} sound={s.kind === "in" ? "stampIn" : "stampOut"} volume={0.45} lead={0} />
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};
export const stampHoldFrames = (dataset: string, day: number, first = 8) => first + crossings(dataset, day).length * STAMP_GAP + 40;

// ---------- A1: normal moment (side panel) ----------
const NRG_WILDCARD: Match = {
  event: "Sample event", stage: "Lower bracket", date: "Nov 1", spots: 9, sample: true,
  teams: [
    { name: "Wildcard", score: 2, points: 18, rankFrom: 9, rankTo: 9 },
    { name: "NRG", score: 1, points: -13, rankFrom: 10, rankTo: 10 },
  ],
  maps: [{ name: "Ancient", score: [13, 10] }, { name: "Mirage", score: [9, 13] }, { name: "Inferno", score: [13, 8] }],
};
export const MomentNormal = () => (
  <AbsoluteFill>
    <Frozen dataset="amDaily" highlight={[]} rows={14} day={27} focus={["NRG", "Wildcard"]} />
    <MatchCard match={NRG_WILDCARD} variant="panel" delay={8} exitAt={140} />
    <Sfx at={8} sound="whooshCard" volume={0.6} />
  </AbsoluteFill>
);

// ---------- A2: big moment (split card), then Oct 28 -> Oct 29 and its stamps ----------
const B8_FAZE: Match = {
  event: "Sample event", stage: "3rd-place decider", date: "Oct 29", spots: 18, sample: true,
  teams: [
    { name: "B8", score: 1, points: -46, rankFrom: 17, rankTo: 20 },
    { name: "FaZe", score: 2, points: -15, rankFrom: 14, rankTo: 14 },
  ],
  maps: [{ name: "Nuke", score: [13, 9] }, { name: "Anubis", score: [10, 13] }, { name: "Dust2", score: [11, 13] }],
};
const EU_BUBBLE = ["B8", "HOTU", "fnatic", "100 Thieves"];
const BIG_CARD = 110;
export const MomentBig = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={BIG_CARD}>
      <Frozen dataset="euDaily" highlight={[]} rows={24} day={23} focus={EU_BUBBLE} />
      <AbsoluteFill style={{ backgroundColor: "rgba(14,17,23,0.5)" }} />
      <MatchCard match={B8_FAZE} variant="split" delay={8} exitAt={108} />
      <Sfx at={8} sound="whooshBig" volume={0.7} />
    </Sequence>
    <Sequence from={BIG_CARD} durationInFrames={MOVE}>
      <SlowStep dataset="euDaily" highlight={[]} rows={24} day={24} focus={EU_BUBBLE} />
    </Sequence>
    <Sequence from={BIG_CARD + MOVE}>
      <StampHold dataset="euDaily" highlight={[]} rows={24} day={24} focus={EU_BUBBLE} />
    </Sequence>
  </AbsoluteFill>
);

// ---------- B: didn't play ----------
export const MomentNoPlay = () => (
  <AbsoluteFill>
    <Frozen dataset="asDaily" highlight={[]} rows={10} day={27} focus={["Lynn Vision", "TYLOO"]} />
    <NoPlayCard
      team="Lynn Vision" date="Oct 31 → Nov 1" headline="Chance of a Major invite (HLTV projection)" from={21} to={98} unit="%"
      why="TYLOO lost to Metizport by forfeit. Lynn Vision climbed without playing a match." delay={8} exitAt={150}
    />
    <Sfx at={8} sound="whooshCard" volume={0.6} />
  </AbsoluteFill>
);

// ---------- C: roster changes, then Oct 19 -> Oct 20 and its stamps ----------
const ROSTER_CARD = 200;
export const MomentRoster = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={ROSTER_CARD}>
      <Frozen dataset="euDaily" highlight={[]} rows={24} day={14} focus={["Luminosity", "BIG"]} />
      <RosterCard team="Luminosity" fromDate="2026-10-05" toDate="2026-10-20" spots={18} delay={8} exitAt={198} />
      <Sfx at={8} sound="whooshCard" volume={0.6} />
    </Sequence>
    <Sequence from={ROSTER_CARD} durationInFrames={MOVE}>
      <SlowStep dataset="euDaily" highlight={[]} rows={24} day={15} focus={["Luminosity", "BIG"]} />
    </Sequence>
    <Sequence from={ROSTER_CARD + MOVE}>
      <StampHold dataset="euDaily" highlight={[]} rows={24} day={15} focus={["Luminosity", "BIG"]} />
    </Sequence>
  </AbsoluteFill>
);

// ---------- D2 then D1: final verdict ----------
const EU_LINE = [
  { rank: 16, name: "FaZe", points: 1538 },
  { rank: 17, name: "Eternal Fire", points: 1508 },
  { rank: 18, name: "HOTU", points: 1484 },
  { rank: 19, name: "fnatic", points: 1482 },
  { rank: 20, name: "100 Thieves", points: 1474 },
  { rank: 21, name: "B8", points: 1468 },
];
const NOTE = "Points as of Nov 1 — the final numbers come with Valve's Nov 2 file";
const D2_IN = 8;
const D2_FLASH = D2_IN + Math.round((0.4 + EU_LINE.length * 0.12) * 30 + 15); // "2 POINTS APART" lands (see VerdictCard)
const D1_IN = 152;
const D1_BANG = D1_IN + 27; // the big number lands (0.9 s after D1 enters)
export const MomentVerdict = () => (
  <AbsoluteFill>
    <Frozen dataset="euDaily" highlight={[]} rows={24} day={27} focus={["HOTU", "fnatic"]} />
    <AbsoluteFill style={{ backgroundColor: "rgba(14,17,23,0.6)" }} />
    <VerdictCard region="Europe" spots={18} rows={EU_LINE} variant="zoom" note={NOTE} delay={D2_IN} exitAt={150} />
    <VerdictCard region="Europe" spots={18} rows={EU_LINE} variant="versus" note={NOTE} delay={D1_IN} exitAt={320} />
    <Sfx at={D2_IN} sound="whooshCard" volume={0.6} />
    <Sfx at={D2_FLASH} sound="stamp" volume={0.7} />
    <Sfx at={D1_BANG} sound="riser" volume={0.5} lead={60} />
    <Sfx at={D1_BANG} sound="impact" volume={0.9} />
  </AbsoluteFill>
);

// ---------- one reel with all of them, labelled ----------
const Label: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: "absolute", left: "50%", top: 18, translate: "-50% 0", padding: "6px 18px", borderRadius: 8, backgroundColor: "rgba(255,255,255,0.08)", fontFamily: FONT, fontSize: 22, color: C.muted, letterSpacing: 2 }}>
    {text}
  </div>
);
export const REEL = [
  { id: "A1", label: "A1 · NORMAL MOMENT · SIDE PANEL", C: MomentNormal, frames: 150 },
  { id: "A2", label: "A2 · BIG MOMENT · SPLIT CARD → DAY PLAYS → STAMPS", C: MomentBig, frames: BIG_CARD + MOVE + stampHoldFrames("euDaily", 24) },
  { id: "B", label: "B · DIDN'T PLAY", C: MomentNoPlay, frames: 160 },
  { id: "C", label: "C · ROSTER CHANGES → DAY PLAYS → STAMPS", C: MomentRoster, frames: ROSTER_CARD + MOVE + stampHoldFrames("euDaily", 15) },
  { id: "D", label: "D2 → D1 · FINAL VERDICT", C: MomentVerdict, frames: 330 },
];
export const REEL_FRAMES = REEL.reduce((n, r) => n + r.frames, 0);
export const CardReel = () => (
  <Series>
    {REEL.map((r) => (
      <Series.Sequence key={r.id} durationInFrames={r.frames}>
        <r.C />
        <Label text={r.label} />
      </Series.Sequence>
    ))}
  </Series>
);
