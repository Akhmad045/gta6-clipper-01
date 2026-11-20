// gta6-clipper-01 entry program (Node 22, standard library only).
//
// The entry itself is a public YouTube Short: a 38-second vertical GTA 6
// hype clip cut from original art by my agent (build_video.py in this
// repository), with an original synth soundtrack (make_audio.py). Its
// description carries the bounty's line, the bounty link and my play code,
// and the ranking is the video's real view count as YouTube reports it.
// This program's whole job is to hand the video's address to the grader:
// it reads VIDEO.json at the repository root, sanity-checks the address,
// and copies the file to the output directory, where the gate picks it up
// and reads the video through the YouTube Data API.
//
// Local run (the grader's /bot and /output are replaced by two env vars):
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const LINK_FILE = 'VIDEO.json';

// A YouTube video address: a Shorts or watch URL, or the short youtu.be
// form; the id is 11 characters of letters, digits, "-" and "_".
const VIDEO_URL =
  /^https:\/\/(www\.|m\.)?youtube\.com\/(shorts\/|watch\?v=)[A-Za-z0-9_-]{11}(?:[?&#].*)?$|^https:\/\/youtu\.be\/[A-Za-z0-9_-]{11}(?:[?#].*)?$/;

function readLink(): string {
  const raw = readFileSync(join(BOT_DIR, LINK_FILE), 'utf8');
  const data = JSON.parse(raw) as { url?: unknown };
  if (typeof data.url !== 'string' || data.url.length === 0) {
    throw new Error(`${LINK_FILE} must be a JSON object with a "url" string`);
  }
  return data.url;
}

function main(): void {
  const url = readLink();
  if (!VIDEO_URL.test(url)) {
    // Not fatal here: the placeholder that ships before the upload exists
    // has this shape too. The gate on the site is the judge of the address.
    console.error(`warning: ${url} is not a finished YouTube address yet`);
  }
  mkdirSync(OUTPUT_DIR, { recursive: true });
  copyFileSync(join(BOT_DIR, LINK_FILE), join(OUTPUT_DIR, LINK_FILE));
  console.log(`${LINK_FILE}: ${url}`);
  console.log(`copied to ${join(OUTPUT_DIR, LINK_FILE)}`);
}

try {
  main();
} catch (err) {
  console.error(`gta6-clipper-01: ${(err as Error).message}`);
  process.exit(1);
}
