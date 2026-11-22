import React from "react";
import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Captions, CapCue } from "../cards/Captions";
import { C } from "../theme";
import { EDIT } from "./edit";
import { EVIDENCE } from "./evidence";
import { MAP } from "./map";
import {
  BLUE,
  GREEN,
  Y,
  RED,
  WHITE,
  COLOR,
  Flag,
  Tag,
  Head,
  Center,
  Stamp,
  Sticker,
  Chart,
  BigNumber,
  Split,
  Row,
  go,
  bodyFont,
} from "./visuals";

export type Shot = {
  id: string;
  block: string;
  from: number;
  frames: number;
  style: string;
  file: string;
  offset: number;
  title: string;
  credit: string;
};
export type Props = {
  burnCaptions?: boolean;
  nativeVideo?: boolean;
  onlyShot?: string;
};
const D = EVIDENCE;
const shots = EDIT.shots as Shot[];
const rows = D.tables as Row[][];
const get = (tier: number, iso: string) =>
  rows[tier].find((r) => r.iso === iso)!;
const names = Object.fromEntries(rows.flat().map((r) => [r.iso, r.name]));

const CountryHero: React.FC<{
  iso: string;
  value: string;
  label: string;
  f: number;
  count?: string;
}> = ({ iso, value, label, f, count }) => (
  <Center>
    <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
      <Flag iso={iso} h={90} />
      <Head size={66}>{names[iso].toUpperCase()}</Head>
    </div>
    <Head
      size={260}
      color={COLOR[iso]}
      style={{
        marginTop: 25,
        fontVariantNumeric: "tabular-nums",
        transform: `scale(${1.15 - 0.15 * go(f, 0, 9)})`,
      }}
    >
      {value}
    </Head>
    <Tag color={WHITE} style={{ fontSize: 36 }}>
      {label}
    </Tag>
    {count && (
      <div
        style={{ ...bodyFont, fontSize: 31, color: "#a5afc0", marginTop: 24 }}
      >
        {count}
      </div>
    )}
  </Center>
);

const Threshold: React.FC<{ index: number; f: number }> = ({ index, f }) => {
  const t = D.thresholds[index];
  return (
    <>
      <div style={{ position: "absolute", left: 150, top: 100 }}>
        <Tag>RAISE THE BAR</Tag>
        <Head size={132} style={{ marginTop: 15 }}>
          {t.minimum}+ <span style={{ color: BLUE }}>MAPS</span>
        </Head>
      </div>
      <div style={{ position: "absolute", left: 155, top: 440, width: 1080 }}>
        {t.top.slice(0, 2).map((r, i) => (
          <div
            key={r.iso}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 24,
              height: 130,
              opacity: go(f, 4 + i * 4, 8),
            }}
          >
            <Head size={74} color={i ? WHITE : Y}>
              #{i + 1}
            </Head>
            <Flag iso={r.iso} h={65} />
            <Head size={65}>{names[r.iso]}</Head>
            <Head size={68} color={COLOR[r.iso]} style={{ marginLeft: "auto" }}>
              {r.rate.toFixed(2)}
            </Head>
          </div>
        ))}
        <Tag color="#aab5c5" style={{ fontSize: 25, marginTop: 18 }}>
          PER MILLION CITIZENS
        </Tag>
      </div>
      <div
        style={{
          position: "absolute",
          right: 140,
          top: 300,
          textAlign: "center",
        }}
      >
        <Flag iso="MNG" h={120} />
        <Head size={180} color={COLOR.MNG} style={{ marginTop: 40 }}>
          #{t.mongoliaRank}
        </Head>
        <Tag color={WHITE}>MONGOLIA</Tag>
      </div>
    </>
  );
};

const Baltic: React.FC<{ f: number; animateNames: boolean }> = ({
  f,
  animateNames,
}) => {
  const countryShot = shots.find((s) => s.style === "baltic_countries")!;
  const pullFrames = shots.find((s) => s.style === "baltic_pull")!.frames;
  const voice = EDIT.narration.find((r) => r.id === "a05")!;
  const bx = MAP.baltic.x,
    by = MAP.baltic.y,
    z =
      1 +
      1.3 *
        interpolate(f + (animateNames ? pullFrames : 0), [0, 42], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.45, 0, 0.55, 1),
        });
  const selected = ["EST", "LVA", "DNK", "FIN", "SWE", "LTU"];
  const cues = selected.map((iso) => {
    const word = voice.words
      .filter(
        (w) =>
          w.w.replace(/[.,]/g, "").toLowerCase() === names[iso].toLowerCase(),
      )
      .slice(-1)[0];
    return { iso, at: Math.round(voice.from + word.s * 30) - countryShot.from };
  });
  const finishWord = voice.words.find((w) => w.w === "There")!;
  const finish = Math.round(voice.from + finishWord.s * 30) - countryShot.from;
  const cue =
    animateNames && f < finish
      ? cues.filter((c) => f >= c.at).slice(-1)[0]
      : undefined;
  const active = cue?.iso || "";
  return (
    <>
      <svg
        width={1920}
        height={1080}
        style={{ position: "absolute", inset: 0 }}
      >
        <g
          transform={`translate(1060 480) scale(${z}) translate(${-bx} ${-by})`}
        >
          {MAP.countries.map((r, i) => (
            <path
              key={i}
              d={r.d}
              fill={selected.includes(r.iso) ? COLOR[r.iso] || Y : "#273342"}
              opacity={
                !active || r.iso === active || !selected.includes(r.iso)
                  ? 1
                  : 0.45
              }
              stroke={r.iso === active ? "#fff" : "#0b1018"}
              strokeWidth={(r.iso === active ? 3 : 1) / z}
            />
          ))}
        </g>
      </svg>
      <div style={{ position: "absolute", left: 100, top: 100 }}>
        <Tag>THE BALTIC</Tag>
        <Head size={126} style={{ marginTop: 24 }}>
          6 OF 8.
          <br />
          <span style={{ color: Y }}>ONE SEA.</span>
        </Head>
      </div>
      {active && (
        <div
          style={{
            position: "absolute",
            left: 105,
            top: 650,
            display: "flex",
            alignItems: "center",
            gap: 20,
          }}
        >
          <Flag iso={active} h={76} />
          <Head size={62}>{names[active]}</Head>
        </div>
      )}
    </>
  );
};

const Dots: React.FC<{ highlight: boolean; f: number }> = ({
  highlight,
  f,
}) => (
  <>
    <div style={{ position: "absolute", left: 120, top: 100 }}>
      <Tag>2026 / COLLECTED EVENT SAMPLE</Tag>
      <Head size={124} style={{ marginTop: 15 }}>
        {highlight ? (
          <>
            <span style={{ color: COLOR.MNG }}>28</span> FROM MONGOLIA
          </>
        ) : (
          <>
            420 <span style={{ color: BLUE }}>PLAYERS</span>
          </>
        )}
      </Head>
    </div>
    <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: 420 }, (_, i) => {
        const on = highlight && i < 28,
          col = i % 30,
          r = Math.floor(i / 30),
          p = go(f, Math.min(16, Math.floor(i / 30)), 10);
        return (
          <rect
            key={i}
            x={123 + col * 56}
            y={330 + r * 30}
            rx={4}
            width={36 * p}
            height={20 * p}
            fill={on ? COLOR.MNG : "#435165"}
            opacity={highlight && !on ? 0.25 : 0.8}
          />
        );
      })}
    </svg>
    {highlight && (
      <div
        style={{
          position: "absolute",
          right: 155,
          top: 800,
          display: "flex",
          gap: 20,
          alignItems: "center",
        }}
      >
        <Flag iso="MNG" h={64} />
        <Head size={52}>3.52M CITIZENS</Head>
      </div>
    )}
  </>
);

const Graphic: React.FC<{ shot: Shot; f: number }> = ({ shot, f }) => {
  const s = shot.style;
  if (s === "raw_russia" || s === "russia_total")
    return (
      <CountryHero
        iso="RUS"
        value="525"
        label="RECORDED CS2 PRIZE EARNERS"
        f={f}
      />
    );
  if (s === "raw_compare")
    return <Chart rows={[get(0, "RUS"), get(0, "EST")]} f={f} max={525} raw />;
  if (s === "divide")
    return (
      <Center>
        <Tag color={WHITE}>THE LEADERBOARD CHANGES WHEN YOU</Tag>
        <Head size={200} color={Y} style={{ marginTop: 35 }}>
          ÷ POPULATION
        </Head>
      </Center>
    );
  if (s === "rank_flip") {
    const p = go(f, 0, 17);
    return (
      <>
        <div style={{ position: "absolute", top: 100, left: 135 }}>
          <Tag>PLAYERS PER MILLION CITIZENS</Tag>
          <Head size={82} style={{ marginTop: 18 }}>
            THE MAP FLIPS.
          </Head>
        </div>
        {["RUS", "EST"].map((iso, i) => {
          const r = get(0, iso),
            y = 370 + (i ? 1 - p : p) * 210;
          return (
            <div
              key={iso}
              style={{
                position: "absolute",
                left: 140,
                top: y,
                display: "flex",
                alignItems: "center",
                gap: 25,
              }}
            >
              <Flag iso={iso} h={82} />
              <Head size={62} style={{ width: 265 }}>
                {r.name}
              </Head>
              <div
                style={{
                  width: 820,
                  height: 70,
                  background: "#ffffff09",
                  borderRadius: 5,
                }}
              >
                <div
                  style={{
                    width: ((820 * r.rate) / 35) * go(f, 0, 20),
                    height: "100%",
                    background: COLOR[iso],
                    borderRadius: 5,
                  }}
                />
              </div>
              <Head size={100} color={COLOR[iso]}>
                {r.rate.toFixed(1)}
              </Head>
              <div style={{ marginLeft: 20 }}>
                <Stamp f={f} at={10 + i * 4} color={i ? GREEN : RED} size={70}>
                  #{r.rank}
                </Stamp>
              </div>
            </div>
          );
        })}
      </>
    );
  }
  if (s === "three_tests" || s === "rules_question")
    return (
      <Center>
        <Tag>THE ANSWER DEPENDS ON THE QUESTION</Tag>
        <Head size={150} style={{ textAlign: "center", marginTop: 40 }}>
          THREE TESTS.
          <br />
          <span style={{ color: Y }}>THREE WINNERS.</span>
        </Head>
      </Center>
    );
  if (s === "rules_reach")
    return (
      <BigNumber
        value="4,974"
        label="REACH / RECORDED PRIZE EARNERS"
        color={BLUE}
        f={f}
      />
    );
  if (s === "rules_stack")
    return (
      <Center style={{ gap: 25 }}>
        {[
          ["4,974", "REACH", BLUE],
          ["420", "PRESENT", COLOR.MNG],
          ["99", "LEGACY", Y],
        ].map(([value, title, color], i) => (
          <div
            key={title}
            style={{
              display: "flex",
              gap: 50,
              alignItems: "baseline",
              opacity: go(f, i * 5, 7),
              transform: `translateX(${(1 - go(f, i * 5, 8)) * 120}px)`,
            }}
          >
            <Head
              size={110}
              color={color}
              style={{ width: 450, textAlign: "right" }}
            >
              {value}
            </Head>
            <Head size={58} style={{ width: 380 }}>
              {title}
            </Head>
          </div>
        ))}
      </Center>
    );
  if (s === "denominator")
    return (
      <Center>
        <Tag>ONE SHARED DENOMINATOR</Tag>
        <Head size={190} color={Y} style={{ marginTop: 40 }}>
          PER MILLION
        </Head>
        <Head size={65} style={{ marginTop: 32 }}>
          CITIZENS
        </Head>
        <Tag color="#aab5c5" style={{ marginTop: 45, fontSize: 25 }}>
          WORLD BANK / 2024 POPULATIONS
        </Tag>
      </Center>
    );
  if (s === "population_rule")
    return (
      <Split
        left={
          <>
            <Head size={160} color={Y}>
              ≥1M
            </Head>
            <Tag color={WHITE}>COUNTRY POPULATION</Tag>
          </>
        }
        right={
          <>
            <Head size={85}>3 SAMPLES</Head>
            <Tag color="#aab5c5">DIFFERENT TIME WINDOWS</Tag>
          </>
        }
      />
    );
  if (s === "prize_count")
    return (
      <BigNumber value="4,974" label="01 / THE WIDEST NET" color={BLUE} f={f} />
    );
  if (s === "prize_scale")
    return (
      <Center>
        <Head size={100}>
          ONLINE CUP <span style={{ color: Y }}>→</span> MAJOR
        </Head>
        <Head size={150} color={Y} style={{ marginTop: 55 }}>
          ANY PRIZE MONEY.
        </Head>
      </Center>
    );
  if (s === "estonia_rate")
    return (
      <CountryHero
        iso="EST"
        value="34.2"
        label="PLAYERS PER MILLION"
        count="47 PLAYERS / 1.37M CITIZENS"
        f={f}
      />
    );
  if (s === "reach_chart")
    return <Chart rows={rows[0].slice(0, 5)} f={f} max={35} highlight="EST" />;
  if (s === "russia_rate")
    return <Chart rows={[get(0, "EST"), get(0, "RUS")]} f={f} max={35} />;
  if (s === "ratio_bars")
    return (
      <Split
        left={
          <>
            <Flag iso="RUS" h={75} />
            <Head size={175} color={RED}>
              11.2×
            </Head>
            <Tag color={WHITE}>AS MANY PRIZE EARNERS</Tag>
          </>
        }
        right={
          <>
            <Head size={175} color={Y}>
              104.7×
            </Head>
            <Tag color={WHITE}>AS MANY CITIZENS</Tag>
          </>
        }
      />
    );
  if (s === "baltic_pull" || s === "baltic_countries")
    return <Baltic f={f} animateNames={s === "baltic_countries"} />;
  if (s === "scene_breadth")
    return <CountryHero iso="EST" value="47" label="PRIZE EARNERS" f={f} />;
  if (s === "ropz_reveal" || s === "ropz_eight")
    return (
      <Center style={{ flexDirection: "row", gap: 90 }}>
        <Sticker name="ropz" size={450} f={f} />
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 25 }}>
            <Flag iso="EST" h={70} />
            <Head size={110}>ropz</Head>
          </div>
          <div style={{ marginTop: 55 }}>
            <Stamp f={f} at={5} size={86}>
              {s === "ropz_eight" ? "8× TOP 20" : "ONE UNIQUE PLAYER"}
            </Stamp>
          </div>
        </div>
      </Center>
    );
  if (s === "sample_dots" || s === "mongolia_dots")
    return <Dots highlight={s === "mongolia_dots"} f={f} />;
  if (s === "mongolia_rate")
    return (
      <CountryHero iso="MNG" value="7.94" label="PLAYERS PER MILLION" f={f} />
    );
  if (s === "present_chart")
    return (
      <>
        <Chart
          rows={rows[1].slice(0, 3)}
          f={f}
          max={8}
          highlight="MNG"
          digits={2}
        />
        <div style={{ position: "absolute", right: 180, bottom: 230 }}>
          <Stamp f={f} at={14} color={Y}>
            ALMOST 2× DENMARK
          </Stamp>
        </div>
      </>
    );
  if (s === "sample_label")
    return (
      <Center>
        <Tag color={BLUE}>THE SOURCE'S LABEL</Tag>
        <Head size={220} style={{ marginTop: 25 }}>
          S / A TIER
        </Head>
        <Stamp f={f} at={7} color={Y} size={58}>
          INCLUDES REGIONAL EVENTS
        </Stamp>
      </Center>
    );
  if (s === "one_map")
    return (
      <Center>
        <Head size={220} color={Y}>
          1 MAP
        </Head>
        <Head size={130} style={{ marginTop: 35 }}>
          ≠ A SEASON
        </Head>
      </Center>
    );
  if (s === "threshold20") return <Threshold index={1} f={f} />;
  if (s === "threshold50") return <Threshold index={2} f={f} />;
  if (s === "threshold100")
    return (
      <>
        <Threshold index={3} f={f} />
        <div style={{ position: "absolute", right: 150, bottom: 230 }}>
          <Tag color={Y} style={{ fontSize: 25 }}>
            KOSOVO: 2 PLAYERS / MONGOLIA: 4
          </Tag>
        </div>
      </>
    );
  if (s === "never_second")
    return (
      <Center>
        <Flag iso="MNG" h={100} />
        <Head size={176} style={{ marginTop: 35 }}>
          NEVER BELOW
        </Head>
        <Head size={260} color={Y}>
          2ND.
        </Head>
      </Center>
    );
  if (s === "austin_score" || s === "winners_final")
    return (
      <Center>
        <Tag>AUSTIN MAJOR / 2025 FINAL</Tag>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 85,
            marginTop: 55,
          }}
        >
          <div style={{ textAlign: "center" }}>
            <Sticker name="ropz" size={240} f={f} />
            <Head size={50}>VITALITY</Head>
            <div style={{ marginTop: 20 }}>
              <Flag iso="EST" h={62} />
            </div>
          </div>
          <Head size={220} color={Y}>
            2 : 1
          </Head>
          <div style={{ textAlign: "center" }}>
            <Img
              src={staticFile("logos/the-mongolz.png")}
              style={{ width: 200, height: 200, objectFit: "contain" }}
            />
            <Head size={50} style={{ marginTop: 40 }}>
              THE MONGOLZ
            </Head>
            <div style={{ marginTop: 20 }}>
              <Flag iso="MNG" h={62} />
            </div>
          </div>
        </div>
      </Center>
    );
  if (s === "legacy_archive")
    return (
      <Center>
        <Tag color={Y}>03 / THE HISTORICAL ELITE</Tag>
        <Head size={190} style={{ marginTop: 45 }}>
          HLTV TOP 20
        </Head>
        <Head size={75} color="#aab5c5" style={{ marginTop: 35 }}>
          2013 — 2025
        </Head>
      </Center>
    );
  if (s === "places260")
    return (
      <BigNumber
        value="260"
        label="ANNUAL PLACES / INCLUDING REPEATS"
        color={Y}
        f={f}
      />
    );
  if (s === "unique99")
    return (
      <BigNumber
        value="99"
        label="DIFFERENT PEOPLE / COUNTED ONCE"
        color={GREEN}
        f={f}
      />
    );
  if (s === "denmark14")
    return (
      <CountryHero
        iso="DNK"
        value="14"
        label="UNIQUE TOP 20 PLAYERS"
        count="5.98M CITIZENS / 2.34 PER MILLION"
        f={f}
      />
    );
  if (s === "legacy_chart")
    return (
      <Chart
        rows={rows[2].slice(0, 5)}
        f={f}
        max={2.5}
        highlight="DNK"
        digits={2}
        title="UNIQUE TOP 20 PLAYERS / MILLION CITIZENS"
      />
    );
  if (s === "both_ways")
    return (
      <Center>
        <Flag iso="DNK" h={100} />
        <Head size={150} style={{ marginTop: 45 }}>
          #1 IN TOTAL.
        </Head>
        <Head size={150} color={GREEN}>
          #1 PER PERSON.
        </Head>
      </Center>
    );
  if (s === "crown_relay") {
    const leaders = D.history.filter((r) => r.year >= 2016);
    const index = Math.min(
      leaders.length - 1,
      Math.floor(f / Math.max(1, (shot.frames - 10) / leaders.length)),
    );
    const current = leaders[index];
    const recent = leaders.slice(Math.max(0, index - 4), index + 1);
    return (
      <Center>
        <Tag>THE YEARLY CROWN / TOP 20 PLAYERS PER MILLION</Tag>
        <div
          style={{
            display: "flex",
            gap: 55,
            alignItems: "center",
            marginTop: 45,
          }}
        >
          <Head size={180} color={COLOR[current.iso]}>
            {current.year}
          </Head>
          <Flag iso={current.iso} h={130} />
          <Head size={105}>{names[current.iso]}</Head>
        </div>
        <div
          style={{
            display: "flex",
            gap: 22,
            marginTop: 70,
            minWidth: 900,
            justifyContent: "center",
          }}
        >
          {recent.map((r) => (
            <div
              key={r.year}
              style={{
                width: 154,
                textAlign: "center",
                padding: 16,
                borderBottom: `5px solid ${COLOR[r.iso]}`,
                background: "#ffffff08",
              }}
            >
              <Flag iso={r.iso} h={52} />
              <Head size={35} style={{ marginTop: 15 }}>
                {r.year}
              </Head>
            </div>
          ))}
        </div>
      </Center>
    );
  }
  if (s === "one_career")
    return (
      <Split
        left={<Sticker name="ropz" size={400} f={f} />}
        right={
          <>
            <Head size={190} color={Y}>
              8 → 1
            </Head>
            <Tag color={WHITE}>APPEARANCES → PERSON</Tag>
          </>
        }
      />
    );
  if (s === "fourteen_careers")
    return (
      <Center>
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          <Flag iso="DNK" h={82} />
          <Head size={160} color={GREEN}>
            42 → 14
          </Head>
        </div>
        <div style={{ display: "flex", gap: 18, marginTop: 60 }}>
          {Array.from({ length: 14 }, (_, i) => (
            <svg
              key={i}
              width="78"
              height="130"
              viewBox="0 0 78 130"
              style={{ opacity: go(f, i * 2, 7) }}
            >
              <circle cx="39" cy="25" r="20" fill={GREEN} />
              <path d="M10 125V78Q10 54 39 54Q68 54 68 78V125Z" fill={GREEN} />
            </svg>
          ))}
        </div>
        <Tag color={WHITE} style={{ marginTop: 35 }}>
          APPEARANCES → UNIQUE PEOPLE
        </Tag>
      </Center>
    );
  if (s === "astralis_title")
    return (
      <Center>
        <Head size={170} color={GREEN}>
          ASTRALIS.
        </Head>
        <Head size={120} style={{ marginTop: 40 }}>
          A DANISH DYNASTY.
        </Head>
      </Center>
    );
  if (s.startsWith("verdict_")) {
    const iso =
      s === "verdict_estonia"
        ? "EST"
        : s === "verdict_mongolia"
          ? "MNG"
          : "DNK";
    const m = D.matrix.find((x) => x.iso === iso)!;
    return (
      <Center>
        <div style={{ display: "flex", gap: 25, alignItems: "center" }}>
          <Flag iso={iso} h={100} />
          <Head size={100}>{names[iso]}</Head>
        </div>
        <div style={{ display: "flex", gap: 80, marginTop: 65 }}>
          {m.ranks.map((n, i) => (
            <div
              key={i}
              style={{ textAlign: "center", opacity: go(f, i * 5, 6) }}
            >
              <Head size={150} color={n <= 3 ? GREEN : "#7d899c"}>
                #{n}
              </Head>
              <Tag color="#aab5c5" style={{ marginTop: 22, fontSize: 26 }}>
                {["REACH", "PRESENT", "LEGACY"][i]}
              </Tag>
            </div>
          ))}
        </div>
      </Center>
    );
  }
  if (s === "three_winners")
    return (
      <Center>
        <div style={{ display: "flex", gap: 100 }}>
          {["EST", "MNG", "DNK"].map((iso, i) => (
            <div
              key={iso}
              style={{ textAlign: "center", opacity: go(f, i * 5, 8) }}
            >
              <Flag iso={iso} h={130} />
              <Head size={65} style={{ marginTop: 35 }}>
                {names[iso]}
              </Head>
              <Tag style={{ marginTop: 24 }}>
                {["REACH", "PRESENT", "LEGACY"][i]}
              </Tag>
            </div>
          ))}
        </div>
      </Center>
    );
  if (s === "overall_denmark")
    return (
      <CountryHero
        iso="DNK"
        value="3 → 2 → 1"
        label="THE ALL-ROUND ANSWER"
        f={f}
      />
    );
  if (s === "russia_ranks")
    return (
      <Center>
        <div style={{ display: "flex", alignItems: "center", gap: 25 }}>
          <Flag iso="RUS" h={80} />
          <Head size={70}>PER PERSON</Head>
        </div>
        <Head size={190} color={RED} style={{ marginTop: 65 }}>
          29 → 25 → 20
        </Head>
        <div style={{ display: "flex", gap: 245, marginTop: 30 }}>
          {["REACH", "PRESENT", "LEGACY"].map((x) => (
            <Tag key={x} color="#aab5c5">
              {x}
            </Tag>
          ))}
        </div>
      </Center>
    );
  if (s === "challenger_mongolia")
    return (
      <CountryHero
        iso="MNG"
        value="#1"
        label="IN THE PRESENT-DAY SAMPLE"
        f={f}
      />
    );
  if (s === "challenger_denmark")
    return (
      <Split
        left={
          <>
            <Flag iso="DNK" h={130} />
            <Head size={60} style={{ marginTop: 20 }}>
              BREADTH
            </Head>
          </>
        }
        right={
          <>
            <Flag iso="MNG" h={130} />
            <Head size={60} style={{ marginTop: 20 }}>
              CHALLENGER
            </Head>
          </>
        }
        versus="?"
      />
    );
  if (s === "your_country")
    return (
      <Center>
        <Head size={155}>WHERE DOES</Head>
        <Head size={185} color={Y}>
          YOUR COUNTRY SIT?
        </Head>
        <Tag color="#aab5c5" style={{ marginTop: 45 }}>
          FULL DATA WITH THE EPISODE
        </Tag>
      </Center>
    );
  return (
    <Center>
      <Head size={140}>
        SPORTS<span style={{ color: Y }}>ON</span>THELINE
      </Head>
      <Tag color={WHITE} style={{ fontSize: 35, marginTop: 40 }}>
        THE STORY BEHIND THE NUMBERS.
      </Tag>
    </Center>
  );
};

const Native: React.FC<{ shot: Shot }> = ({ shot }) => {
  const interview = shot.style === "interview";
  return (
    <AbsoluteFill style={{ background: "#080b10" }}>
      <OffthreadVideo
        src={staticFile(`video08-codex-v2/${shot.file}`)}
        muted
        trimBefore={shot.offset}
        style={{
          width: "100%",
          height: "100%",
          objectFit:
            interview && shot.file !== "karrigan.mp4" ? "contain" : "cover",
        }}
      />
      {shot.style !== "ident" && (
        <>
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              height: 220,
              background: "linear-gradient(#080b10c0, transparent)",
            }}
          />
          <div style={{ position: "absolute", left: 95, top: 60 }}>
            <Tag style={{ fontSize: 30 }}>{shot.title}</Tag>
            <Tag color="#d5d9e2" style={{ fontSize: 19, marginTop: 14 }}>
              {shot.credit}
            </Tag>
          </div>
        </>
      )}
    </AbsoluteFill>
  );
};

export const Scene: React.FC<{ shot: Shot; nativeVideo: boolean }> = ({
  shot,
  nativeVideo,
}) => {
  const f = useCurrentFrame();
  if (["video", "interview", "ident"].includes(shot.style))
    return nativeVideo ? (
      <Native shot={shot} />
    ) : (
      <AbsoluteFill style={{ background: "#0b1018" }} />
    );
  const p = shot.style === "baltic_countries" ? 1 : go(f, 0, 7);
  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 55% 30%,#202d42 0%,#101620 55%,#090d13 100%)",
        color: WHITE,
        overflow: "hidden",
        ...bodyFont,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 55,
          top: 32,
          color: "#b0bdcc60",
          fontSize: 17,
          letterSpacing: 4,
        }}
      >
        SPORTSONTHELINE
      </div>
      <AbsoluteFill
        style={{
          opacity: p,
          transform: "translateX(0px) scale(1)",
        }}
      >
        <Graphic shot={shot} f={f} />
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          right: -100 + 2100 * go(f, 0, 7),
          top: 0,
          width: 95,
          height: 1080,
          background: Y,
          transform: "skew(-14deg)",
          opacity: 0,
        }}
      />
    </AbsoluteFill>
  );
};

export const Video08CodexV2: React.FC<Props> = ({
  burnCaptions = true,
  nativeVideo = true,
}) => (
  <AbsoluteFill style={{ background: C.bg }}>
    <style>{"*{box-sizing:border-box}"}</style>
    {shots.map((shot) => (
      <Sequence key={shot.id} from={shot.from} durationInFrames={shot.frames}>
        <Scene shot={shot} nativeVideo={nativeVideo} />
      </Sequence>
    ))}
    {burnCaptions && (
      <Captions cues={EDIT.captions as CapCue[]} size={54} bottom={62} />
    )}
    <Audio src={staticFile("video08-codex-v2/program_audio.m4a")} />
  </AbsoluteFill>
);
