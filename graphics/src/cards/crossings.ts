import dailyEu from "../../public/data/vrs_daily_eu.json";
import dailyAm from "../../public/data/vrs_daily_am.json";
import dailyAs from "../../public/data/vrs_daily_as.json";

// IN / OUT stamps come from the data, never by hand: a team gets IN on `day` when it was below the Major line the
// day before and is above it now, OUT the other way round. Ranks are the true regional ranks of that day, which is
// exactly what the frozen race shows, so a stamp can only sit on the right row.

type Frame = { date: string; label: string; teams: { name: string; rank: number; points: number }[] };
type Data = { spots: number; frames: Frame[] };
export const RACES: Record<string, Data> = { euDaily: dailyEu as Data, amDaily: dailyAm as Data, asDaily: dailyAs as Data };

export type Crossing = { team: string; kind: "in" | "out"; rank: number };

export const crossings = (dataset: string, day: number): Crossing[] => {
  const { spots, frames } = RACES[dataset];
  const before = new Map(frames[day - 1].teams.map((t) => [t.name, t.rank]));
  return frames[day].teams
    .filter((t) => before.has(t.name) && (before.get(t.name)! <= spots) !== (t.rank <= spots))
    .map((t) => ({ team: t.name, kind: t.rank <= spots ? ("in" as const) : ("out" as const), rank: t.rank }))
    .sort((a, b) => a.rank - b.rank);
};

// Same rule between any two days (net change), for a chart that moves several days at once. Optionally only some teams.
export const crossingsBetween = (dataset: string, fromDay: number, toDay: number, only?: string[]): Crossing[] => {
  const { spots, frames } = RACES[dataset];
  const before = new Map(frames[fromDay].teams.map((t) => [t.name, t.rank]));
  return frames[toDay].teams
    .filter((t) => (!only || only.includes(t.name)) && before.has(t.name) && (before.get(t.name)! <= spots) !== (t.rank <= spots))
    .map((t) => ({ team: t.name, kind: t.rank <= spots ? ("in" as const) : ("out" as const), rank: t.rank }))
    .sort((a, b) => a.rank - b.rank);
};

// Guard for any stamp list: throws (fails the render) if an IN sits below the line or an OUT above it on that day.
export const checkStamps = (dataset: string, day: number, stamps: { team: string; kind: "in" | "out" }[]) => {
  const { spots, frames } = RACES[dataset];
  for (const s of stamps) {
    const t = frames[day].teams.find((x) => x.name === s.team);
    if (!t) throw new Error(`stamp on ${s.team}: not in the ${dataset} list on ${frames[day].date}`);
    if ((s.kind === "in") !== (t.rank <= spots)) {
      throw new Error(`stamp ${s.kind.toUpperCase()} on ${s.team} is wrong: rank ${t.rank} on ${frames[day].date}, line after ${spots}`);
    }
  }
  return stamps;
};
