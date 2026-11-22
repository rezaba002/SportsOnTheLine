import React from "react";
import { AbsoluteFill, Html5Audio as Audio, OffthreadVideo, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import timeline from "../../public/data/video09_v4.json";
import cutaways from "../../public/data/video09_broll.json";
import { framing, soloFramingKeys, CameraKey } from "./camera";
import { FONT } from "../theme";
import { Logo } from "../cards/parts";
import { SFX, POOLS, SfxSeed } from "../cards/Sfx";
import { CapCue } from "../cards/Captions";
import { EditorialCaptions, EmphasisMoments } from "./EditorialCaptions";
import { INTRO3_FRAMES } from "../cards/ChannelIntro3";

type Player = { team: string; maps: number; swing_per_map: number; by_time: Record<string, number>; by_phase: Record<string, number>; late_by_phase?: Record<string, number>; ci95_match_bootstrap: [number, number] };
type Block = { id: string; scene: string; focus: string; text: string; from: number; dur: number; file?: string };
type Segment = { scene: string; from: number; to: number; blocks: string[] };
const D = timeline as unknown as { preview_only: boolean; total: number; end_from: number; intro: { from: number }; blocks: Block[];
  segments: Segment[]; words: {w: string; s: number; block: string}[]; captions: CapCue[]; research: { coverage: { rounds: number }; players: Record<string, Player>; team_objectives: Record<string, Record<string, number>> } };
export const VIDEO09_V4_FRAMES = D.total;
const BG = "#080f14", WHITE = "#eff4ed", MUTED = "#a0b4b5", GREEN = "#81f1b2", YELLOW = "#edff35", RED = "#ff827b", BLUE = "#73cbff";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(.18, .82, .22, 1);
const enter = (f: number, at = 0, dur = 18) => interpolate(f, [at, at + dur], [0, 1], { ...clamp, easing: ease });

const normalized = (word: string) => word.toLowerCase().replace(/'s\b/g, "").replace(/[^a-z0-9]/g, "");
const blockAt = (id: string) => D.blocks.find(b => b.id === id)?.from ?? 0;
const visibleFrame = (frame: number) => {
  const cut = cutaways.find(c => frame >= c.at * 30 - 4 && frame < (c.at + c.duration) * 30);
  return cut ? Math.round((cut.at + cut.duration) * 30) + 5 : frame;
};
const cue = (id: string, word: string, start: number, fallback = 20) => Math.max(0,
  visibleFrame((D.words.find(w => w.block === id && normalized(w.w) === normalized(word))?.s ?? blockAt(id) + fallback) - 3) - start);
const pop = (f: number, at: number) => interpolate(f, [at, at + 7, at + 30], [0, 1, 0], { ...clamp, easing: ease });
const revealStyle = (f: number, at: number, distance = 24): React.CSSProperties => ({
  opacity: enter(f, at, 18), transform: `translateY(${(1 - enter(f, at, 18)) * distance}px)`,
});

const fmt = (x: number) => `${x >= 0 ? "+" : "−"}${Math.abs(x).toFixed(2)}`;
const stats = (name: string) => D.research.players[name];
// Native audio keeps WAV effects out of the software decoder that asserted
// while reading the otherwise-valid intro sound bed during the full render.
const Sfx: React.FC<{ at: number; sound: keyof typeof SFX | keyof typeof POOLS; volume?: number; n?: number }> = ({ at, sound, volume = .25, n = 0 }) => {
  const pool = (POOLS as Record<string, readonly (keyof typeof SFX)[]>)[sound];
  const seed = Math.abs(Math.round(at) + n * 17 + [...sound].reduce((s, c) => s + c.charCodeAt(0), 0));
  const member = pool ? pool[seed % pool.length] : sound as keyof typeof SFX;
  const pitch = seed % 7 - 3;
  const src = SFX[member].replace(/^sfx\/(.+)\.wav$/, `sfx/v/$1_${pitch}.wav`);
  return <Sequence from={Math.max(0, Math.round(at - 2))} durationInFrames={90} layout="none"><Audio src={staticFile(src)} volume={volume} /></Sequence>;
};
const objective = (team: string) => {
  const norm = (s: string) => s.toLowerCase().replace(/team|esports|[^a-z0-9]/g, "");
  const out: Record<string, number> = {};
  for (const [name, values] of Object.entries(D.research.team_objectives)) {
    if (norm(name) === norm(team)) for (const [k, v] of Object.entries(values)) out[k] = (out[k] ?? 0) + v;
  }
  return out;
};
const color = (p: Player) => p.ci95_match_bootstrap[0] <= 0 && p.ci95_match_bootstrap[1] >= 0 ? WHITE : p.swing_per_map >= 0 ? GREEN : RED;
const PLAYERS: Record<string, string[]> = { hook: ["donk", "ZywOo", "m0NESY"], spirit: ["donk", "sh1ro", "zont1x"], heroic: ["nilo", "MartinezSa", "Brollan", "susp"],
  vitality: ["ZywOo"], parivision: ["Jame"], falcons: ["m0NESY", "NiKo", "kyousuke", "karrigan"], mongolz: ["910"] };
const LABELS: Record<string, [string, string]> = { hook: ["SINGAPORE / 2026", "WATCH THE WHOLE TEAM"], spirit: ["SPIRIT", "THE STAR. THE FOLLOW-THROUGH. THE QUESTION."],
  heroic: ["DISCOVERY 01 / HEROIC", "NILO DESERVES YOUR ATTENTION"], vitality: ["VITALITY", "WAIT FOR ZYWOO'S ROUND"], parivision: ["DISCOVERY 02 / PVISION", "THE CALLER WITH A POSITIVE SWING"],
  falcons: ["FALCONS", "KEEP THE WHOLE TEAM IN FRAME"], mongolz: ["DISCOVERY 03 / THE MONGOLZ", "THE OTHER SIDE HAS AN AWP TOO"], method: ["THE MEASURE", "THE BOMB CHANGES THE QUESTION"], watch: ["YOUR MAJOR WATCH LIST", "STARS + DISCOVERIES"], end: ["SPORTS ON THE LINE", "TAKE ANOTHER QUESTION INTO THE MATCH"] };
const TAKEAWAY: Record<string, string> = { s1: "WATCH THE FIRST FIGHT", s2: "THEN WATCH THE FOLLOW-THROUGH", s3: "CAN ZONT1X GIVE THEM MORE?", n1: "WATCH HEROIC FOR NILO", n2: "WHO SHARES THE BURDEN?",
  z1: "DON'T STOP WATCHING AFTER THE FIRST MINUTE", z2: "LATE ROUND ≠ ONE KIND OF SITUATION", j1: "TWO JOBS. ONE PLAYER TO FOLLOW.", j2: "WATCH THE SITUATION AROUND THE AWP", f1: "WATCH WHAT M0NESY CAN BUILD ON", f2: "ADVANTAGE — OR A RESCUE JOB?", f3: "FRAGGING SWING DOES NOT PRICE THE CALLS", t1: "PUT 910 ON YOUR WATCH LIST", t2: "A REASON TO WATCH. AN EXPECTATION TO TEST." };

const Backdrop: React.FC<{ scene: string }> = ({ scene }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: BG, overflow: "hidden" }}>
    <AbsoluteFill style={{ backgroundImage: "linear-gradient(#1b333740 1px, transparent 1px),linear-gradient(90deg,#1b333740 1px,transparent 1px)", backgroundSize: "70px 70px", transform: `translateY(${f % 70}px)`, opacity: .6 }} />
    <div style={{ position: "absolute", width: 1200, height: 1200, borderRadius: "50%", left: 500 + Math.sin(f / 170) * 80, top: -450, background: `radial-gradient(circle,${scene === "heroic" || scene === "parivision" || scene === "mongolz" ? "#375315" : "#163c42"}88,transparent 65%)` }} />
    <svg width="1920" height="1080" style={{ position: "absolute", opacity: .15 }}><path d="M0 800 H260 V630 H520 V790 H780 V350 H1180 V550 H1550 V280 H1920" fill="none" stroke={BLUE} strokeWidth="3" strokeDasharray="15 18" strokeDashoffset={-f * 1.2} /></svg>
    <div style={{ position: "absolute", left: 0, right: 0, height: 2, background: YELLOW, top: (f * 3) % 1080, opacity: .045 }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at center,transparent 35%,#03080cb0 100%)" }} />
  </AbsoluteFill>;
};

const Portrait: React.FC<{ name: string; style?: React.CSSProperties }> = ({ name, style }) => <Img src={staticFile(name === "ZywOo" ? "thumb/zywoo_cut.png" : `video09-v4/players/${name}.webp`)}
  style={{ objectFit: "contain", objectPosition: "center bottom", ...style }} />;

const PlayerPanel: React.FC<{ name: string; x: number; active: boolean; index: number; hook?: boolean; at?: number; numberAt?: number; mentionAt?: number }> = ({ name, x, active, index, hook, at = index * 4, numberAt = at + 28, mentionAt = at }) => {
  const f = useCurrentFrame(), p = stats(name), col = color(p), reveal = enter(f, at, 20), accent = pop(f, mentionAt);
  return <div style={{ position: "absolute", left: x - 200, top: 225, width: 400, height: 540, opacity: reveal * (active ? 1 : .66),
    transform: `translateY(${(1 - reveal) * 90}px)`, border: `1px solid ${active ? col : "#36515a"}`, borderRadius: 22,
    background: `linear-gradient(160deg,${active ? "#203840" : "#152029"}e8,#0a131af5)`, boxShadow: active ? `0 0 ${50 + accent * 65}px ${col}30` : "none" }}>
    <div style={{ position: "absolute", left: 26, right: 26, top: 20, display: "flex", alignItems: "center", justifyContent: "space-between", color: MUTED, fontSize: 20, letterSpacing: 3 }}>
      <span>{p.team.toUpperCase()}</span><Logo team={p.team} size={48} />
    </div>
    <Portrait name={name} style={{ position: "absolute", left: 10, top: 65, width: 380, height: 285, opacity: enter(f, at + 5), transform: `scale(${1 + .025 * accent})`, filter: active ? `drop-shadow(0 0 18px ${col}35)` : "saturate(.45)" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 280, height: 70, background: "linear-gradient(transparent,#10212b)" }} />
    <div style={{ position: "absolute", left: 25, right: 25, top: 330, fontSize: name.length > 9 ? 43 : 54, fontWeight: 700, ...revealStyle(f, at + 12, 15) }}>{name}</div>
    {!hook && <>
      <div style={{ position: "absolute", left: 25, top: 390, color: col, fontSize: 88, fontWeight: 700, fontVariantNumeric: "tabular-nums", letterSpacing: -3, ...revealStyle(f, numberAt, 18) }}>{fmt(p.swing_per_map * enter(f, numberAt, 26))}</div>
      <div style={{ position: "absolute", left: 27, top: 485, color: MUTED, fontSize: 21, letterSpacing: 2, ...revealStyle(f, numberAt + 9, 10) }}>MODEL SWING / MAP</div>
      <div style={{ position: "absolute", left: 27, top: 515, color: MUTED, fontSize: 18, ...revealStyle(f, numberAt + 18, 8) }}>{p.maps} season maps · kills & deaths</div>
    </>}
    {hook && <div style={{ position: "absolute", left: 25, top: 425, fontSize: 31, letterSpacing: 3, color: YELLOW }}>YOU KNOW THE NAME.</div>}
  </div>;
};

const TeamBoard: React.FC<{ segment: Segment; blocks: Block[] }> = ({ segment, blocks }) => {
  const f = useCurrentFrame(), names = PLAYERS[segment.scene], hook = segment.scene === "hook";
  const current = [...blocks].reverse().find(b => f >= b.from - segment.from) ?? blocks[0];
  const xs = names.map((_, i) => names.length === 1 ? 590 : names.length === 4 ? 300 + i * 440 : 420 + i * 540);
  const keys: CameraKey[] = names.length === 1 ? soloFramingKeys(blocks, segment.from) : [];
  const norm = (s: string) => s.toLowerCase().replace(/'s\b/g, "").replace(/[^a-z0-9]/g, "");
  const nameCues: {f: number; name: string}[] = [];
  if (names.length > 1) for (const b of blocks) {
    const i = names.indexOf(b.focus), at = b.from - segment.from;
    const wideZ = names.length === 4 ? .88 : .94;
    const other = D.words.find(w => w.block === b.id && names.some(n => norm(n) === norm(w.w) && n !== b.focus));
    const comparisonAt = other ? other.s - segment.from - 60 : Infinity;
    if (i < 0 || comparisonAt <= at + 72) {
      keys.push({ f: at, x: 960, z: wideZ, dur: 60 });
    } else {
      keys.push({ f: at, x: Math.max(700, Math.min(1220, xs[i])), z: 1.015, dur: 48 });
      keys.push({ f: Math.min(comparisonAt, at + Math.max(90, b.dur * .68)), x: 960, z: wideZ, dur: 60 });
    }
  }
  if (names.length > 1) {
    for (const word of D.words.filter(w => segment.blocks.includes(w.block))) {
      const i = names.findIndex(n => norm(n) === norm(word.w));
      if (i >= 0) {
        const at = Math.max(0, word.s - segment.from - 3);
        nameCues.push({f: at, name: names[i]});
      }
    }
  }
  keys.sort((a, b) => a.f - b.f);
  const shot = framing(keys, f);
  const spokenFocus = [...nameCues].reverse().find(c => c.f <= f)?.name ?? current.focus;
  const main = stats(names[0]);
  const chartAt = current.from - segment.from;
  const graphValues = segment.scene === "vitality" ? (current.id === "z1" ? main.by_time : main.late_by_phase ?? main.by_phase) : main.by_phase;
  return <>
    <AbsoluteFill style={{ transformOrigin: "0 0", transform: `translate(960px,490px) scale(${shot.z}) translate(${-shot.x}px,-490px)` }}>
      {names.map((name, i) => {
        const mentions = D.words.filter(w => segment.blocks.includes(w.block) && normalized(w.w) === normalized(name));
        const first = mentions[0];
        const at = name === blocks[0].focus ? 8 : first ? Math.max(8, visibleFrame(first.s - 5) - segment.from) : segment.to - segment.from + 30;
        const owner = blocks.find(b => b.focus === name) ?? blocks.find(b => b.text.includes(name));
        const metricWord = owner?.text.includes("negative") ? "negative" : owner?.text.includes("positive") ? "positive" : "swing";
        const numberAt = Math.max(at + 26, owner ? cue(owner.id, metricWord, segment.from, Math.max(30, at + segment.from - owner.from + 26)) : at + 26);
        const mentionAt = [...mentions].reverse().find(w => w.s - segment.from <= f)?.s ?? segment.from + at;
        return <PlayerPanel key={name} name={name} x={xs[i]} index={i} at={at} numberAt={numberAt} mentionAt={mentionAt - segment.from} active={name === spokenFocus || f > current.from - segment.from + current.dur * .72} hook={hook} />;
      })}
      {names.length === 1 && <div style={{ position: "absolute", left: 920, top: 280, width: 730 }}>
        <div style={{ color: YELLOW, fontSize: 25, letterSpacing: 4, ...revealStyle(f, chartAt + 12) }}>{current.id === "z2" ? "WHERE THE LATE SWING HAPPENS" : "WHERE THE SWING HAPPENS"}</div>
        {segment.scene === "mongolz" && current.id === "t2" && f >= cue("t2", "plant", segment.from) ? <ObjectivePanel team="The MongolZ" start={segment.from} /> : Object.entries(graphValues).map(([key, value], i) => {
          const phaseWord = key === "preplant" ? "plant" : key === "postplant_attack" ? "defend" : "defuse";
          const at = current.id === "z2" ? cue(current.id, phaseWord, segment.from, 35 + i * 28) + i * 6
            : current.id === "z1" && key === "60+" ? cue("z1", "minute", segment.from)
            : Math.max(chartAt + 30 + i * 26, visibleFrame(segment.from + chartAt + 30 + i * 26) - segment.from);
          const emphasisAt = key === "60+" ? cue(current.id, "minute", segment.from, 150) : key === "preplant" ? cue(current.id, "plant", segment.from, 100) : at;
          return <div key={current.id + key} style={{ marginTop: 35, ...revealStyle(f, at, 20), transformOrigin: "left center", scale: 1 + .025 * pop(f, emphasisAt), opacity: enter(f, at, 18) * (segment.scene === "mongolz" && current.id === "t2" ? 1 - enter(f, cue("t2", "plant", segment.from) - 12, 12) : 1) }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, color: WHITE }}><span>{({ "0-30": "FIRST 30 SECONDS", "30-60": "30–60 SECONDS", "60+": "AFTER ONE MINUTE", preplant: "BEFORE THE PLANT", postplant_attack: "BOMB DEFENCE / T", retake: "RETAKE / CT" } as Record<string, string>)[key]}</span><span style={{ color: value >= 0 ? GREEN : RED }}>{fmt(value)}</span></div>
          <div style={{ height: 12, marginTop: 15, width: Math.max(3, Math.abs(value) / Math.max(.001, ...Object.values(graphValues).map(Math.abs)) * 680) * enter(f, at + 5, 30), background: value >= 0 ? GREEN : RED, borderRadius: 6 }} />
        </div>;
        })}
        {current.id !== "t2" && <div style={{ marginTop: 36, color: MUTED, fontSize: 22, ...revealStyle(f, chartAt + 125, 10) }}>Contributions per map · different phase opportunities</div>}
      </div>}
    </AbsoluteFill>
    {hook ? <HookPromise active={current.id === "h2"} /> : blocks.map((b, i) => {
      const at = b.from - segment.from + 18, next = blocks[i + 1]?.from ?? segment.to;
      const opacity = enter(f, at, 18) * (1 - enter(f, next - segment.from - 10, 10));
      return <div key={b.id} style={{ position: "absolute", top: 840, left: 100, right: 100, textAlign: "center", color: YELLOW, fontSize: 34, fontWeight: 700, letterSpacing: 2, opacity, transform: `translateY(${(1 - enter(f, at, 18)) * 20}px)` }}>{TAKEAWAY[b.id]}</div>;
    })}
    {blocks.map((b, i) => <React.Fragment key={b.id}>
      <Sfx at={b.from - segment.from + 2} sound="camWhoosh" n={i} volume={.32} />
      <Sfx at={b.from - segment.from + 11} sound="impact2" volume={.2} />
    </React.Fragment>)}
  </>;
};

const ObjectivePanel: React.FC<{ team: string; start: number }> = ({ team, start }) => {
  const f = useCurrentFrame(), v = objective(team), titleAt = cue("t2", "plant", start);
  return <div style={{ marginTop: 30 }}>
    <div style={{ fontSize: 44, color: YELLOW, marginBottom: 30, ...revealStyle(f, titleAt) }}>{team.toUpperCase()} / AFTER THE PLANT</div>
    {[["T-SIDE POST-PLANTS WON", "postplant_attack"], ["CT RETAKES WON", "retake"]].map(([label, key], i) => {
      const n = v[`${key}_rounds`] ?? 0, wins = v[`${key}_wins`] ?? 0, p = n ? wins / n : 0;
      const at = Math.max(titleAt + 18 + i * 30, cue("t2", i ? "baseline" : "conversion", start));
      const progress = enter(f, at + 5, 30);
      return <div key={key} style={{ marginBottom: 35, ...revealStyle(f, at) }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 26 }}><span>{label}</span><strong style={{ color: key === "retake" ? BLUE : GREEN, fontSize: 40 }}>{Math.round(p * progress * 100)}%</strong></div>
        <div style={{ height: 14, marginTop: 12, background: "#284149", borderRadius: 7 }}><div style={{ width: `${p * progress * 100}%`, height: 14, background: key === "retake" ? BLUE : GREEN, borderRadius: 7 }} /></div>
        <div style={{ marginTop: 10, color: MUTED, fontSize: 21, opacity: enter(f, at + 25) }}>{wins} wins / {n} planted rounds · team outcomes</div>
      </div>;
    })}
    <div style={{ color: MUTED, fontSize: 22, ...revealStyle(f, cue("t2", "guarantee", start), 12) }}>Season opponents · a baseline to watch, not a forecast</div>
  </div>;
};

const HookPromise: React.FC<{ active: boolean }> = ({ active }) => {
  const f = useCurrentFrame();
  return <div style={{ position: "absolute", left: 100, right: 100, top: 760, padding: "26px 50px", background: "#0a181cf5", borderTop: `3px solid ${YELLOW}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    <div style={{ fontSize: 29, letterSpacing: 4, color: MUTED }}>{active ? "OUTSIDE THE FAVOURITES" : "SINGAPORE MAJOR"}</div>
    <div style={{ fontSize: active ? 53 : 47, fontWeight: 700, color: active ? YELLOW : WHITE }}>{active ? "3 PLAYERS YOU SHOULD KNOW" : "THERE'S MORE TO WATCH"}</div>
    <div style={{ height: 6, width: 90, background: YELLOW, transform: `scaleX(${.7 + Math.sin(f / 10) * .15})` }} />
  </div>;
};

const BombDiagram: React.FC<{ blocks: Block[]; start: number }> = ({ blocks, start }) => {
  const f = useCurrentFrame(), rightAt = cue("m1", "planted", start);
  const plusAt = cue("m2", "Plus", start), limitAt = cue("m2", "utility", start);
  const second = f >= blocks[1].from - start;
  return <>
    <div style={{ position: "absolute", left: 150, top: 240, width: 1620, height: 530, borderRadius: 30, border: "1px solid #45636b", background: "#112028dd", ...revealStyle(f, 4, 35) }}>
      <div style={{ position: "absolute", top: 40, left: 40, fontSize: 24, letterSpacing: 3, color: MUTED, ...revealStyle(f, 14, 10) }}>SCHEMATIC EXAMPLE · {D.research.coverage.rounds.toLocaleString("en-US")} ROUNDS IN THE ANALYSIS</div>
      {[false, true].map((planted, index) => {
        const at = planted ? rightAt : 22, heading = enter(f, at, 18);
        const highlight = pop(f, planted ? rightAt : cue("m1", "players", start));
        return <div key={index} style={{ position: "absolute", left: index * 790 + 55, top: 120, width: 650, height: 350 }}>
          <div style={{ fontSize: 52, color: planted ? YELLOW : BLUE, fontWeight: 700, opacity: heading, transform: `translateX(${(1 - heading) * (planted ? 35 : -35)}px)` }}>{planted ? "BOMB DOWN" : "BEFORE THE PLANT"}</div>
          <div style={{ display: "flex", gap: 18, marginTop: 40 }}>{[0, 1, 2, 3, 4, 5].map(i => {
            if (i === 3) return <span key={i} style={{ fontSize: 55, marginLeft: 18, opacity: enter(f, at + 20) }}>vs</span>;
            const col = i < 3 ? BLUE : YELLOW, p = enter(f, at + 10 + i * 5, 14);
            return <div key={i} style={{ width: 66, height: 66, border: `3px solid ${col}`, borderRadius: "50%", background: `${i < 3 ? "#285c76" : "#a6ad19"}40`, opacity: p, transform: `translateY(${(1 - p) * 26}px) scale(${.65 + .35 * p + .06 * highlight})`, boxShadow: `0 0 ${highlight * 28}px ${col}88` }} />;
          })}</div>
          <div style={{ fontSize: 36, marginTop: 50, color: planted ? YELLOW : WHITE, ...revealStyle(f, at + 52, 15) }}>{planted ? "DEFEND IT — OR DEFUSE IT" : "TAKE THE SITE. FIND THE PLANT."}</div>
          {planted && <div style={{ position: "absolute", left: 540, top: -10, width: 88, height: 88, borderRadius: 14, border: `3px solid ${YELLOW}`, display: "grid", placeItems: "center", fontSize: 50, color: YELLOW, opacity: enter(f, rightAt + 12), transform: `scale(${.5 + .5 * enter(f, rightAt + 12) + .08 * pop(f, rightAt + 12)})`, boxShadow: `0 0 ${15 + 35 * pop(f, rightAt + 12)}px ${YELLOW}66` }}>C4</div>}
        </div>;
      })}
      <div style={{ position: "absolute", left: 790, top: 130, bottom: 90, width: 2, background: "#45636b", transform: `scaleY(${enter(f, rightAt - 12)})`, transformOrigin: "top" }} />
      <div style={{ position: "absolute", left: 55, bottom: 22, display: "flex", gap: 20 }}>
        {[["ALIVE", "alive"], ["BUYS", "buys"], ["MAP", "map"], ["CLOCK", "clock"]].map(([label, word], i) => {
          const at = cue("m1", word, start) + i * 5;
          return <div key={word} style={{ padding: "7px 18px", border: `1px solid ${BLUE}88`, borderRadius: 8, color: BLUE, fontSize: 20, letterSpacing: 2, ...revealStyle(f, at, 14), background: `rgba(115,203,255,${.05 + .14 * pop(f, at)})` }}>{label}</div>;
        })}
      </div>
    </div>
    <div style={{ position: "absolute", top: 810, left: 150, right: 150, textAlign: "center", fontSize: 34, color: YELLOW, opacity: enter(f, 90) * (1 - enter(f, blocks[1].from - start - 8, 8)) }}>THE SAME KILL CAN CHANGE A DIFFERENT SITUATION</div>
    <div style={{ position: "absolute", top: 800, left: 150, right: 150, textAlign: "center", fontSize: 33, color: WHITE, ...revealStyle(f, plusAt, 30) }}>
      <span style={{ color: YELLOW, fontSize: 52, display: "inline-block", transform: `scale(${1 + .1 * pop(f, plusAt)})` }}>+1</span> = A ROUND'S WORTH OF ESTIMATED FIGHT SWING
    </div>
    {second && <div style={{ position: "absolute", top: 870, left: 150, right: 150, textAlign: "center", color: MUTED, fontSize: 25, ...revealStyle(f, limitAt, 12) }}>FIGHTS ONLY · UTILITY AND CALLING ARE OUTSIDE THIS MEASURE</div>}
    <Sfx at={5} sound="sweep" volume={.25} /><Sfx at={blocks[1].from - start} sound="toggle" volume={.17} />
  </>;
};

const WatchList: React.FC = () => {
  const f = useCurrentFrame(), start = D.segments.find(s => s.scene === "watch")?.from ?? 0;
  return <>
    {[["THE STARS", ["donk", "sh1ro", "ZywOo", "m0NESY"], BLUE, 130], ["THE DISCOVERIES", ["nilo", "Jame", "910"], YELLOW, 1010]].map(([heading, names, col, x]) => <div key={heading as string} style={{ position: "absolute", left: x as number, top: 240, width: 780 }}>
      <div style={{ color: col as string, fontSize: 42, letterSpacing: 4, marginBottom: 36, ...revealStyle(f, cue("w1", heading === "THE STARS" ? "stars" : "discoveries", start)) }}>{heading as string}</div>
      {(names as string[]).map((n, i) => <div key={n} style={{ display: "flex", alignItems: "center", gap: 28, borderTop: "1px solid #38535b", padding: "22px 10px", opacity: enter(f, cue("w1", n, start) + i * 2), transform: `translateX(${(1 - enter(f, cue("w1", n, start) + i * 2)) * 60}px)`, background: `rgba(237,255,53,${.11 * pop(f, cue("w1", n, start))})` }}>
        <Logo team={stats(n).team} size={62} /><div style={{ fontSize: 56, fontWeight: 700 }}>{n}</div><div style={{ marginLeft: "auto", fontSize: 27, color: MUTED }}>{stats(n).team}</div>
      </div>)}
    </div>)}
    <div style={{ position: "absolute", left: 130, right: 130, top: 850, textAlign: "center", fontSize: 32, color: YELLOW, ...revealStyle(f, blockAt("w2") - start + 4) }}>EXPECTATIONS TO TEST WHEN THE MATCHES START.</div>
    {[0, 1, 2, 3].map(i => <Sfx key={i} at={i * 6 + 4} sound="click" n={i} volume={.13} />)}
  </>;
};

const EndScreenV4: React.FC = () => {
  const f = useCurrentFrame();
  return <>
    <div style={{ position: "absolute", left: 110, right: 110, top: 225, textAlign: "center", fontSize: 42, color: MUTED }}>KEEP WATCHING THE STORY BEHIND THE NUMBERS</div>
    {[140, 1140].map((x, i) => <div key={x} style={{ position: "absolute", left: x, top: 370, width: 640, height: 360, borderRadius: 18, border: `2px solid ${i ? BLUE : YELLOW}66`, background: "#12202955", opacity: enter(f, 14 + i * 18, 20), transform: `translateY(${(1 - enter(f, 14 + i * 18, 20)) * 35}px)` }}>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: -60, color: MUTED, fontSize: 25, letterSpacing: 4, textAlign: "center" }}>{i ? "ANOTHER ANGLE" : "WATCH NEXT"}</div>
    </div>)}
    <div style={{ position: "absolute", left: 855, top: 445, width: 210, height: 210, borderRadius: "50%", border: "1px solid #779092", display: "grid", placeItems: "center" }}><Img src={staticFile("brand/logo.png")} style={{ width: 155, height: 155, objectFit: "contain" }} /></div>
    <Sfx at={0} sound="swell" volume={.14} />
  </>;
};

const Scene: React.FC<{ segment: Segment }> = ({ segment }) => {
  const f = useCurrentFrame(), blocks = D.blocks.filter(b => segment.blocks.includes(b.id));
  const [kicker, title] = LABELS[segment.scene];
  const opacity = enter(f, 0, 12) * (segment.scene === "end" ? 1 : 1 - enter(f, segment.to - segment.from - 10, 10));
  return <AbsoluteFill style={{ opacity }}>
    <Backdrop scene={segment.scene} />
    <div style={{ position: "absolute", top: 55, left: 100, right: 100, color: YELLOW, letterSpacing: 5, fontSize: 23, ...revealStyle(f, 0, 12) }}>{kicker}<span style={{ float: "right", color: MUTED, fontSize: 19 }}>SPORTS ON THE LINE / ORIGINAL ANALYSIS</span></div>
    <div style={{ position: "absolute", top: 100, left: 100, right: 100, fontSize: title.length > 43 ? 44 : 54, fontWeight: 700, letterSpacing: 1, zIndex: 2, ...revealStyle(f, 7, 22) }}>{title}</div>
    {PLAYERS[segment.scene] ? <TeamBoard segment={segment} blocks={blocks} /> : segment.scene === "method" ? <BombDiagram blocks={blocks} start={segment.from} /> : segment.scene === "watch" ? <WatchList /> : <EndScreenV4 />}
    <div style={{ position: "absolute", top: 0, left: 0, bottom: 0, width: 12, background: YELLOW, transform: `scaleY(${1 - enter(f, 4, 18)})`, transformOrigin: "top" }} />
    <Sfx at={0} sound="whooshMed" volume={.24} />
  </AbsoluteFill>;
};

export const Video09V4: React.FC = () => <AbsoluteFill style={{ background: BG, color: WHITE, fontFamily: FONT }}>
  <SfxSeed offset={0}>
    {D.segments.map((s, i) => <Sequence key={`${s.scene}-${i}`} from={s.from} durationInFrames={s.to - s.from}><SfxSeed offset={s.from}><Scene segment={s} /></SfxSeed></Sequence>)}
    <Sequence from={D.intro.from} durationInFrames={INTRO3_FRAMES}><OffthreadVideo src={staticFile("video09-v4/intro.mp4")} /></Sequence>
    {D.blocks.filter(b => b.file).map(b => <Sequence key={b.id} from={b.from} durationInFrames={b.dur + 3} layout="none"><Audio src={staticFile(b.file as string)} volume={1} /></Sequence>)}
  </SfxSeed>
  <EmphasisMoments />
  <EditorialCaptions cues={D.captions} />
  {D.preview_only && <div style={{ position: "absolute", right: 24, bottom: 12, color: YELLOW, fontSize: 20, background: BG }}>WORKING CUT · PARTIAL RESEARCH</div>}
</AbsoluteFill>;
