"""Synthesized interaction sounds for AwesomeWM.

No audio files. No dependencies. Every cue is generated live
from mathematical waveforms and piped to ffplay via stdout.
"""

import math
import struct
import subprocess
import sys
import random

RATE = 44100
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit

# -- Utility ------------------------------------------------------------------

def _sine(f, t):
    return math.sin(2 * math.pi * f * t)

def _square(f, t):
    return 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0

def _saw(f, t):
    return 2.0 * (f * t % 1.0) - 1.0

def _noise():
    return random.uniform(-1.0, 1.0)

def _envelope(t, attack, hold, decay, sustain=0.0):
    """Simple ADSR-ish envelope. Returns amplitude 0..1."""
    if t < attack:
        return t / attack
    t2 = t - attack
    if t2 < hold:
        return 1.0
    t3 = t2 - hold
    if t3 < decay:
        return 1.0 - (1.0 - sustain) * (t3 / decay)
    return sustain

def _generate(duration, fn):
    """Generate PCM samples from a generator function fn(t) -> float [-1,1]."""
    n = int(RATE * duration)
    samples = bytearray(n * SAMPLE_WIDTH)
    for i in range(n):
        t = i / RATE
        val = max(-1.0, min(1.0, fn(t)))
        struct.pack_into('<h', samples, i * SAMPLE_WIDTH, int(val * 32767))
    return bytes(samples)

def _play(pcm):
    """Pipe raw PCM to ffplay."""
    proc = subprocess.Popen(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet',
         '-f', 's16le', '-ar', str(RATE), '-ac', str(CHANNELS), '-i', 'pipe:0'],
        stdin=subprocess.PIPE,
    )
    proc.communicate(input=pcm)

# -- Cues ---------------------------------------------------------------------

def press():
    """Short click/tap — key press."""
    def gen(t):
        e = _envelope(t, 0.002, 0.005, 0.02)
        return e * (_square(1200, t) * 0.3 + _noise() * 0.15)
    return _generate(0.03, gen)

def release():
    """Softer release click."""
    def gen(t):
        e = _envelope(t, 0.001, 0.003, 0.015)
        return e * (_square(900, t) * 0.2 + _noise() * 0.1)
    return _generate(0.02, gen)

def tick():
    """Very short tick."""
    def gen(t):
        e = _envelope(t, 0.001, 0.001, 0.008)
        return e * _sine(2000, t) * 0.4
    return _generate(0.01, gen)

def toggle():
    """Two-tone toggle — on/off."""
    def gen(t):
        if t < 0.04:
            e = _envelope(t, 0.002, 0.01, 0.02)
            return e * _sine(800, t) * 0.4
        else:
            t2 = t - 0.04
            e = _envelope(t2, 0.002, 0.01, 0.02)
            return e * _sine(1200, t) * 0.35
    return _generate(0.08, gen)

def success():
    """Ascending chime — two notes up."""
    def gen(t):
        if t < 0.08:
            e = _envelope(t, 0.005, 0.02, 0.04)
            return e * _sine(523, t) * 0.4
        else:
            t2 = t - 0.08
            e = _envelope(t2, 0.005, 0.03, 0.06)
            return e * _sine(784, t) * 0.45
    return _generate(0.18, gen)

def error():
    """Descending buzz — two notes down."""
    def gen(t):
        if t < 0.1:
            e = _envelope(t, 0.005, 0.03, 0.05)
            return e * (_square(330, t) * 0.25 + _saw(165, t) * 0.1)
        else:
            t2 = t - 0.1
            e = _envelope(t2, 0.005, 0.03, 0.06)
            return e * (_square(220, t) * 0.2 + _saw(110, t) * 0.08)
    return _generate(0.22, gen)

def chime():
    """Pleasant bell-like tone with harmonics."""
    def gen(t):
        e = _envelope(t, 0.003, 0.05, 0.15)
        fundamental = _sine(880, t) * 0.3
        harmonic2 = _sine(1760, t) * 0.15
        harmonic3 = _sine(2640, t) * 0.08
        return e * (fundamental + harmonic2 + harmonic3)
    return _generate(0.25, gen)

def sparkle():
    """High frequency shimmer — random sparkly tones."""
    def gen(t):
        e = _envelope(t, 0.005, 0.02, 0.08)
        # Multiple detuned high frequencies for sparkle
        s = (_sine(3200, t) * 0.15 +
             _sine(4100, t) * 0.12 +
             _sine(5300, t) * 0.08 +
             _sine(6100, t) * 0.05)
        return e * s
    return _generate(0.12, gen)

def droplet():
    """Water drop — fast frequency sweep down."""
    def gen(t):
        e = _envelope(t, 0.002, 0.01, 0.08)
        # Exponential frequency sweep from high to low
        f = 2000 * math.exp(-t * 40) + 200
        return e * _sine(f, t) * 0.45
    return _generate(0.12, gen)

def bloom():
    """Swelling tone that rises then fades."""
    def gen(t):
        # Slow attack, long decay
        e = _envelope(t, 0.06, 0.04, 0.2)
        f = 440 + 80 * math.sin(2 * math.pi * 0.5 * t)  # slight vibrato
        return e * (_sine(f, t) * 0.35 + _sine(f * 2, t) * 0.1)
    return _generate(0.35, gen)

def whisper():
    """Filtered noise burst."""
    def gen(t):
        e = _envelope(t, 0.005, 0.02, 0.06)
        # Simple noise with slight low-pass feel (moving average-ish)
        n = _noise() * 0.3
        # Mix with a quiet tone for body
        return e * (n + _sine(600, t) * 0.05)
    return _generate(0.1, gen)

def loading():
    """Rhythmic pulse — three quick beats."""
    def gen(t):
        beat_len = 0.05
        pause = 0.03
        cycle = beat_len + pause
        pos = t % cycle
        if pos < beat_len:
            e = _envelope(pos, 0.002, 0.01, 0.02)
            return e * _sine(1000, t) * 0.35
        return 0.0
    return _generate(0.24, gen)

def ready():
    """Confirmation — quick ascending chirp."""
    def gen(t):
        e = _envelope(t, 0.003, 0.02, 0.04)
        f = 600 + 600 * (t / 0.08)  # linear sweep up
        return e * _sine(f, t) * 0.4
    return _generate(0.08, gen)

def page():
    """Page turn — filtered noise swoosh."""
    def gen(t):
        e = _envelope(t, 0.01, 0.03, 0.06)
        # Noise with frequency-dependent amplitude (swoosh)
        f = 300 + 2000 * t
        mod = 0.5 + 0.5 * math.sin(2 * math.pi * f * t)
        return e * _noise() * 0.25 * mod
    return _generate(0.1, gen)


# -- Registry -----------------------------------------------------------------

CUES = {
    "press":    press,
    "release":  release,
    "tick":     tick,
    "toggle":   toggle,
    "success":  success,
    "error":    error,
    "chime":    chime,
    "sparkle":  sparkle,
    "droplet":  droplet,
    "bloom":    bloom,
    "whisper":  whisper,
    "loading":  loading,
    "ready":    ready,
    "page":     page,
}

def play(cue_name):
    """Play a cue by name."""
    fn = CUES.get(cue_name)
    if fn is None:
        print(f"Unknown cue: {cue_name}", file=sys.stderr)
        print(f"Available: {', '.join(sorted(CUES))}", file=sys.stderr)
        sys.exit(1)
    _play(fn())

def main():
    if len(sys.argv) < 2:
        print(f"Usage: awesound <cue>", file=sys.stderr)
        print(f"Available cues: {', '.join(sorted(CUES))}", file=sys.stderr)
        sys.exit(1)
    play(sys.argv[1])


if __name__ == "__main__":
    main()
