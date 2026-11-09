"""Video 07 English subtitles (SRT) from the narration's own word timings (script spellings, absolute frames in
sotl-graphics/public/data/video07.json), so names are right (Nemiga, MOUZ, PR, Brollan, jL...) and timing is exact.
Numbers become digits for reading (+17, 40th, 80%). Cues: <= 42 chars a line, <= 2 lines, >= 20 frames.
Writes final/video07_en.srt (the uploaded cut) and final/video07_en_trimmed.srt (if 0:22.33-0:49.47 is cut in Studio)."""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "final"
D = json.loads(pathlib.Path(r"D:\Youtube\sotl-graphics\public\data\video07.json").read_text(encoding="utf-8"))
FPS = D["fps"]
PUBLIC = pathlib.Path(r"D:\Youtube\sotl-graphics\public")
NBSP = " "
NUM = {"one": 1, "two": 2, "four": 4, "five": 5, "seven": 7, "eight": 8, "ten": 10, "twelve": 12, "fourteen": 14, "fifteen": 15,
       "sixteen": 16, "seventeen": 17, "twenty": 20, "sixty": 60, "eighty": 80}
ORD = {"first": "1st", "fifth": "5th", "tenth": "10th", "nineteenth": "19th", "fortieth": "40th", "fifty-third": "53rd"}
KEEP_WORD = {"one", "two", "four", "five"}   # "one thing", "two academy players", "four months", "kept their five": stay words


def split_punct(w):
    m = re.match(r"^(.*?)([.,:;?!]*)$", w)
    return m.group(1), m.group(2)


def digits(words):
    """Number words -> digits, 'plus/minus N' -> '+N'/'-N', 'N percent' -> 'N%'. Timing spans merge."""
    out, i = [], 0
    while i < len(words):
        w = dict(words[i]); core, p = split_punct(w["w"]); low = core.lower()
        nxt = words[i + 1] if i + 1 < len(words) else None
        ncore, np_ = split_punct(nxt["w"]) if nxt else ("", "")
        if low in ("plus", "minus") and nxt and ncore.lower() in NUM:
            out.append({**w, "w": ("+" if low == "plus" else "\u2212") + str(NUM[ncore.lower()]) + np_, "e": nxt["e"]}); i += 2; continue
        if low in NUM and nxt and ncore.lower() == "percent":
            out.append({**w, "w": f"{NUM[low]}%" + np_, "e": nxt["e"]}); i += 2; continue
        if low in ORD and not (low == "first" and i and words[i - 1]["w"].lower() != "to"):
            w["w"] = ORD[low] + p
        elif low in NUM and low not in KEEP_WORD:
            w["w"] = str(NUM[low]) + ("%" if low == "sixty" else "") + p     # "from 80% to 60"
        out.append(w); i += 1
    return out


def cues_for(words):
    """Group a block's words into cues: whole sentences packed up to 80 chars; a longer sentence splits at the comma
    nearest its middle (else the middle word); a short leftover ("+17.") joins its neighbour when that fits."""
    L = lambda ws: len(" ".join(x["w"] for x in ws))
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"][-1] in ".?!":
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    pieces = []
    for se in sents:
        todo = [se]
        while todo:
            x = todo.pop(0)
            if L(x) <= 80:
                pieces.append(x); continue
            cuts = [k for k in range(1, len(x)) if x[k - 1]["w"].endswith((",", ":"))] or list(range(1, len(x)))
            k = min(cuts, key=lambda k: abs(L(x[:k]) - L(x[k:])))
            todo[:0] = [x[:k], x[k:]]
    cues = []
    for x in pieces:
        if cues and (L(x) < 18 or L(cues[-1]) < 18) and L(cues[-1]) + 1 + L(x) <= 80:
            cues[-1] = cues[-1] + x
        elif cues and L(cues[-1]) + 1 + L(x) <= 40:
            cues[-1] = cues[-1] + x
        else:
            cues.append(x)
    return cues


def two_lines(text):
    if len(text) <= 42:
        return text
    ws = text.split(" ")
    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(" ".join(ws[k:]))))
    return " ".join(ws[:best]) + "\n" + " ".join(ws[best:])


def build():
    cues = []
    for b in D["blocks"]:
        ws = digits([w for w in D["words"] if w["block"] == b["id"]])
        for c in cues_for(ws):
            cues.append([c[0]["s"], c[-1]["e"], " ".join(x["w"].replace(" ", " ") for x in c), c])
    for k, c in enumerate(cues):              # hold each cue until the next (max +0.6 s), at least 20 frames
        nxt = cues[k + 1][0] if k + 1 < len(cues) else D["end_from"]
        c[1] = min(max(c[1] + 6, c[0] + 20), nxt - 1) if nxt - 1 > c[0] + 20 else max(c[1], c[0] + 20)
    return cues


def ts(sec):
    ms = round(sec * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write(path, cues):
    lines = [f"{i}\n{ts(s)} --> {ts(e)}\n{two_lines(t).replace(NBSP, ' ')}\n" for i, (s, e, t) in enumerate(cues, 1)]
    path.write_text("\n".join(lines), encoding="utf-8")


BUILT = build()
cues = [[s / FPS, e / FPS, t] for s, e, t, _ in BUILT]


def split_words(ws):
    """The same balanced two-line split as two_lines(), on the word list (for the burned-in captions)."""
    txt = lambda part: " ".join(w["w"] for w in part)
    if len(txt(ws)) <= 42 or len(ws) < 2:
        return [ws]
    k = min(range(1, len(ws)), key=lambda k: abs(len(txt(ws[:k])) - len(txt(ws[k:]))))
    return [ws[:k], ws[k:]]


# burned-in captions (sotl-graphics/src/cards/Captions.tsx): frames, lines as word lists, word starts for the highlight
burn = [{"s": s, "e": e, "lines": [[{"w": w["w"], "s": w["s"]} for w in part] for part in split_words(ws)]} for s, e, t, ws in BUILT]
(PUBLIC / "data" / "video07_captions.json").write_text(json.dumps(burn, ensure_ascii=False), encoding="utf-8")
write(OUT / "video07_en.srt", cues)
CUT_A, CUT_B = 22.33, 49.47                 # the optional Studio trim (keeps m1, removes m2-m4)
trimmed = [[s - (CUT_B - CUT_A) if s >= CUT_B else s, e - (CUT_B - CUT_A) if s >= CUT_B else min(e, CUT_A), t]
           for s, e, t in cues if not (CUT_A <= s < CUT_B)]
write(OUT / "video07_en_trimmed.srt", trimmed)
print(f"{len(cues)} cues; trimmed version {len(trimmed)} cues; longest line {max(len(l) for c in cues for l in two_lines(c[2]).splitlines())}")
