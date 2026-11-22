# SportsOnTheLine: code and data

The analysis and graphics code behind the [SportsOnTheLine](https://www.youtube.com/@SportsOnTheLine) YouTube channel: data-driven Counter-Strike 2 videos that check the numbers behind the debates.

Each video has its own folder with the scripts I ran and the derived tables behind the numbers on screen. The animated graphics are made with [Remotion](https://www.remotion.dev/) and are in [`graphics/`](graphics).

| # | Video | Code and data |
|---|---|---|
| 02 | [Every CS2 Major So Far: The Must-Watch Recap Before Singapore 2026](https://youtu.be/dr_DOWp8eg8) | [videos/02-every-cs2-major](videos/02-every-cs2-major) |
| 03 | [Are CS2 timeouts useless? I Checked all 430 timeouts from Cologne Major 2026](https://youtu.be/pUSPR1zwcZc) | [videos/03-cologne-timeouts](videos/03-cologne-timeouts) |
| 04 | [Do Pistol Rounds Decide CS2 maps? I Checked Every Major](https://youtu.be/Vjlev_o5zDY) | [videos/04-pistol-rounds](videos/04-pistol-rounds) |
| 05 | [How the Singapore Major 2026 Invites Were Decided (and Who Dropped Out)](https://youtu.be/YKWjoljq4JY) | [videos/05-singapore-major-invites](videos/05-singapore-major-invites) |
| 07 | [Which CS2 Transfer Actually Worked?](https://youtu.be/zwpl93MQuU4) | [videos/07-roster-moves](videos/07-roster-moves) |
| 08 | [The Smallest Country Dominating CS2](https://youtu.be/lCIl8yoWiUg) | [videos/08-smallest-country-cs2](videos/08-smallest-country-cs2) |
| 09 | [Singapore Major: 3 Players You Shouldn’t Overlook](https://youtu.be/C_JbnVVSQGY) | [videos/09-singapore-major-players](videos/09-singapore-major-players) |
| 10 | [Predicting The Singapore Major Champion Using Data !](https://youtu.be/iA88kOETvlA) | [videos/10-singapore-major-contenders](videos/10-singapore-major-contenders) |
| 11 | [Stage 1 Simulated 100,000 Times / Honest Singapore Major Pick’Em](https://youtu.be/Zf1xwtK5IjQ) | [videos/11-singapore-pickem](videos/11-singapore-pickem) |

New videos are added here when they go live.

## What's here and what isn't

- **Included:** Python analysis scripts, the Remotion source, and derived data (counts, rates, simulation outputs).
- **Not included:** match footage, narration audio, team logos, player photos, fonts, sound effects, and raw scraped pages. They are large, and most of them belong to someone else. The scripts show where each piece came from.
- The scripts were written to run on my machine, so file paths point to `D:/Youtube/...`. Read them as a record of the method, not a packaged tool.
- Scripts that go online (YouTube, Twitch, Edge TTS) have an **EDIT ME** block at the top for a network proxy. Leave it as `None` to connect directly. If a request fails, the script tells you to check that block.

## Sources

Match and player data come from HLTV, bo3.gg, Liquipedia and Valve's public [VRS standings](https://github.com/ValveSoftware/counter-strike_regional_standings). The fetch scripts in each video folder show which source each number came from.

## Using this

Code is under the [MIT license](LICENSE). Derived data is under [CC BY 4.0](LICENSE-data), so you can reuse it with credit. To cite this repository, use the "Cite this repository" button (it reads [CITATION.cff](CITATION.cff)).

Reza Baghestani
