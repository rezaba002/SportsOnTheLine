import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { RankingRace } from "../RankingRace";
import { C } from "../theme";
import timeline from "../../public/data/video05_timeline.json";
import { checkStamps, crossingsBetween, RACES } from "../cards/crossings";
import { STAMP_LAND } from "../cards/Stamp";
import { Sfx, SfxSeed } from "../cards/Sfx";
import { CameraRig, CamKey, lineShot, Shot, SHOTS } from "../cards/Camera";
import { NoPlayCard, RosterCard, VerdictCard } from "../cards/OtherCards";
import { DuelCard, ListCard, MadeItCard, MissedCard, RegionBanner, StoryCard } from "./Cards05";
import { cue, Field, Page05 } from "./Pages05";

// Video 05 — "The Road to Singapore". Everything comes from public/data/video05_timeline.json (work/timeline.py):
// narration blocks, and for each segment what is on screen and on which spoken word it changes.

type Card = Record<string, unknown> & { type: string };
type Step = { at: number; toDay: number; move: number | null; card: Card | null };
type Seg = Record<string, unknown> & { kind: string; from: number; dur: number };
const T = timeline as unknown as { total: number; audio: { id: string; file: string; from: number }[]; segments: Seg[] };
export const VIDEO05_FRAMES = T.total;

const FIELD: Field = T.segments
  .filter((s) => s.kind === "madeit")
  .map((s) => ({ region: s.region as string, teams: (s.stages as { teams: string[] }[]).flatMap((st) => st.teams) }));

type Ds = "euDaily" | "amDaily" | "asDaily";
const STAMP_GAP = 12;
const SETTLE = 8;

// The race held on one day (with optional data-derived stamps that land one by one from `stampsAt`).
const Held: React.FC<{ ds: Ds; rows: number; day: number; focus: string[]; dimNow?: boolean; stamps?: { team: string; kind: "in" | "out" }[]; stampsAt?: number }> = ({
  ds, rows, day, focus, dimNow, stamps = [], stampsAt = 6,
}) => {
  const st = stamps.map((s, i) => ({ ...s, style: "rubber" as const, at: stampsAt + i * STAMP_GAP }));
  const lands = st.map((s) => s.at + STAMP_LAND);
  return (
    <AbsoluteFill>
      <RankingRace dataset={ds} highlight={[]} rows={rows} secondsPerStep={0.6} holdSeconds={0} freezeDay={day} focus={focus.length ? focus : undefined}
        focusAt={dimNow ? -60 : 0} stamps={st} pulseAt={lands} />
      {st.map((s, i) => (
        <React.Fragment key={s.team}>
          <Sfx at={lands[i]} sound="stamp" volume={0.7} />
          <Sfx at={lands[i]} sound="impact3" volume={0.45} />
          <Sfx at={lands[i] + 1} sound={s.kind === "in" ? "win" : "lose"} volume={0.38} lead={0} />
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};

// The race moving from one day to another in `frames` frames, stopping on `toDay`.
const Moving: React.FC<{ ds: Ds; rows: number; fromDay: number; toDay: number; frames: number; focus: string[] }> = ({ ds, rows, fromDay, toDay, frames, focus }) => {
  const days = Math.max(1, toDay - fromDay);
  const stepFrames = Math.max(4, (frames - SETTLE) / days);
  return (
    <>
      <Sequence from={-Math.round(fromDay * stepFrames)}>
        <RankingRace dataset={ds} highlight={[]} rows={rows} secondsPerStep={stepFrames / 30} holdSeconds={0} endDay={toDay} focus={focus.length ? focus : undefined} focusAt={-600} />
      </Sequence>
      {/* a clock tick each time the date flips (the date label changes half-way through each step) */}
      {Array.from({ length: days }, (_, d) => (
        <Sfx key={d} at={Math.round((d + 0.45) * stepFrames)} sound={d % 2 ? "tickSoft" : "tick"} volume={0.16} lead={0}
          pitch={-3 + (6 * (fromDay + d + 1)) / Math.max(1, RACES[ds].frames.length - 1)} />
      ))}
    </>
  );
};

const CardView: React.FC<{ card: Card; spots: number; exitAt?: number }> = ({ card, spots, exitAt }) => {
  // cards are typed by work/timeline.py; the casts only bridge the JSON import
  const as = <P,>(c: Card) => c as unknown as P;
  if (card.type === "list") return <ListCard {...as<React.ComponentProps<typeof ListCard>>(card)} spots={spots} exitAt={exitAt} />;
  if (card.type === "duel") return <DuelCard {...as<React.ComponentProps<typeof DuelCard>>(card)} spots={spots} exitAt={exitAt} />;
  if (card.type === "roster") return <RosterCard {...as<React.ComponentProps<typeof RosterCard>>(card)} spots={spots} delay={0} exitAt={exitAt} />;
  const c = card as unknown as { team: string; from: number; to: number; why: string; date: string };
  return <NoPlayCard team={c.team} date={c.date} headline="Didn't play a match. Rank:" from={c.from} to={c.to} unit="th" why={c.why} delay={0} exitAt={exitAt} />;
};

// Timing of each step of a race segment (shared by RaceSeg and the camera).
const stepTimes = (seg: Seg) => {
  let day = seg.startDay as number;
  const steps = (seg.steps as Step[]) ?? [];
  return steps.map((st, i) => {
    const end = i + 1 < steps.length ? steps[i + 1].at : seg.dur;
    const moving = st.toDay !== day;
    const moveAt = st.move ?? (st.card ? Math.round(st.at + (end - st.at) * 0.45) : st.at);
    const moveFrames = moving ? Math.min(Math.max(36, (st.toDay - day) * 10 + SETTLE), Math.max(24, end - moveAt - 30)) : 0;
    const t = { st, i, fromDay: day, end, moving, moveAt, moveFrames };
    if (moving) day = st.toDay;
    return t;
  });
};

// One race segment: for each step, hold (card up) → move → hold with the stamps of that step.
const RaceSeg: React.FC<{ seg: Seg }> = ({ seg }) => {
  const ds = seg.ds as Ds;
  const rows = seg.rows as number;
  const focus = (seg.focus as string[]) ?? [];
  const steps = (seg.steps as Step[]) ?? [];
  const spots = RACES[ds].spots;
  const banner = seg.banner as { title: string; sub: string } | null;
  const parts: React.ReactNode[] = [];
  let day = seg.startDay as number;
  if (seg.free) {   // the race running on its own, bright, no card, no stamps
    return (
      <AbsoluteFill>
        <Moving ds={ds} rows={rows} fromDay={day} toDay={steps[0].toDay} frames={seg.dur} focus={[]} />
        <Sfx at={0} sound="swoosh" volume={0.3} />
      </AbsoluteFill>
    );
  }
  if (!steps.length) {
    parts.push(<Sequence key="hold" durationInFrames={seg.dur}><Held ds={ds} rows={rows} day={day} focus={focus} /></Sequence>);
  }
  stepTimes(seg).forEach(({ st, i, end, moving, moveAt, moveFrames }) => {
    // hold before the move (with the card)
    if (moveAt > st.at || !moving) {
      parts.push(
        <Sequence key={`a${i}`} from={st.at} durationInFrames={(moving ? moveAt : end) - st.at}><SfxSeed offset={st.at}>
          <Held ds={ds} rows={rows} day={day} focus={focus} dimNow={i > 0} />
          {st.card ? (
            <>
              <CardView card={st.card} spots={spots} exitAt={moving ? moveAt - st.at : undefined} />
              <Sfx at={0} sound={st.card.type === "duel" ? "whooshLong" : "whooshMed"} volume={0.4} />
              <Sfx at={6} sound={st.card.type === "duel" ? "hit" : "impact"} volume={st.card.type === "duel" ? 0.45 : 0.6} />
            </>
          ) : null}
        </SfxSeed></Sequence>,
      );
    }
    if (moving) {
      parts.push(
        <Sequence key={`m${i}`} from={moveAt} durationInFrames={moveFrames}><SfxSeed offset={moveAt}>
          <Moving ds={ds} rows={rows} fromDay={day} toDay={st.toDay} frames={moveFrames} focus={focus} />
          {/* the card leaves and the camera moves to the line: one swoosh for both */}
          <Sfx at={0} sound="swoosh" volume={0.26} />
        </SfxSeed></Sequence>,
      );
      const stamps = checkStamps(ds, st.toDay, crossingsBetween(ds, day, st.toDay, focus.length ? focus : undefined));
      parts.push(
        <Sequence key={`b${i}`} from={moveAt + moveFrames} durationInFrames={Math.max(1, end - moveAt - moveFrames)}><SfxSeed offset={moveAt + moveFrames}>
          <Held ds={ds} rows={rows} day={st.toDay} focus={focus} dimNow stamps={stamps} />
        </SfxSeed></Sequence>,
      );
      day = st.toDay;
    }
  });
  return (
    <AbsoluteFill>
      {parts}
      {banner ? <RegionBanner title={banner.title} sub={banner.sub} until={Math.min(seg.dur, 75)} /> : null}
      {banner ? <Sfx at={0} sound="bigWhoosh" volume={0.5} /> : null}
      {banner ? <Sfx at={8} sound="hit" volume={0.55} /> : null}
    </AbsoluteFill>
  );
};

const VerdictSeg: React.FC<{ seg: Seg }> = ({ seg }) => {
  const { fps } = useVideoConfig();
  const ds = seg.ds as Ds;
  const rows = seg.rows as { rank: number; name: string; points: number }[];
  const sw = seg.switchAt as number;
  const spots = seg.spots as number;
  const lastIn = rows.find((r) => r.rank === spots)!, firstOut = rows.find((r) => r.rank === spots + 1)!;
  const tie = rows.filter((r) => r.rank > spots && r.points === firstOut.points).map((r) => r.name);
  const note = tie.length > 1 ? `${tie.join(" and ")} tied on ${firstOut.points} · Valve standings, Nov 2` : "Valve standings, Nov 2";
  const d2Flash = 8 + Math.round((0.4 + rows.length * 0.12) * fps + 15);
  return (
    <AbsoluteFill>
      <Held ds={ds} rows={{ euDaily: 24, amDaily: 14, asDaily: 10 }[ds]} day={seg.dayIndex as number} focus={[lastIn.name, firstOut.name]} />
      <AbsoluteFill style={{ backgroundColor: "rgba(14,17,23,0.62)" }} />
      <Sequence from={8} durationInFrames={sw - 8}>
        <VerdictCard region={seg.region as string} spots={spots} rows={rows} variant="zoom" note={note} delay={0} exitAt={sw - 8} />
      </Sequence>
      <Sequence from={sw}>
        <VerdictCard region={seg.region as string} spots={spots} rows={rows} variant="versus" note={note} delay={0} exitAt={seg.dur - sw - 4} />
      </Sequence>
      <Sfx at={8} sound="whooshMed" volume={0.45} />
      {rows.map((r, i) => <Sfx key={r.name} at={8 + i * 3} sound="click" n={i} volume={0.6} lead={0} />)}
      <Sfx at={d2Flash} sound="stamp" volume={0.6} />
      <Sfx at={d2Flash} sound="impact3" volume={0.4} />
      <Sfx at={sw} sound="whooshLong" volume={0.35} />
      <Sfx at={sw + 27} sound="riser" volume={0.35} lead={Math.min(60, sw + 20)} />
      <Sfx at={sw + 27} sound="hit" volume={0.6} />
      <Sfx at={sw + 27} sound="impact2" volume={0.6} />
    </AbsoluteFill>
  );
};

const RegionEndBg: React.FC<{ ds: Ds }> = ({ ds }) => (
  <>
    <Held ds={ds} rows={{ euDaily: 24, amDaily: 14, asDaily: 10 }[ds]} day={RACES[ds].frames.length - 1} focus={["__none__"]} />
    <AbsoluteFill style={{ backgroundColor: "rgba(14,17,23,0.95)" }} />
  </>
);

const Segment: React.FC<{ seg: Seg }> = ({ seg }) => {
  if (seg.kind === "race") return <RaceSeg seg={seg} />;
  if (seg.kind === "verdict") return <VerdictSeg seg={seg} />;
  if (seg.kind === "missed") {
    const teams = seg.teams as { name: string; at: number }[];
    return (
      <AbsoluteFill>
        <RegionEndBg ds={seg.ds as Ds} />
        <MissedCard region={seg.region as string} teams={seg.teams as never} lastIn={seg.lastIn as string} lastPoints={seg.lastPoints as number} />
        <Sfx at={0} sound="whooshMed" volume={0.4} />
        {teams.map((t) => (
          <React.Fragment key={t.name}>
            <Sfx at={t.at + 6} sound="stamp" volume={0.55} />
            <Sfx at={t.at + 7} sound="stampOut" volume={0.25} lead={0} />
          </React.Fragment>
        ))}
      </AbsoluteFill>
    );
  }
  if (seg.kind === "story") {
    const cues = seg.cues as Record<string, number>;
    const at = { blocked: cue(cues, "blocked", 1, 60), appeal: cue(cues, "appealed", 1, 200), second: cue(cues, "second", 1, 400), s1mple: cue(cues, "s1mple", 2, 480) };
    return (
      <AbsoluteFill>
        <Held ds={seg.ds as Ds} rows={10} day={1} focus={[seg.team as string]} />
        <AbsoluteFill style={{ backgroundColor: "rgba(14,17,23,0.6)" }} />
        <StoryCard team={seg.team as string} roster={seg.roster as [string, string][]} rank={seg.rank as [number, number]} at={at} />
        <Sfx at={0} sound="whooshBig" volume={0.45} />
        <Sfx at={at.blocked} sound="lose" volume={0.35} lead={0} />
        <Sfx at={at.blocked} sound="impact3" volume={0.4} />
        <Sfx at={at.appeal} sound="chime" volume={0.35} />
        <Sfx at={at.second} sound="pop1" volume={0.4} lead={0} />
        <Sfx at={at.s1mple} sound="hit" volume={0.55} />
      </AbsoluteFill>
    );
  }
  if (seg.kind === "madeit") {
    const stages = seg.stages as { teamAt: number[] }[];
    return (
      <AbsoluteFill>
        <RegionEndBg ds={seg.ds as Ds} />
        <MadeItCard region={seg.region as string} stages={seg.stages as never} />
        <Sfx at={0} sound="whooshMed" volume={0.4} />
        {(seg.stages as { at: number }[]).map((s, i) => <Sfx key={`u${i}`} at={s.at} sound="up" volume={0.3} />)}
        {stages.flatMap((s, i) => s.teamAt.map((f, j) => <Sfx key={`${i}-${j}`} at={f} sound={(i + j) % 2 ? "pop2" : "pop1"} volume={0.45} lead={0} />))}
        <Sfx at={Math.max(...stages.flatMap((s) => s.teamAt)) + 10} sound="chime" volume={0.35} />
      </AbsoluteFill>
    );
  }
  return <Page05 page={seg.page as string} cues={seg.cues as Record<string, number>} field={FIELD} />;
};

// Segments run back to back: each one lasts until the next starts (no empty frames in the pauses between regions).
const SPANS = T.segments.map((s, i) => {
  const from = i === 0 ? 0 : s.from;
  const to = i + 1 < T.segments.length ? T.segments[i + 1].from : T.total;
  return { seg: { ...s, from, dur: s.dur + (s.from - from) }, from, dur: to - from };
});

// Camera plan: one key per beat, glides only (no cuts). Values are deliberately small (see cards/Camera.tsx).
const rowHOf = (rows: number) => Math.min(72, Math.floor((1080 - 190 - 70) / rows));   // as in RankingRace
const lineY = (ds: Ds, rows: number) => 190 + RACES[ds].spots * rowHOf(rows);
const CAMERA: CamKey[] = (() => {
  const keys: CamKey[] = [{ f: 0, glide: 1, shot: SHOTS.wide }];
  let side: 1 | -1 = -1;
  const tilt = (): Shot => ((side = side === 1 ? -1 : 1) === 1 ? SHOTS.left : SHOTS.right);
  let page = 0;
  for (const { seg, from, dur } of SPANS) {
    const s = seg as Seg;
    const k = (f: number, glide: number, shot: Shot) => keys.push({ f: from + f, glide: Math.max(20, glide), shot });
    if (s.kind === "race") {
      const ly = lineY(s.ds as Ds, s.rows as number);
      if (s.free) k(0, dur, lineShot(ly, side));                                   // slow push to the line while the days run
      else if (!((s.steps as Step[]) ?? []).length) { k(0, 40, SHOTS.wide); k(45, dur - 45, SHOTS.push); }   // region banner
      else {
        for (const t of stepTimes(s)) {
          if (t.st.card) k(t.st.at, 45, tilt());                                    // the card comes up: orbit a little
          if (t.moving) {
            k(t.moveAt, 40, lineShot(ly, 0));                                       // the race moves: close on the line
            k(t.moveAt + t.moveFrames + 20, t.end - t.moveAt - t.moveFrames - 20, lineShot(ly, side));   // stamps: hold, drift
          }
        }
      }
    } else if (s.kind === "verdict") { k(0, 45, SHOTS.high); k(s.switchAt as number, 50, tilt()); }
    else if (s.kind === "missed" || s.kind === "madeit" || s.kind === "story") { k(0, 40, SHOTS.push); k(40, dur - 40, tilt()); }
    else { k(0, 30, SHOTS.wide); k(30, dur - 30, page++ % 2 ? SHOTS.high : SHOTS.push); }   // full pages: centred shots only
  }
  return keys;
})();

export const Video05: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg }}>
    <SfxSeed offset={0}>
    <CameraRig keys={CAMERA} background={C.bg}>
      {SPANS.map(({ seg: s, from, dur }, i) => (
        <Sequence key={i} from={from} durationInFrames={dur} premountFor={30}>
          <SfxSeed offset={from}>
            <Segment seg={s} />
          </SfxSeed>
        </Sequence>
      ))}
    </CameraRig>
    {SPANS.filter(({ seg }) => (seg as Seg).kind === "race" && !(seg as Seg).free && ((seg as Seg).steps as Step[])?.[0]?.card).map(({ from }) => (
      <Sfx key={`r${from}`} at={from + 6} sound="riser" volume={0.32} lead={56} />
    ))}
    {T.audio.map((a) => (
      <Sequence key={a.id} from={a.from} layout="none">
        <Audio src={staticFile(a.file)} volume={1} />
      </Sequence>
    ))}
    </SfxSeed>
  </AbsoluteFill>
);
