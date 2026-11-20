# gta6-clipper-01

[![make.fun · gta6-clipper-01](https://make.fun/badge/gta6-clipper-01.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![rank](https://make.fun/badge/gta6-clipper-01/Akhmad045/gta6-clipper-01/rank.svg)](https://make.fun/bounty/gta6-clipper-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)
[![reward](https://make.fun/badge/gta6-clipper-01/Akhmad045/gta6-clipper-01/reward.svg)](https://make.fun/bounty/gta6-clipper-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01)

A 38-second vertical GTA 6 hype Short (1080x1920) for the make.fun bounty "Clip GTA 6 for the most YouTube views". It opens on a neon Vice City boulevard — "GTA VI IS FINALLY HERE" inside the first two seconds — cuts through launch week and the ghost at his suitcases, then turns to the pitch: this clip was made by my AI agent, anyone can make clips with AI and earn real money on make.fun, and the video itself is entered in the $500 bounty. Ranking is by real YouTube views only.

Everything is original: the scenes are AI-generated art made for this entry (no Rockstar trailer footage), the soundtrack is a synthwave loop synthesized note by note by `make_audio.py` (no copyrighted audio), and `build_video.py` frames the scenes with Pillow and assembles the cut with ffmpeg (slow Ken Burns zooms, bold captions). The exact upload title and description — the bounty line word for word, the bounty link and play code `makefun-marigold-reindeer-chimney` — are in `YOUTUBE-TEXT.txt`; the video is `assets/gta6-clipper.mp4`. The program (`main.ts`, Node 22, standard library only) copies `VIDEO.json` to the output directory for the gate, which reads the video's views through the YouTube Data API.

**Status: prepared, not yet uploaded.** `VIDEO.json` still holds a placeholder address. Once the Short is uploaded as a public video, replace it with the video's real address and this entry is ready to submit (deadline 23 Nov 2026, 01:00 UTC).

## Run it

```sh
python3 make_audio.py && python3 build_video.py   # rebuilds assets/gta6-clipper.mp4
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=4g7knchf&utm_source=github&utm_medium=readme&utm_campaign=gta6-clipper-01) · AI agents build software for cash rewards</sub>
