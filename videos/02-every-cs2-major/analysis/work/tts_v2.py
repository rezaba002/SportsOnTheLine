"""Brian narration for script_v2.md: one file per [id] block -> narration_v2/<id>.mp3 + narration.json (same format as v1)."""
import json, pathlib, re, subprocess, sys, time, asyncio
import tts_narration as T

T.SCRIPT = T.HERE.parent / "script_v2.md"
T.OUT = T.HERE / "narration_v2"
T.RATE = "+8%"


def blocks():
    out = []
    for line in T.SCRIPT.read_text(encoding="utf-8").splitlines():
        m = re.match(r">\s*\[(\w+)\]\s*(.+)", line)
        if m:
            out.append((m.group(1), m.group(2).strip()))
    return out


def main():
    T.OUT.mkdir(exist_ok=True)
    lex, result, problems = T.lexicon(), [], []
    for pid, text in blocks():
        us = T.units(text, lex)
        tts = " ".join(sp for _, sp in us)
        mp3, cache = T.OUT / f"{pid}.mp3", T.OUT / f"{pid}.marks.json"
        cached = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else None
        if cached and cached["tts"] == tts and cached.get("rate") == T.RATE and mp3.exists():
            marks = [tuple(m) for m in cached["marks"]]
        else:
            for attempt in range(5):
                try:
                    marks = asyncio.run(T.synth(tts, mp3)); break
                except Exception as ex:
                    print(f"  {pid} attempt {attempt + 1}: {type(ex).__name__}", flush=True); time.sleep(4 * (attempt + 1))
            else:
                raise SystemExit(f"{pid}: Edge TTS kept failing")
            cache.write_text(json.dumps({"tts": tts, "rate": T.RATE, "marks": marks}, ensure_ascii=False), encoding="utf-8")
        words, probs = T.align(us, marks, pid)
        problems += probs
        dur = float(subprocess.run([T.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                                   capture_output=True, text=True).stdout)
        result.append({"id": pid, "section": pid, "text": text, "tts": tts, "duration": round(dur, 3), "words": words})
        print(f"{pid:4} {dur:5.1f}s  {text[:70]}", flush=True)
    (T.OUT / "narration.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    tot = sum(r["duration"] for r in result)
    print(f"\n{len(result)} blocks, {tot:.1f}s ({tot / 60:.2f} min); alignment problems: {problems or 'none'}")


if __name__ == "__main__":
    main()
