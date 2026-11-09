import React from "react";
import { z } from "zod";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Easing,
  interpolate,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT } from "./theme";
import { Stamp } from "./cards/Stamp";
import raceEu from "../public/data/vrs_race_eu.json";
import dailyEu from "../public/data/vrs_daily_eu.json";
import dailyAm from "../public/data/vrs_daily_am.json";
import dailyAs from "../public/data/vrs_daily_as.json";
import logoIndex from "../public/logos/logos.json";

// Ranking race: one VRS snapshot per step, teams glide to their new rank, the Major line drawn after `spots`.
// Data: video05/work/build_race_data.py (monthly, Valve's files) and build_daily_race.py (daily, HLTV).

type Team = { name: string; points: number; rank: number };
type RaceData = { region: string; spots: number; show: number; teams: string[]; frames: { label: string; teams: Team[] }[] };

const VALVE = "Source: Valve Regional Standings (github.com/ValveSoftware/counter-strike_regional_standings)";
const DATA: Record<string, { data: RaceData; source: string }> = {
  eu: { data: raceEu as RaceData, source: `${VALVE}. Jan–Aug: Europe rank derived from the global list.` },
  euDaily: { data: dailyEu as RaceData, source: `${VALVE}, daily values via HLTV.org` },
  amDaily: { data: dailyAm as RaceData, source: `${VALVE}, daily values via HLTV.org` },
  asDaily: { data: dailyAs as RaceData, source: `${VALVE}, daily values via HLTV.org` },
};
const LOGOS = logoIndex as Record<string, { file: string }>;
const DARK_LOGOS = ["Voca", "Nemesis"]; // logos with no dark-mode version: shown on a light badge

export const rankingRaceSchema = z.object({
  dataset: z.enum(["eu", "euDaily", "amDaily", "asDaily"]),
  highlight: z.array(z.string()),
  rows: z.number().min(10).max(30),
  secondsPerStep: z.number().min(0.05).max(6),
  holdSeconds: z.number().min(0).max(10),
  focus: z.array(z.string()).optional(), // when set, every other row dims (callout moments)
  freezeDay: z.number().optional(), // when set, the chart holds that day exactly (index into frames)
  endDay: z.number().optional(), // when set, a moving chart stops on this day instead of running to the last one
  stamps: z.array(z.object({ team: z.string(), kind: z.enum(["in", "out"]), style: z.enum(["rubber", "pill"]), at: z.number().optional() })).optional(),
  focusAt: z.number().optional(), // frame where the dimming of the other rows starts (default 0)
  pulseAt: z.array(z.number()).optional(), // frames where the Major line flashes (a team crossing it)
});
type Props = z.infer<typeof rankingRaceSchema>;

export const calculateRankingRaceMetadata: CalculateMetadataFunction<Props> = ({ props }) => {
  const steps = DATA[props.dataset].data.frames.length - 1;
  return { durationInFrames: Math.round((steps * props.secondsPerStep + props.holdSeconds) * 30) };
};

const TOP = 190;
const LEFT = 90;
const NAME_W = 330;
const BAR_X = LEFT + 70 + NAME_W;
const BAR_MAX = 1920 - BAR_X - 260; // room after the bar for the logo
const FLOOR = 700; // bars start at 700 points so the differences near the line are visible

export const RankingRace: React.FC<Props> = ({ dataset, highlight, rows, secondsPerStep, focus, stamps, freezeDay, endDay, focusAt = 0, pulseAt = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { data, source } = DATA[dataset];
  const steps = data.frames.length - 1;
  const rowH = Math.min(72, Math.floor((1080 - TOP - 70) / rows));

  // Points glide between snapshots (85 % of each step is movement, spread out so swaps happen one after another; the rest a hold). The rank on any
  // frame is the order of the gliding points, so two rows never sit on top of each other; each row's position is
  // the average rank over the last SMOOTH frames, which turns every swap into a short slide.
  const stepAt = (f: number) => {
    const pos = Math.min(Math.max(f, 0) / (secondsPerStep * fps), endDay ?? steps);
    const i = Math.min(Math.floor(pos), steps - 1);
    const k = interpolate(pos - i, [0, 0.85], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.3, 0, 0.7, 1),
    });
    return { a: data.frames[i], b: data.frames[i + 1], k };
  };
  const pointsAt = (f: number) => {
    const { a, b, k } = stepAt(f);
    const pts = new Map<string, number>();
    for (const name of data.teams) {
      const pa = a.teams.find((t) => t.name === name)?.points ?? 0; // absent = below the list, slides out
      const pb = b.teams.find((t) => t.name === name)?.points ?? 0;
      pts.set(name, pa * (1 - k) + pb * k);
    }
    return pts;
  };
  const ranksAt = (f: number) => {
    const sorted = [...pointsAt(f).entries()].sort((x, y) => y[1] - x[1]);
    return new Map(sorted.map(([name], idx) => [name, idx + 1]));
  };

  const SMOOTH = 6;
  const frozen = freezeDay === undefined ? null : data.frames[Math.min(freezeDay, steps)];
  let label: string;
  let teams: { name: string; points: number; rank: number }[];
  if (frozen) {
    label = frozen.label;
    teams = frozen.teams.map((t) => ({ name: t.name, points: Math.max(t.points, FLOOR), rank: t.rank }));
  } else {
    const history = Array.from({ length: SMOOTH }, (_, j) => ranksAt(frame - j));
    const now = pointsAt(frame);
    const { a, b, k } = stepAt(frame);
    label = (k < 0.5 ? a : b).label;
    teams = [...now.entries()].map(([name, points]) => ({
      name,
      points: Math.max(points, FLOOR),
      rank: history.reduce((sum, r) => sum + (r.get(name) ?? rows + 3), 0) / SMOOTH,
    }));
  }
  const dim = interpolate(frame, [focusAt, focusAt + 0.35 * fps], [1, 0.22], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = Math.max(0, ...pulseAt.map((p) => interpolate(frame, [p, p + 3, p + 0.8 * fps], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })));
  const top = Math.max(...teams.map((t) => t.points));
  const cutY = TOP + data.spots * rowH;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg, fontFamily: FONT, color: C.white, isolation: "isolate" }}>
      <div style={{ position: "absolute", left: LEFT, top: 58, fontSize: 40, fontWeight: 600, color: C.muted, letterSpacing: 2 }}>
        {data.region.toUpperCase()} · VALVE REGIONAL STANDINGS
      </div>
      <div style={{ position: "absolute", left: LEFT, top: 104, fontSize: 30, color: C.dim }}>
        Top {data.spots} get a Major invite
      </div>
      <div style={{ position: "absolute", right: 90, top: 30, fontSize: 132, fontWeight: 700, color: C.white, fontVariantNumeric: "tabular-nums" }}>
        {label}
      </div>

      {/* rows, clipped to the visible area so teams slide in and out at the bottom */}
      <div style={{ position: "absolute", left: 0, top: TOP, width: 1920, height: rows * rowH, overflow: "hidden" }}>
        {teams.map((t) => {
          const y = (t.rank - 1) * rowH;
          const isHi = highlight.includes(t.name);
          const below = t.rank > data.spots + 0.5;
          const w = Math.max(6, ((t.points - FLOOR) / (top - FLOOR)) * BAR_MAX);
          const barColor = isHi ? C.yellow : below ? "rgb(150, 62, 66)" : C.ct;
          return (
            <div key={t.name} style={{ position: "absolute", left: 0, top: y, width: 1920, height: rowH, zIndex: isHi ? 2 : 1, opacity: focus?.length && !focus.includes(t.name) ? dim : 1 }}>
              <div style={{ position: "absolute", left: LEFT, width: 60, height: rowH, lineHeight: `${rowH}px`, fontSize: Math.min(rowH * 0.62, 34), color: C.dim, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
                {Math.round(t.rank)}
              </div>
              <div style={{ position: "absolute", left: LEFT + 84, width: NAME_W, height: rowH, lineHeight: `${rowH}px`, fontSize: Math.min(rowH * 0.66, 36), fontWeight: isHi ? 700 : 500, color: isHi ? C.yellow : below ? C.muted : C.white, whiteSpace: "nowrap", overflow: "hidden" }}>
                {t.name}
              </div>
              <div style={{ position: "absolute", left: BAR_X, top: rowH * 0.16, width: w, height: rowH * 0.68, borderRadius: 4, backgroundColor: barColor }} />
              {LOGOS[t.name] ? (
                <div style={{ position: "absolute", left: BAR_X + w + 12, top: rowH * 0.08, height: rowH * 0.84, width: rowH * 2.2, display: "flex", alignItems: "center" }}>
                  <Img src={staticFile(LOGOS[t.name].file)} style={{ maxHeight: "100%", maxWidth: "100%", objectFit: "contain", backgroundColor: DARK_LOGOS.includes(t.name) ? "rgba(238, 240, 245, 0.92)" : undefined, borderRadius: 4, padding: DARK_LOGOS.includes(t.name) ? 3 : 0 }} />
                </div>
              ) : null}
              {stamps
                ?.filter((st) => st.team === t.name)
                .map((st) => (
                  <Stamp key={st.kind} kind={st.kind} variant={st.style} left={BAR_X + w + 12 + rowH * 2.3} rowH={rowH} at={st.at} />
                ))}
              <div style={{ position: "absolute", left: BAR_X, width: w - 12, height: rowH, lineHeight: `${rowH}px`, fontSize: Math.min(rowH * 0.5, 28), fontWeight: 700, color: C.bg, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
                {Math.round(t.points)}
              </div>
            </div>
          );
        })}
      </div>

      {/* the Major line */}
      <div style={{ position: "absolute", left: LEFT, top: cutY - 2 - 2 * pulse, width: 1920 - 2 * LEFT, height: 0, borderTop: `${4 + 4 * pulse}px dashed ${C.yellow}`, boxShadow: `0 0 ${40 * pulse}px ${12 * pulse}px rgba(255, 211, 77, ${0.55 * pulse})` }} />
      <div style={{ position: "absolute", right: 90, top: cutY - 46, fontSize: 30, fontWeight: 700, color: C.yellow, letterSpacing: 1 }}>
        MAJOR LINE
      </div>

      <div style={{ position: "absolute", left: LEFT, bottom: 26, fontSize: 22, color: C.dim }}>{source}</div>
    </AbsoluteFill>
  );
};
