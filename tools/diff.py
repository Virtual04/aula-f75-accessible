"""Felvételek elemzése: mely beállításbájtokat változtatta a gyári program.

    python tools\\diff.py NEV [NEV ...]

Minden felvételnél kiírja, milyen parancsokat küldött a program, és hogy a
beállításblokk írásakor (0x04) mely bájtok tértek el a kiolvasott (0x84) blokktól.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dump  # noqa: E402


def analyse(name):
    commands = []
    last_read = None
    print(f"{name}:")
    for _, direction, data in dump.packets(name):
        if len(data) < 8 or data[0] != 0x06:
            continue
        if direction == "küldés":
            commands.append(f"{data[1]:02x}/{data[2]}")
        if direction == "válasz" and data[1] == 0x84:
            last_read = data[8:136]
        if direction == "küldés" and data[1] == 0x04:
            written = data[8:136]
            if last_read is None:
                print("  írás olvasás nélkül:", written.rstrip(b"\x00").hex(" "))
            else:
                diffs = [f"{i}: {last_read[i]:02x} -> {written[i]:02x}" for i in range(128) if last_read[i] != written[i]]
                print("  eltérő bájtok:", ", ".join(diffs) or "nincs")
    print("  parancsok (kód/index):", " ".join(commands) or "nincs")


if __name__ == "__main__":
    for name in sys.argv[1:]:
        analyse(name)
