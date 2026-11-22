"""Exact Andrew word cues in Claude's Bahnschrift/yellow-active-word style."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "deps"))

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from settings import EDITION, HERE, ROOT, prepare


def ts(frame, comma=False):
    t = round(frame / 30 * (1000 if comma else 100))
    scale = 1000 if comma else 100
    h, rem = divmod(t, 3600 * scale)
    m, rem = divmod(rem, 60 * scale)
    s, fraction = divmod(rem, scale)
    return f"{h:02}:{m:02}:{s:02},{fraction:03}" if comma else f"{h}:{m:02}:{s:02}.{fraction:02}"


def clean(text):
    return text.replace("{", "(").replace("}", ")").replace("\n", " ")


def main():
    prepare()
    fonts = HERE / "fonts"
    fonts.mkdir(exist_ok=True)
    font_path = fonts / "SOTLCaption.ttf"
    if not font_path.exists():
        original = TTFont(ROOT / "sotl-graphics/public/fonts/bahnschrift.ttf")
        font = instantiateVariableFont(original, {"wght": 700, "wdth": 90}, inplace=False)
        for record in font["name"].names:
            if record.nameID in [1, 4, 6, 16]:
                record.string = "SOTLCaption".encode(record.getEncoding())
            elif record.nameID in [2, 17]:
                record.string = "Bold".encode(record.getEncoding())
        font.save(font_path)
    data = json.loads((HERE / "edit.json").read_text(encoding="utf-8"))
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,SOTLCaption,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4.3,2.4,2,80,80,62,1
Style: Info,SOTLCaption,31,&H004DD3FF,&H00FFFFFF,&H00201810,&H00000000,-1,0,0,0,100,100,1.2,0,1,1.5,1,7,92,80,57,1
Style: Credit,SOTLCaption,20,&H00E2D9D5,&H00FFFFFF,&H00201810,&H00000000,0,0,0,0,100,100,1,0,1,1,1,7,92,80,102,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events, plain = [], []
    for cap in data["captions"]:
        words = [w for line in cap["lines"] for w in line]
        pieces = []
        for i, w in enumerate(words):
            a = max(0, round((w["s"] - cap["s"]) / 30 * 1000))
            end_frame = words[i + 1]["s"] if i + 1 < len(words) else cap["e"]
            b = max(a + 1, round((end_frame - cap["s"]) / 30 * 1000))
            tag = "{\\rCaption\\1c&HFFFFFF&\\t(" + str(a) + "," + str(a + 1) + ",\\1c&H4DD3FF&)\\t(" + str(b) + "," + str(b + 1) + ",\\1c&HFFFFFF&)}"
            pieces.append(tag + clean(w["w"]))
        text = "{\\fad(70,0)}" + " ".join(pieces)
        events.append(f"Dialogue: 2,{ts(cap['s'])},{ts(cap['e'] + 1)},Caption,,0,0,0,,{text}")
        plain.append((cap["s"], cap["e"] + 1, " ".join(w["w"] for w in words)))
    for shot in data["shots"]:
        if shot["style"] in ["video", "interview"]:
            a, b = shot["from"], shot["from"] + shot["frames"]
            events.append(f"Dialogue: 1,{ts(a + 3)},{ts(b)},Info,,0,0,0,,{{\\fad(80,60)}}{clean(shot['title'])}")
            events.append(f"Dialogue: 1,{ts(a + 5)},{ts(b)},Credit,,0,0,0,,{{\\fad(80,60)}}{clean(shot['credit'])}")
    (HERE / "captions.ass").write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")
    srt = "\n\n".join(f"{i}\n{ts(a, True)} --> {ts(b, True)}\n{text}" for i, (a, b, text) in enumerate(plain, 1))
    (EDITION / "final/video08_codex_v2_en.srt").write_text(srt + "\n", encoding="utf-8")
    print(f"{len(plain)} word-tracked caption phrases; Bahnschrift wght700 / wdth90 instantiated.")


if __name__ == "__main__":
    main()
