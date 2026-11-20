#!/usr/bin/env python3
"""Synthesize the original soundtrack for the gta6-clipper-01 Short.

A 38-second synthwave loop at 122 BPM in A minor (Am - F - C - G), built
from first principles with numpy: pitch-dropping kick, noise hats and clap,
a harmonic bass on eighth notes, a plucked arpeggio over the chord tones and
a soft pad. No samples, no copyrighted audio. Output: assets/soundtrack.wav
(44.1 kHz, stereo, 16-bit).
"""
import math
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "assets", "soundtrack.wav")

SR = 44100
DURATION = 38.0
BPM = 122.0
BEAT = 60.0 / BPM
BAR = BEAT * 4

# A minor progression, one chord per bar: root freq + chord tones (Hz)
CHORDS = [
    (55.00, [220.00, 261.63, 329.63]),   # Am
    (43.65, [174.61, 220.00, 261.63]),   # F
    (65.41, [196.00, 261.63, 329.63]),   # C
    (49.00, [196.00, 246.94, 293.66]),   # G
]

rng = np.random.default_rng(20261120)
n = int(SR * DURATION)
t = np.arange(n) / SR
mix = np.zeros((n, 2), dtype=np.float64)


def add(start, wave_mono, gain=1.0, pan=0.0):
    """Mix a mono segment into the stereo buffer at `start` seconds."""
    i0 = int(start * SR)
    i1 = min(n, i0 + len(wave_mono))
    if i0 >= n or i1 <= i0:
        return
    seg = wave_mono[: i1 - i0] * gain
    mix[i0:i1, 0] += seg * (1.0 - max(pan, 0.0))
    mix[i0:i1, 1] += seg * (1.0 + min(pan, 0.0))


def env(length, attack=0.002, decay=8.0):
    tt = np.arange(length) / SR
    return np.exp(-decay * tt) * np.minimum(1.0, tt / max(attack, 1e-4))


def kick():
    length = int(0.14 * SR)
    tt = np.arange(length) / SR
    freq = 42 + 90 * np.exp(-38 * tt)
    phase = np.cumsum(freq) / SR * 2 * np.pi
    return np.sin(phase) * env(length, decay=16.0)


def hat(open_=False):
    length = int((0.09 if open_ else 0.035) * SR)
    noise = rng.standard_normal(length)
    # crude high-pass: difference of the noise with itself shifted
    hp = np.diff(np.concatenate(([0.0], noise)))
    return hp * env(length, decay=(26 if open_ else 60))


def clap():
    length = int(0.11 * SR)
    noise = rng.standard_normal(length)
    return noise * env(length, decay=30.0) * 0.7


def bass_note(freq, dur):
    length = int(dur * SR)
    tt = np.arange(length) / SR
    tone = (np.sin(2 * np.pi * freq * tt)
            + 0.45 * np.sin(2 * np.pi * freq * 2 * tt)
            + 0.18 * np.sin(2 * np.pi * freq * 3 * tt))
    return tone * env(length, decay=5.5) / 1.63


def pluck(freq, dur=0.22):
    length = int(dur * SR)
    tt = np.arange(length) / SR
    tone = (np.sin(2 * np.pi * freq * tt)
            + 0.35 * np.sin(2 * np.pi * freq * 2 * tt))
    return tone * env(length, decay=13.0) / 1.35


def pad(freqs, dur):
    length = int(dur * SR)
    tt = np.arange(length) / SR
    tone = sum(np.sin(2 * np.pi * f * tt) for f in freqs) / len(freqs)
    swell = np.minimum(1.0, tt / 0.4) * np.minimum(1.0, (dur - tt) / 0.4)
    return tone * swell


KICK, HAT, HAT_O, CLAP = kick(), hat(), hat(True), clap()

bars = int(DURATION / BAR) + 1
for bar_i in range(bars):
    bar_start = bar_i * BAR
    root, tones = CHORDS[bar_i % len(CHORDS)]
    # pad under the whole bar
    add(bar_start, pad(tones, BAR), gain=0.10)
    for beat_i in range(4):
        bt = bar_start + beat_i * BEAT
        add(bt, KICK, gain=0.85)
        add(bt + BEAT / 2, HAT, gain=0.20)
        if beat_i in (1, 3):
            add(bt, CLAP, gain=0.30)
        # bass on eighth notes, root-root-octave pattern
        for e in range(2):
            f = root * (2 if e == 1 and beat_i % 2 == 1 else 1)
            add(bt + e * BEAT / 2, bass_note(f, BEAT / 2), gain=0.42)
        # arpeggio on sixteenths, cycling chord tones + octave colour
        arp = tones + [tones[0] * 2, tones[1] * 2]
        for s in range(4):
            f = arp[(bar_i * 3 + beat_i * 4 + s) % len(arp)]
            add(bt + s * BEAT / 4, pluck(f), gain=0.16,
                pan=0.25 if s % 2 else -0.25)
    add(bar_start + BAR - BEAT / 2, HAT_O, gain=0.10)

# gentle master: soft clip, normalise, fade the tail out
mix = np.tanh(mix * 1.1)
peak = np.max(np.abs(mix))
if peak > 0:
    mix *= 0.82 / peak
fade_len = int(2.5 * SR)
mix[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)[:, None]
mix[: int(0.05 * SR)] *= np.linspace(0.0, 1.0, int(0.05 * SR))[:, None]

pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT_PATH, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {OUT_PATH} ({DURATION:.0f}s, {BPM:.0f} BPM)")
