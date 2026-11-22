"""Video 09 captions from Brian's own word timings (sotl-graphics/public/data/video09.json): script spellings (ropz, MongolZ,
GeT_RiGhT, fejtZ…), numbers as digits for reading (525, 29th, 1.4 million, 3,067, −40°C). Cues <= 42 chars a line, <= 2 lines.
Writes final/video09_en.srt (upload to YouTube) and public/data/video09_captions.json (burned-in, src/cards/Captions.tsx)."""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "final"
PUBLIC = pathlib.Path(r"D:\Youtube\sotl-graphics\public")
D = json.loads((PUBLIC / "data" / "video09.json").read_text(encoding="utf-8"))
FPS = D["fps"]

UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
         "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALE = {"hundred": 100, "thousand": 1000}
ORDS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "ninth": 9, "twentieth": 20, "twenty-ninth": 29,
        "forty-fourth": 44, "forty-ninth": 49, "seventieth": 70}
KEEP_ORD = {"first", "second", "third"}           # "the first Asian team", "in second" read better as words
STAT = re.compile(r"^(pros?|players?|maps?|million|times?|majors?|danes|days?|people|per|for|of|years?|swedes)$", re.I)
NUMBER_ONE = {"one"}


def split_punct(w):
    m = re.match(r"^(.*?)([.,:;?!]*)$", w)
    return m.group(1), m.group(2)


def parse_run(tokens):
    """['five','hundred','and','twenty-five'] -> 525; returns None if not a number."""
    total, cur, seen = 0, 0, False
    for t in tokens:
        t = t.lower()
        if t == "and" or t == "a":
            continue
        parts = t.split("-")
        if all(p in UNITS for p in parts):
            cur += sum(UNITS[p] for p in parts); seen = True
        elif t in SCALE:
            cur = max(cur, 1) * SCALE[t]
            if t == "thousand":
                total += cur; cur = 0
            seen = True
        else:
            return None
    return total + cur if seen else None


def is_num(t):
    t = t.lower()
    return t in SCALE or all(p in UNITS for p in t.split("-"))


def fmt_int(n):
    return f"{n:,}"


def digits(words):
    out, i = [], 0
    n = len(words)
    while i < n:
        w = words[i]; core, p = split_punct(w["w"]); low = core.lower()
        nxt = lambda k: split_punct(words[i + k]["w"]) if i + k < n else ("", "")
        # "minus forty degrees" -> "−40°C"
        if low == "minus" and is_num(nxt(1)[0]) and nxt(2)[0].lower() == "degrees":
            out.append({**w, "w": "\u2212" + str(parse_run([nxt(1)[0]])) + "°C" + nxt(2)[1], "e": words[i + 2]["e"]}); i += 3; continue
        # "two to one" -> "2–1"
        if low == "two" and nxt(1)[0].lower() == "to" and nxt(2)[0].lower() == "one":
            out.append({**w, "w": "2\u20131" + nxt(2)[1], "e": words[i + 2]["e"]}); i += 3; continue
        # "number one" -> "#1"
        if low == "number" and nxt(1)[0].lower() in NUMBER_ONE:
            out.append({**w, "w": "#1" + nxt(1)[1], "e": words[i + 1]["e"]}); i += 2; continue
        # ordinals
        if low in ORDS and low not in KEEP_ORD:
            v = ORDS[low]; suf = "th" if 10 <= v % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(v % 10, "th")
            out.append({**w, "w": f"{v}{suf}" + p}); i += 1; continue
        # cardinal runs, incl. "a hundred and one", "one point four million", "three and a half million"
        if is_num(low) or (low == "a" and i + 1 < n and split_punct(words[i + 1]["w"])[0].lower() in SCALE):
            j, toks, last_p = i, [], ""
            while j < n:
                c, pp = split_punct(words[j]["w"])
                cl = c.lower()
                if is_num(cl) or (cl in ("and", "a") and j + 1 < n and is_num(split_punct(words[j + 1]["w"])[0])
                                  and not (cl == "and" and split_punct(words[j + 1]["w"])[0].lower() == "a")):
                    toks.append(c); last_p = pp; j += 1
                    if pp:
                        break
                else:
                    break
            val = parse_run(toks)
            # decimals: "one point four", "three point two"; "and a half"
            dec = ""
            if not last_p and j + 1 < n and split_punct(words[j]["w"])[0].lower() == "point" and is_num(split_punct(words[j + 1]["w"])[0]):
                dec = "." + str(parse_run([split_punct(words[j + 1]["w"])[0]])); last_p = split_punct(words[j + 1]["w"])[1]; j += 2
            elif not last_p and j + 2 < n and [split_punct(words[j + k]["w"])[0].lower() for k in range(3)] == ["and", "a", "half"]:
                dec = ".5"; last_p = split_punct(words[j + 2]["w"])[1]; j += 3
            follow = split_punct(words[j]["w"])[0] if j < n else ""
            if val is None:
                out.append(w); i += 1; continue
            small = val <= 10 and not dec
            prev = split_punct(words[i - 1]["w"])[0].lower() if i else ""
            prev_digit = bool(out) and re.search(r"\d$", split_punct(out[-1]["w"])[0] or "") is not None
            if prev_digit:                               # "Top 20 eight times": never two numbers side by side
                out.append(w); i += 1; continue
            if small and not STAT.match(follow) and prev not in ("level", "top"):
                out.append(w); i += 1; continue          # "one man", "one sea", "two Danes"… stay words unless a stat follows
            if low == "one" and follow.lower() in ("country", "man", "sea", "last", "level"):
                out.append(w); i += 1; continue
            txt = (fmt_int(val) if val >= 10000 or (val >= 1000 and not str(val).startswith("20")) else str(val)) + dec
            out.append({**w, "w": txt + last_p, "e": words[j - 1]["e"]}); i = j; continue
        out.append(w); i += 1
    return out


def cues_for(words):
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


def split_words(ws):
    txt = lambda part: " ".join(w["w"] for w in part)
    if len(txt(ws)) <= 42 or len(ws) < 2:
        return [ws]
    k = min(range(1, len(ws)), key=lambda k: abs(len(txt(ws[:k])) - len(txt(ws[k:]))))
    return [ws[:k], ws[k:]]


def ts(sec):
    ms = round(sec * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


SMALL = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def small_words(ws):
    """Video 09: one to ten read as words ("two of the top four"); bigger stats stay digits (164, 46,000, 15 of the 18)."""
    out = []
    for w in ws:
        m = re.match(r"^(\d+)([.,:;?!]*)$", w["w"])
        if m and int(m.group(1)) <= 10:
            word = SMALL[int(m.group(1))]
            if not out or re.search(r"[.?!:]$", out[-1]["w"]):       # sentence start -> capital
                word = word.capitalize()
            w = {**w, "w": word + m.group(2)}
        out.append(w)
    return out


built = []
for b in D["blocks"]:
    ws = small_words(digits([w for w in D["words"] if w["block"] == b["id"]]))
    for c in cues_for(ws):
        built.append([c[0]["s"], c[-1]["e"], c])
for k, c in enumerate(built):               # hold each cue until the next (max +0.6 s), at least 20 frames
    nxt = built[k + 1][0] if k + 1 < len(built) else D["end_from"]
    c[1] = min(max(c[1] + 6, c[0] + 20), nxt - 1) if nxt - 1 > c[0] + 20 else max(c[1], c[0] + 20)

# channel intro (its words are already on screen as big type, so SRT only): two cues from public/data/intro.json
IW = json.loads((PUBLIC / "data" / "intro.json").read_text(encoding="utf-8"))["words"]
i0 = (D["intro"]["from"] + 8) / FPS          # the intro's voice starts 8 frames in (LEAD in ChannelIntro2.tsx)
srt = [(s / FPS, e / FPS, "\n".join(" ".join(w["w"] for w in part) for part in split_words(c))) for s, e, c in built]
srt += [(i0 + IW[0]["s"], i0 + IW[5]["e"] + 0.3, "This is SportsOnTheLine.\nData-driven CS2 analysis."),
        (i0 + IW[6]["s"], i0 + IW[17]["e"] + 0.5, "We don't guess. We count every round,\nand show you the proof.")]
srt.sort()
OUT.mkdir(exist_ok=True)
(OUT / "video09_en.srt").write_text("\n".join(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n" for i, (s, e, t) in enumerate(srt, 1)), encoding="utf-8")
burn = [{"s": s, "e": e, "lines": [[{"w": w["w"], "s": w["s"]} for w in part] for part in split_words(c)]} for s, e, c in built]
(PUBLIC / "data" / "video09_captions.json").write_text(json.dumps(burn, ensure_ascii=False), encoding="utf-8")
print(f"{len(burn)} burned cues, {len(srt)} SRT cues; longest line {max(len(' '.join(w['w'] for w in l)) for c in burn for l in c['lines'])}")
for c in burn:
    print(f"{c['s'] / FPS:7.2f}  " + " / ".join(" ".join(w["w"] for w in l) for l in c["lines"]))
