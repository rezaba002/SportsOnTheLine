"""Narration for video 02: Brian (Edge TTS), one file per script paragraph, with word timings.

Reads the NARRATION blocks (lines starting with ">") of script_v1.md. Names are swapped for their spoken spelling
from lexicon.json; Edge TTS word boundaries are mapped back to the script's own words, so captions show
"ZywOo" while the voice says "Zai-woo".

Output: work/narration/pNN.mp3 + narration.json [{id, section, text, tts, duration, words: [{w, s, e}]}]
Usage: python tts_narration.py [--rate +0%]
"""
import asyncio, json, pathlib, re, subprocess, sys, time
import edge_tts

HERE = pathlib.Path(__file__).parent
SCRIPT = HERE.parent / "script_v1.md"
OUT = HERE / "narration"
VOICE = "en-US-BrianNeural"
# ---- EDIT ME: network proxy ----------------------------------------------------
# I reach YouTube / Twitch / Edge TTS through a local proxy. If you need one too, put
# its URL here, e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None


def network_hint(what):
    print(f"\n[network] {what} failed. If your connection needs a proxy, set PROXY in the "
          f"EDIT ME block at the top of {pathlib.Path(__file__).name} (now: {PROXY!r}).", file=sys.stderr)
# ---------------------------------------------------------------------------------
RATE = sys.argv[sys.argv.index("--rate") + 1] if "--rate" in sys.argv else "+0%"
FFPROBE = r"EDIT_ME\ffmpeg\bin\ffprobe.exe"


def paragraphs():
    """(section title, paragraph text) for every narration paragraph, in script order."""
    section, cur, out = None, [], []
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        if line.startswith(">"):
            body = line[1:].strip()
            if body.startswith("[SIGNATURE OUTRO"):     # the ident is its own audio file
                continue
            if body:
                cur.append(body); continue
        if cur:
            out.append((section, " ".join(cur))); cur = []
    if cur:
        out.append((section, " ".join(cur)))
    return out


def lexicon():
    lex = json.load(open(HERE / "lexicon.json", encoding="utf-8"))
    pairs = [(e[0], e[1]) for g in ("players", "teams", "terms") for e in lex[g] if e[0] != e[1]]
    return sorted(pairs, key=lambda p: -len(p[0].split()))           # multi-word keys first


def core(t):
    return re.sub(r"[^\w'-]", "", t).lower()


def units(text, lex):
    """Split a paragraph into units: (script text, spoken text). A unit is a word or a multi-word name."""
    toks, out, i = text.split(), [], 0
    while i < len(toks):
        for key, spoken in lex:
            n = len(key.split())
            seg = toks[i:i + n]
            if len(seg) == n and [core(t) for t in seg] == [core(k) for k in key.split()]:
                tail = re.search(r"[^\w']*$", seg[-1]).group(0)
                out.append((" ".join(seg), spoken + tail)); i += n; break
        else:
            out.append((toks[i], toks[i])); i += 1
    return out


def spoken_words(s):
    """How many boundary events Edge TTS emits for this spoken text (words with letters or digits)."""
    return [p for p in s.split() if re.search(r"\w", p)]


async def synth(text, path):
    com = edge_tts.Communicate(text, VOICE, rate=RATE, proxy=PROXY, boundary="WordBoundary")
    audio, marks = bytearray(), []
    try:
        async for c in com.stream():
            if c["type"] == "audio":
                audio += c["data"]
            elif c["type"] == "WordBoundary":
                marks.append((c["text"], c["offset"] / 1e7, (c["offset"] + c["duration"]) / 1e7))
    except Exception as e:
        network_hint(f"Edge TTS ({type(e).__name__}: {e})")
        raise
    path.write_bytes(bytes(audio))
    return marks


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def align(us, marks, pid):
    """Character-level alignment. Edge TTS sometimes merges words ("March 2024") or splits them ("K / D"), so each
    boundary is located in the spoken text by its characters, and each script unit takes the time span of the
    characters it covers (a merged boundary is shared out in proportion to length)."""
    stream, spans = "", []
    for script, spoken in us:
        n = norm(spoken)
        spans.append((len(stream), len(stream) + len(n)))
        stream += n
    timed, pos, problems = [], 0, []       # (char_start, char_end, t_start, t_end) per boundary
    for text, s, e in marks:
        n = norm(text)
        if not n:
            continue
        at = stream.find(n, pos)
        if at < 0 or at - pos > 3:
            problems.append(f"{pid}: boundary '{text}' not found near char {pos}")
            continue
        timed.append((at, at + len(n), s, e)); pos = at + len(n)
    words = []
    for (script, spoken), (a, b) in zip(us, spans):
        if a == b:                          # a dash: no audio of its own
            continue
        ts, te = [], []
        for ca, cb, s, e in timed:
            lo, hi = max(a, ca), min(b, cb)
            if lo < hi:
                ts.append(s + (e - s) * (lo - ca) / (cb - ca))
                te.append(s + (e - s) * (hi - ca) / (cb - ca))
        if not ts:
            problems.append(f"{pid}: no timing for '{script}'"); continue
        words.append({"w": script, "s": round(min(ts), 3), "e": round(max(te), 3)})
    return words, problems


def main():
    OUT.mkdir(exist_ok=True)
    lex, result, problems = lexicon(), [], []
    for n, (section, text) in enumerate(paragraphs(), 1):
        pid = f"p{n:02d}"
        us = units(text, lex)
        tts = " ".join(sp for _, sp in us)
        mp3, cache = OUT / f"{pid}.mp3", OUT / f"{pid}.marks.json"
        cached = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else None
        if cached and cached["tts"] == tts and cached.get("rate") == RATE and mp3.exists():
            marks = [tuple(m) for m in cached["marks"]]           # same text, same voice settings: reuse
        else:
            for attempt in range(4):                              # the Edge service drops connections now and then
                try:
                    marks = asyncio.run(synth(tts, mp3)); break
                except Exception as ex:
                    print(f"  {pid} attempt {attempt + 1} failed: {type(ex).__name__}", flush=True)
                    time.sleep(5 * (attempt + 1))
            else:
                raise SystemExit(f"{pid}: Edge TTS kept failing; re-run later (finished paragraphs are cached)")
            cache.write_text(json.dumps({"tts": tts, "rate": RATE, "marks": marks}, ensure_ascii=False), encoding="utf-8")
        words, probs = align(us, marks, pid)
        problems += probs
        dur = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                                   capture_output=True, text=True).stdout)
        result.append({"id": pid, "section": section, "text": text, "tts": tts, "duration": round(dur, 3), "words": words,
                       "marks": [[t, round(s, 3), round(e, 3)] for t, s, e in marks]})
        print(f"{pid} {dur:5.1f}s  {section[:28]:28}  {text[:60]}", flush=True)
    (OUT / "narration.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    total = sum(r["duration"] for r in result)
    print(f"\n{len(result)} paragraphs, {total:.1f}s of narration ({total / 60:.1f} min)")
    print("alignment problems:", problems or "none")


if __name__ == "__main__":
    main()
