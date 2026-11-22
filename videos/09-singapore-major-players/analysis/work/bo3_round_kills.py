"""Kill times for one round from bo3.gg's 2D-replay file, without downloading all of it.

File layout (keys in order): effects, kills, match, shots, states, team_*.
1. Fetch the head until the first state parses -> kills (frame -> killer/victim), match info, state 0.
2. Find one sampled state (phase is written every 10 frames) that is live (phase 1); its timer
   gives the exact live-start tick: tick - (115 - time_remaining) * 64. Normally one 40 KB probe
   right after the usual 20 s freeze is enough; after timeouts/halftime we binary-search.
Times are seconds after freeze end.
"""
import json, re, sys
from bo3 import get_range

ROUND_TIME = 115.0
SAMPLE = re.compile(rb'"ingame_tick":\s*(\d+).*?"timer":\s*\{([^}]*)\}', re.S)
PHASE = re.compile(rb'"phase":\s*(\d+)')
REMAIN = re.compile(rb'"time_remaining":\s*(-?\d+)')


def _samples(url, off, n=40_000):
    body, _ = get_range(url, off, off + n - 1)
    out = []
    for m in SAMPLE.finditer(body):
        ph, tr = PHASE.search(m.group(2)), REMAIN.search(m.group(2))
        if ph:
            out.append((int(m.group(1)), int(ph.group(1)), int(tr.group(1)) / 1e9 if tr else None))
    return out, len(body)


def round_kills(game, rnd):
    url = f"https://files.bo3.gg/round_maps/{game}/{rnd}.json"
    buf, chunk, size = b"", 120_000, None
    dec = json.JSONDecoder()
    while True:
        body, size = get_range(url, len(buf), len(buf) + chunk - 1)
        buf += body
        si = buf.find(b'"states"')
        if si >= 0:
            t = buf[si:].decode("utf-8", "ignore")
            try:
                s0, _ = dec.raw_decode(t, t.index("{"))
                break
            except (json.JSONDecodeError, ValueError):
                pass
        if len(buf) >= size or not body:
            raise RuntimeError(f"no states in {url}")
        chunk = min(chunk * 2, 800_000)
    fetched = len(buf)
    ki, hi = buf.find(b'"kills"'), buf.find(b'"shots"')
    head = json.loads(b"{" + buf[ki:hi].rstrip().rstrip(b",") + b"}")
    m = head["match"]
    rate, step = m["tick_rate"], m["teke_nth_frame"]
    tick0, frames = s0["ingame_tick"], m["current_frame"] + 1

    live_tick, how = None, "state0"
    if s0["timer"].get("phase", 0) != 0:
        live_tick = tick0  # replay starts already live (rare)
    else:
        bpf = (size - si) / frames
        est = s0["timer"]["time_remaining"] / 1e9 * (rate / step)  # usual freeze end frame
        lo, hi_ = si, size
        off = int(si + bpf * (est + 14))
        how = "probe"
        for _ in range(24):
            pts, n = _samples(url, off)
            fetched += n
            live = [p for p in pts if p[1] == 1 and p[2] is not None]
            if live:
                tk, _, tr = live[0]
                live_tick = tk - (ROUND_TIME - tr) * rate
                break
            if not pts or pts[-1][1] == 0:
                lo = off  # still freeze (timeout / halftime) -> go later
            else:
                hi_ = off  # bomb planted / round over -> go earlier
            if hi_ - lo < 20_000:
                break
            off = (lo + hi_) // 2
            how = "search"
    if live_tick is None:
        raise RuntimeError(f"live start not found {url}")

    kills = []
    for fr, ks in head["kills"].items():
        kt = tick0 + int(fr) * step
        for k in ks:
            kills.append([round((kt - live_tick) / rate, 2), k.get("killer_name"), k.get("killer_team"),
                          k.get("victim_name"), k.get("victim_team"), k.get("weapon")])
    kills.sort(key=lambda k: k[0])
    roster = [[p.get("name"), p.get("steam_id_64"), p.get("team"), p.get("money")] for p in s0.get("players", [])]
    return {"g": game, "r": rnd, "tick0": tick0, "live_tick": live_tick, "frames": frames,
            "step": step, "rate": rate, "size": size, "fetched": fetched, "how": how, "roster": roster, "kills": kills}


if __name__ == "__main__":
    for r in sys.argv[2:]:
        d = round_kills(int(sys.argv[1]), int(r))
        print(f"round {r}: {d['how']}, fetched {d['fetched'] // 1000} KB of {d['size'] // 1000} KB")
        for k in d["kills"]:
            print(f"   {k[0]:6.1f}s {k[1]:>12} -> {k[3]}")
