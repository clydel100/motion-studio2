#!/usr/bin/env python3
"""Original 15-second score for videos/showreel.html (the motion design reel).

Composed from scratch in code (no samples, no stock music), so it is free to use anywhere.
120 BPM (one beat = 0.5 s), every hit lands on a visual cut:
  0.0-1.0   riser into the ignition burst          (impact at 1.0)
  2.0-4.0   kinetic type: a stab on every word      TYPE. SHAPE. SPACE. TIME. + glitch stutter
  4.0-6.0   geometry: four-on-the-floor + arp, riser into the zoom
  6.0-8.0   3D: hit, sparkles on each shape morph
  8.0-10.0  particles: whoosh into the word, riser, explosion at 9.45
  10.0-11.85 data: full groove, snare roll build
  11.85-15  finale: huge hit, drums drop out, warm resolve to F major

Usage: python3 scripts/compose-showreel-score.py [out.wav]
"""
import sys
import wave
import numpy as np

SR = 48000
DUR = 15.0
N = int(SR * DUR)
BEAT = 0.5
rng = np.random.default_rng(1125)  # fixed seed: same file every time
buf = np.zeros((2, N))


def hz(note):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Eb": 3, "Ab": 8}
    name, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[name] + 12 * (octave + 1) - 69) / 12)


def tt(length):
    return np.arange(int(length * SR)) / SR


def add(start, sig, pan=0.0, gain=1.0):
    i = int(round(start * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: N - i] * gain
    buf[0, i:i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4)
    buf[1, i:i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4)


def smooth(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def highpass(x, k=6):
    return x - smooth(x, k)


# ---------------- instruments ----------------
def kick(vel=1.0):
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = highpass(rng.standard_normal(len(t)), 4) * np.exp(-t / 0.004) * 0.3
    return vel * np.tanh(1.6 * (body + click))


def snare(vel=1.0, length=0.25):
    t = tt(length)
    noise = highpass(rng.standard_normal(len(t)), 5) * np.exp(-t / 0.07)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04)
    return vel * (0.7 * noise + 0.5 * tone)


def hat(vel=1.0, length=0.06):
    t = tt(length)
    return vel * highpass(highpass(rng.standard_normal(len(t)), 3), 3) * np.exp(-t / (length / 4))


def saw(freq, t, harmonics=18, bright=1.0):
    out = np.zeros_like(t)
    for h in range(1, harmonics + 1):
        if freq * h > 16000:
            break
        out += np.sin(2 * np.pi * freq * h * t) / h * np.exp(-(h - 1) / (6 * bright))
    return out


def supersaw(freq, length, attack=0.02, release=0.3, bright=1.0, voices=(-0.006, 0, 0.006)):
    t = tt(length)
    out = sum(saw(freq * (1 + d), t + rng.uniform(0, 1), bright=bright) for d in voices) / len(voices)
    env = np.clip(t / attack, 0, 1) * np.clip((length - t) / release, 0, 1)
    return out * env


def stab(notes, length=0.4, bright=1.4):
    t = tt(length)
    out = sum(supersaw(hz(n), length, attack=0.004, release=0.1, bright=bright) for n in notes)
    return out * np.exp(-t / 0.16) / len(notes)


def pluck(freq, length=0.3):
    t = tt(length)
    out = np.sin(2 * np.pi * freq * t) + 0.45 * np.sin(4 * np.pi * freq * t) * np.exp(-t / 0.05) + 0.2 * np.sin(6 * np.pi * freq * t) * np.exp(-t / 0.03)
    return out * np.exp(-t / 0.09) * np.clip(t / 0.002, 0, 1)


def sub(freq, length):
    t = tt(length)
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    return np.tanh(1.5 * s) * np.clip(t / 0.005, 0, 1) * np.clip((length - t) / 0.03, 0, 1)


def pad(notes, length, attack=0.6, release=1.2, bright=0.7):
    out = sum(supersaw(hz(n), length, attack=attack, release=release, bright=bright, voices=(-0.008, -0.003, 0.003, 0.008)) for n in notes)
    return out / len(notes)


def riser(length, f0=200, f1=2400):
    t = tt(length)
    x = t / length
    noise = rng.standard_normal(len(t))
    # sweep "filter": mix from smooth (dark) to raw (bright) noise as it rises
    dark = smooth(noise, 24)
    nz = (dark * (1 - x) + highpass(noise, 4) * x) * x ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f0 * (f1 / f0) ** x) / SR) * x ** 3 * 0.25
    return nz + tone


def whoosh(length=0.5):
    t = tt(length)
    x = t / length
    env = np.sin(np.pi * x) ** 2
    return smooth(rng.standard_normal(len(t)), 6) * env


def impact(vel=1.0, length=2.5):
    t = tt(length)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 80 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.7)
    crash = highpass(rng.standard_normal(len(t)), 3) * np.exp(-t / 0.5) * 0.35
    thud = smooth(rng.standard_normal(len(t)), 30) * np.exp(-t / 0.05) * 1.5
    return vel * np.tanh(1.3 * (boom + crash + thud))


def bell(freq, length=2.5, vel=1.0):
    t = tt(length)
    out = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.4) + 0.15 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t / 0.2)
    return vel * out * np.exp(-t / 1.0) * np.clip(t / 0.003, 0, 1)


def glitch(start, length, freq):
    """Stuttered, bit-crushed tone for the TIME. glitch."""
    t = tt(length)
    s = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5 + saw(freq * 2, t, 8) * 0.5
    gate = (np.floor(t / 0.0315) % 2 == 0).astype(float)
    crushed = np.round(s * 4) / 4
    add(start, crushed * gate * np.exp(-t / 0.25), pan=rng.uniform(-0.5, 0.5), gain=0.12)


# ---------------- arrangement ----------------
drums = np.zeros((2, N))


def addd(start, sig, pan=0.0, gain=1.0):
    global buf
    keep = buf
    buf = drums
    add(start, sig, pan, gain)
    buf = keep


# Intro: clock ticks on the ruler, riser into the burst
for k, s in enumerate(np.arange(0.25, 1.0, 0.125)):
    addd(s, hat(0.5 + k * 0.08, 0.03), pan=0.3 * (-1) ** k, gain=0.5)
add(0.0, riser(1.0, 120, 3000), gain=0.35)
add(0.0, sub(hz("D1"), 1.0) * np.linspace(0, 1, int(SR)) ** 2, gain=0.25)
add(1.0, impact(1.0), gain=0.9)
add(1.0, pad(["D3", "A3", "F4", "A4"], 1.1, attack=0.05, release=0.5), gain=0.22)
add(1.6, riser(0.4, 400, 4000), gain=0.25)

# Kinetic type: one chord stab per word
WORD_STABS = [(2.0, ["D4", "F4", "A4", "D5"]), (2.5, ["Bb3", "D4", "F4", "Bb4"]), (3.0, ["C4", "E4", "G4", "C5"]), (3.5, ["A3", "E4", "A4", "C#5"])]
for s, notes in WORD_STABS:
    add(s, stab(notes), pan=0.0, gain=0.42)
    add(s, sub(hz(notes[0]) / 4, 0.45), gain=0.4)
glitch(3.5, 0.3, hz("A4"))
add(3.78, whoosh(0.3), gain=0.25)

# Groove: kick on the beat 2.0-11.85, claps on 2 and 4, hats on 8ths/16ths
for i in range(int(2.0 / BEAT), int(11.85 / BEAT)):
    s = i * BEAT
    addd(s, kick(1.0 if s >= 4.0 else 0.85), gain=0.75)
    if s >= 4.0 and i % 2 == 1:
        addd(s, snare(0.8), pan=0.05, gain=0.45)
    for h in range(4 if s >= 6.0 else 2):
        hs = s + h * BEAT / (4 if s >= 6.0 else 2)
        if h % 2 == 1 or s >= 6.0:
            addd(hs, hat(0.9 if h % 2 else 0.5), pan=0.35, gain=0.18)
# Snare roll build into the finale
for k, s in enumerate(np.arange(11.0, 11.85, 0.0625)):
    addd(s, snare(0.3 + 0.7 * k / 14, 0.12), pan=-0.1, gain=0.35)
add(11.0, riser(0.85, 200, 5000), gain=0.35)

# Sidechain pump on the music (not on drums) from every kick
pump = np.ones(N)
t_all = np.arange(N) / SR
for i in range(int(2.0 / BEAT), int(11.85 / BEAT)):
    s = i * BEAT
    a, b = int(s * SR), int((s + BEAT) * SR)
    tt_ = t_all[a:b] - s
    pump[a:b] = np.minimum(pump[a:b], 1 - 0.65 * np.exp(-tt_ / 0.09))

# Harmony per 2-second bar: Bb - F - C - Dm
BARS = [(4.0, "Bb1", ["Bb3", "D4", "F4", "A4"]), (6.0, "F1", ["F3", "A3", "C4", "E4"]), (8.0, "C2", ["C4", "E4", "G4", "B4"]), (10.0, "D2", ["D4", "F4", "A4", "C5"])]
music = np.zeros((2, N))
keep = buf
buf = music
for s, bass, notes in BARS:
    length = 2.0 if s < 10.0 else 1.85
    add(s, pad(notes, length + 0.15, attack=0.08, release=0.15), gain=0.20)
    for k in range(int(length / (BEAT / 2))):  # 8th-note pumping bass
        add(s + k * BEAT / 2, sub(hz(bass) * (2 if k % 2 else 1), BEAT / 2 - 0.01), gain=0.22)
    arp = [notes[0], notes[1], notes[2], notes[3], notes[2], notes[1]]
    for k in range(int(length / (BEAT / 4))):  # 16th-note arp, an octave up
        f = hz(arp[k % len(arp)]) * 2
        add(s + k * BEAT / 4, pluck(f), pan=0.5 * np.sin(k * 0.7), gain=0.10 if s >= 4.0 else 0)
buf = keep
buf += music * pump

# Hits, sparkles and transitions that follow the picture
add(5.3, riser(0.7, 150, 6000), gain=0.35)                 # zoom through the cell
add(6.0, impact(0.8), gain=0.7)
for s, n in ((6.95, "A6"), (7.45, "E6"), (7.5, "C7")):     # shape morphs
    add(s, bell(hz(n), 1.2, 0.6), pan=rng.uniform(-0.6, 0.6), gain=0.12)
add(8.0, whoosh(0.65), pan=-0.3, gain=0.35)                # points fly into the word
add(8.65, impact(0.6, 1.5), gain=0.5)
add(8.7, bell(hz("G6"), 1.5), pan=0.3, gain=0.12)
add(8.95, riser(0.5, 300, 7000), gain=0.35)
add(9.45, impact(1.0), gain=0.9)                           # explosion
add(9.45, whoosh(0.6), pan=0.5, gain=0.4)
add(10.0, stab(["D4", "F4", "A4", "D5"], 0.6), gain=0.3)

# Finale: everything drops, one huge hit, warm resolve
add(11.85, impact(1.2, 3.0), gain=1.0)
add(11.85, sub(hz("Bb0"), 1.6) * np.exp(-tt(1.6) / 0.8), gain=0.5)
add(11.85, pad(["Bb2", "F3", "A3", "D4", "C5"], 1.8, attack=0.02, release=0.6, bright=0.9), gain=0.30)
add(13.2, pad(["F2", "C3", "A3", "F4", "G4", "C5"], 1.8, attack=0.6, release=1.2, bright=0.8), gain=0.30)
# a bell note for each phrase of the closing line
for s, n in ((13.15, "C6"), (13.6, "A5"), (14.05, "F5"), (14.2, "C6")):
    add(s, bell(hz(n), 2.2, 0.8), pan=rng.uniform(-0.4, 0.4), gain=0.12)

# ---------------- reverb + master ----------------
ir_len = int(1.8 * SR)
ir_t = np.arange(ir_len) / SR
ir = rng.standard_normal((2, ir_len)) * np.exp(-ir_t / 0.45)
ir = np.array([smooth(ch, 18) for ch in ir])
ir[:, : int(0.015 * SR)] = 0
ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
size = 1 << int(np.ceil(np.log2(N + ir_len)))
wet = np.array([np.fft.irfft(np.fft.rfft(buf[c], size) * np.fft.rfft(ir[c], size), size)[:N] for c in range(2)])
mix = buf + 0.28 * wet + drums

fade = np.clip(t_all / 0.02, 0, 1) * np.clip((DUR - t_all) / 0.9, 0, 1) ** 1.5
mix *= fade
mix = np.tanh(mix * 1.2) / 1.2
mix *= 10 ** (-1.0 / 20) / np.abs(mix).max()  # peak at -1 dBFS

out = sys.argv[1] if len(sys.argv) > 1 else "audio/showreel-score.wav"
pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"Wrote {out} ({DUR:.1f}s, {SR} Hz stereo)")
