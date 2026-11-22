"""Check speech handoffs and actual caption font widths without another encode."""
import json

from PIL import ImageFont

from settings import HERE


def main():
    edit = json.loads((HERE / "edit.json").read_text(encoding="utf-8"))
    intervals = [{"id": r["id"], "start": r["from"] / 30, "end": r["from"] / 30 + r["duration"]} for r in edit["narration"]]
    intervals += [{"id": s["id"], "start": s["from"] / 30, "end": (s["from"] + s["frames"]) / 30} for s in edit["shots"] if s["style"] == "interview"]
    intervals.sort(key=lambda r: r["start"])
    handoffs = [{"from": a["id"], "to": b["id"], "gap_seconds": round(b["start"] - a["end"], 6)} for a, b in zip(intervals, intervals[1:])]
    assert min(h["gap_seconds"] for h in handoffs) >= 0, "Speech files overlap"
    font = ImageFont.truetype(str(HERE / "fonts/SOTLCaption.ttf"), 54)
    widths = []
    for c in edit["captions"]:
        text = " ".join(w["w"] for line in c["lines"] for w in line)
        width = font.getlength(text)
        assert width < 1760, (text, width)
        widths.append({"text": text, "pixels": round(width, 2)})
    report = {"speech_intervals": len(intervals), "minimum_handoff_seconds": min(h["gap_seconds"] for h in handoffs), "handoffs": handoffs, "widest_caption": max(widths, key=lambda r: r["pixels"]), "caption_safe_width_pixels": 1760, "caption_phrases": len(widths)}
    (HERE / "qa/timing_and_caption_widths.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"{len(intervals)} speech intervals: no overlaps. Caption width max: {report['widest_caption']['pixels']} px / 1760 px safe width.")


if __name__ == "__main__":
    main()
