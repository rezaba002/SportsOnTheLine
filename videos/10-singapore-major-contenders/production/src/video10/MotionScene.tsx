import React from "react";
import { AbsoluteFill, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import timeline from "../../public/video10/timeline.json";
import { FONT } from "../theme";
import { Logo } from "../cards/parts";

export type Scene = typeof timeline.scenes[number];
const WHITE = "#f2f5f7", MUTED = "#94a4b4", GOLD = "#ffd34d", CYAN = "#56d7e1";
const COLOR: Record<string, string> = { MOUZ: "#ff5e64", Vitality: GOLD, FURIA: "#a2e4a8", Spirit: CYAN, Falcons: "#4cd4a0" };
const clamp = (x: number) => Math.max(0, Math.min(1, x));
const ease = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
export const pct = (n: number) => {
  const x = n * 1000, whole = Math.floor(x), frac = x - whole;
  return `${((Math.abs(frac - .5) < 1e-7 ? whole + whole % 2 : Math.round(x)) / 10).toFixed(1)}%`;
};

const Backdrop: React.FC<{ color: string }> = ({ color }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: "#080e15", overflow: "hidden" }}>
    <div style={{ position: "absolute", width: 1500, height: 1500, left: 400, top: -500, transform: `translateX(${Math.sin(f / 100) * 70}px)`, willChange: "transform", background: `radial-gradient(circle,${color}20,transparent 62%)` }} />
    <div style={{ position: "absolute", width: 1400, height: 2, background: `linear-gradient(90deg,transparent,${color}70,transparent)`, left: 600, top: 650, transform: `rotate(${-28 + f / 900}deg)` }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse,transparent 30%,#02070cc0)" }} />
  </AbsoluteFill>;
};

// Every object has an entrance, a readable hold, and an exit. No persistent frame furniture.
const Beat: React.FC<{ f: number; start?: number; end: number; x?: number; y?: number; width?: number; from?: number; scale?: number; children: React.ReactNode }> = ({ f, start = 0, end, x = 960, y = 540, width = 1600, from = 100, scale = 1, children }) => {
  if (f < start || f > end) return null;
  const enter = ease((f - start) / 20), leave = ease((f - end + 15) / 15);
  return <div style={{ position: "absolute", left: x, top: y, width, textAlign: "center", opacity: enter * (1 - leave),
    transform: `translate(-50%,-50%) translateX(${(1 - enter) * from - leave * 100}px) scale(${(.78 + enter * .22 + leave * .1) * scale})`, filter: enter < 1 ? `blur(${(1 - enter) * 3}px)` : undefined }}>{children}</div>;
};
const Label: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = MUTED }) => <div style={{ fontSize: 32, letterSpacing: 3, color, marginTop: 20, lineHeight: 1.3 }}>{children}</div>;
const NumberHero: React.FC<{ value: string; label: string; color?: string; size?: number }> = ({ value, label, color = WHITE, size = 260 }) => <><div style={{ fontSize: size, fontWeight: 700, lineHeight: .96, color, letterSpacing: -8 }}>{value}</div><Label>{label}</Label></>;

const Trio: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  {["MOUZ", "FURIA", "Vitality"].map((team, i) => <Beat key={team} f={f} start={i * n * .24} end={(i + 1) * n * .24 + 2} from={i % 2 ? -180 : 180}>
    <div style={{ display: "flex", justifyContent: "center" }}><Logo team={team} size={420} /></div><Label color={COLOR[team]}>{["FORM", "MOMENTUM", "EXPERIENCE"][i]}</Label>
  </Beat>)}
  <Beat f={f} start={n * .73} end={n}>
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 200 }}>{["MOUZ", "Vitality", "FURIA"].map((team) => <Logo key={team} team={team} size={245} />)}</div>
    <div style={{ marginTop: 70, fontSize: 80, fontWeight: 700 }}>ONE TROPHY.</div>
  </Beat>
</>;

const Method: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  <Beat f={f} end={n * .32}><NumberHero value="2,619" label="MAPS • THROUGH 15 NOV" color={GOLD} /></Beat>
  <Beat f={f} start={n * .32} end={n * .65}><NumberHero value="21 DAYS" label="RECENCY HALF-LIFE" color={CYAN} size={205} /></Beat>
  <Beat f={f} start={n * .65} end={n}><NumberHero value="14%" label="WEIGHT OF A 60-DAY-OLD MAP" color={CYAN} /><div style={{ margin: "45px auto 0", width: 1000, height: 18, background: "#283743" }}><div style={{ height: "100%", width: "13.8%", background: CYAN }} /></div></Beat>
</>;

const Field: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  {[{ team: "Falcons", face: "m0NESY", label: "DEFENDING CHAMPIONS" }, { team: "Spirit", face: "donk", label: "2–0 vs MOUZ • HONG KONG" }].map((r, i) => <Beat key={r.team} f={f} start={i * n / 2} end={(i + 1) * n / 2}>
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 110 }}><Img src={staticFile(`video09-v4/players/${r.face}.webp`)} style={{ height: 760, objectFit: "contain", filter: `drop-shadow(0 0 60px ${COLOR[r.team]}30)` }} /><div><Logo team={r.team} size={280} /><Label color={COLOR[r.team]}>{r.label}</Label></div></div>
  </Beat>)}
</>;

const Result: React.FC<{ team: string; f: number; n: number }> = ({ team, f, n }) => {
  const mouz = team === "MOUZ", scores = mouz ? [["MIRAGE", "13–5"], ["DUST2", "13–6"], ["INFERNO", "13–4"]] : [["ANCIENT", "13–11"], ["DUST2", "13–5"], ["MIRAGE", "13–8"]];
  return <>
    <Beat f={f} end={n * .43}><div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 95 }}><Logo team={team} size={290} /><NumberHero value="3–0" label={mouz ? "BEIJING FINAL" : "HONG KONG FINAL"} color={COLOR[team]} /><Logo team={mouz ? "The MongolZ" : "Spirit"} size={235} /></div></Beat>
    {scores.map(([map, score], i) => <Beat key={map} f={f} start={n * (.43 + i * .19)} end={n * (.43 + (i + 1) * .19)} from={-160}><NumberHero value={score} label={map} color={COLOR[team]} /></Beat>)}
  </>;
};

const Probability: React.FC<{ team: "MOUZ" | "FURIA"; f: number; n: number }> = ({ team, f, n }) => {
  const value = timeline.baseline[team], t = ease((f - n * .48) / 35);
  return <>
    <Beat f={f} end={n} x={960 - t * 500} y={510 + t * 60} scale={1 - t * .44} width={1000}>
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 45 }}><Logo team={team} size={125} /></div><NumberHero value={pct(value.title)} label="TITLE • BASELINE" color={COLOR[team]} />
    </Beat>
    <Beat f={f} start={n * .5} end={n} x={1350} y={550} width={850} from={160}><NumberHero value={pct(value.title / value.advance_s3)} label="TITLE • IF PLAYOFFS" color={WHITE} size={210} /></Beat>
  </>;
};

const Maps: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  {[["MIRAGE", "10–2", "12 MAPS"], ["NUKE", "6–1", "7 MAPS"], ["CACHE", "2–2", "ONLY 4 MAPS"]].map(([map, record, sample], i) => <Beat key={map} f={f} start={i * n / 3} end={(i + 1) * n / 3} from={i % 2 ? 150 : -150}>
    <div style={{ fontSize: 75, color: COLOR.MOUZ, fontWeight: 700, marginBottom: 30 }}>{map}</div><NumberHero value={record} label={`${sample} • W–L`} /><Label>16 OCT – 15 NOV • RAW RESULTS</Label>
  </Beat>)}
</>;

const Roster: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  <Beat f={f} end={n * .25}><NumberHero value="30" label="STAND-IN MAPS" color={GOLD} /></Beat>
  {[{ original: "mezii", event: "PORTO", maps: "14 MAPS" }, { original: "apEX", event: "BUCHAREST", maps: "16 MAPS" }].map((r, i) => <Beat key={r.event} f={f} start={n * (.25 + i * .23)} end={n * (.48 + i * .23)}>
    <div style={{ fontSize: 125, fontWeight: 700 }}><span style={{ opacity: .45 }}>{r.original}</span><span style={{ color: GOLD, margin: "0 60px" }}>→</span>jL</div><Label color={GOLD}>{r.event} • {r.maps}</Label>
  </Beat>)}
  <Beat f={f} start={n * .71} end={n}><div style={{ display: "flex", justifyContent: "center", gap: 60, alignItems: "center" }}>{["apEX", "ZywOo", "flameZ", "mezii", "ropz"].map((name, i) => <div key={name} style={{ fontSize: name === "apEX" ? 105 : 65, color: name === "apEX" ? GOLD : WHITE, transform: `translateY(${Math.sin(i * 1.7) * 35}px)` }}>{name}</div>)}</div><Label color={GOLD}>THE EXPECTED MAJOR FIVE</Label></Beat>
</>;

const Experience: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  {[{ a: "14", b: "1", label: "PLAYER MAJOR-TITLE CREDITS" }, { a: "1,083", b: "543", label: "AVG CAREER LAN MAPS • 4 NOV" }].map((r, i) => <Beat key={r.label} f={f} start={i * n / 2} end={(i + 1) * n / 2}>
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 170 }}><div><Logo team="Vitality" size={145} /><div style={{ fontSize: i ? 205 : 280, fontWeight: 700, color: GOLD }}>{r.a}</div></div><div style={{ color: MUTED, fontSize: 48 }}>vs</div><div><Logo team="MOUZ" size={145} /><div style={{ fontSize: i ? 205 : 280, fontWeight: 700, color: COLOR.MOUZ }}>{r.b}</div></div></div><Label>{r.label}</Label>
  </Beat>)}
</>;

const Scenario: React.FC<{ f: number; n: number }> = ({ f, n }) => {
  const phases = [timeline.baseline.Vitality.title, timeline.rosterVitality, timeline.moderate.Vitality.title];
  return <>{phases.map((value, i) => <Beat key={i} f={f} start={i * n / 3} end={(i + 1) * n / 3} from={180}>
    <div style={{ display: "flex", justifyContent: "center", marginBottom: 35 }}><Logo team="Vitality" size={135} /></div><NumberHero value={pct(value)} label={["TITLE • BASELINE", "TITLE • STAND-IN GAMES DISCOUNTED", "TITLE • EXPERIENCE SCENARIO"][i]} color={i === 2 ? "#e9a4ff" : GOLD} />
    {i === 2 && <div style={{ display: "inline-block", marginTop: 25, padding: "12px 25px", color: "#e9a4ff", border: "2px solid #e9a4ff", fontSize: 37, letterSpacing: 5 }}>ASSUMED EFFECT</div>}
  </Beat>)}</>;
};

const Condition: React.FC<{ team: string; f: number; n: number }> = ({ team, f, n }) => {
  const words = team === "MOUZ" ? ["KEEP THE FIVE INVOLVED", "FIND THE NEXT ANSWER", "REPEAT IT"] : team === "Vitality" ? ["THE FULL FIVE", "COORDINATE", "SHOW IT TODAY"] : ["SUSTAIN IT", "ADAPT", "FINISH THE SERIES"];
  return <>{words.map((word, i) => <Beat key={word} f={f} start={i * n / 3} end={(i + 1) * n / 3} from={i % 2 ? -200 : 200}><div style={{ display: "flex", justifyContent: "center", marginBottom: 55 }}><Logo team={team} size={200} /></div><div style={{ fontSize: 115, fontWeight: 700, color: COLOR[team] }}>{word}</div></Beat>)}</>;
};

const Farewell: React.FC<{ f: number; n: number }> = ({ f, n }) => <>
  <Beat f={f} end={n * .52}><div style={{ fontSize: 80, color: GOLD, marginBottom: 20 }}>FalleN</div><div style={{ fontSize: 150, fontWeight: 700 }}>THE PROFESSOR</div></Beat>
  <Beat f={f} start={n * .52} end={n}><NumberHero value="ONE LAST MAJOR" label="SCHEDULED FAREWELL • END 2026" color={GOLD} size={130} /></Beat>
</>;

const Comparison: React.FC<{ f: number; n: number }> = ({ f, n }) => {
  const assumed = f >= n * .5, change = ease((f - n * .5) / 25);
  return <>
    {["MOUZ", "FURIA", "Vitality"].map((team, i) => {
      const values = assumed ? timeline.moderate : timeline.baseline, isVit = team === "Vitality";
      return <Beat key={team} f={f} end={n * .88} x={420 + i * 540 - (isVit ? change * 200 : change * 110)} y={520 - (isVit ? change * 50 : 0)} width={650} scale={isVit ? 1 + change * .13 : 1 - change * .15}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 45 }}><Logo team={team} size={185} /></div><div style={{ fontSize: 145, fontWeight: 700, color: COLOR[team] }}>{pct(values[team as "MOUZ"].title)}</div>
      </Beat>;
    })}
    <Beat f={f} end={n * .5} y={825}><Label>TITLE • BASELINE</Label></Beat>
    <Beat f={f} start={n * .5} end={n * .88} y={825}><Label color="#e9a4ff">TITLE • ASSUMED EXPERIENCE SCENARIO</Label></Beat>
    <Beat f={f} start={n * .88} end={n}><div style={{ fontSize: 115, fontWeight: 700 }}>WHICH CASE HOLDS?</div></Beat>
  </>;
};

export const MotionScene: React.FC<{ scene: Scene; sample?: boolean }> = ({ scene, sample = false }) => {
  const f = useCurrentFrame(), n = sample ? 180 : scene.frames, color = COLOR[scene.chapter] ?? GOLD;
  // Sample timings show whole motion beats. Full edit retains original clip placements.
  const footage = sample ? undefined : scene.footage.find((clip) => clip.file && f >= clip.at && f < clip.at + clip.frames);
  let content: React.ReactNode;
  switch (scene.kind) {
    case "trio": content = <Trio f={f} n={n} />; break;
    case "method": content = <Method f={f} n={n} />; break;
    case "field": content = <Field f={f} n={n} />; break;
    case "result": content = <Result team={scene.chapter} f={f} n={n} />; break;
    case "probability": content = <Probability team={scene.chapter as "MOUZ" | "FURIA"} f={f} n={n} />; break;
    case "maps": content = <Maps f={f} n={n} />; break;
    case "roster": content = <Roster f={f} n={n} />; break;
    case "experience": content = <Experience f={f} n={n} />; break;
    case "scenario": content = <Scenario f={f} n={n} />; break;
    case "comparison": content = <Comparison f={f} n={n} />; break;
    case "farewell": content = <Farewell f={f} n={n} />; break;
    default: content = <Condition team={scene.chapter} f={f} n={n} />;
  }
  return <AbsoluteFill style={{ fontFamily: FONT, color: WHITE, overflow: "hidden" }}>
    <Backdrop color={color} />{content}
    {footage?.file && <AbsoluteFill style={{ background: "#080e15", opacity: Math.min(ease((f - footage.at) / 8), interpolate(f, [footage.at + footage.frames - 8, footage.at + footage.frames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })) }}>
      <Sequence from={footage.at} durationInFrames={footage.frames}><OffthreadVideo src={staticFile(footage.file)} muted style={{ width: "100%", height: "100%", objectFit: "contain" }} /></Sequence>
      <div style={{ position: "absolute", left: 55, bottom: 42, background: "#080e15b8", padding: "9px 16px", color: WHITE, fontSize: 28 }}>{footage.label}</div>
    </AbsoluteFill>}
  </AbsoluteFill>;
};
