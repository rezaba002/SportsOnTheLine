import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";
import { teamColor } from "../teams";
import { AccentBar, cardStyle, Delta, Logo, RankMove, SampleTag } from "./parts";
import { Appear, CountUp, Halo, Rise, usePulse } from "./fx";

// Card A: the match behind a move (approved 2026-11-01).
//  panel — normal moments: a column on the right, the race stays readable on the left
//  split — the biggest moments: a big centred card in the teams' colours
// Timeline inside the card's Sequence: in at `delay`, score counts up, winner flashes, impact rows rise, out at `exitAt`.

export type Side = { name: string; score: number; points: number; rankFrom: number; rankTo: number };
export type Match = {
  event: string;
  stage: string;
  date: string;
  spots: number;
  teams: [Side, Side];
  maps: { name: string; score: [number, number] }[];
  sample?: boolean;
};

const winnerIdx = (m: Match) => (m.teams[0].score > m.teams[1].score ? 0 : 1);

const Score: React.FC<{ value: number; win: boolean; delay: number }> = ({ value, win, delay }) => {
  const { fps } = useVideoConfig();
  const flash = usePulse(delay + 0.75 * fps, 0.7);
  return (
    <span
      style={{
        display: "inline-block",
        color: win ? C.yellow : C.dim,
        fontVariantNumeric: "tabular-nums",
        scale: win ? String(1 + 0.18 * flash) : "1",
        textShadow: win ? `0 0 ${10 + 40 * flash}px rgba(255, 211, 77, ${0.25 + 0.6 * flash})` : "none",
      }}
    >
      <CountUp value={value} delay={delay} seconds={0.6} />
    </span>
  );
};

export const MatchCard: React.FC<{ match: Match; variant: "panel" | "split"; delay?: number; exitAt?: number }> = ({
  match,
  variant,
  delay = 0,
  exitAt,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = winnerIdx(match);
  const [a, b] = match.teams;
  const ca = teamColor(a.name);
  const cb = teamColor(b.name);
  const scoreAt = delay + 0.35 * fps;
  const impactAt = delay + 1.3 * fps;

  if (variant === "panel") {
    return (
      <Appear delay={delay} exitAt={exitAt} from="right">
        <div style={{ ...cardStyle(teamColor(match.teams[w].name)), right: 70, top: 250, width: 610, padding: "34px 34px 30px" }}>
          <AccentBar colors={[ca, cb]} />
          {match.sample ? <SampleTag /> : null}
          <div style={{ fontSize: 24, color: C.muted, letterSpacing: 2, fontWeight: 600 }}>{match.event.toUpperCase()}</div>
          <div style={{ fontSize: 22, color: C.dim, marginTop: 2 }}>
            {match.stage} · {match.date}
          </div>
          {[a, b].map((t, i) => (
            <Rise key={t.name} delay={delay + (4 + i * 4)} style={{ display: "flex", alignItems: "center", marginTop: i === 0 ? 26 : 14, gap: 22 }}>
              <div style={{ position: "relative", width: 96, height: 96, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Halo color={teamColor(t.name)} size={150} strength={i === w ? 1 : 0.5} />
                <Logo team={t.name} size={86} />
              </div>
              <div style={{ flex: 1, fontSize: 44, fontWeight: 700, color: i === w ? C.white : C.muted }}>{t.name}</div>
              <div style={{ fontSize: 86, fontWeight: 700 }}>
                <Score value={t.score} win={i === w} delay={scoreAt} />
              </div>
            </Rise>
          ))}
          <Rise delay={delay + 0.9 * fps} style={{ display: "flex", gap: 12, marginTop: 20 }}>
            {match.maps.map((m) => (
              <div key={m.name} style={{ flex: 1, backgroundColor: C.bg, borderRadius: 10, padding: "8px 0", textAlign: "center", borderTop: `3px solid ${m.score[0] > m.score[1] ? ca : cb}` }}>
                <div style={{ fontSize: 18, color: C.dim, letterSpacing: 1 }}>{m.name.toUpperCase()}</div>
                <div style={{ fontSize: 28, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
                  <span style={{ color: m.score[0] > m.score[1] ? C.white : C.dim }}>{m.score[0]}</span>
                  <span style={{ color: C.dim }}>–</span>
                  <span style={{ color: m.score[1] > m.score[0] ? C.white : C.dim }}>{m.score[1]}</span>
                </div>
              </div>
            ))}
          </Rise>
          <div style={{ marginTop: 22, paddingTop: 18, borderTop: `1px solid ${C.line}` }}>
            <Rise delay={impactAt} style={{ fontSize: 20, color: C.dim, letterSpacing: 3, fontWeight: 700, marginBottom: 10 }}>
              IMPACT
            </Rise>
            {[a, b].map((t, i) => (
              <Rise key={t.name} delay={impactAt + 4 + i * 5} style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginTop: 4 }}>
                <span style={{ fontSize: 30, color: C.muted }}>{t.name}</span>
                <span style={{ display: "flex", gap: 22, alignItems: "baseline" }}>
                  <Delta value={t.points} size={34} />
                  <RankMove from={t.rankFrom} to={t.rankTo} spots={match.spots} size={28} />
                </span>
              </Rise>
            ))}
          </div>
        </div>
      </Appear>
    );
  }

  // split: logos fly in from their sides, the score zooms in, colours sweep across
  const sweep = interpolate(frame, [delay, delay + 0.8 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Appear delay={delay} exitAt={exitAt} from="zoom">
      <div style={{ ...cardStyle(teamColor(match.teams[w].name), 1.6), left: 260, top: 250, width: 1400, height: 520 }}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: sweep,
            background: `linear-gradient(105deg, ${ca}55 0%, ${ca}14 44%, transparent 50%, ${cb}14 56%, ${cb}55 100%)`,
          }}
        />
        <AccentBar colors={[ca, ca, cb, cb]} height={8} />
        {match.sample ? <SampleTag /> : null}
        <div style={{ position: "absolute", top: 34, width: "100%", textAlign: "center", fontSize: 28, color: C.muted, letterSpacing: 3, fontWeight: 600 }}>
          {match.event.toUpperCase()} · {match.stage.toUpperCase()}
        </div>
        <div style={{ position: "absolute", top: 74, width: "100%", textAlign: "center", fontSize: 24, color: C.dim }}>{match.date}</div>
        {[a, b].map((t, i) => (
          <div
            key={t.name}
            style={{
              position: "absolute",
              top: 120,
              [i === 0 ? "left" : "right"]: 70,
              width: 420,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              translate: interpolate(frame, [delay, delay + 0.5 * fps], [i === 0 ? "-140px 0px" : "140px 0px", "0px 0px"], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          >
            <div style={{ position: "relative", width: 200, height: 200, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Halo color={teamColor(t.name)} size={330} strength={i === w ? 1.2 : 0.6} />
              <Logo team={t.name} size={190} />
            </div>
            <div style={{ fontSize: 52, fontWeight: 700, marginTop: 12, color: i === w ? C.white : C.muted }}>{t.name}</div>
            <Rise delay={impactAt + i * 5} style={{ marginTop: 14, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
              <Delta value={t.points} size={40} />
              <RankMove from={t.rankFrom} to={t.rankTo} spots={match.spots} size={30} />
            </Rise>
          </div>
        ))}
        <div
          style={{
            position: "absolute",
            top: 150,
            left: 0,
            width: "100%",
            textAlign: "center",
            fontSize: 190,
            fontWeight: 700,
            lineHeight: 1,
            scale: String(interpolate(frame, [scoreAt - 4, scoreAt + 8], [1.6, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })),
            opacity: interpolate(frame, [scoreAt - 4, scoreAt + 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          <Score value={a.score} win={w === 0} delay={scoreAt} />
          <span style={{ color: C.line }}> : </span>
          <Score value={b.score} win={w === 1} delay={scoreAt} />
        </div>
        <Rise delay={delay + 0.9 * fps} style={{ position: "absolute", top: 380, left: 0, width: "100%", display: "flex", justifyContent: "center", gap: 16 }}>
          {match.maps.map((m) => (
            <div key={m.name} style={{ width: 150, backgroundColor: "rgba(14,17,23,0.85)", borderRadius: 10, padding: "8px 0", textAlign: "center", borderTop: `3px solid ${m.score[0] > m.score[1] ? ca : cb}` }}>
              <div style={{ fontSize: 18, color: C.dim, letterSpacing: 1 }}>{m.name.toUpperCase()}</div>
              <div style={{ fontSize: 30, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
                {m.score[0]}–{m.score[1]}
              </div>
            </div>
          ))}
        </Rise>
      </div>
    </Appear>
  );
};
