#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""(MENTAL) the FX kit: 16 one-shots for a user drum slot - screeches, larsens, impacts, risers.

Synthesised here, so nothing sampled goes into the repository. Each sound lands on one lane of the
drum track (drums.c LANE_NOTE), which is what the white keys 1..16 play, so the kit sits under the
fingers in the order below and costs no synth track.

    python3 tools/gen_fxkit.py out/            # the 16 WAVs, the slot (.hdr / .bin) and a demo

A user slot holds 80 KiB of IMA ADPCM at 22050 Hz: 7.38 s for the sixteen together, so these are
short on purpose. The script prints what it used.
"""
import math
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import sampleio as S

SR = S.SLOT_RATE
LANE_NOTE = [36, 35, 38, 39, 42, 46, 44, 37, 40, 43, 48, 49, 51, 70, 63, 56]   # drums.c

rng = np.random.default_rng(0x9E3779B9)


def t(d):
    return np.arange(int(SR * d)) / SR


def noise(d):
    return rng.uniform(-1.0, 1.0, int(SR * d))


def env(x, a=0.002, d=None, curve=2.0):
    """attack then a curved decay over the rest"""
    n = len(x)
    na = max(1, int(SR * a))
    e = np.ones(n)
    e[:na] = np.linspace(0, 1, na)
    tail = np.linspace(0, 1, n - na) if n > na else np.zeros(0)
    e[na:] = (1 - tail) ** curve
    return x * e


def _svf(x, cut, res, want):
    """Chamberlin state-variable filter, low-pass or band-pass out. It is only stable while
    f + q < 2, so f is bounded here rather than left to blow up at the top of the range."""
    cut = np.broadcast_to(np.asarray(cut, dtype=float), x.shape)
    q = max(1e-3, 1.0 - res)
    f = 2 * np.sin(np.pi * np.clip(cut, 20, SR * 0.45) / SR)
    f = np.clip(f, 0.0, min(1.4, 2.0 - q - 0.2))
    out = np.zeros_like(x)
    b = l = 0.0
    for i in range(len(x)):
        h = x[i] - l - q * b
        b += f[i] * h
        l += f[i] * b
        out[i] = l if want == 0 else b if want == 1 else h
    return out


def svf(x, cut, res=0.9):
    return _svf(x, cut, res, 0)


def bp(x, cut, res=0.97):
    return _svf(x, cut, res, 1)


def hp1(x, fc):
    """one-pole high-pass: stable at any cutoff, which is where the bright sounds live"""
    a = math.exp(-2 * math.pi * min(fc, SR * 0.45) / SR)
    y = np.zeros_like(x)
    prev = acc = 0.0
    for i in range(len(x)):
        acc = a * (acc + x[i] - prev)
        prev = x[i]
        y[i] = acc
    return y


def phase(hz):
    return np.cumsum(2 * np.pi * np.asarray(hz) / SR)


def drive(x, k=4.0):
    return np.tanh(x * k)


# ---------------------------------------------------------------- the sixteen ---
def f_screech_down():                                   # 1: metal falling, the classic teuf screech
    x = t(0.45)
    c = 5200 * np.exp(-6.5 * x) + 240
    s = bp(noise(0.45) * 0.6 + np.sin(phase(c * 0.5)), c, 0.985)
    return drive(env(s, 0.004, curve=1.6), 6)


def f_screech_up():                                     # 2: and rising
    x = t(0.38)
    c = 300 * np.exp(6.0 * x) + 200
    s = bp(noise(0.38) * 0.5 + np.sin(phase(c * 0.5)), c, 0.985)
    return drive(env(s, 0.01, curve=0.8), 5)


def f_larsen():                                         # 3: the feedback whine, drifting
    x = t(0.6)
    hz = 2300 + 260 * np.sin(2 * np.pi * 1.7 * x) + 700 * x
    s = np.sin(phase(hz)) + 0.35 * np.sin(phase(hz * 2.01))
    e = np.clip(x / 0.08, 0, 1) * np.clip((0.6 - x) / 0.12, 0, 1)
    return drive(s * e, 3)


def f_impact():                                         # 4: the sub boom with its crack
    x = t(0.55)
    sub = np.sin(phase(70 * np.exp(-9 * x) + 32)) * np.exp(-5.5 * x)
    crack = svf(noise(0.55), 3000 * np.exp(-40 * x) + 120, 0.6) * np.exp(-26 * x)
    return drive(sub * 1.1 + crack * 0.8, 2.2)


def f_riser():                                          # 5: noise climbing, for the drop
    x = t(0.75)
    s = bp(noise(0.75), np.minimum(180 * np.exp(4.6 * x), 3400), 0.93) + hp1(noise(0.75), 2000) * (x / 0.75)
    return drive(s * (x / 0.75) ** 1.7, 3)


def f_downlift():                                       # 6: and falling away
    x = t(0.55)
    s = bp(noise(0.55), 7000 * np.exp(-7.0 * x) + 120, 0.93)
    return drive(env(s, 0.004, curve=1.2), 3)


def f_zap():                                            # 7: short, FM, nasty
    x = t(0.2)
    m = np.sin(phase(1400 * np.exp(-24 * x))) * 2600 * np.exp(-18 * x)
    s = np.sin(phase(520 * np.exp(-11 * x) + m))
    return drive(env(s, 0.001, curve=2.2), 4)


def f_scrape():                                         # 8: metal dragged, grainy
    x = t(0.45)
    g = (np.floor(x * 70) % 2) * 0.7 + 0.3
    c = 1800 + 1400 * np.sin(2 * np.pi * 9 * x)
    s = bp(noise(0.45) * g, c, 0.98)
    return drive(env(s, 0.006, curve=1.0), 5)


def f_reverse():                                        # 9: the swell that arrives backwards
    x = t(0.45)
    s = bp(noise(0.45), 500 + 3500 * (x / 0.45), 0.95)
    s = s * (x / 0.45) ** 2.4
    return drive(s, 3)


def f_siren():                                          # 10: two tones, the alarm of a teuf
    x = t(0.55)
    hz = 760 + 420 * np.sign(np.sin(2 * np.pi * 5.5 * x))
    s = np.sin(phase(hz)) + 0.3 * np.sin(phase(hz * 1.5))
    e = np.clip(x / 0.02, 0, 1) * np.clip((0.55 - x) / 0.1, 0, 1)
    return drive(s * e, 3.5)


def f_subdrop():                                        # 11: the floor falling out
    x = t(0.5)
    s = np.sin(phase(210 * np.exp(-7.5 * x) + 26))
    return drive(env(s, 0.002, curve=1.4), 2.4)


def f_glass():                                          # 12: bright shatter
    x = t(0.28)
    s = hp1(noise(0.28), 5200) + 0.5 * bp(noise(0.28), 3200, 0.95)
    return drive(env(s, 0.001, curve=2.6), 3)


def f_stab():                                           # 13: the dissonant cluster
    x = t(0.35)
    s = sum(np.sin(phase(np.full(len(x), h))) for h in (196, 233, 277, 370))
    s = svf(s / 4 + noise(0.35) * 0.12, 2600 * np.exp(-7 * x) + 300, 0.85)
    return drive(env(s, 0.003, curve=1.8), 5)


def f_tapestop():                                       # 14: everything slowing to nothing
    x = t(0.45)
    s = np.sin(phase(440 * (1 - x / 0.45) ** 1.5 + 24)) + 0.4 * np.sin(phase(660 * (1 - x / 0.45) ** 1.5 + 30))
    return drive(env(s, 0.002, curve=1.1), 3)


def f_blip():                                           # 15: the short alarm blip
    x = t(0.3)
    hz = np.where(x < 0.15, 1180, 880)
    s = np.sign(np.sin(phase(hz))) * 0.6
    e = np.clip(x / 0.004, 0, 1) * np.clip((0.3 - x) / 0.04, 0, 1)
    return svf(s * e, 4200, 0.4)


def f_snap():                                           # 16: the shortest, for rolls
    x = t(0.12)
    s = hp1(noise(0.12), 3000) * np.exp(-14 * x) + svf(noise(0.12), 2600, 0.5) * 0.6
    return drive(env(s, 0.0005, curve=3.2), 3)


FX = [("SCREECH", f_screech_down), ("SCREECH UP", f_screech_up), ("LARSEN", f_larsen), ("IMPACT", f_impact),
      ("RISER", f_riser), ("DOWNLIFT", f_downlift), ("ZAP", f_zap), ("SCRAPE", f_scrape),
      ("REVERSE", f_reverse), ("SIREN", f_siren), ("SUB DROP", f_subdrop), ("GLASS", f_glass),
      ("STAB", f_stab), ("TAPE STOP", f_tapestop), ("BLIP", f_blip), ("SNAP", f_snap)]



# ------------------------------------------------------- the six drums (mixed kit) ---
# Mentale drums, synthesised the same way, so one slot can hold a kit AND the FX: six lanes of
# drums under the left hand, ten FX under the right.
def d_kick():                                           # 1: the deep one, long, with its click
    x = t(0.42)
    hz = 46 * np.exp(-16 * x) + 41
    s = np.sin(phase(hz)) * np.exp(-4.2 * x)
    click = svf(noise(0.42), 2200 * np.exp(-90 * x) + 90, 0.5) * np.exp(-70 * x)
    return drive(s * 1.2 + click * 0.5, 3.2)


def d_kick2():                                          # 2: shorter, harder, more drive
    x = t(0.3)
    hz = 70 * np.exp(-24 * x) + 44
    s = np.sin(phase(hz)) * np.exp(-7.5 * x)
    click = svf(noise(0.3), 3400 * np.exp(-110 * x) + 120, 0.5) * np.exp(-90 * x)
    return drive(s * 1.1 + click * 0.7, 6.0)


def d_snare():                                          # 3
    x = t(0.26)
    tone = (np.sin(phase(np.full(len(x), 190))) + np.sin(phase(np.full(len(x), 278)))) * np.exp(-22 * x)
    n = bp(noise(0.26), 1900, 0.7) * np.exp(-14 * x)
    return drive(tone * 0.5 + n * 0.9, 3.0)


def d_clap():                                           # 4: four bursts then the tail
    x = t(0.3)
    e = np.exp(-11 * x)
    for o in (0.0, 0.009, 0.018, 0.027):
        k = int(SR * o)
        e[k:k + int(SR * 0.004)] += 1.6
    return drive(bp(noise(0.3), 1600, 0.82) * e, 2.6)


def d_hat():                                            # 5: closed, tight
    x = t(0.09)
    return drive(hp1(noise(0.09), 6500) * np.exp(-55 * x), 2.0)


def d_ohat():                                           # 6: open, ringing
    x = t(0.34)
    return drive(hp1(noise(0.34), 5600) * np.exp(-9 * x), 2.0)


DRUMS = [("KICK", d_kick), ("KICK 2", d_kick2), ("SNARE", d_snare), ("CLAP", d_clap),
         ("HAT", d_hat), ("OPEN HAT", d_ohat)]
MIXED = DRUMS + [f for f in FX if f[0] in
                 ("IMPACT", "SCREECH", "LARSEN", "RISER", "DOWNLIFT", "ZAP", "SIREN", "SUB DROP", "STAB", "SNAP")]


def wav16(path, x, sr=SR):
    d = np.asarray(x, dtype=np.int16).tobytes()
    with open(path, "wb") as f:
        f.write(struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(d), b"WAVE", b"fmt ", 16, 1, 1,
                            sr, sr * 2, 2, 16, b"data", len(d)))
        f.write(d)


def main(out, kit=None, slot_name="MNTFX", tag="MENTAL_FX"):
    os.makedirs(out, exist_ok=True)
    zones, demo, total = [], [], 0
    for i, (name, fn) in enumerate(kit or FX):
        s = np.asarray(fn(), dtype=float)
        s[-int(SR * 0.004):] *= np.linspace(1, 0, int(SR * 0.004))   # never end on a step
        v = S.to_int16(s)
        note = LANE_NOTE[i]
        zones.append((v, note, note, note))                          # one lane, one key
        total += (len(v) + 1) // 2
        demo += list(v) + [0] * int(SR * 0.12)
        wav16(os.path.join(out, "%02d_%s.wav" % (i + 1, name.replace(" ", ""))), np.array(v, dtype=np.int16))
        print("  %2d  %-11s %5.2f s  key %2d (note %d)" % (i + 1, name, len(v) / SR, i + 1, note))
    hdr, data = S.user_slot(slot_name, zones)
    open(os.path.join(out, tag + "_slot.hdr"), "wb").write(hdr)
    open(os.path.join(out, tag + "_slot.bin"), "wb").write(data)
    wav16(os.path.join(out, tag + "_demo.wav"), np.array(demo, dtype=np.int16))
    print("slot: %d B of %d (%.0f %%), %.2f s of the %.2f s a slot holds"
          % (len(data), S.SLOT_MAX_DATA, 100.0 * len(data) / S.SLOT_MAX_DATA,
             len(data) * 2 / SR, S.SLOT_MAX_DATA * 2 / SR))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "build/fxkit"
    which = sys.argv[2] if len(sys.argv) > 2 else "fx"
    if which == "mixed":                                 # 6 drums under the left hand, 10 FX under the right
        print("MENTAL LIVE (6 drums + 10 FX):")
        main(os.path.join(out, "live"), MIXED, "MNTLIVE", "MENTAL_LIVE")
    else:
        print("MENTAL FX (16 one-shots):")
        main(os.path.join(out, "fx"), FX, "MNTFX", "MENTAL_FX")
