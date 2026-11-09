import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, FONT } from "../theme";
import { teamColor } from "../teams";
import { AccentBar, cardStyle, Delta, Logo, ordinal, RankMove } from "../cards/parts";
import { Appear, Halo, Rise, usePulse } from "../cards/fx";
import { Sfx } from "../cards/Sfx";

// Video-05 cards. Built on the approved designs: A1 side panel (list of matches), A2 split (duel / head-to-head),
// plus the region-end cards. No series scores in the data (HLTV results pages are behind a bot check): W / L only.

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const GREEN = "#4cc878";
const RED = "#e44c4c";
const YELLOW = "#ffd34d";

type Row = { date: string; opp: string; wl: string; event: string };
type Impact = { team: string; rankFrom: number; rankTo: number; points: number };

const WL: React.FC<{ wl: string; size?: number }> = ({ wl, size = 24 }) => (
  <span style={{ display: "inline-block", minWidth: size * 2.6, textAlign: "center", padding: `${size * 0.12}px ${size * 0.4}px`, borderRadius: 8, fontWeight: 700, fontSize: size, letterSpacing: 2,
    backgroundColor: wl === "W" ? GREEN : RED, color: C.bg, boxShadow: `0 0 16px ${wl === "W" ? GREEN : RED}66` }}>
    {wl === "W" ? "WIN" : "LOSS"}
  </span>
);

// A1: one team's matches (one or several), with the impact on the ranking.
export const ListCard: React.FC<{ team: string; event: string; title?: string | null; tag?: string | null; tagOpp?: string | null; rows: Row[]; impact: Impact; spots: number; exitAt?: number }> = ({
  team, title, tag, tagOpp, rows, impact, spots, exitAt,
}) => {
  const { fps } = useVideoConfig();
  const col = teamColor(team);
  const eventName = rows[0]?.event ?? "";
  return (
    <Appear delay={0} exitAt={exitAt}>
      <div style={{ ...cardStyle(col), right: 70, top: 220, width: 620, padding: "34px 34px 28px" }}>
        <AccentBar colors={[col, YELLOW]} />
        <Rise delay={3} style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div style={{ position: "relative", width: 104, height: 104, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Halo color={col} size={170} />
            <Logo team={team} size={96} />
          </div>
          <div>
            <div style={{ fontSize: 46, fontWeight: 700, lineHeight: 1.05 }}>{team}</div>
            <div style={{ fontSize: 22, color: C.muted, letterSpacing: 1, marginTop: 4 }}>{eventName.toUpperCase()}</div>
          </div>
        </Rise>
        {title ? <Rise delay={8} style={{ marginTop: 18, fontSize: 26, fontWeight: 700, color: YELLOW, letterSpacing: 3 }}>{title}</Rise> : null}
        <div style={{ marginTop: 14 }}>
          {rows.map((r, i) => (
            <Rise key={i} delay={10 + i * 5} style={{ display: "flex", alignItems: "center", gap: 16, padding: "9px 0", borderTop: i ? `1px solid ${C.line}` : "none" }}>
              <span style={{ width: 92, fontSize: 24, color: C.dim, fontVariantNumeric: "tabular-nums" }}>{r.date}</span>
              <Logo team={r.opp} size={44} />
              <span style={{ flex: 1, fontSize: 30, fontWeight: 600 }}>
                <span style={{ color: C.dim, fontWeight: 500 }}>vs </span>
                {r.opp}
              </span>
              {tag && tagOpp === r.opp ? (
                <span style={{ padding: "2px 10px", border: `3px solid ${RED}`, borderRadius: 6, color: RED, fontWeight: 700, fontSize: 20, letterSpacing: 3, rotate: "-4deg" }}>{tag}</span>
              ) : null}
              <WL wl={r.wl} />
            </Rise>
          ))}
        </div>
        {tag && !tagOpp ? (
          <Rise delay={14} style={{ marginTop: 10, display: "inline-block", padding: "6px 16px", borderRadius: 8, border: `3px solid ${RED}`, color: RED, fontWeight: 700, fontSize: 26, letterSpacing: 4, rotate: "-3deg" }}>
            {tag}
          </Rise>
        ) : null}
        <Rise delay={Math.round(0.9 * fps)} style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${C.line}`, display: "flex", alignItems: "baseline", justifyContent: "space-between" }}>
          <span style={{ fontSize: 22, color: C.dim, letterSpacing: 3, fontWeight: 700 }}>POINTS · RANK</span>
          <span style={{ display: "flex", gap: 22, alignItems: "baseline" }}>
            <Delta value={impact.points} size={36} />
            <RankMove from={impact.rankFrom} to={impact.rankTo} spots={spots} size={30} />
          </span>
        </Rise>
        {rows.map((r, i) => <Sfx key={i} at={10 + i * 5} sound="click" n={i} volume={0.6} lead={0} />)}
        {tag ? <Sfx at={(tagOpp ? 10 + Math.max(0, rows.findIndex((r) => r.opp === tagOpp)) * 5 : 14) + 3} sound="toggle" volume={0.55} lead={0} /> : null}
        <Sfx at={Math.round(0.9 * fps)} sound="click" n={rows.length} volume={0.6} lead={0} />
      </div>
    </Appear>
  );
};

// A2: two sides. Head-to-head (same event, same match) or two teams at two events on the same day.
type Side = { team: string; event: string; rows: Row[]; impact: Impact };
export const DuelCard: React.FC<{ sides: Side[]; sameEvent: boolean; spots: number; exitAt?: number }> = ({ sides, sameEvent, spots, exitAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const [a, b] = sides;
  const ca = teamColor(a.team), cb = teamColor(b.team);
  const winsA = a.rows.filter((r) => r.wl === "W").length, winsB = b.rows.filter((r) => r.wl === "W").length;
  const winner = winsA >= winsB ? 0 : 1;
  const sweep = interpolate(frame, [0, 0.8 * fps], [0, 1], clamp);
  const flash = usePulse(0.9 * fps, 0.8);
  return (
    <Appear delay={0} exitAt={exitAt} from="zoom">
      <div style={{ ...cardStyle(winner === 0 ? ca : cb, 1.6), left: 220, top: 230, width: 1480, height: 560 }}>
        <div style={{ position: "absolute", inset: 0, opacity: sweep, background: `linear-gradient(105deg, ${ca}50 0%, ${ca}12 44%, transparent 50%, ${cb}12 56%, ${cb}50 100%)` }} />
        <AccentBar colors={[ca, ca, cb, cb]} height={8} />
        <div style={{ position: "absolute", top: 30, width: "100%", textAlign: "center", fontSize: 28, color: C.muted, letterSpacing: 3, fontWeight: 600 }}>
          {sameEvent ? `${a.rows[0].event.toUpperCase()} · ${a.rows.map((r) => r.date).join(" & ").toUpperCase()}` : `SAME DAY · ${a.rows[0].date.toUpperCase()} · TWO EVENTS`}
        </div>
        {[a, b].map((s, i) => (
          <div key={s.team} style={{ position: "absolute", top: 96, [i === 0 ? "left" : "right"]: 60, width: 560, display: "flex", flexDirection: "column", alignItems: "center",
            translate: interpolate(frame, [0, 0.5 * fps], [i === 0 ? "-140px 0px" : "140px 0px", "0px 0px"], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) }) }}>
            <div style={{ position: "relative", width: 190, height: 190, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Halo color={teamColor(s.team)} size={320} strength={i === winner ? 1.2 : 0.5} />
              <Logo team={s.team} size={180} style={{ opacity: i === winner ? 1 : 0.7 }} />
            </div>
            <div style={{ fontSize: 50, fontWeight: 700, marginTop: 8, color: i === winner ? C.white : C.muted }}>{s.team}</div>
            {!sameEvent ? <div style={{ fontSize: 22, color: C.dim, letterSpacing: 2, marginTop: 2 }}>{s.event.toUpperCase()}</div> : null}
            <Rise delay={14 + i * 4} style={{ display: "flex", gap: 10, marginTop: 14, flexWrap: "wrap", justifyContent: "center", maxWidth: 540 }}>
              {(sameEvent ? s.rows.slice(0, 2) : s.rows).map((r, j) => (
                <span key={j} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                  {!sameEvent ? <span style={{ fontSize: 22, color: C.muted }}>vs {r.opp}</span> : null}
                  <span style={{ scale: String(1 + (i === winner ? 0.12 * flash : 0)) }}>
                    <WL wl={r.wl} size={sameEvent ? 30 : 22} />
                  </span>
                </span>
              ))}
            </Rise>
            <Rise delay={Math.round(1.1 * fps) + i * 4} style={{ marginTop: 16, display: "flex", gap: 18, alignItems: "baseline" }}>
              <Delta value={s.impact.points} size={34} />
              <RankMove from={s.impact.rankFrom} to={s.impact.rankTo} spots={spots} size={28} />
            </Rise>
          </div>
        ))}
        <div style={{ position: "absolute", top: 190, width: "100%", textAlign: "center", fontSize: 70, fontWeight: 700, color: C.line, letterSpacing: 6 }}>VS</div>
        {[0, 1].map((i) => <Sfx key={`r${i}`} at={14 + i * 4} sound="click" n={i} volume={0.6} lead={0} />)}
        {[0, 1].map((i) => <Sfx key={`p${i}`} at={Math.round(1.1 * fps) + i * 4} sound="click" n={i + 2} volume={0.6} lead={0} />)}
      </div>
    </Appear>
  );
};

// Region intro banner over the race (first ~2.5 s of a region).
export const RegionBanner: React.FC<{ title: string; sub: string; until: number }> = ({ title, sub, until }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inP = interpolate(frame, [0, 0.45 * fps], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const outP = interpolate(frame, [until - 0.4 * fps, until], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", inset: 0, backgroundColor: `rgba(14,17,23,${0.78 * Math.min(inP, outP)})`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT }}>
      <div style={{ textAlign: "center", opacity: Math.min(inP, outP), scale: String(0.9 + 0.1 * inP) }}>
        <div style={{ fontSize: 190, fontWeight: 700, color: C.white, letterSpacing: 12, lineHeight: 1 }}>{title}</div>
        <div style={{ fontSize: 56, fontWeight: 700, color: YELLOW, letterSpacing: 10, marginTop: 18 }}>{sub}</div>
      </div>
    </div>
  );
};

// End of a region, card 1: the big names that missed. Tiles drop in as each name is spoken.
type Miss = { name: string; rank: number; points: number; short: number; at: number };
export const MissedCard: React.FC<{ region: string; teams: Miss[]; lastIn: string; lastPoints: number }> = ({ region, teams, lastIn, lastPoints }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cols = teams.length > 4 ? 3 : teams.length;
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT, color: C.white }}>
      <Rise delay={0} style={{ position: "absolute", top: 70, width: "100%", textAlign: "center" }}>
        <div style={{ fontSize: 30, color: C.muted, letterSpacing: 6, fontWeight: 700 }}>{region.toUpperCase()}</div>
        <div style={{ fontSize: 84, fontWeight: 700, color: RED, letterSpacing: 4, textShadow: `0 0 30px ${RED}55` }}>BIG NAMES THAT MISSED</div>
      </Rise>
      <div style={{ position: "absolute", top: 260, left: 0, right: 0, display: "grid", gridTemplateColumns: `repeat(${cols}, 400px)`, justifyContent: "center", gap: 36 }}>
        {teams.map((t) => {
          const p = interpolate(frame, [t.at - 2, t.at + 8], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
          const land = interpolate(frame, [t.at + 6, t.at + 6 + 0.08 * fps, t.at + 6 + 0.5 * fps], [0, 1, 0], clamp);
          return (
            <div key={t.name} style={{ ...cardStyle(teamColor(t.name), 0.6), position: "relative", height: 330, opacity: p, scale: String(1.25 - 0.25 * p),
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10 }}>
              <div style={{ position: "relative", width: 150, height: 150, display: "flex", alignItems: "center", justifyContent: "center", filter: "grayscale(0.55)" }}>
                <Halo color={teamColor(t.name)} size={230} strength={0.6} />
                <Logo team={t.name} size={140} />
              </div>
              <div style={{ fontSize: 42, fontWeight: 700 }}>{t.name}</div>
              <div style={{ display: "flex", gap: 16, alignItems: "baseline", fontVariantNumeric: "tabular-nums" }}>
                <span style={{ fontSize: 30, color: C.muted }}>{ordinal(t.rank)}</span>
                <span style={{ fontSize: 30, fontWeight: 700, color: RED }}>−{t.short} pts</span>
              </div>
              <div style={{ position: "absolute", top: 18, right: 18, padding: "4px 12px", border: `4px solid ${RED}`, borderRadius: 8, color: RED, fontWeight: 700, fontSize: 24, letterSpacing: 3, rotate: "-8deg",
                boxShadow: `0 0 ${10 + 24 * land}px ${RED}88` }}>OUT</div>
            </div>
          );
        })}
      </div>
      <Rise delay={20} style={{ position: "absolute", bottom: 60, width: "100%", textAlign: "center", fontSize: 26, color: C.dim }}>
        points short of the last spot · {lastIn} {lastPoints} · rank on Nov 2
      </Rise>
    </div>
  );
};

// End of a region, card 2: the teams that made it, row by row (stage), logos popping in as they are named.
type Stage = { label: string; teams: string[]; at: number; teamAt: number[] };
export const MadeItCard: React.FC<{ region: string; stages: Stage[] }> = ({ region, stages }) => {
  const frame = useCurrentFrame();
  const size = stages.some((s) => s.teams.length > 6) ? 130 : 150;
  return (
    <div style={{ position: "absolute", inset: 0, fontFamily: FONT, color: C.white }}>
      <Rise delay={0} style={{ position: "absolute", top: 60, width: "100%", textAlign: "center" }}>
        <div style={{ fontSize: 30, color: C.muted, letterSpacing: 6, fontWeight: 700 }}>{region.toUpperCase()}</div>
        <div style={{ fontSize: 84, fontWeight: 700, color: GREEN, letterSpacing: 4, textShadow: `0 0 30px ${GREEN}55` }}>GOING TO SINGAPORE</div>
      </Rise>
      <div style={{ position: "absolute", top: 250, left: 0, right: 0, display: "flex", flexDirection: "column", gap: 34, alignItems: "center" }}>
        {stages.map((st) => (
          <div key={st.label} style={{ display: "flex", alignItems: "center", gap: 28, opacity: interpolate(frame, [st.at - 4, st.at + 6], [0, 1], clamp) }}>
            <div style={{ width: 200, textAlign: "right", fontSize: 34, fontWeight: 700, color: YELLOW, letterSpacing: 3 }}>{st.label}</div>
            <div style={{ display: "flex", gap: 22 }}>
              {st.teams.map((t, i) => {
                const p = interpolate(frame, [st.teamAt[i] - 2, st.teamAt[i] + 8], [0, 1], { ...clamp, easing: Easing.spring({ damping: 12 }) });
                return (
                  <div key={t} style={{ ...cardStyle(teamColor(t), 0.5), position: "relative", width: size + 40, height: size + 70, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                    opacity: Math.min(1, p * 1.5), scale: String(0.6 + 0.4 * p) }}>
                    <Logo team={t} size={size - 20} />
                    <div style={{ fontSize: 20, fontWeight: 600, marginTop: 8, color: C.muted, whiteSpace: "nowrap" }}>{t.length > 14 ? t.split(" ")[0] : t}</div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Asia story card: BC.Game and s1mple's way back to a Major. Each beat appears on the word that tells it.
export const StoryCard: React.FC<{ team: string; roster: [string, string][]; rank: [number, number]; at: { blocked: number; appeal: number; second: number; s1mple: number } }> = ({ team, roster, rank, at }) => {
  const frame = useCurrentFrame();
  const col = teamColor(team);
  const beat = (f: number) => interpolate(frame, [f, f + 10], [0, 1], { ...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const steps = [
    { f: at.blocked, icon: "✕", color: RED, text: "VALVE BLOCKS THE ASIA ROUTE", sub: "crackdown on teams switching regions" },
    { f: at.appeal, icon: "✓", color: GREEN, text: "APPEAL ACCEPTED", sub: "built naturally, around an Asian core" },
    { f: at.second, icon: String(rank[0]), color: YELLOW, text: `${ordinal(rank[0]).toUpperCase()} IN ASIA`, sub: `${rank[1]} points · Nov 2` },
  ];
  const big = beat(at.s1mple);
  return (
    <Appear delay={0} from="zoom">
      <div style={{ ...cardStyle(col, 1.4), left: 160, top: 150, width: 1600, height: 780 }}>
        <AccentBar colors={[col, YELLOW]} height={8} />
        <div style={{ position: "absolute", left: 60, top: 60, width: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div style={{ position: "relative", width: 300, height: 300, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Halo color={col} size={480} strength={1.2} />
            <Logo team={team} size={290} />
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "center", marginTop: 26 }}>
            {roster.map(([p, tag], i) => (
              <Rise key={p} delay={6 + i * 3} style={{ padding: "8px 18px", borderRadius: 10, backgroundColor: p === "s1mple" ? YELLOW : C.bg, color: p === "s1mple" ? C.bg : C.white,
                fontSize: 32, fontWeight: 700, border: `1px solid ${C.line}` }}>
                {p}{tag ? <span style={{ fontSize: 18, fontWeight: 500, color: C.muted, marginLeft: 8 }}>{tag}</span> : null}
              </Rise>
            ))}
          </div>
        </div>
        <div style={{ position: "absolute", left: 660, top: 80, right: 60, display: "flex", flexDirection: "column", gap: 26 }}>
          {steps.map((s) => {
            const p = beat(s.f);
            return (
              <div key={s.text} style={{ display: "flex", alignItems: "center", gap: 26, opacity: p, translate: `${40 * (1 - p)}px 0px` }}>
                <div style={{ width: 92, height: 92, borderRadius: 46, border: `5px solid ${s.color}`, color: s.color, fontSize: 52, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: `0 0 26px ${s.color}66` }}>{s.icon}</div>
                <div>
                  <div style={{ fontSize: 46, fontWeight: 700, color: s.color }}>{s.text}</div>
                  <div style={{ fontSize: 28, color: C.muted }}>{s.sub}</div>
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ position: "absolute", left: 660, right: 60, bottom: 60, padding: "26px 34px", borderRadius: 14, backgroundColor: `${YELLOW}1f`, border: `2px solid ${YELLOW}`,
          opacity: big, scale: String(0.9 + 0.1 * big), boxShadow: `0 0 ${40 * big}px ${YELLOW}55` }}>
          <div style={{ fontSize: 30, color: C.muted, letterSpacing: 3, fontWeight: 700 }}>s1mple</div>
          <div style={{ fontSize: 54, fontWeight: 700, color: YELLOW, lineHeight: 1.05, whiteSpace: "nowrap" }}>FIRST MAJOR SINCE AUSTIN 2025</div>
          <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>last one on loan with FaZe · missed Budapest and Cologne</div>
        </div>
        {roster.map(([p], i) => <Sfx key={p} at={6 + i * 3} sound="click" n={i} volume={0.55} lead={0} />)}
      </div>
    </Appear>
  );
};
