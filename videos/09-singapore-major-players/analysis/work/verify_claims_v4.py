"""Release gate for the actual spoken statistical claims, independent of graphics."""
import json
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
d = json.loads((ROOT / "data/swing_v4.json").read_text(encoding="utf-8"))
p = d["players"]
assert d["complete"], "Season collection is incomplete"
assert d["model_version"] == "bomb-v4-objective-end-shapley"
assert d["coverage"]["rounds"] >= 40000, "Investigate material missing objective coverage"
for name in ("donk", "sh1ro", "nilo", "MartinezSa", "ZywOo", "Jame", "910", "m0NESY"):
    assert p[name]["swing_per_map"] > 0, f"Revise positive-swing claim: {name}"
for name in ("zont1x", "Brollan", "susp", "karrigan"):
    assert p[name]["swing_per_map"] < 0, f"Revise negative-swing claim: {name}"
for name in ("ZywOo", "910"):
    assert max(p[name]["by_time"],key=p[name]["by_time"].get) == "60+", f"Revise late-round claim: {name}"
assert p["nilo"]["by_time"]["30-60"] > 0
assert p["Jame"]["by_phase"]["preplant"] > 0
assert p["Jame"]["by_phase"]["preplant"] == max(p["Jame"]["by_phase"].values())
eligible = sorted((n for n,v in p.items() if v["maps"] >= 60),key=lambda n:-p[n]["swing_per_map"])
assert "m0NESY" in eligible[:10], "Revise 'one of the strongest' claim"
original = json.loads((ROOT / "data/players.json").read_text(encoding="utf-8"))
opening = next(v["opening_kill_pct"] for v in original if v["player"]=="donk")
assert 18 <= opening <= 22, "Revise 'one in five' opening-kill claim"
receipt = {"passed":True,"coverage":d["coverage"],"donk_original_fullbuy_opening_pct":opening,
    "featured":{n:p[n] for n in ("donk","sh1ro","zont1x","nilo","Brollan","susp","ZywOo","Jame","m0NESY","910","karrigan")},
    "validation":d["validation"],"limits":d["limitations"]}
(ROOT / "research/claims_v4_verified.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding="utf-8")
print("All statistical narration claims verified",d["coverage"])
