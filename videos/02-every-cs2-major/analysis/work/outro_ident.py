"""Channel signature outro: "This is... Sports On The Line." (Christopher) with sound design, three styles.

Edge TTS reports word boundaries, so the impact lands exactly on "Line".
Output: work/voice_samples/ident_<style>.wav (48 kHz stereo, -14 LUFS) + ALL_ident_samples.mp3
"""
import asyncio, pathlib, subprocess, sys
import edge_tts

FF = r"EDIT_ME\ffmpeg\bin\ffmpeg.exe"
# ---- EDIT ME: network proxy ----------------------------------------------------
# I reach YouTube / Twitch / Edge TTS through a local proxy. If you need one too, put
# its URL here, e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None


def network_hint(what):
    print(f"\n[network] {what} failed. If your connection needs a proxy, set PROXY in the "
          f"EDIT ME block at the top of {pathlib.Path(__file__).name} (now: {PROXY!r}).", file=sys.stderr)
# ---------------------------------------------------------------------------------
HERE = pathlib.Path(__file__).parent
SFX = HERE / "sfx"
OUT = HERE / "voice_samples"
TEXT = "This is... Sports On The Line."


async def tts(path):
    """Christopher, slower and lower; returns {word: start_seconds}."""
    com = edge_tts.Communicate(TEXT, "en-US-ChristopherNeural", rate="-12%", pitch="-8Hz", proxy=PROXY,
                               boundary="WordBoundary")
    marks, audio = {}, bytearray()
    try:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
            elif chunk["type"] == "WordBoundary":
                marks[chunk["text"].strip(".")] = chunk["offset"] / 1e7  # 100-ns units
    except Exception as e:
        network_hint(f"Edge TTS ({type(e).__name__}: {e})")
        raise
    path.write_bytes(bytes(audio))
    return marks


def ff(*args):
    subprocess.run([FF, "-v", "error", "-y", *map(str, args)], check=True)


# Voice chains. All: high-pass, compression, low-end + presence EQ. Then a style-specific space.
BASE = ("highpass=f=70,acompressor=threshold=-20dB:ratio=4:attack=5:release=120:makeup=4,"
        "equalizer=f=120:t=q:w=1:g=4,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=7000:t=q:w=2:g=-2")
STYLES = {
    # big hall tail, slow build, low boom on "Line"
    "cinematic": dict(voice=BASE + ",aecho=0.8:0.7:70|140|230:0.30|0.20|0.12", pre="reverse-cymbal-2s.wav", pre_lead=1.7,
                      hits=[("stinger-serious-low.wav", 0.0, 1.0), ("dry-thud.wav", 0.0, 0.8)], width_ms=14),
    # tight slap echo, whoosh in, punchy hit
    "esports": dict(voice=BASE + ",aecho=0.8:0.5:45:0.25", pre="whoosh-reverse-1s.wav", pre_lead=0.95,
                    hits=[("stinger-hit-short.wav", -0.02, 1.0), ("dry-thud.wav", 0.0, 1.0)], width_ms=9),
    # clean, light room, energetic hit after the line
    "broadcast": dict(voice=BASE + ",aecho=0.8:0.4:35|60:0.15|0.08", pre="riser-short-2s.wav", pre_lead=1.6,
                      hits=[("stinger-energetic-hit.wav", 0.05, 0.9)], width_ms=0),
}


def build(name, cfg, voice_mp3, line_t):
    lead = cfg["pre_lead"]
    inputs = ["-i", voice_mp3, "-i", SFX / cfg["pre"]]
    for f, *_ in cfg["hits"]:
        inputs += ["-i", SFX / f]
    vd = f"[0:a]aresample=48000,{cfg['voice']},pan=stereo|c0=c0|c1=c0"
    if cfg["width_ms"]:  # Haas double for width: right channel slightly delayed and quieter
        vd += f",asplit[vl][vr];[vr]adelay=0|{cfg['width_ms']},volume=0.85[vr2];[vl][vr2]amix=inputs=2:normalize=0"
    vd += f",adelay={int(lead * 1000)}|{int(lead * 1000)}[v]"
    parts = [vd, f"[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.8[pre]"]
    mix = "[v][pre]"
    for k, (f, off, vol) in enumerate(cfg["hits"], start=2):
        t = int((lead + line_t + off) * 1000)
        parts.append(f"[{k}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={vol},adelay={t}|{t}[h{k}]")
        mix += f"[h{k}]"
    n = 2 + len(cfg["hits"])
    graph = ";".join(parts) + f";{mix}amix=inputs={n}:normalize=0,afade=t=out:st={lead + line_t + 2.2}:d=1.0," \
                              f"loudnorm=I=-14:TP=-1.0:LRA=7[out]"
    out = OUT / f"ident_{name}.wav"
    ff(*inputs, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", "-t", f"{lead + line_t + 3.3:.2f}", out)
    return out


def main():
    OUT.mkdir(exist_ok=True)
    voice = OUT / "ident_voice_raw.mp3"
    marks = asyncio.run(tts(voice))
    line_t = marks.get("Line")
    print("word starts:", marks)
    outs = [build(n, c, voice, line_t) for n, c in STYLES.items()]
    ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "1.0", OUT / "gap_st.wav")
    lst = OUT / "ident_concat.txt"
    lst.write_text("".join(f"file '{o.name}'\nfile 'gap_st.wav'\n" for o in outs), encoding="utf-8")
    ff("-f", "concat", "-safe", "0", "-i", lst, "-b:a", "192k", OUT / "ALL_ident_samples.mp3")
    print([o.name for o in outs])


if __name__ == "__main__":
    main()
