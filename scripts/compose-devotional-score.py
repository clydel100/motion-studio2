#!/usr/bin/env python3
"""Original 15-second score for the Be Made Whole devotional promo.

Composed from scratch (no samples, no stock music), so it is free to use on
YouTube, Instagram, TikTok, Facebook and the website.

Warm string-like pad + soft piano, in D major, timed to the video:
  0.0-3.4  opening question      Bm9, sparse piano
  3.4-6.4  the three words       Gmaj7 -> Asus4, a rising note on each word
  6.4-9.9  cover reveal          Dadd9 opens up, gentle shimmer
  9.9-15   quote + call to action Gmaj9 -> D, calm resolve and fade

Usage: python3 scripts/compose-devotional-score.py [out.wav]
"""
import sys
import wave
import numpy as np

SR = 48000
DUR = 15.0
N = int(SR * DUR)
t_all = np.arange(N) / SR
rng = np.random.default_rng(7)  # fixed seed: same file every time


def midi(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    name, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[name] + 12 * (octave + 1) - 69) / 12)


def envelope(n, attack, release, total):
    """Linear-in-dB-ish smooth envelope over n samples."""
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1) ** 2 if attack > 0 else np.ones(n)
    r = np.clip((total - t) / release, 0, 1) ** 2 if release > 0 else np.ones(n)
    return a * r


def add(buf, start, sig, pan=0.0):
    """Mix a mono signal into the stereo buffer at time `start` with constant-power pan."""
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[0, i : i + len(sig)] += sig * l
    buf[1, i : i + len(sig)] += sig * r


def pad_voice(freq, length, attack=1.4, release=1.6):
    """Soft string-like tone: detuned voices with gently rolled-off harmonics and slow vibrato."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for detune in (-0.0035, 0.0, 0.0035):
        f = freq * (1 + detune)
        vib = 1 + 0.0018 * np.sin(2 * np.pi * 4.8 * t + rng.uniform(0, 6.28))
        phase = 2 * np.pi * np.cumsum(f * vib) / SR
        for h, amp in ((1, 1.0), (2, 0.38), (3, 0.16), (4, 0.07), (5, 0.03)):
            out += amp * np.sin(h * phase + rng.uniform(0, 6.28))
    return out / 3 * envelope(n, attack, release, length)


def piano(freq, length=3.5, vel=1.0):
    """Soft felt-piano tone: quick attack, warm harmonics that fade faster than the fundamental."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h, amp, decay in ((1, 1.0, 1.6), (2, 0.42, 0.9), (3, 0.18, 0.6), (4, 0.08, 0.4), (6, 0.03, 0.25)):
        inharm = h * (1 + 0.0004 * h * h)
        out += amp * np.exp(-t / decay) * np.sin(2 * np.pi * freq * inharm * t)
    attack = np.clip(t / 0.006, 0, 1)
    tail = np.clip((length - t) / 0.4, 0, 1)
    return vel * out * attack * tail


def bell(freq, length=4.0, vel=1.0):
    """Very soft high shimmer for the cover reveal."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.5)
    return vel * out * np.exp(-t / 1.8) * np.clip(t / 0.02, 0, 1) * np.clip((length - t) / 0.5, 0, 1)


buf = np.zeros((2, N))

# ---- Pad chords (start, end, bass, voicing) ----
CHORDS = [
    (0.0, 3.6, "B1", ["B3", "D4", "F#4", "A4", "C#5"]),        # Bm9: the question
    (3.3, 5.3, "G1", ["G3", "B3", "D4", "F#4"]),               # Gmaj7: confession, repentance
    (5.0, 6.7, "A1", ["A3", "D4", "E4", "A4"]),                # Asus4: transformation (lift)
    (6.4, 10.1, "D2", ["D3", "A3", "E4", "F#4", "A4"]),        # Dadd9: cover reveal opens up
    (9.8, 12.7, "G1", ["B3", "D4", "F#4", "A4"]),              # Gmaj9: the quote
    (12.4, 15.0, "D2", ["D3", "A3", "D4", "F#4", "A4"]),       # D: resolve under the call to action
]
for start, end, bass, notes in CHORDS:
    length = end - start + 1.2
    for k, nname in enumerate(notes):
        pan = -0.5 + k / max(1, len(notes) - 1)
        add(buf, start, 0.055 * pad_voice(midi(nname), length), pan * 0.7)
    add(buf, start, 0.11 * pad_voice(midi(bass), length, attack=1.8, release=1.8))

# ---- Piano: sparse, each note lands on a visual moment ----
PIANO = [
    (0.35, "B4", 0.55), (1.55, "F#4", 0.45), (2.45, "A4", 0.40),   # question lines
    (3.45, "F#5", 0.60), (4.25, "A5", 0.60), (5.05, "D6", 0.62),   # one note per word, rising
    (6.40, "D5", 0.55), (6.42, "A5", 0.45),                        # cover appears
    (7.10, "F#5", 0.42), (7.80, "E5", 0.36),                       # title, author
    (9.90, "B4", 0.50), (10.60, "D5", 0.44), (11.20, "F#5", 0.46), # quote, attribution, call to action
    (12.40, "A4", 0.40), (12.42, "D5", 0.40),                      # resolve
]
for start, nname, vel in PIANO:
    add(buf, start, 0.20 * piano(midi(nname), vel=vel), pan=rng.uniform(-0.3, 0.3))

# ---- Shimmer as the cover is lit ----
for start, nname, pan in ((6.55, "A6", -0.4), (7.0, "E6", 0.4), (7.6, "F#6", 0.0)):
    add(buf, start, 0.035 * bell(midi(nname)), pan)

# ---- Reverb: convolve with a smooth, decaying stereo noise tail ----
ir_len = int(2.8 * SR)
ir_t = np.arange(ir_len) / SR
ir = rng.standard_normal((2, ir_len)) * np.exp(-ir_t / 0.75)
# soften the reverb's high end with a short moving average
k = 24
ir = np.array([np.convolve(ch, np.ones(k) / k, mode="same") for ch in ir])
ir[:, : int(0.012 * SR)] = 0  # small pre-delay
ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
size = 1 << int(np.ceil(np.log2(N + ir_len)))
wet = np.array([np.fft.irfft(np.fft.rfft(buf[c], size) * np.fft.rfft(ir[c], size), size)[:N] for c in range(2)])
mix = 0.72 * buf + 0.42 * wet

# ---- Master: gentle fade in/out, soft limit, normalize ----
fade = np.clip(t_all / 0.8, 0, 1) * np.clip((DUR - t_all) / 1.6, 0, 1) ** 1.5
mix *= fade
mix = np.tanh(mix * 1.4) / 1.4
peak = np.abs(mix).max()
mix *= 10 ** (-5.5 / 20) / peak  # peak at -5.5 dBFS (about -16 LUFS: a soft bed)

out = sys.argv[1] if len(sys.argv) > 1 else "audio/devotional-score.wav"
pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"Wrote {out} ({DUR:.1f}s, {SR} Hz stereo)")
