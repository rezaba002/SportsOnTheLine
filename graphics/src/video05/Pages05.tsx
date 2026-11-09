import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";
import { teamColor } from "../teams";
import { cardStyle, Logo } from "../cards/parts";
import { CountUp, Halo } from "../cards/fx";
import { Sfx } from "../cards/Sfx";

// Full-screen pages of video 05 (cold open, how it works, outro). Elements enter on the narration word that names
// them: `cues` maps "block:word:index" -> frame (from work/timeline.py).

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const OUT = Easing.bezier(0.16, 1, 0.3, 1);
const GREEN = "#4cc878";
const RED = "#e44c4c";
const YELLOW = "#ffd34d";

export type Field = { region: string; teams: string[] }[];
type Props = { page: string; cues: Record<string, number>; field: Field };

const norm = (s: string) => s.replace(/[^\w']/g, "").toLowerCase();
export const cue = (cues: Record<string, number>, word: string, nth = 1, fallback = 0) => {
  const hits = Object.entries(cues).filter(([k]) => norm(k.split(":")[1].split(" ")[0]) === norm(word)).sort((a, b) => a[1] - b[1]);
  return hits[nth - 1]?.[1] ?? fallback;
};

const useIn = (at: number, len = 10) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [at, at + len], [0, 1], { ...clamp, easing: OUT });
};

const Big: React.FC<{ at: number; children: React.ReactNode; size?: number; color?: string; style?: React.CSSProperties }> = ({ at, children, size = 120, color = C.white, style }) => {
  const p = useIn(at);
  return (
    <div style={{ fontSize: size, fontWeight: 700, color, letterSpacing: 6, lineHeight: 1.05, opacity: p, translate: `0px ${30 * (1 - p)}px`, ...style }}>{children}</div>
  );
};

const LogoTile: React.FC<{ team: string; at: number; size: number }> = ({ team, at, size }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + 9], [0, 1], { ...clamp, easing: Easing.spring({ damping: 12 }) });
  return (
    <div style={{ ...cardStyle(teamColor(team), 0.4), position: "relative", width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center", opacity: Math.min(1, p * 1.4), scale: String(0.5 + 0.5 * p) }}>
      <Logo team={team} size={size * 0.72} />
    </div>
  );
};

const Teaser: React.FC<{ team: string; at: number; line1: string; line2: string; color: string }> = ({ team, at, line1, line2, color }) => {
  const p = useIn(at, 12);
  return (
    <div style={{ ...cardStyle(teamColor(team), 1.2), position: "relative", width: 420, height: 540, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 18,
      opacity: p, translate: `0px ${60 * (1 - p)}px` }}>
      <div style={{ position: "relative", width: 230, height: 230, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Halo color={teamColor(team)} size={340} />
        <Logo team={team} size={210} />
      </div>
      <div style={{ fontSize: 46, fontWeight: 700, color, letterSpacing: 2, textAlign: "center", lineHeight: 1.1 }}>{line1}</div>
      <div style={{ fontSize: 30, color: C.muted, textAlign: "center" }}>{line2}</div>
    </div>
  );
};

export const Page05: React.FC<Props> = ({ page, cues, field }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const all = field.flatMap((r) => r.teams);
  const base: React.CSSProperties = { backgroundColor: C.bg, fontFamily: FONT, color: C.white, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" };

  if (page === "teams32") {
    const stamp = cue(cues, "no", 1, 60);
    const sp = interpolate(frame, [stamp, stamp + 6], [2.4, 1], clamp);
    return (
      <AbsoluteFill style={base}>
        <Big at={0} size={150}>32 TEAMS</Big>
        <Big at={6} size={44} color={C.muted} style={{ marginTop: 10 }}>PGL MAJOR SINGAPORE · NOV 24 – DEC 13</Big>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(8, 150px)", gap: 18, marginTop: 50 }}>
          {all.map((t, i) => <LogoTile key={t} team={t} at={8 + i * 2} size={150} />)}
        </div>
        <div style={{ position: "absolute", bottom: 70, right: 110, padding: "10px 26px", border: `6px solid ${YELLOW}`, borderRadius: 12, color: YELLOW, fontWeight: 700, fontSize: 52, letterSpacing: 6,
          rotate: "-8deg", scale: String(sp), opacity: frame >= stamp ? 1 : 0, boxShadow: `0 0 30px ${YELLOW}66`, backgroundColor: "rgba(14,17,23,0.85)" }}>NO QUALIFIERS</div>
        <Sfx at={0} sound="hit" volume={0.5} />
        {all.filter((_, i) => i % 3 === 0).map((t, i) => <Sfx key={t} at={8 + i * 6} sound={i % 2 ? "pop2" : "pop1"} volume={0.35} lead={0} />)}
        <Sfx at={stamp + 6} sound="stamp" volume={0.7} />
        <Sfx at={stamp + 6} sound="impact3" volume={0.45} />
      </AbsoluteFill>
    );
  }
  if (page === "cutoff") {
    return (
      <AbsoluteFill style={base}>
        <Big at={cue(cues, "one", 1)} size={140}>ONE RANKING</Big>
        <Big at={cue(cues, "one", 2)} size={140} style={{ marginTop: 20 }}>ONE DATE</Big>
        <Big at={cue(cues, "november", 1)} size={200} color={YELLOW} style={{ marginTop: 30, textShadow: `0 0 40px ${YELLOW}55` }}>NOV 2</Big>
        <Sfx at={cue(cues, "one", 1)} sound="knock" volume={0.5} />
        <Sfx at={cue(cues, "one", 2)} sound="knock" volume={0.5} />
        <Sfx at={cue(cues, "november", 1)} sound="hit" volume={0.55} />
      </AbsoluteFill>
    );
  }
  if (page === "teasers") {
    return (
      <AbsoluteFill style={{ ...base, flexDirection: "row", gap: 36 }}>
        <Teaser team="100 Thieves" at={cue(cues, "one", 1)} line1="IN ON THE LAST DAY" line2="18th · Nov 1" color={GREEN} />
        <Teaser team="TYLOO" at={cue(cues, "one", 2)} line1="MISSED BY 2 POINTS" line2="1,266 vs 1,268" color={RED} />
        <Teaser team="B8" at={cue(cues, "one", 3)} line1="13TH → STAYING HOME" line2="Oct 6 → Nov 2" color={RED} />
        <Teaser team="BC.Game" at={cue(cues, "s1mple", 1)} line1="S1MPLE IS BACK" line2="missed the last two Majors" color={YELLOW} />
        {[cue(cues, "one", 1), cue(cues, "one", 2), cue(cues, "one", 3)].map((f, i) => (
          <React.Fragment key={i}>
            <Sfx at={f} sound="whooshCard" volume={0.35} />
            <Sfx at={f + 6} sound={i === 0 ? "win" : "lose"} volume={0.3} lead={0} />
          </React.Fragment>
        ))}
        <Sfx at={cue(cues, "s1mple", 1)} sound="whooshCard" volume={0.35} />
        {[cue(cues, "one", 1), cue(cues, "one", 2), cue(cues, "one", 3), cue(cues, "s1mple", 1)].map((f, i) => <Sfx key={`c${i}`} at={f + 10} sound="click" n={i} volume={0.5} lead={0} />)}
        <Sfx at={cue(cues, "s1mple", 1) + 6} sound="chime" volume={0.35} />
      </AbsoluteFill>
    );
  }
  if (page === "title") {
    return (
      <AbsoluteFill style={base}>
        <Big at={0} size={46} color={YELLOW}>PGL MAJOR SINGAPORE 2026</Big>
        <Big at={4} size={170} style={{ marginTop: 16 }}>THE ROAD TO</Big>
        <Big at={8} size={170}>SINGAPORE</Big>
        <Big at={cue(cues, "day", 1)} size={48} color={C.muted} style={{ marginTop: 30 }}>DAY BY DAY · REGION BY REGION</Big>
        <Sfx at={36} sound="energetic" volume={0.45} lead={36} />
      </AbsoluteFill>
    );
  }
  if (page === "ranking") {
    const bar = interpolate(frame, [12, 2.2 * fps], [0, 1], { ...clamp, easing: OUT });
    const flag = cue(cues, "november", 1, 90);
    return (
      <AbsoluteFill style={base}>
        <Big at={0} size={90}>VALVE REGIONAL STANDINGS</Big>
        <div style={{ position: "relative", width: 1400, height: 120, marginTop: 90 }}>
          <div style={{ position: "absolute", top: 40, left: 0, width: 1400 * bar, height: 40, borderRadius: 20, background: `linear-gradient(90deg, rgba(93,156,236,0.15), ${C.ct})` }} />
          <div style={{ position: "absolute", top: 96, left: 0, fontSize: 30, color: C.muted }}>May 2</div>
          <div style={{ position: "absolute", top: 96, right: 0, fontSize: 30, color: C.muted }}>Nov 2</div>
          <div style={{ position: "absolute", top: -16, left: 560, fontSize: 34, fontWeight: 700, color: C.white, opacity: bar }}>LAST 6 MONTHS OF RESULTS</div>
          <div style={{ position: "absolute", top: 10, right: -20, width: 6, height: 100, backgroundColor: YELLOW, opacity: frame >= flag ? 1 : 0 }} />
        </div>
        <Big at={flag} size={64} color={YELLOW} style={{ marginTop: 50 }}>NOV 2 → THE INVITES</Big>
        <Sfx at={flag} sound="toggle" volume={0.6} lead={0} />
      </AbsoluteFill>
    );
  }
  if (page === "spots") {
    const cols = [
      { name: "EUROPE", n: 18, at: cue(cues, "europe", 1), stages: [["STAGE 3", 6], ["STAGE 2", 6], ["STAGE 1", 6]] },
      { name: "AMERICAS", n: 9, at: cue(cues, "americas", 1), stages: [["STAGE 3", 2], ["STAGE 2", 1], ["STAGE 1", 6]] },
      { name: "ASIA", n: 5, at: cue(cues, "asia", 1), stages: [["STAGE 2", 1], ["STAGE 1", 4]] },
    ] as const;
    const stageAt = cue(cues, "and", 1, 160);
    return (
      <AbsoluteFill style={{ ...base, flexDirection: "row", gap: 70, alignItems: "flex-start", paddingTop: 200 }}>
        {cols.map((c, i) => <Sfx key={`s${i}`} at={c.at} sound={i % 2 ? "pop2" : "pop1"} volume={0.45} lead={0} />)}
        <Sfx at={stageAt} sound="up" volume={0.35} />
        {[0, 1, 2].map((i) => <Sfx key={`c${i}`} at={stageAt + i * 5} sound="click" n={i} volume={0.6} lead={0} />)}
        {cols.map((c) => {
          const p = interpolate(frame, [c.at, c.at + 10], [0, 1], { ...clamp, easing: OUT });
          return (
            <div key={c.name} style={{ ...cardStyle("#5d9cec", 0.6), position: "relative", width: 470, height: 600, opacity: p, translate: `0px ${50 * (1 - p)}px`, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 40 }}>
              <div style={{ fontSize: 40, fontWeight: 700, color: C.muted, letterSpacing: 6 }}>{c.name}</div>
              <div style={{ fontSize: 220, fontWeight: 700, color: C.white, lineHeight: 1 }}><CountUp value={c.n} delay={c.at} seconds={0.6} /></div>
              <div style={{ fontSize: 34, color: C.muted, letterSpacing: 4 }}>SPOTS</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 30, width: 360 }}>
                {c.stages.map(([s, k], i) => (
                  <div key={s} style={{ display: "flex", justifyContent: "space-between", fontSize: 34, fontWeight: 700, opacity: interpolate(frame, [stageAt + i * 5, stageAt + i * 5 + 8], [0, 1], clamp),
                    color: s === "STAGE 3" ? YELLOW : s === "STAGE 2" ? C.white : C.muted }}>
                    <span>{s}</span><span>{k}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    );
  }
  if (page === "daily") {
    return (
      <AbsoluteFill style={base}>
        <Big at={0} size={120}>EVERY DAY</Big>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(14, 90px)", gap: 12, marginTop: 60 }}>
          {Array.from({ length: 28 }, (_, i) => {
            const lit = interpolate(frame, [10 + i * 4, 16 + i * 4], [0, 1], clamp);
            const d = new Date(Date.UTC(2026, 9, 6 + i));
            return (
              <div key={i} style={{ height: 90, borderRadius: 10, backgroundColor: lit > 0.5 ? "rgba(93,156,236,0.9)" : C.panel, border: `1px solid ${C.line}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                fontSize: 22, fontWeight: 700, color: lit > 0.5 ? C.bg : C.dim, scale: String(1 + 0.08 * Math.sin(Math.PI * lit)) }}>
                <span>{["Oct", "Nov"][d.getUTCMonth() - 9]}</span><span style={{ fontSize: 30 }}>{d.getUTCDate()}</span>
              </div>
            );
          })}
        </div>
        <Big at={cue(cues, "hltv", 1, 20)} size={36} color={C.muted} style={{ marginTop: 50 }}>VALVE'S MODEL, RUN DAILY BY HLTV</Big>
        {Array.from({ length: 28 }, (_, i) => <Sfx key={i} at={13 + i * 4} sound={i % 2 ? "tickSoft" : "tick"} volume={0.18} lead={0} />)}
      </AbsoluteFill>
    );
  }
  if (page === "field") {
    return (
      <AbsoluteFill style={base}>
        <Big at={0} size={110}>THE FIELD</Big>
        <div style={{ display: "flex", flexDirection: "column", gap: 26, marginTop: 40 }}>
          {field.map((r, ri) => (
            <div key={r.region} style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 230, textAlign: "right", fontSize: 30, fontWeight: 700, color: C.muted, letterSpacing: 3 }}>{r.region.toUpperCase()}</div>
              {r.teams.map((t, i) => <LogoTile key={t} team={t} at={6 + ri * 8 + i * 2} size={r.teams.length > 9 ? 76 : 96} />)}
            </div>
          ))}
        </div>
        <Big at={cue(cues, "stage", 1, 90)} size={60} color={YELLOW} style={{ marginTop: 40 }}>STAGE 1 · NOV 24</Big>
        {field.map((r, ri) => <Sfx key={r.region} at={6 + ri * 8} sound="up" volume={0.3} />)}
        {field.flatMap((r, ri) => r.teams.filter((_, i) => i % 3 === 0).map((t, j) => <Sfx key={`c${t}`} at={6 + ri * 8 + j * 6} sound="click" n={ri * 7 + j} volume={0.45} lead={0} />))}
        <Sfx at={cue(cues, "stage", 1, 90)} sound="hit" volume={0.5} />
      </AbsoluteFill>
    );
  }
  // next
  const sub = cue(cues, "subscribe", 1, 150);
  const pulse = interpolate(frame, [sub, sub + 5, sub + 20], [0, 1, 0], clamp);
  return (
    <AbsoluteFill style={base}>
      <Big at={0} size={44} color={C.muted}>NEXT VIDEO</Big>
      <div style={{ fontSize: 230, fontWeight: 700, color: YELLOW, lineHeight: 1, fontVariantNumeric: "tabular-nums", textShadow: `0 0 50px ${YELLOW}44` }}>
        <CountUp value={100000} delay={cue(cues, "hundred", 1, 30)} seconds={1.6} format={(n) => Math.round(n).toLocaleString("en-US")} />
      </div>
      <Big at={cue(cues, "majors", 1, 40)} size={70}>MAJORS. ONE WINNER.</Big>
      <div style={{ marginTop: 60, padding: "22px 60px", borderRadius: 14, backgroundColor: RED, color: C.white, fontSize: 52, fontWeight: 700, letterSpacing: 4, opacity: frame >= sub ? 1 : 0,
        scale: String(1 + 0.12 * pulse), boxShadow: `0 0 ${20 + 40 * pulse}px ${RED}aa` }}>SUBSCRIBE</div>
      <Sfx at={cue(cues, "hundred", 1, 30)} sound="riser" volume={0.3} lead={0} />
      <Sfx at={cue(cues, "hundred", 1, 30) + 50} sound="hit" volume={0.5} />
      <Sfx at={sub} sound="bell" volume={0.45} />
    </AbsoluteFill>
  );
};
