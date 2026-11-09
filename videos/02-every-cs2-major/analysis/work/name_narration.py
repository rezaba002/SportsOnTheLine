"""Rebuild a01/a02/a03 narration: Brian's pieces + the casters' own name calls (work/names/<name>.wav).
Writes narration_v2/<id>.mp3 and replaces those entries in narration_v2/narration.json (word timings incl. the names)."""
import asyncio, json, subprocess, time, pathlib
import tts_narration as T

HERE = pathlib.Path(__file__).parent
OUT = HERE / "narration_v2"
NAMES = HERE / "names"
FF = T.FFPROBE.replace("ffprobe.exe", "ffmpeg.exe")
T.RATE = "+8%"
GAP_BEFORE, GAP_AFTER = 0.10, 0.16

SCRIPTS = {
    "a01": ["In-game leader:", "#apEX,", "the only captain with two CS2 Majors. AWP:", "#ZywOo.", "Star rifler:", "#donk", "no debate. Rifler:",
            "#jL,", "the fans' favourite. Anchor:", "#ropz", "the most clutches in Major playoffs."],
    "a02": ["And the team that argues with them:", "#karrigan,", "four Major finals.", "#m0NESY,", "the most AWP kills.", "#NiKo,",
            "a Cologne champion.", "#frozen,", "the most clutches of anyone.", "#b1t", "for analyst Mauisnake, one of the two best anchors after ropz."],
    "a03": ["So which role does team two win?", "#jL", "or", "#frozen?", "#apEX", "or", "#karrigan?", "#ZywOo", "or", "#m0NESY?",
            "Build your all-star five in the comments. Singapore starts on the twenty-fifth of November. Will FaZe finally win a final? See you in Singapore."],
}


def dur(p):
    return float(subprocess.run([T.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def main():
    lex = T.lexicon()
    data = json.loads((OUT / "narration.json").read_text(encoding="utf-8"))
    for sid, parts in SCRIPTS.items():
        tmp = HERE / "tmp" / f"nn_{sid}"
        tmp.mkdir(parents=True, exist_ok=True)
        files, words, t, texts = [], [], 0.0, []
        for k, part in enumerate(parts):
            if part.startswith("#"):
                word = part[1:]
                name = word.strip(",.?")
                f = NAMES / f"{name}.wav"
                t += GAP_BEFORE
                files.append((f, t))
                d = dur(f)
                words.append({"w": word, "s": round(t, 3), "e": round(t + d, 3)})
                t += d + GAP_AFTER
                texts.append(word)
                continue
            us = T.units(part, lex)
            tts = " ".join(sp for _, sp in us)
            mp3 = tmp / f"p{k}.mp3"
            for a in range(5):
                try:
                    marks = asyncio.run(T.synth(tts, mp3)); break
                except Exception as ex:
                    print("  retry", type(ex).__name__); time.sleep(4 * (a + 1))
            ws, probs = T.align(us, marks, f"{sid}.{k}")
            d = dur(mp3)
            # trim Brian's trailing silence so the name call lands right after his colon
            last_end = max((x["e"] for x in ws), default=d)
            files.append((mp3, t))
            for x in ws:
                words.append({"w": x["w"], "s": round(t + x["s"], 3), "e": round(t + x["e"], 3)})
            t += min(d, last_end + 0.12)
            texts.append(part)
        total = t + 0.2
        args, filt = [], []
        for i, (f, at) in enumerate(files):
            args += ["-i", str(f)]
            ms = int(at * 1000)
            filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[x{i}]")
        filt.append("".join(f"[x{i}]" for i in range(len(files))) + f"amix=inputs={len(files)}:normalize=0:duration=longest,atrim=0:{total:.3f}[o]")
        out = OUT / f"{sid}.mp3"
        subprocess.run([FF, "-v", "error", "-y", *args, "-filter_complex", ";".join(filt), "-map", "[o]", "-c:a", "libmp3lame", "-q:a", "2", str(out)], check=True)
        entry = {"id": sid, "section": sid, "text": " ".join(texts).replace("#", ""), "tts": "(Brian + caster name calls)",
                 "duration": round(dur(out), 3), "words": words}
        data = [entry if e["id"] == sid else e for e in data]
        print(f"{sid}: {entry['duration']:.1f}s, {len(words)} words")
    (OUT / "narration.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
