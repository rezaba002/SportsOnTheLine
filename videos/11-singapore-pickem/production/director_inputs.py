"""Prepare the director's edition separately from the B2/B3 review cut."""
import asyncio
import hashlib
import json
import math
import pathlib
import sys

# ---- EDIT ME: network proxy for Edge TTS -----------------------------------------
# If you need a proxy to reach Microsoft's speech service, put its URL here,
# e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None

WORK = pathlib.Path(__file__).resolve().parent
ROOT = WORK.parents[1]
PUBLIC = ROOT / "sotl-graphics/public"
CUT = WORK / "director"
FINAL = WORK.parent / "final"
CUT.mkdir(exist_ok=True)
FINAL.mkdir(exist_ok=True)


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


async def prepare():
    sys.path.insert(0, str(ROOT / "video09/work/vendor"))
    import edge_tts
    tl = read(PUBLIC / "video11/timeline.json")
    changed = {
        "s1": "Sixteen teams. Ten picks. And the best ticket our search found still fails about two times out of three. This is our Stage one pick em for the Singapore Major. We'll show you the model's ticket, my ticket, and exactly what it costs to trust your eye.",
        "s2": "We started with two thousand six hundred and nineteen maps from the invited teams. May third to November fifteenth. We paired those results with Valve's November second standings, roster changes, and the expected lineups' career LAN maps and Major titles.",
        "s3": "A map played twenty-one days ago gets half the weight of a map played today. Each team starts from its Valve ranking. Maps before a roster change count less, and a map-specific edge needs evidence. Then come the vetoes, the early best of ones, and the best of threes when advancement or elimination is on the line. On the twenty series we held back, the model called fourteen right. Its log loss was zero point six two, against zero point six nine for a coin flip. Lower is better. We tested an experience layer, too. It didn't earn its way into the published forecast. The ticket you're about to see uses the results-only baseline.",
        "s5": "The three and oh table. One hundred Thieves leads at twenty-seven percent. Ninjas in Pyjamas and Heroic follow at twenty-three and twenty-one. After the top eight, every sweep chance is in single digits. Only Imperial and Chinggis Warriors are below five percent.",
        "s7": "Now look at three and two. The top ten teams sit between nineteen and twenty-three percent. Just over four percentage points separate first from tenth. The bottom six fall away, but inside that top group, the model gives us very little reason to prefer one team over another.",
        "s10": "Now, my ticket. Nine of the same teams, but two trade places. Ninjas in Pyjamas takes a three and oh slot over Heroic. The model already gives the Ninjas a higher sweep chance, and I trust their core. Heroic still advances on my ticket. Then one team changes: Den-deh-leh out, nine zee in. Den-deh-leh's chance of advancing swings from forty-nine to fifty-seven percent across settings. They open against Paree-vision. Nine zee opens against Lynn Vision, the lowest seed. What does the eye test cost? Thirty-one point nine percent becomes twenty-eight point eight. About three percentage points for going my own way. Lock your ten picks in the comments. Mine, the model's, or your own. We'll grade them after Stage one.",
        "s11": "Before you lock in: the standings are from November second. Results stop November fifteenth. Keep the ticket fixed and change the model's recency settings: the chance of completing the stage runs from thirty-two to forty-one percent. That's sensitivity to the model, not a confidence interval. The full method is in the description.",
    }
    cursor = 0
    for s in tl["scenes"]:
        sid = s["id"]
        if sid in changed:
            text = changed[sid]
            digest = hashlib.sha256(text.encode()).hexdigest()[:12]
            audio = CUT / f"{sid}-{digest}.mp3"
            meta = audio.with_suffix(".json")
            if not audio.exists() or not meta.exists():
                for proxy in [PROXY, None] if PROXY else [None]:
                    async def fetch():
                        data, marks = bytearray(), []
                        talk = edge_tts.Communicate(text, "en-US-BrianNeural", rate="+3%", boundary="WordBoundary", proxy=proxy)
                        async for event in talk.stream():
                            if event["type"] == "audio":
                                data.extend(event["data"])
                            elif event["type"] == "WordBoundary":
                                marks.append(dict(w=event["text"], s=event["offset"]/1e7, e=(event["offset"]+event["duration"])/1e7))
                        if not data or not marks:
                            raise RuntimeError("Empty take")
                        audio.write_bytes(data)
                        write(meta, marks)
                    try:
                        await asyncio.wait_for(fetch(), 50)
                        break
                    except Exception as exc:
                        print(sid, type(exc).__name__, flush=True)
                else:
                    raise RuntimeError(f"Brian unavailable for {sid}")
            s.update(words=read(meta), text=text, file=str(audio))
        else:
            s["file"] = str(PUBLIC / s["audio"])
        s["leadFrames"] = 8
        s["frames"] = s["leadFrames"] + math.ceil(s["words"][-1]["e"]*30) + (135 if sid=="s12" else 38 if sid in ("s5","s6","s7","s8","s9") else 22)
        s.update(fromFrame=cursor, audioStart=cursor+s["leadFrames"])
        cursor += s["frames"]
        print(sid, s["frames"], flush=True)
    tl["frames"] = cursor
    write(CUT/"edit.json", tl)


if __name__ == "__main__":
    asyncio.run(prepare())
