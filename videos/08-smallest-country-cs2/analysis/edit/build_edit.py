"""Editorial cut from approved Andrew takes, real interviews and verified evidence."""
import ast
import hashlib
import json
import math
import shutil
from pathlib import Path

from settings import EDITION, HERE, PUBLIC, ROOT, SOURCE, V1, prepare

FPS = 30
REMOVE = {"a04", "b06", "v02", "z01"}
INTERVIEWS = {
    "h02": {"id": "interview_math", "file": "estonia_math.mp4", "frames": 366, "title": "THE SAME QUESTION / 2018", "credit": "TOLKIENFANATIC / AROUND THE GLOBAL OFFENSIVE", "captions": [(0.2, 3.45, "So, the population of Estonia is about 1.3 million"), (3.45, 6.4, "and you guys have had two Estonians at a Major, right?"), (6.6, 9.35, "So if Estonia was the same size as the United States,"), (9.35, 12.2, "you guys would have 209 Major players.")]},
    "a06": {"id": "interview_ropz", "file": "ropz_scene.mp4", "frames": 252, "title": "ROPZ / THE ESTONIAN SCENE / 2018", "credit": "TOLKIENFANATIC / AROUND THE GLOBAL OFFENSIVE", "captions": [(0.25, 5.95, "I guess me, HS and fejtZ just define the scene as of now."), (6.2, 8.4, "We're the most known people here.")]},
    "c05": {"id": "interview_karrigan", "file": "karrigan.mp4", "frames": 216, "title": "KARRIGAN / ON TSM'S 2015 BREAKTHROUGH", "credit": "THORIN / REFLECTIONS / INTERVIEW RECORDED 2023", "captions": [(0.1, 2.7, "I think that was the first time"), (2.7, 7.05, "we really put Denmark on the map of winning tournaments.")]},
}


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def caption_number_helper():
    # Reuse only the established pure text functions; do not execute the old writer.
    text = (ROOT / "video08/work/captions.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    constants = {"UNITS", "SCALE", "ORDS", "KEEP_ORD", "STAT", "NUMBER_ONE"}
    functions = {"split_punct", "parse_run", "is_num", "fmt_int", "digits"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in functions or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in n.targets)]
    scope = {"re": __import__("re")}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "original-caption-text-helpers", "exec"), scope)
    def normalized(words):
        # The earlier helper assumes years arrive as digits. Andrew spells them out.
        out, i = [], 0
        split = scope["split_punct"]
        parse = scope["parse_run"]
        while i < len(words):
            word = words[i]
            a, _ = split(word["w"])
            if i + 1 < len(words) and a.casefold() == "twenty":
                b, punct = split(words[i + 1]["w"])
                value = parse([b])
                if value is not None and 10 <= value <= 29:
                    out.append({**word, "w": str(2000 + value) + punct, "e": words[i + 1]["e"]})
                    i += 2
                    continue
            if i + 2 < len(words) and words[i + 1]["w"].casefold() == "point":
                integer = parse([a])
                j, fraction, punct = i + 2, "", ""
                while j < len(words):
                    part, pp = split(words[j]["w"])
                    digit = parse([part])
                    if digit is None or not 0 <= digit <= 9:
                        break
                    fraction += str(digit)
                    punct = pp
                    j += 1
                    if punct:
                        break
                if integer is not None and fraction:
                    out.append({**word, "w": f"{integer}.{fraction}{punct}", "e": words[j - 1]["e"]})
                    i = j
                    continue
            out.append(word)
            i += 1
        return scope["digits"](out)
    return normalized


def cue(record, token, fallback=0, occurrence=0):
    norm = lambda s: "".join(c for c in s.casefold() if c.isalnum() or c == "-")
    hits = [w for w in record["words"] if norm(w["w"]) == norm(token)]
    return round(hits[occurrence]["s"] * 30) if len(hits) > occurrence else fallback


def split_caps(words, numeric):
    converted = numeric(words)
    groups, group = [], []
    for w in converted:
        if group and (len(group) >= 5 or len(" ".join(x["w"] for x in group + [w])) > 38):
            groups.append(group)
            group = []
        group.append(w)
        if w["w"].endswith((".", "?", "!", ":")):
            groups.append(group)
            group = []
    if group:
        groups.append(group)
    merged = []
    for group in groups:
        if len(group) == 1 and merged and len(" ".join(w["w"] for w in merged[-1] + group)) <= 42 and group[0]["s"] - merged[-1][-1]["e"] <= 15:
            merged[-1] += group
        else:
            merged.append(group)
    groups = merged
    out = []
    for i, group in enumerate(groups):
        end = group[-1]["e"] + 3
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0]["s"] - 1)
        out.append({"s": group[0]["s"], "e": max(group[-1]["e"], end), "lines": [[{"w": w["w"], "s": w["s"]} for w in group]]})
    return out


def main():
    prepare()
    baseline = HERE / "preservation.json"
    if not baseline.exists():
        original = json.loads((V1 / "work/original_hashes.json").read_text(encoding="utf-8"))
        for p in list((V1 / "final").glob("*")) + list((ROOT / "sotl-graphics/src/video08-codex").glob("*.tsx")) + [V1 / "script_codex_v1.md"]:
            if p.is_file():
                original[str(p.relative_to(ROOT)).replace("\\", "/")] = hashlib.sha256(p.read_bytes()).hexdigest()
        dump(baseline, original)
    evidence = json.loads((V1 / "work/claims.json").read_text(encoding="utf-8"))
    assert evidence["elite"]["unique"] == 99
    dump(PUBLIC / "evidence.json", evidence)
    (SOURCE / "evidence.ts").write_text("export const EVIDENCE = " + json.dumps(evidence, ensure_ascii=False) + ";\n", encoding="utf-8")
    map_data = json.loads((ROOT / "sotl-graphics/public/data/video08_map.json").read_text(encoding="utf-8"))
    (SOURCE / "map.ts").write_text("export const MAP = " + json.dumps(map_data) + ";\n", encoding="utf-8")
    for f in ["world.svg", "baltic.svg", "intro.mp4"]:
        shutil.copyfile(ROOT / "sotl-graphics/public/video08-codex" / f, PUBLIC / f)
    for f in ["estonia_math.mp4", "ropz_scene.mp4", "antwerp.mp4", "mongolia.mp4", "astralis.mp4", "olof.mp4"]:
        shutil.copyfile(ROOT / "sotl-graphics/public/footage08" / f, PUBLIC / f)
    shutil.copyfile(ROOT / "video08/footage/candidates/clipD_karrigan_denmark_map.mp4", PUBLIC / "karrigan.mp4")
    # EDIT ME: sound library. My CC0 sound effects and music are not in this repo; point this at your own folder with the same file names.
    music_root = Path("EDIT_ME/sound-library")
    shutil.copyfile(music_root / "music/music-tension-soft.mp3", HERE / "renders/music.mp3")
    shutil.copyfile(music_root / "LICENSES.md", HERE / "qa/audio_licenses.md")
    shutil.copyfile(V1 / "final/full_country_table.csv", EDITION / "final/full_country_table.csv")
    numeric = caption_number_helper()
    records = json.loads((V1 / "work/narration/narration.json").read_text(encoding="utf-8"))
    narr, shots, captions, sfx = [], [], [], []
    frame = 0

    def add_shot(pid, start, stop, style, file="", offset=0, title="", credit=""):
        if stop - start < 2:
            return
        shots.append({"id": f"{pid}_{len(shots):02}", "block": pid, "from": start, "frames": stop - start, "style": style, "file": file, "offset": offset, "title": title, "credit": credit})

    for rec in records:
        pid = rec["id"]
        if pid in REMOVE or pid == "ident":
            continue
        r = dict(rec)
        r["words"] = [dict(w) for w in rec["words"]]
        if pid == "z03":
            # Retain the question and direction to full data; cut the table-pause clause.
            words = r["words"]
            pause = next(i for i, w in enumerate(words) if w["w"] == "Pause")
            use = next(i for i, w in enumerate(words) if w["w"] == "use")
            cut_a = words[pause - 1]["e"] + .10
            cut_b = max(cut_a, words[use]["s"] - .03)
            shift = cut_b - cut_a
            r["edit"] = {"cut_a": cut_a, "cut_b": cut_b}
            r["duration"] -= shift
            r["words"] = words[:pause] + [{**w, "s": w["s"] - shift, "e": w["e"] - shift} for w in words[use:]]
            r["words"][pause]["w"] = "Use"
            r["text"] = " ".join(w["w"] for w in r["words"])
        lead, tail = 4, 6
        length = math.ceil(r["duration"] * 30) + lead + tail
        r.update({"from": frame + lead, "frames": math.ceil(r["duration"] * 30), "path": str(V1 / "work/narration" / f"{pid}.mp3")})
        narr.append(r)
        ws = [{"w": w["w"], "s": r["from"] + round(w["s"] * 30), "e": r["from"] + round(w["e"] * 30)} for w in r["words"]]
        captions += split_caps(ws, numeric)
        start, end = frame, frame + length
        at = lambda word, fallback=0, occurrence=0: max(start + 5, min(end - 5, r["from"] + cue(r, word, fallback, occurrence)))

        # Each block becomes one or more editorial shots, not one presentation page.
        if pid == "h01":
            e = at("Estonia", 105)
            add_shot(pid, start, e, "raw_russia")
            add_shot(pid, e, end, "raw_compare")
        elif pid == "h02":
            e = at("Now", 65)
            add_shot(pid, start, e, "divide")
            add_shot(pid, e, end, "rank_flip")
        elif pid == "h03":
            add_shot(pid, start, end, "three_tests")
        elif pid == "r01":
            p, q = at("paid", 80), at("current-season", 145)
            add_shot(pid, start, p, "rules_question")
            add_shot(pid, p, q, "rules_reach")
            add_shot(pid, q, end, "rules_stack")
        elif pid == "r02":
            p = at("Countries", 180)
            add_shot(pid, start, p, "denominator")
            add_shot(pid, p, end, "population_rule")
        elif pid == "a01":
            p = at("small", 190)
            add_shot(pid, start, p, "prize_count")
            add_shot(pid, p, end, "prize_scale")
        elif pid == "a02":
            p = at("Latvia", 230)
            add_shot(pid, start, p, "estonia_rate")
            add_shot(pid, p, end, "reach_chart")
        elif pid == "a03":
            p = at("Its", 155)
            add_shot(pid, start, p, "russia_rate")
            add_shot(pid, p, end, "ratio_bars")
        elif pid == "a05":
            p = at("Estonia", 155)
            add_shot(pid, start, p, "baltic_pull")
            add_shot(pid, p, end, "baltic_countries")
        elif pid == "a06":
            p = at("Across", 140)
            add_shot(pid, start, p, "scene_breadth")
            add_shot(pid, p, end, "ropz_reveal")
        elif pid == "a07":
            p = min(end - 10, start + 65)
            add_shot(pid, start, p, "ropz_eight")
            add_shot(pid, p, end, "video", "antwerp.mp4", 0, "ROPZ / ANTWERP 2022", "PGL BROADCAST")
        elif pid == "b01":
            p = at("Twenty-eight", 160)
            add_shot(pid, start, p, "sample_dots")
            add_shot(pid, p, end, "mongolia_dots")
        elif pid == "b02":
            p = at("Denmark", 90)
            add_shot(pid, start, p, "mongolia_rate")
            add_shot(pid, p, end, "present_chart")
        elif pid == "b03":
            p = at("Appearing", 185)
            add_shot(pid, start, p, "sample_label")
            add_shot(pid, p, end, "one_map")
        elif pid == "b04":
            p = at("fifty", 220)
            add_shot(pid, start, p, "threshold20")
            add_shot(pid, p, end, "threshold50")
        elif pid == "b05":
            p = at("Different", 180)
            add_shot(pid, start, p, "threshold100")
            add_shot(pid, p, end, "never_second")
        elif pid == "b07":
            p = at("Vitality", 220)
            add_shot(pid, start, p, "video", "mongolia.mp4", 0, "AUSTIN 2025 / ULAANBAATAR WATCH PARTY", "FAN FOOTAGE")
            add_shot(pid, p, end, "austin_score")
        elif pid == "b08":
            add_shot(pid, start, end, "winners_final")
        elif pid == "c01":
            p = at("Thirteen", 210)
            add_shot(pid, start, p, "legacy_archive")
            add_shot(pid, p, end, "places260")
        elif pid == "c02":
            p = at("Denmark", 120)
            add_shot(pid, start, p, "unique99")
            add_shot(pid, p, end, "denmark14")
        elif pid == "c03":
            p = at("Denmark", 170)
            add_shot(pid, start, p, "legacy_chart")
            add_shot(pid, p, end, "both_ways")
        elif pid == "c04":
            p = at("Denmark", 140)
            add_shot(pid, start, p, "video", "olof.mp4", 0, "SWEDEN / 2013–2015", "OLOFMEISTER / OVERPASS 2014 / DEMO POV")
            add_shot(pid, p, end, "crown_relay")
        elif pid == "c05":
            p = at("Denmark's", 200)
            add_shot(pid, start, p, "one_career")
            add_shot(pid, p, end, "fourteen_careers")
        elif pid == "c06":
            p = max(start + 48, end - 360)
            add_shot(pid, start, p, "astralis_title")
            add_shot(pid, p, end, "video", "astralis.mp4", 0, "ASTRALIS / FOUR MAJORS", "ESL / IEM KATOWICE 2019")
        elif pid == "v01":
            p, q = at("Mongolia", 110), at("Denmark", 210)
            add_shot(pid, start, p, "verdict_estonia")
            add_shot(pid, p, q, "verdict_mongolia")
            add_shot(pid, q, end, "verdict_denmark")
        elif pid == "v03":
            p = at("Denmark", 140)
            add_shot(pid, start, p, "three_winners")
            add_shot(pid, p, end, "overall_denmark")
        elif pid == "v04":
            p = at("Per", 130)
            add_shot(pid, start, p, "russia_total")
            add_shot(pid, p, end, "russia_ranks")
        elif pid == "z02":
            p = at("Denmark", 170)
            add_shot(pid, start, p, "challenger_mongolia")
            add_shot(pid, p, end, "challenger_denmark")
        elif pid == "z03":
            add_shot(pid, start, end, "your_country")
        else:
            raise ValueError(pid)
        frame = end
        if pid in INTERVIEWS:
            clip = INTERVIEWS[pid]
            add_shot(clip["id"], frame, frame + clip["frames"], "interview", clip["file"], 0, clip["title"], clip["credit"])
            # Phrase boundaries come from the verified clip transcript. Narration word timings are exact.
            for a, b, text in clip["captions"]:
                words = text.split()
                duration = b - a
                ws = [{"w": w, "s": frame + round((a + duration * i / len(words)) * 30), "e": frame + round((a + duration * (i + .94) / len(words)) * 30)} for i, w in enumerate(words)]
                captions += split_caps(ws, numeric)
            frame += clip["frames"]
        if pid == "h03":
            add_shot("ident", frame, frame + 228, "ident", "intro.mp4")
            ident = next(x for x in records if x["id"] == "ident")
            narr.append({**ident, "from": frame + 9, "frames": math.ceil(ident["duration"] * 30), "path": str(V1 / "work/narration/ident.mp3")})
            frame += 228
    add_shot("end", frame, frame + 180, "end")
    frame += 180
    for a, b in zip(shots, shots[1:]):
        assert a["from"] + a["frames"] == b["from"], (a, b)
    captions.sort(key=lambda c: c["s"])
    for a, b in zip(captions, captions[1:]):
        a["e"] = min(a["e"], b["s"] - 1)
    for i, shot in enumerate(shots):
        kind = shot["style"]
        if kind == "ident" or shot["frames"] < 15:
            continue
        name = "whoosh-short.wav" if kind in {"video", "interview"} else ["slide-1.wav", "whoosh-soft.wav", "slide-2.wav", "whoosh-short.wav"][i % 4]
        sfx.append({"from": max(0, shot["from"] - 2), "file": name, "gain": .7 if kind in {"video", "interview"} else .38})
        if kind in {"rank_flip", "ropz_eight", "mongolia_rate", "unique99", "denmark14", "never_second", "overall_denmark", "both_ways"}:
            sfx.append({"from": shot["from"] + 7, "file": "impact-soft-2.wav", "gain": .9})
        if kind.endswith("chart"):
            for j in range(5):
                sfx.append({"from": shot["from"] + 7 + j * 5, "file": ["tap.wav", "click-soft.wav", "select-1.wav"][j % 3], "gain": .6})
    data = {"fps": 30, "totalFrames": frame, "shots": shots, "narration": narr, "captions": captions, "sfx": sfx, "interviews": INTERVIEWS}
    dump(HERE / "edit.json", data)
    dump(PUBLIC / "edit.json", data)
    (SOURCE / "edit.ts").write_text("export const EDIT = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    (SOURCE / "duration.ts").write_text(f"export const TOTAL_FRAMES = {frame};\n", encoding="utf-8")
    script = ["# Video08 v2 — narration and interview edit", "", "Approved Andrew takes, tightened editorially; original interviews interrupt the graphics.", ""]
    for r in narr:
        script += [f"## {r['id']} / {r['from'] / 30:.2f}s", r["text"], ""]
    script += ["## Source interviews", *[f"- {c['title']}: {c['frames'] / 30:.1f}s, original audio, {c['credit']}" for c in INTERVIEWS.values()]]
    (EDITION / "script_edit.md").write_text("\n".join(script), encoding="utf-8")
    print(f"Edit: {len(shots)} shots, {frame} frames / {frame / 30:.2f}s; {len(captions)} caption phrases, {len(sfx)} sound cues.")


if __name__ == "__main__":
    main()
