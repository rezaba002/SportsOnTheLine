import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";
import { teamColor } from "../teams";
import dailyEu from "../../public/data/vrs_daily_eu.json";
import transfers from "../../public/data/transfers.json";
import { AccentBar, cardStyle, Logo, ordinal, SampleTag } from "./parts";
import { Appear, CountUp, Halo, Rise, usePulse } from "./fx";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const BLUE = "#5d9cec";
const ORANGE = "#ec963c";
const GREEN = "#4cc878";
const RED = "#e44c4c";
const YELLOW = "#ffd34d";

const Pill: React.FC<{ color: string; children: React.ReactNode }> = ({ color, children }) => (
  <div style={{ display: "inline-block", padding: "6px 16px", borderRadius: 20, backgroundColor: color, color: C.bg, fontSize: 22, fontWeight: 700, letterSpacing: 2, boxShadow: `0 0 22px ${color}66` }}>
    {children}
  </div>
);

// Card B: a team moved across the line without playing.
export const NoPlayCard: React.FC<{
  team: string; headline: string; from: number; to: number; unit: string; why: string; date: string; delay?: number; exitAt?: number; sample?: boolean;
}> = ({ team, headline, from, to, unit, why, date, delay = 0, exitAt, sample }) => {
  const { fps } = useVideoConfig();
  const pop = usePulse(delay + 1.3 * fps, 0.8);
  return (
    <Appear delay={delay} exitAt={exitAt}>
      <div style={{ ...cardStyle(BLUE), right: 70, top: 280, width: 610, padding: "34px 34px 30px" }}>
        <AccentBar colors={[BLUE, teamColor(team)]} />
        {sample ? <SampleTag /> : null}
        <Pill color={BLUE}>DIDN'T PLAY</Pill>
        <Rise delay={delay + 5} style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 22 }}>
          <div style={{ position: "relative", width: 120, height: 120, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Halo color={teamColor(team)} size={190} />
            <Logo team={team} size={110} />
          </div>
          <div>
            <div style={{ fontSize: 48, fontWeight: 700 }}>{team}</div>
            <div style={{ fontSize: 22, color: C.dim }}>{date}</div>
          </div>
        </Rise>
        <Rise delay={delay + 12} style={{ fontSize: 26, color: C.muted, marginTop: 24 }}>
          {headline}
        </Rise>
        <div style={{ fontSize: 92, fontWeight: 700, lineHeight: 1.05, fontVariantNumeric: "tabular-nums" }}>
          <span style={{ color: C.dim }}>
            {from}
            {unit}
          </span>
          <span style={{ color: C.line }}> → </span>
          <span style={{ display: "inline-block", color: C.win, scale: String(1 + 0.12 * pop), textShadow: `0 0 ${12 + 40 * pop}px rgba(76, 200, 120, ${0.3 + 0.5 * pop})` }}>
            <CountUp value={to} from={from} delay={delay + 0.6 * fps} seconds={0.7} />
            {unit}
          </span>
        </div>
        <Rise delay={delay + 1.5 * fps} style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${C.line}`, fontSize: 28, color: C.white, lineHeight: 1.3 }}>
          {why}
        </Rise>
      </div>
    </Appear>
  );
};

// Card C: every roster move of a team since the Cologne Major (grouped by date, + in green, − out in red), and its rank
// in the days after the move that mattered (dashed line = the Major line), drawn on as the card plays.
type Move = { date: string; player: string; dir: string; kind: string; note: string };
type Day = { date: string; label: string; teams: { name: string; rank: number; points: number }[] };
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const short = (d: string) => `${MON[Number(d.slice(5, 7)) - 1]} ${Number(d.slice(8))}`;

export const RosterCard: React.FC<{ team: string; fromDate: string; toDate: string; spots: number; delay?: number; exitAt?: number }> = ({
  team, fromDate, toDate, spots, delay = 0, exitAt,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const moves = ((transfers as Record<string, Move[]>)[team] ?? []).filter((m) => m.date <= toDate);
  const byDate = moves.reduce<Record<string, Move[]>>((acc, m) => ({ ...acc, [m.date]: [...(acc[m.date] ?? []), m] }), {});
  const days = (dailyEu.frames as Day[]).filter((f) => f.date >= fromDate && f.date <= toDate);
  const ranks = days.map((d) => d.teams.find((t) => t.name === team)?.rank ?? 30);
  const W = 560, H = 170, lo = Math.max(1, Math.min(...ranks, spots) - 3), hi = Math.max(...ranks, spots) + 3;
  const x = (i: number) => (i / (days.length - 1)) * W;
  const y = (r: number) => ((r - lo) / (hi - lo)) * H;
  const path = ranks.map((r, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(r).toFixed(1)}`).join(" ");
  const chartAt = delay + (0.6 + Object.keys(byDate).length * 0.15) * fps;
  const draw = interpolate(frame, [chartAt, chartAt + 1.1 * fps], [0, 1], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const endPop = usePulse(chartAt + 1.1 * fps, 0.7);
  return (
    <Appear delay={delay} exitAt={exitAt}>
      <div style={{ ...cardStyle(ORANGE), right: 70, top: 170, width: 640, padding: "34px 34px 26px" }}>
        <AccentBar colors={[ORANGE, teamColor(team)]} />
        <Pill color={ORANGE}>ROSTER CHANGES SINCE COLOGNE</Pill>
        <Rise delay={delay + 5} style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 18 }}>
          <div style={{ position: "relative", width: 100, height: 100, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Halo color={teamColor(team)} size={170} />
            <Logo team={team} size={92} />
          </div>
          <div style={{ fontSize: 46, fontWeight: 700 }}>{team}</div>
        </Rise>
        <div style={{ marginTop: 14 }}>
          {Object.entries(byDate).map(([date, list], i) => (
            <Rise key={date} delay={delay + 0.5 * fps + i * 0.15 * fps} style={{ display: "flex", alignItems: "baseline", gap: 14, marginTop: 8 }}>
              <span style={{ width: 86, flexShrink: 0, fontSize: 24, color: C.dim, fontVariantNumeric: "tabular-nums" }}>{short(date)}</span>
              <span style={{ flex: 1, display: "flex", flexWrap: "wrap", gap: "4px 16px" }}>
                {list.map((m) => (
                  <span key={m.dir + m.player} style={{ fontSize: 30, fontWeight: 700, color: m.dir === "+" ? GREEN : RED }}>
                    {m.dir === "+" ? "+ " : "− "}
                    {m.player}
                    {m.kind === "coach" ? <span style={{ fontSize: 20, color: C.dim, fontWeight: 500 }}> coach</span> : null}
                    {m.note === "benched" ? <span style={{ fontSize: 20, color: C.dim, fontWeight: 500 }}> benched</span> : null}
                  </span>
                ))}
              </span>
            </Rise>
          ))}
        </div>
        <Rise delay={chartAt - 6} style={{ fontSize: 20, color: C.dim, marginTop: 20, letterSpacing: 2, fontWeight: 700 }}>
          EUROPE RANK, {short(fromDate).toUpperCase()} → {short(toDate).toUpperCase()}
        </Rise>
        <svg width={W} height={H + 44} style={{ marginTop: 10, overflow: "visible", opacity: frame >= chartAt - 6 ? 1 : 0 }}>
          <line x1={0} x2={W} y1={y(spots + 0.5)} y2={y(spots + 0.5)} stroke={YELLOW} strokeWidth={3} strokeDasharray="10 8" />
          <text x={0} y={y(spots + 0.5) + 28} fill={YELLOW} fontSize={20} fontWeight={700}>MAJOR LINE</text>
          <path d={path} fill="none" stroke={teamColor(team)} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw} style={{ filter: `drop-shadow(0 0 8px ${teamColor(team)}aa)` }} />
          <circle cx={x(0)} cy={y(ranks[0])} r={9} fill={C.white} />
          <text x={x(0) + 16} y={y(ranks[0]) - 12} fill={C.white} fontSize={30} fontWeight={700}>{ordinal(ranks[0])}</text>
          <g opacity={draw >= 1 ? 1 : 0}>
            <circle cx={x(ranks.length - 1)} cy={y(ranks[ranks.length - 1])} r={11 + 8 * endPop} fill={RED} style={{ filter: `drop-shadow(0 0 ${6 + 16 * endPop}px ${RED})` }} />
            <text x={x(ranks.length - 1) - 18} y={y(ranks[ranks.length - 1]) + 42} fill={RED} fontSize={34} fontWeight={700} textAnchor="end">
              {ordinal(ranks[ranks.length - 1])}
            </text>
          </g>
        </svg>
      </div>
    </Appear>
  );
};

// Card D: the final verdict of a region. Approved order: D2 (zoom on the line) first, then D1 (last in vs first out).
type Row = { name: string; points: number; rank: number };
export const VerdictCard: React.FC<{ region: string; spots: number; rows: Row[]; variant: "versus" | "zoom"; note?: string; delay?: number; exitAt?: number; sample?: boolean }> = ({
  region, spots, rows, variant, note, delay = 0, exitAt, sample,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lastIn = rows.find((r) => r.rank === spots)!;
  const firstOut = rows.find((r) => r.rank === spots + 1)!;
  const gap = lastIn.points - firstOut.points;
  const unit = gap === 1 ? "POINT" : "POINTS";
  // zoom timings
  const lineAt = delay + (0.4 + rows.length * 0.12) * fps;
  const flash = usePulse(lineAt + 0.5 * fps, 0.8);
  // versus timings
  const bang = usePulse(delay + 0.9 * fps, 1.0);

  if (variant === "versus") {
    return (
      <Appear delay={delay} exitAt={exitAt} from="zoom">
        <div style={{ ...cardStyle(YELLOW, 1.4), left: 260, top: 230, width: 1400, height: 600 }}>
          <AccentBar colors={[GREEN, YELLOW, RED]} height={8} />
          {sample ? <SampleTag /> : null}
          <div style={{ position: "absolute", top: 36, width: "100%", textAlign: "center", fontSize: 30, letterSpacing: 4, color: C.muted, fontWeight: 700 }}>
            {region.toUpperCase()} · THE LAST SPOT
          </div>
          {[lastIn, firstOut].map((t, i) => (
            <div
              key={t.name}
              style={{
                position: "absolute", top: 110, [i === 0 ? "left" : "right"]: 80, width: 400, display: "flex", flexDirection: "column", alignItems: "center",
                translate: interpolate(frame, [delay, delay + 0.5 * fps], [i === 0 ? "-160px 0px" : "160px 0px", "0px 0px"], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) }),
              }}
            >
              <Rise delay={delay + 1.2 * fps + i * 4}>
                <div style={{ padding: "6px 22px", borderRadius: 22, backgroundColor: i === 0 ? GREEN : RED, color: C.bg, fontWeight: 700, fontSize: 26, letterSpacing: 2, boxShadow: `0 0 26px ${i === 0 ? GREEN : RED}88` }}>
                  {ordinal(t.rank).toUpperCase()} · {i === 0 ? "IN" : "OUT"}
                </div>
              </Rise>
              <div style={{ position: "relative", width: 220, height: 220, marginTop: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Halo color={teamColor(t.name)} size={340} strength={i === 0 ? 1.2 : 0.5} />
                <Logo team={t.name} size={200} style={{ opacity: i === 0 ? 1 : 0.6 }} />
              </div>
              <div style={{ fontSize: 54, fontWeight: 700, marginTop: 6, color: i === 0 ? C.white : C.muted }}>{t.name}</div>
              <div style={{ fontSize: 40, color: C.muted, fontVariantNumeric: "tabular-nums" }}>
                <CountUp value={t.points} from={t.points - 60} delay={delay + 0.2 * fps} /> pts
              </div>
            </div>
          ))}
          <div style={{ position: "absolute", top: 200, left: 0, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", opacity: frame >= delay + 0.9 * fps ? 1 : 0 }}>
            <div style={{ position: "absolute", top: -60, width: 420, height: 420, borderRadius: "50%", background: `radial-gradient(circle, ${YELLOW}${Math.round(0x66 * bang + 0x14).toString(16).padStart(2, "0")} 0%, ${YELLOW}00 65%)` }} />
            <div style={{ fontSize: 210, fontWeight: 700, color: C.yellow, lineHeight: 1, scale: String(1 + 0.35 * bang), textShadow: `0 0 ${20 + 50 * bang}px rgba(255, 211, 77, 0.7)` }}>{gap}</div>
            <div style={{ fontSize: 40, fontWeight: 700, color: C.yellow, letterSpacing: 6 }}>{unit}</div>
          </div>
          {note ? <div style={{ position: "absolute", bottom: 26, width: "100%", textAlign: "center", fontSize: 24, color: C.dim }}>{note}</div> : null}
        </div>
      </Appear>
    );
  }

  // zoom: the rows around the line, bars scaled to the small range so a 2-point gap is visible; bars grow in turn
  const lo = Math.min(...rows.map((r) => r.points)) - 10;
  const hi = Math.max(...rows.map((r) => r.points)) + 2;
  const BAR = 600, rowH = 84;
  const lineY = 110 + rows.filter((r) => r.rank <= spots).length * rowH + 4;
  return (
    <Appear delay={delay} exitAt={exitAt} from="up">
      <div style={{ ...cardStyle(YELLOW), left: 260, top: 200, width: 1400, height: 120 + rows.length * rowH + 60 }}>
        <AccentBar colors={[BLUE, YELLOW, RED]} />
        {sample ? <SampleTag /> : null}
        <div style={{ position: "absolute", top: 36, left: 60, fontSize: 30, letterSpacing: 4, color: C.muted, fontWeight: 700 }}>
          {region.toUpperCase()} · ZOOMED IN ON THE LINE
        </div>
        {rows.map((r, i) => {
          const inside = r.rank <= spots;
          const grow = interpolate(frame, [delay + (0.3 + i * 0.12) * fps, delay + (0.8 + i * 0.12) * fps], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
          const w = ((r.points - lo) / (hi - lo)) * BAR * grow;
          const key = r.rank === spots || r.rank === spots + 1;
          return (
            <div key={r.name} style={{ position: "absolute", top: 110 + i * rowH + (inside ? 0 : 30), left: 60, right: 60, height: rowH - 14, display: "flex", alignItems: "center", opacity: interpolate(frame, [delay + i * 3, delay + i * 3 + 8], [0, 1], clamp) }}>
              <div style={{ width: 70, fontSize: 36, color: C.dim, textAlign: "right" }}>{r.rank}</div>
              <Logo team={r.name} size={62} style={{ marginLeft: 22 }} />
              <div style={{ width: 280, marginLeft: 18, fontSize: 40, fontWeight: 700, color: inside ? C.white : C.muted }}>{r.name}</div>
              <div
                style={{
                  width: w, height: rowH - 30, borderRadius: 6, backgroundColor: inside ? C.ct : "rgb(150, 62, 66)",
                  display: "flex", alignItems: "center", justifyContent: "flex-end", paddingRight: w > 120 ? 14 : 0, fontSize: 34, fontWeight: 700, color: C.bg, overflow: "hidden",
                  boxShadow: key ? `0 0 ${18 + 30 * flash}px ${inside ? BLUE : RED}aa` : "none",
                }}
              >
                {w > 120 ? r.points : null}
              </div>
            </div>
          );
        })}
        <div
          style={{
            position: "absolute", top: lineY, left: 40, width: interpolate(frame, [lineAt, lineAt + 0.5 * fps], [0, 1320], clamp),
            borderTop: `${5 + 3 * flash}px dashed ${C.yellow}`, boxShadow: `0 0 ${30 * flash}px ${10 * flash}px rgba(255, 211, 77, ${0.5 * flash})`,
          }}
        />
        <div style={{ position: "absolute", top: lineY - 56, right: 70, fontSize: 40, fontWeight: 700, color: C.yellow, opacity: interpolate(frame, [lineAt + 0.5 * fps, lineAt + 0.7 * fps], [0, 1], clamp), scale: String(1 + 0.15 * flash), textShadow: `0 0 ${10 + 30 * flash}px rgba(255,211,77,0.7)` }}>
          {gap} {unit} APART
        </div>
        {note ? <div style={{ position: "absolute", bottom: 18, left: 60, fontSize: 22, color: C.dim }}>{note}</div> : null}
      </div>
    </Appear>
  );
};
