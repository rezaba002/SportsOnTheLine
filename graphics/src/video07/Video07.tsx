import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import data from "../../public/data/video07.json";
import { C, FONT } from "../theme";
import { teamColor } from "../teams";
import { Logo } from "../cards/parts";
import { Halo } from "../cards/fx";
import { Sfx, SfxSeed } from "../cards/Sfx";
import { CameraRig, CamKey, Shot } from "../cards/Camera";

// Video 07 — "Every CS2 roster move since Cologne: which ones worked?" (16:9, ~3 min).
// All numbers from public/data/video07.json (video07/work/timeline.py <- moves.py). One scene per script section; inside a
// section, elements enter on the word that names them. Camera rig + varied sounds (no repeated jingles).

type Word = { w: string; s: number; e: number; block: string };
type Block = { id: string; from: number; dur: number; file: string };
type Card = { team: string; in: string[]; out: string[]; win_A: number; win_B: number; verdict_pts: number; rank_jun: number | null; rank_nov: number | null; moved: boolean };
const D = data as unknown as {
  total: number; end_from: number; blocks: Block[]; words: Word[]; hook_teams: { team: string; n_in: number }[];
  answer: { moved_n: number; moved_up: number; kept_n: number; kept_up: number; avg_pts: number };
  method_example: Card; best: Card[]; best_more: Card[]; worst: Card[]; still: Card[];
  spirit: Card & { valve_ranks: Record<string, number | null> }; too_early: string[];
  jl: { team: string; from: string; to: string; matches: number }[];
};
export const VIDEO07_FRAMES = D.total;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const OUT = Easing.bezier(0.16, 1, 0.3, 1);
const GREEN = "#4cc878", RED = "#e44c4c", YELLOW = "#ffd34d", CT = "#5d9cec";
const B = Object.fromEntries(D.blocks.map((b) => [b.id, b]));
const norm = (s: string) => s.toLowerCase().replace(/[^\w]/g, "");
const cue = (id: string, word: string, nth = 1) => D.words.filter((w) => w.block === id && norm(w.w) === norm(word))[nth - 1]?.s ?? B[id].from;
const SECTIONS = [["hook", "h1"], ["method", "m1"], ["answer", "a1"], ["best", "b1"], ["jl", "s1"], ["worst", "w1"], ["early", "t1"], ["close", "z1"]] as const;
const SPAN: { name: string; from: number; to: number }[] = [
  ...SECTIONS.map(([name, first], i) => ({ name: name as string, from: i === 0 ? 0 : B[first].from - 6, to: i + 1 < SECTIONS.length ? B[SECTIONS[i + 1][1]].from - 6 : D.end_from })),
  { name: "end", from: D.end_from, to: D.total },          // 20 s end screen for YouTube's end-screen elements
];
const pIn = (f: number, at: number, len = 9) => interpolate(f, [at, at + len], [0, 1], { ...clamp, easing: OUT });
const short = (t: string) => (t === "Natus Vincere" ? "NAVI" : t === "Ninjas in Pyjamas" ? "NIP" : t);

const Title: React.FC<{ children: React.ReactNode; size?: number; color?: string; at?: number; style?: React.CSSProperties }> = ({ children, size = 60, color = C.white, at = 0, style }) => {
  const f = useCurrentFrame(); const p = pIn(f, at);
  return <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: size, color, letterSpacing: 3, lineHeight: 1.05, opacity: p, translate: `0px ${30 * (1 - p)}px`, ...style }}>{children}</div>;
};
const Chip: React.FC<{ name: string; kind: "in" | "out" | "sub"; at: number; size?: number }> = ({ name, kind, at, size = 34 }) => {
  const f = useCurrentFrame(); const p = pIn(f, at, 7);
  const col = kind === "in" ? GREEN : kind === "out" ? RED : YELLOW;
  return (
    <span style={{ display: "inline-block", padding: `${size * 0.18}px ${size * 0.5}px`, borderRadius: 10, border: `3px solid ${col}`, color: col, fontFamily: FONT, fontWeight: 700,
      fontSize: size, backgroundColor: `${col}1a`, opacity: p, scale: String(0.7 + 0.3 * p), marginRight: 10, textDecoration: kind === "out" ? `line-through ${RED} 3px` : "none" }}>
      {kind === "in" ? "+" : kind === "out" ? "−" : ""}{name}
    </span>
  );
};
const Bar: React.FC<{ label: string; v: number; at: number; col: string; width?: number }> = ({ label, v, at, col, width = 620 }) => {
  const f = useCurrentFrame(); const w = interpolate(f, [at, at + 16], [0, v], { ...clamp, easing: OUT });
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 18, opacity: pIn(f, at - 4) }}>
      <div style={{ width: 160, fontFamily: FONT, fontWeight: 700, fontSize: 30, color: C.muted, letterSpacing: 3 }}>{label}</div>
      <div style={{ width, height: 46, borderRadius: 8, backgroundColor: C.panel, overflow: "hidden" }}>
        <div style={{ width: `${w * 100}%`, height: "100%", backgroundColor: col, boxShadow: `0 0 20px ${col}77` }} />
      </div>
      <div style={{ width: 120, fontFamily: FONT, fontWeight: 700, fontSize: 52, color: col }}>{Math.round(w * 100)}%</div>
    </div>
  );
};
const Verdict: React.FC<{ v: number; at: number; size?: number }> = ({ v, at, size = 120 }) => {
  const f = useCurrentFrame(); const p = pIn(f, at, 6);
  const col = v >= 0 ? GREEN : RED;
  return <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: size, color: col, lineHeight: 1, opacity: p, scale: String(1.5 - 0.5 * p), textShadow: `0 0 40px ${col}88` }}>{v >= 0 ? "+" : "−"}{Math.round(Math.abs(v))}</div>;
};
const Stamp: React.FC<{ text: string; at: number; color?: string; size?: number; style?: React.CSSProperties }> = ({ text, at, color = RED, size = 56, style }) => {
  const f = useCurrentFrame(); const s = interpolate(f, [at, at + 6], [2.2, 1], clamp);
  return <div style={{ padding: "8px 26px", border: `6px solid ${color}`, borderRadius: 12, color, fontFamily: FONT, fontWeight: 700, fontSize: size, letterSpacing: 4, rotate: "-6deg",
    scale: String(s), opacity: f >= at ? 1 : 0, backgroundColor: "rgba(14,17,23,0.88)", boxShadow: `0 0 30px ${color}66`, whiteSpace: "nowrap", ...style }}>{text}</div>;
};

// a full move card: logo, in/out chips, Cologne -> now bars, verdict, Valve rank
const MoveCard: React.FC<{ c: Card; at: number; vAt: number }> = ({ c, at, vAt }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ padding: "120px 150px", flexDirection: "row", gap: 70, opacity: pIn(f, at) }}>
      <div style={{ width: 420, display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
        <div style={{ position: "relative", width: 360, height: 360, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Halo color={teamColor(c.team)} size={560} strength={1.3} /><Logo team={c.team} size={330} />
        </div>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 64 }}>{short(c.team)}</div>
        {c.rank_jun && c.rank_nov ? <Title size={32} color={C.muted} at={at + 6} style={{ whiteSpace: "nowrap" }}>VALVE RANK #{c.rank_jun} → <span style={{ color: c.rank_nov < c.rank_jun ? GREEN : RED }}>#{c.rank_nov}</span></Title> : null}
      </div>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 34, justifyContent: "center" }}>
        <div>{c.in.map((p, i) => <Chip key={p} name={p} kind="in" at={at + 4 + i * 4} />)}{c.out.map((p, i) => <Chip key={p} name={p} kind="out" at={at + 8 + c.in.length * 4 + i * 4} />)}
          {!c.moved ? <Chip name="NO CHANGE" kind="sub" at={at + 4} /> : null}</div>
        <Bar label="COLOGNE" v={c.win_A} at={at + 12} col={C.muted} />
        <Bar label="NOW" v={c.win_B} at={at + 22} col={c.win_B >= c.win_A ? GREEN : RED} />
        <div style={{ fontFamily: FONT, fontSize: 26, color: C.dim, letterSpacing: 2 }}>CHANCE TO BEAT AN AVERAGE SINGAPORE TEAM ON A MAP</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 24 }}>
          <Verdict v={c.verdict_pts} at={vAt} /><Title size={36} color={C.muted} at={vAt + 4}>VS EXPECTED</Title>
        </div>
      </div>
      <Sfx at={at} sound="swoosh" volume={0.3} />
      {[...c.in, ...c.out].map((p, i) => <Sfx key={p} at={at + 4 + i * 4} sound="click" n={i} volume={0.45} lead={0} />)}
      <Sfx at={vAt} sound={c.verdict_pts >= 0 ? "impact2" : "impact3"} volume={0.55} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------------------------------------ sections
const Hook: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const nobody = cue("h3", "nobody") - s;
  const dim = interpolate(f, [nobody - 4, nobody + 8], [1, 0.12], clamp);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 160, right: 160, top: 120, display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 30, opacity: dim }}>
        {D.hook_teams.map(({ team: t, n_in }, i) => {
          const p = pIn(f, 6 + i * 3, 8);
          return (
            <div key={t} style={{ height: 230, borderRadius: 18, backgroundColor: C.panel, border: `2px solid ${teamColor(t)}66`, display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", gap: 10, opacity: p, scale: String(0.6 + 0.4 * p) }}>
              <Logo team={t} size={130} />
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: GREEN }}>+{n_in} NEW</div>
            </div>
          );
        })}
      </div>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: pIn(f, nobody, 8) }}>
        <div style={{ position: "relative", width: 520, height: 520, display: "flex", alignItems: "center", justifyContent: "center", filter: "grayscale(0.6)" }}>
          <Halo color={teamColor("Spirit")} size={800} strength={1.2} /><Logo team="Spirit" size={460} />
        </div>
        <Stamp text="NO CHANGE" at={nobody + 4} size={80} style={{ position: "absolute", top: 640 }} />
      </AbsoluteFill>
      {D.hook_teams.filter((_, i) => i % 3 === 0).map((t, i) => <Sfx key={t.team} at={6 + i * 9} sound="click" n={i} volume={0.35} lead={0} />)}
      <Sfx at={nobody + 4} sound="stamp" volume={0.7} />
      <Sfx at={nobody + 4} sound="impact2" volume={0.5} />
    </AbsoluteFill>
  );
};

const Method: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const c = D.method_example;
  const aCol = cue("m1", "Cologne") - s, aNow = cue("m1", "now") - s, m3 = B.m3.from - s, dont = cue("m3", "count") - s, m4 = B.m4.from - s;
  const slide = cue("m4", "slide") - s, climb = cue("m4", "climb") - s, compared = cue("m4", "compared") - s;
  return (
    <AbsoluteFill style={{ padding: "110px 160px", gap: 40 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 30, opacity: pIn(f, 0) }}><Logo team={c.team} size={120} /><Title size={64}>{c.team}</Title></div>
      <Bar label="COLOGNE" v={c.win_A} at={aCol} col={C.muted} width={900} />
      <Bar label="NOW" v={c.win_B} at={aNow} col={GREEN} width={900} />
      <Title size={34} color={YELLOW} at={B.m2.from - s + 10}>= CHANCE TO BEAT AN AVERAGE SINGAPORE MAJOR TEAM ON A MAP · OPPONENTS COUNT</Title>
      <div style={{ display: "flex", gap: 60, marginTop: 30, alignItems: "center", opacity: pIn(f, m3) * (f < m4 ? 1 : 0.25) }}>
        <Chip name="jL · STAND-IN" kind="sub" at={m3} size={44} />
        <Stamp text="DOESN'T COUNT" at={dont} size={50} />
      </div>
      <div style={{ display: "flex", gap: 80, marginTop: 10 }}>
        <Title size={46} color={RED} at={slide}>STRONG TEAMS ↘ SLIDE BACK</Title>
        <Title size={46} color={GREEN} at={climb}>WEAK TEAMS ↗ CLIMB</Title>
      </div>
      <Title size={40} color={C.muted} at={compared}>EVERY TEAM IS JUDGED AGAINST THAT EXPECTED DRIFT</Title>
      <Sfx at={aCol} sound="tap" volume={0.5} /><Sfx at={aNow} sound="tap" volume={0.5} n={1} />
      <Sfx at={dont} sound="stamp" volume={0.55} /><Sfx at={slide} sound="slide1" volume={0.3} /><Sfx at={climb} sound="slide2" volume={0.3} />
    </AbsoluteFill>
  );
};

const Answer: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame(); const A = D.answer;
  const yes = cue("a2", "Yes") - s, a3 = B.a3.from - s, kept = cue("a3", "eight") - s, seven = cue("a4", "seven") - s;
  const grid = (n: number, up: number, at: number, label: string) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20, opacity: pIn(f, at) }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 70px)", gap: 12 }}>
        {Array.from({ length: n }, (_, i) => <div key={i} style={{ width: 70, height: 70, borderRadius: 10, backgroundColor: i < up ? GREEN : C.panel, opacity: pIn(f, at + 6 + i * 2, 5),
          boxShadow: i < up ? `0 0 14px ${GREEN}66` : "none" }} />)}
      </div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 72, color: C.white }}>{up} / {n}</div>
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 32, color: C.muted, letterSpacing: 3 }}>{label}</div>
    </div>
  );
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 70 }}>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: 1 - pIn(f, yes - 6, 6) }}>
        <Title size={150} at={2}>DOES IT <span style={{ color: YELLOW }}>WORK?</span></Title>
      </AbsoluteFill>
      <Title size={110} at={yes} color={YELLOW}>YES. A LITTLE.</Title>
      <div style={{ display: "flex", gap: 180, marginTop: 50 }}>
        {grid(A.moved_n, A.moved_up, a3, "CHANGED PLAYERS · BETTER THAN EXPECTED")}
        {grid(A.kept_n, A.kept_up, kept, "KEPT THEIR FIVE · BETTER THAN EXPECTED")}
      </div>
      <div style={{ position: "absolute", top: 880, padding: "14px 40px", borderRadius: 14, backgroundColor: `${GREEN}22`, border: `4px solid ${GREEN}`, fontFamily: FONT, fontWeight: 700,
        fontSize: 54, color: GREEN, opacity: pIn(f, seven), scale: String(0.8 + 0.2 * pIn(f, seven)) }}>ROSTER MOVE ≈ +{Math.round(A.avg_pts)} POINTS ON AVERAGE</div>
      <Sfx at={yes} sound="hit" volume={0.5} /><Sfx at={a3 + 6} sound="tickAny" volume={0.25} lead={0} /><Sfx at={kept + 6} sound="tickAny" volume={0.25} lead={0} pitch={-2} />
      <Sfx at={seven} sound="impact2" volume={0.5} />
    </AbsoluteFill>
  );
};

const Best: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const [nem, mouz, her] = D.best;
  const b2 = B.b2.from - s, b3 = B.b3.from - s, b4 = B.b4.from - s, brol = cue("b3", "HEROIC") - s, twelve = cue("b3", "twelve") - s;
  const move = interpolate(f, [brol, brol + 24], [0, 1], { ...clamp, easing: OUT });
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={b2}><MoveCard c={nem} at={0} vAt={cue("b1", "seventeen") - s} /></Sequence>
      <Sequence from={b2} durationInFrames={b3 - b2}><MoveCard c={mouz} at={0} vAt={cue("b2", "sixteen") - s - b2} /></Sequence>
      <Sequence from={b3} durationInFrames={b4 - b3}>
        <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-around", padding: "0 160px" }}>
          {[mouz, her].map((c, i) => (
            <div key={c.team} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
              <div style={{ position: "relative", width: 340, height: 340, display: "flex", alignItems: "center", justifyContent: "center" }}><Halo color={teamColor(c.team)} size={520} /><Logo team={c.team} size={300} /></div>
              <Verdict v={c.verdict_pts} at={i === 0 ? 6 : twelve - b3} size={110} />
            </div>
          ))}
          <div style={{ position: "absolute", left: 470 + 760 * move, top: 250 + 60 * Math.sin(Math.PI * move) * -1 }}><Chip name="Brollan →" kind="sub" at={0} size={48} /></div>
          <div style={{ position: "absolute", top: 160, width: "100%", textAlign: "center", left: 0 }}><Title size={56} at={twelve - b3 + 10} color={YELLOW}>ONE TRADE, TWO WINNERS</Title></div>
        </AbsoluteFill>
        <Sfx at={brol - b3} sound="sweep" volume={0.3} /><Sfx at={twelve - b3} sound="impact2" volume={0.5} />
      </Sequence>
      <Sequence from={b4}>
        <AbsoluteFill style={{ flexDirection: "row", gap: 40, alignItems: "center", justifyContent: "center" }}>
          {D.best_more.map((c, i) => (
            <div key={c.team} style={{ width: 360, height: 520, borderRadius: 20, backgroundColor: C.panel, border: `3px solid ${teamColor(c.team)}66`, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", gap: 18, opacity: pIn(f - b4, 4 + i * 10) }}>
              <Logo team={c.team} size={170} />
              <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 40 }}>{short(c.team)}</div>
              <div style={{ textAlign: "center" }}>{c.in.map((p) => <div key={p} style={{ fontFamily: FONT, fontWeight: 700, fontSize: 28, color: GREEN }}>+{p}</div>)}</div>
              <Verdict v={c.verdict_pts} at={8 + i * 10} size={90} />
            </div>
          ))}
        </AbsoluteFill>
        {D.best_more.map((c, i) => <Sfx key={c.team} at={8 + i * 10} sound="click" n={i} volume={0.5} lead={0} />)}
      </Sequence>
    </AbsoluteFill>
  );
};

const MONTHS = ["2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01", "2026-10-01", "2026-11-01", "2026-11-30"];
const xOf = (d: string) => { const t = (Date.parse(d) - Date.parse(MONTHS[0])) / (Date.parse(MONTHS[7]) - Date.parse(MONTHS[0])); return 160 + t * 1600; };
const JL: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const s2 = B.s2.from - s, hops = [cue("s2", "MOUZ") - s, cue("s2", "twice") - s, cue("s2", "Vitality") - s + 6], s3 = B.s3.from - s;
  const k = hops.filter((h) => f >= h).length - 1;
  const at = k >= 0 ? D.jl[Math.min(k, D.jl.length - 1)] : null;
  return (
    <AbsoluteFill>
      <Title size={120} at={s2} color={YELLOW} style={{ position: "absolute", top: 70, width: "100%", textAlign: "center" }}>jL</Title>
      <Title size={40} color={C.muted} at={s2 + 6} style={{ position: "absolute", top: 205, width: "100%", textAlign: "center" }}>THE SUPER-SUB · STAND-IN, NEVER SIGNED</Title>
      <div style={{ position: "absolute", left: 160, width: 1600, top: 640, height: 4, backgroundColor: C.line }} />
      {MONTHS.slice(0, 7).map((m) => <div key={m} style={{ position: "absolute", left: xOf(m) - 40, top: 660, width: 80, textAlign: "center", fontFamily: FONT, fontSize: 28, color: C.muted }}>
        {new Date(m).toLocaleString("en-US", { month: "short", timeZone: "UTC" }).toUpperCase()}</div>)}
      {D.jl.map((r, i) => {
        const p = pIn(f, hops[Math.min(i, 2)], 10);
        return (
          <div key={i} style={{ position: "absolute", left: xOf(r.from) - 40, width: Math.max(190, xOf(r.to) - xOf(r.from) + 20), top: 380, height: 240, borderRadius: 16, backgroundColor: `${teamColor(r.team)}33`,
            border: `3px solid ${teamColor(r.team)}`, display: "flex", alignItems: "center", justifyContent: "center", opacity: p }}>
            <Logo team={r.team} size={160} />
          </div>
        );
      })}
      {at ? <div style={{ position: "absolute", left: xOf(at.from) - 20, top: 300 }}><Chip name="jL" kind="sub" at={hops[0]} size={56} /></div> : null}
      <Title size={58} at={s3} style={{ position: "absolute", top: 800, width: "100%", textAlign: "center" }}>2 OF THE WORLD'S TOP 3 · <span style={{ color: YELLOW }}>1 STAND-IN</span></Title>
      {hops.map((h, i) => <Sfx key={i} at={h} sound={i === 0 ? "pop" : "click"} n={i} volume={0.5} lead={0} />)}
      <Sfx at={s2} sound="hit" volume={0.45} />
    </AbsoluteFill>
  );
};

const Worst: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const [pain, g2] = D.worst;
  const w2 = B.w2.from - s, w3 = B.w3.from - s, w4 = B.w4.from - s, w5 = B.w5.from - s, w6 = B.w6.from - s;
  const sp = D.spirit; const months = ["2026_06_01", "2026_07_06", "2026_08_03", "2026_09_07", "2026_10_05", "2026_11_02"];
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={w2}>
        <MoveCard c={pain} at={0} vAt={cue("w1", "fourteen") - s} />
        <div style={{ position: "absolute", left: 150, top: 90 }}><Stamp text="NOT IN SINGAPORE" at={cue("w1", "Singapore") - s} size={40} /></div>
      </Sequence>
      <Sequence from={w2} durationInFrames={w3 - w2}><MoveCard c={g2} at={0} vAt={cue("w2", "seven") - s - w2} /></Sequence>
      <Sequence from={w3} durationInFrames={w5 - w3}>
        <AbsoluteFill style={{ flexDirection: "row", gap: 80, alignItems: "center", justifyContent: "center" }}>
          {D.still.map((c, i) => (
            <div key={c.team} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18, opacity: pIn(f - w3, [cue("w3", "9z"), cue("w3", "B8"), cue("w3", "Spirit")][i] - s - w3) }}>
              <div style={{ position: "relative", width: 300, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}><Halo color={teamColor(c.team)} size={460} /><Logo team={c.team} size={260} /></div>
              <Verdict v={c.verdict_pts} at={10 + i * 6} size={96} />
              <Stamp text="NO CHANGE" at={w4 - w3 + i * 5} size={42} />
            </div>
          ))}
        </AbsoluteFill>
        {D.still.map((_, i) => <Sfx key={i} at={w4 - w3 + i * 5} sound="stamp" volume={0.55} />)}
      </Sequence>
      <Sequence from={w5} durationInFrames={w6 - w5}>
        <AbsoluteFill style={{ padding: "110px 160px", flexDirection: "row", gap: 80, alignItems: "center" }}>
          <div style={{ position: "relative", width: 420, height: 420, display: "flex", alignItems: "center", justifyContent: "center" }}><Halo color={teamColor("Spirit")} size={640} /><Logo team="Spirit" size={380} /></div>
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 36 }}>
            <div style={{ display: "flex", gap: 18 }}>
              {months.map((m, i) => { const r = sp.valve_ranks[m]; return (
                <div key={m} style={{ width: 150, height: 150, borderRadius: 16, backgroundColor: r === 1 ? `${YELLOW}26` : C.panel, border: `3px solid ${r === 1 ? YELLOW : C.line}`, display: "flex",
                  flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: pIn(f - w5, 4 + i * 5) }}>
                  <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 60, color: r === 1 ? YELLOW : C.white }}>#{r}</div>
                  <div style={{ fontFamily: FONT, fontSize: 24, color: C.muted }}>{new Date(m.replace(/_/g, "-")).toLocaleString("en-US", { month: "short", timeZone: "UTC" }).toUpperCase()}</div>
                </div>); })}
            </div>
            <Bar label="COLOGNE" v={sp.win_A} at={cue("w5", "eighty") - s - w5} col={C.muted} />
            <Bar label="NOW" v={sp.win_B} at={cue("w5", "sixty") - s - w5} col={RED} />
          </div>
        </AbsoluteFill>
        <Sfx at={cue("w5", "sixty") - s - w5} sound="impact3" volume={0.55} />
      </Sequence>
      <Sequence from={w6}>
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <Title size={120} at={0}>STANDING STILL</Title>
          <Title size={120} at={8} color={RED}>WAS THE WORST MOVE</Title>
          <Title size={60} at={14} color={C.muted}>OF THE SEASON</Title>
        </AbsoluteFill>
        <Sfx at={8} sound="energetic" volume={0.5} />
      </Sequence>
    </AbsoluteFill>
  );
};

const Early: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 150 }}>
      <Title size={90} color={YELLOW}>TOO EARLY TO JUDGE</Title>
      <div style={{ display: "flex", gap: 50, marginTop: 90 }}>
        {D.too_early.map((t, i) => (
          <div key={t} style={{ width: 280, height: 320, borderRadius: 20, backgroundColor: C.panel, border: `3px dashed ${YELLOW}88`, display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", gap: 20, opacity: pIn(f, 30 + i * 18) }}>
            <Logo team={t} size={170} /><div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34 }}>{short(t)}</div>
          </div>
        ))}
      </div>
      <Title size={48} at={200} color={C.muted} style={{ marginTop: 70 }}>SINGAPORE IS THEIR FIRST REAL TEST</Title>
      {D.too_early.map((t, i) => <Sfx key={t} at={30 + i * 18} sound="click" n={i} volume={0.45} lead={0} />)}
    </AbsoluteFill>
  );
};

const Close: React.FC<{ s: number }> = ({ s }) => {
  const f = useCurrentFrame();
  const z2 = B.z2.from - s;
  const movers = D.best.concat(D.best_more).map((c) => c.team).slice(0, 5); const still = D.still.map((c) => c.team);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
      <div style={{ display: "flex", gap: 160, opacity: f < z2 ? 1 : 0.15 }}>
        {[["MOVED", movers, GREEN], ["DIDN'T", still, RED]].map(([label, list, col], i) => (
          <div key={label as string} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 30, opacity: pIn(f, i * 30) }}>
            <Title size={80} color={col as string}>{label as string}</Title>
            <div style={{ display: "flex", gap: 20 }}>{(list as string[]).map((t) => <Logo key={t} team={t} size={110} />)}</div>
          </div>
        ))}
      </div>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: pIn(f, z2) }}>
        <Title size={44} color={C.muted} at={z2}>NEXT</Title>
        <Title size={110} at={z2 + 4}>THE MAJOR, <span style={{ color: YELLOW }}>SIMULATED</span></Title>
        <div style={{ marginTop: 50, padding: "20px 70px", borderRadius: 16, backgroundColor: RED, fontFamily: FONT, fontWeight: 700, fontSize: 60, letterSpacing: 5, opacity: pIn(f, cue("z2", "Subscribe") - s) }}>SUBSCRIBE</div>
      </AbsoluteFill>
      <Sfx at={z2} sound="bigWhoosh" volume={0.4} /><Sfx at={cue("z2", "Subscribe") - s} sound="toggle" volume={0.6} />
    </AbsoluteFill>
  );
};

// End screen (last 20 s): clean frames where the owner places YouTube end-screen elements — two video suggestions
// (16:9, left and right) and the subscribe button (circle, bottom centre). Nothing else moves inside those areas.
export const END_BOXES = { left: { x: 150, y: 300, w: 760, h: 428 }, right: { x: 1010, y: 300, w: 760, h: 428 }, sub: { cx: 960, cy: 880, r: 95 } };
const EndScreen: React.FC = () => {
  const f = useCurrentFrame();
  const box = (b: { x: number; y: number; w: number; h: number }, label: string, i: number) => (
    <div style={{ position: "absolute", left: b.x, top: b.y, width: b.w, height: b.h, borderRadius: 18, border: `3px solid ${YELLOW}55`, backgroundColor: "rgba(255,255,255,0.03)",
      boxShadow: `0 0 40px ${YELLOW}22`, opacity: pIn(f, 8 + i * 6, 12), display: "flex", alignItems: "flex-end", justifyContent: "center", paddingBottom: 14 }}>
      <span style={{ fontFamily: FONT, fontSize: 24, letterSpacing: 4, color: C.dim }}>{label}</span>
    </div>
  );
  return (
    <AbsoluteFill>
      <Title size={84} at={0} style={{ position: "absolute", top: 110, width: "100%", textAlign: "center" }}>WATCH <span style={{ color: YELLOW }}>NEXT</span></Title>
      {box(END_BOXES.left, "", 0)}{box(END_BOXES.right, "", 1)}
      <div style={{ position: "absolute", left: END_BOXES.sub.cx - END_BOXES.sub.r, top: END_BOXES.sub.cy - END_BOXES.sub.r, width: 2 * END_BOXES.sub.r, height: 2 * END_BOXES.sub.r,
        borderRadius: "50%", border: `3px solid ${RED}88`, boxShadow: `0 0 40px ${RED}33`, opacity: pIn(f, 20, 12) }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1010, textAlign: "center", fontFamily: FONT, fontSize: 30, letterSpacing: 6, color: C.muted, opacity: pIn(f, 26) }}>SPORTSONTHELINE · CS2, BY THE NUMBERS</div>
      <Sfx at={2} sound="whooshBig" volume={0.3} />
    </AbsoluteFill>
  );
};

const SECTION_VIEW: Record<string, (s: number) => React.ReactNode> = {
  hook: (s) => <Hook s={s} />, method: (s) => <Method s={s} />, answer: (s) => <Answer s={s} />, best: (s) => <Best s={s} />,
  jl: (s) => <JL s={s} />, worst: (s) => <Worst s={s} />, early: () => <Early />, close: (s) => <Close s={s} />, end: () => <EndScreen />,
};

// camera — several "cameras" on the same scene: a new angle on every sentence (quick glide = the angle change),
// a slow dolly inside each shot, punch-ins on the key numbers, and a still hold on the end screen.
const V = (z: number, x: number, y: number, ry: number, rx: number): Shot => ({ z, x, y, ry, rx, ay: 540 });
const ANG = {
  wide: V(1.0, 0, 0, 0, 0), push: V(1.065, 0, 0, 0, 0.6), left: V(1.05, 28, 0, 4, 0.8), right: V(1.05, -28, 0, -4, 0.8),
  high: V(1.05, 0, 22, 0, 2.4), low: V(1.05, 0, -18, 0, -1.8),
};
const ORDER: Shot[] = [ANG.push, ANG.left, ANG.high, ANG.right, ANG.low, ANG.wide, ANG.right, ANG.push, ANG.left, ANG.low, ANG.high, ANG.wide];
const tighter = (a: Shot): Shot => ({ ...a, z: a.z + 0.025, x: a.x * 0.6, ry: a.ry * 0.7 });
const CAM_CHANGES: number[] = [];                       // frames where the angle changes (for the whooshes)
const CAM: CamKey[] = (() => {
  const keys: CamKey[] = [{ f: 0, glide: 1, shot: V(1.06, 0, 0, 0, 0) }];
  D.blocks.forEach((b, i) => {
    const shot = ORDER[i % ORDER.length];
    keys.push({ f: Math.max(0, b.from - 4), glide: 14, shot });
    keys.push({ f: b.from + 10, glide: Math.max(30, b.dur), shot: tighter(shot) });
    if (i > 0) CAM_CHANGES.push(b.from - 4);
  });
  for (const [blk, w] of [["b1", "seventeen"], ["b2", "sixteen"], ["b3", "twelve"], ["a4", "seven"], ["w1", "fourteen"], ["w2", "seven"], ["w5", "sixty"], ["w6", "Standing"]] as const) {
    const at = cue(blk, w);
    keys.push({ f: at, glide: 5, shot: V(1.1, 0, 0, 0, 0) }); keys.push({ f: at + 5, glide: 24, shot: V(1.04, 0, 0, 1.5, 0.5) });
  }
  keys.push({ f: D.end_from, glide: 20, shot: V(1.0, 0, 0, 0, 0) });
  keys.push({ f: D.end_from + 20, glide: 1, shot: V(1.0, 0, 0, 0, 0) });
  return keys.sort((x, y) => x.f - y.f);
})();
const SECTION_STARTS = new Set(SPAN.map((sp) => sp.from));

// background lives OUTSIDE the camera: it drifts slowly on its own, so the content moves against it (depth)
const Background: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${50 + 8 * Math.sin(f / 90)}% 30%, #262b38 0%, ${C.bg} 65%)` }}>
      <AbsoluteFill style={{ background: `linear-gradient(90deg, ${CT}18 0%, transparent 20%, transparent 80%, #ec963c18 100%)` }} />
      <AbsoluteFill style={{ opacity: 0.18, backgroundImage: "radial-gradient(rgba(255,255,255,0.35) 1px, transparent 1.5px)", backgroundSize: "48px 48px",
        backgroundPosition: `${(f * 0.35) % 48}px ${(f * 0.2) % 48}px` }} />
    </AbsoluteFill>
  );
};
const TRANS = ["whooshMed", "slide1", "whooshCard", "sweep", "slide2", "whooshBig", "whooshLong"] as const;
const Section: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame(); const p = interpolate(f, [0, 8], [0, 1], { ...clamp, easing: OUT });
  return <AbsoluteFill style={{ opacity: p, scale: String(1.04 - 0.04 * p) }}>{children}</AbsoluteFill>;
};

export const Video07: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg, fontFamily: FONT, color: C.white }}>
    <Background />
    <SfxSeed offset={0}>
      <CameraRig keys={CAM} background="transparent">
        {SPAN.map((sp, i) => (
          <Sequence key={sp.name} from={sp.from} durationInFrames={sp.to - sp.from}>
            <SfxSeed offset={sp.from}>
              <Section>{SECTION_VIEW[sp.name](sp.from)}</Section>
              {i > 0 ? <Sfx at={0} sound={TRANS[i % TRANS.length]} volume={0.32} lead={4} /> : null}
            </SfxSeed>
          </Sequence>
        ))}
      </CameraRig>
      {/* a whoosh on every angle change (not on section starts, which have their own transition sound) */}
      {CAM_CHANGES.filter((fr) => ![...SECTION_STARTS].some((s0) => Math.abs(s0 - fr) < 12)).map((fr, i) => (
        <Sfx key={`cw${fr}`} at={fr} sound="camWhoosh" n={i} volume={0.2} lead={2} />
      ))}
      {/* risers that land on the big reveals, and a swell into the end screen */}
      <Sfx at={cue("a2", "Yes")} sound="riserLong" volume={0.22} lead={110} />
      <Sfx at={cue("b1", "Nemiga")} sound="riser" volume={0.25} lead={56} />
      <Sfx at={cue("w1", "paiN")} sound="riserLong" volume={0.22} lead={100} pitch={-2} />
      <Sfx at={B.w6.from} sound="riser" volume={0.25} lead={56} pitch={-1} />
      <Sfx at={D.end_from} sound="swell" volume={0.3} lead={70} />
      {D.blocks.map((b) => (
        <Sequence key={b.id} from={b.from} layout="none">
          <Audio src={staticFile(b.file)} volume={1} />
        </Sequence>
      ))}
    </SfxSeed>
  </AbsoluteFill>
);
