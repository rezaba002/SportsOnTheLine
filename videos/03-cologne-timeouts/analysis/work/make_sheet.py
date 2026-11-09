"""Recording sheet for video 03 (same layout as video 02's): one card per paragraph, emphasis + delivery cues +
pronunciations. Reads work/narration/narration.json (for Brian's timing) and the cue text below.
Output: D:\\Youtube\\video03\\recording_sheet.html
"""
import html, json, pathlib

HERE = pathlib.Path(__file__).parent
NAR = json.loads((HERE / "narration" / "narration.json").read_text(encoding="utf-8"))
LEX = json.loads((HERE / "lexicon.json").read_text(encoding="utf-8"))

# Paragraph text with **emphasis** and [cues]; must say the same words as script_v1.md.
CUED = {
 "p01": "[punchy, short] **Five rounds down.** [beat] **Timeout.** [beat] **Five rounds won.** [pause] That's the timeout that turned the game, [up] right? [pause] [doubtful] Or **was it?**",
 "p13": "[tense, measured] **Thirty seconds.** [beat] That's all a coach gets to save a game. [pause] At the Cologne Major, they took **four hundred and thirty** of them. [build] The **champions** did it. The **runners-up** did it. [pause] And one team... [beat] [deadpan] brought a **frog.** [pause] [slower, title voice] So, are timeouts **useless?** [beat] I checked **all four hundred and thirty**, at the Cologne Major.",
 "p12": "[playful, quick] Aurora. [beat] FURIA. [beat] The champions, **Falcons.** [beat] And Spirit's coach... [pause] is a **frog.** [pause] [slower, title voice] Are timeouts **useless?** [beat] I checked **all four hundred and thirty**, at the Cologne Major.",
 "p02": "A tactical timeout is **thirty seconds** where the coach finally gets to talk. Three per team, one more in every overtime. [pause] And here's the detail most people forget: [beat] during **any** timeout, **both** coaches talk.",
 "p03": "I pulled every round from the official demos. [build] One hundred and three maps, two thousand two hundred and fifty-five rounds, every buy, every timeout.",
 "p04": "So, which coach's timeouts worked **best?** Here are all sixteen teams. [pause] On top, Monte's coach **kakafu**: after his timeouts, Monte won their next gun round **fifteen points** more often. At the bottom, B8, PARIVISION and the MongolZ. [pause] kakafu's timeouts look like **magic.** [beat] [lower] Hold that thought.",
 "p05": "Two teams played **without a coach.** Spirit's hally was in hospital, and their second coach was refused a visa. And Legacy's coach was **banned** mid-event, [beat] for a **thumbs-up** after a timeout. [pause] Watch what happened. Spirit called **nine** timeouts in fourteen maps. Their opponents, on the same fourteen maps: [beat] **forty-seven.** Legacy went from four to six timeouts a match, [beat] to **one.** [pause] Why? With no coach, your timeout gives **their** coach thirty free seconds.",
 "p06": "So timeouts must matter. After losing a round, teams that call one win the next round **forty-three** percent of the time. Teams that don't: **thirty-four.** [beat] **Nine points.** [pause] [smug] Case closed?",
 "p07": "[quick] Not so fast. Look at the **money.** Eight in ten teams that call a timeout are about to **full-buy.** Teams that don't are often **saving**: only about half of them full-buy. A rifle beats a pistol. [beat] That's not the coach. [pause] And losing streaks end **on their own**: every lost round, the loss bonus gets bigger.",
 "p08": "So I compared **fair fights.** Same score, same streak, same money, same teams, next gun round. [pause] Timeout versus no timeout: [slower] minus zero point seven. [beat] **Nothing.** [pause] And it's not hiding in the plan either. Opening duels, grenades, bomb site, plant timing: [beat] **no change.**",
 "p09": "Now, **kakafu.** If every coach's timeouts were pure **coin flips**, how good would the best coach look? I ran it **ten thousand** times. The luckiest coach usually looks **even better**: [beat] plus **twenty-one.** [pause] Three of these tables are luck. One is real. [slower] Can you tell which?",
 "p10": "So, are timeouts useless? [pause] For the next round, at this Major, the data can't find **anything.** [beat] But two teams without a coach **stopped calling them.** Maybe the thirty seconds matter in a way the scoreboard **can't see.** [pause] Singapore starts November twenty-fifth. My prediction: [beat] the top of this table **won't stay on top.**",
 "p11": "Who's the best timeout caller in CS? [smile] Tell me in the comments.",
}
SAY = {  # pronunciations to show under a paragraph, from the lexicon (script word -> spoken)
    k: v for g in ("players", "teams", "terms") for k, v, *_ in LEX[g]}


def fmt(s):
    s = html.escape(s)
    out, bold = "", False
    for part in s.split("**"):
        out += (("<b>" if bold else "") + part + ("</b>" if bold else "")) if out or part else ""
        bold = not bold
    import re
    return re.sub(r"\[([^\]]+)\]", r"<i>[\1]</i>", out)


def main():
    cards = []
    for p in sorted(NAR, key=lambda p: (p["id"] not in ("p13", "p12"), p["id"] != "p13", p["id"])):
        cued = CUED[p["id"]]
        plain = __import__("re").sub(r"\[[^\]]+\]\s*|\*\*", "", cued).replace("  ", " ").strip()
        assert plain.split() == p["text"].split(), f"{p['id']}: cued text differs from the script\n{plain}\n{p['text']}"
        says = [f"<b>{html.escape(k)}</b> = “{html.escape(v)}”" for k, v in SAY.items()
                if k != v and k.lower() in p["text"].lower()]
        cards.append(f'<section><div class="id">{p["id"].upper()} <span>{html.escape(p["section"])} · Brian took '
                     f'{p["duration"]:.0f}s</span></div><p>{fmt(cued)}</p>'
                     + (f'<div class="say">say: {" · ".join(says)}</div>' if says else "") + "</section>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Recording sheet</title><style>:root{{--bg:#111;--fg:#f2f0ea;--mut:#9a9aa3;--acc:#ffd23f}}
body{{background:var(--bg);color:var(--fg);font:22px/1.55 system-ui,sans-serif;margin:0 auto;padding:16px;max-width:820px}}
h1{{font-size:26px}} .tips{{color:var(--mut);font-size:17px}} section{{border-top:1px solid #333;padding:14px 0}}
.id{{color:var(--acc);font-weight:700;font-size:18px}} .id span{{color:var(--mut);font-weight:400}}
b{{color:var(--acc)}} i{{color:#7fd1ff;font-style:normal;font-size:16px}} .say{{color:var(--mut);font-size:16px}}</style></head><body><h1>Video 03 · recording sheet</h1><div class="tips">“Are timeouts useless? I checked all 430 at the Cologne Major.” Record each paragraph as its own file, named <b>p13</b> (opener, option B) or <b>p12</b> (opener, option A), and <b>p01</b> … <b>p11</b> (a phone voice memo is fine). Re-take a paragraph as often as you like and keep the best one. Quiet room, phone 15–20 cm from your mouth, same spot every time. <b>Yellow</b> = lean on it. <i>[pause] [beat] [build] [slower]</i> = delivery cues, not read aloud. Numbers are written as you should say them. Tone: tense, investigative, a little playful on the twists. Total ≈ 3 minutes. The closing ident is Christopher's, so it's not on this sheet.</div>{"".join(cards)}</body></html>"""
    out = HERE.parent / "recording_sheet.html"
    out.write_text(page, encoding="utf-8")
    print(f"{len(cards)} paragraphs -> {out}")


if __name__ == "__main__":
    main()
