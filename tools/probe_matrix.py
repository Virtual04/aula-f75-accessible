"""Az ISO-gombok (í, ű) mátrixhelyének megkeresése.

A gyári program által küldött táblát (research\\02_payloads.hex) küldi vissza,
a Caps Lockot visszaállítva, és a Default réteg minden üres helyére egy
azonosítható billentyűt tesz. Alapból csak kiírja a tervet, --send kell a küldéshez.

    python tools\\probe_matrix.py          terv kiírása
    python tools\\probe_matrix.py --send   küldés
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from f75.device import F75, LAYER_END_MARK  # noqa: E402

CAPSLOCK_INDEX = 3
HID_CAPSLOCK = 0x39

# Számjegyek 1-9, majd betűk a-z (HID-kódok). Magyar kiosztásban a 0x1c Z, a 0x1d Y,
# a 0x27 pedig ö, ezért a 0-t kihagyjuk.
PROBE_CODES = [(0x1E + i, str(i + 1)) for i in range(9)]
PROBE_CODES += [(0x04 + i, chr(ord("a") + i)) for i in range(26)]
HU_SWAP = {"y": "z", "z": "y"}


def load_captured_layers():
    lines = (ROOT / "research" / "02_payloads.hex").read_text().split()
    return [bytearray(bytes.fromhex(line)[8:]) for line in lines]


def entry(code):
    return bytes([0x00, 0x00, 0x00, code])


def main():
    layers = load_captured_layers()
    default = layers[0]
    default[CAPSLOCK_INDEX * 4:CAPSLOCK_INDEX * 4 + 4] = entry(HID_CAPSLOCK)

    empty = [i for i in range(127) if default[i * 4:i * 4 + 4] == bytes(4)]
    plan = []
    for index, (code, char) in zip(empty, PROBE_CODES):
        default[index * 4:index * 4 + 4] = entry(code)
        plan.append((index, HU_SWAP.get(char, char)))
    assert all(layer[127 * 4:] == LAYER_END_MARK for layer in layers)

    print(f"A Default réteg {len(empty)} üres helye közül {len(plan)} kap próbabillentyűt.")
    for index, char in plan:
        print(f"Mátrixhely {index}: {char}")
    print("A Caps Lock visszakapja a Caps Lock kódot. A többi réteg változatlan.")

    if "--send" not in sys.argv:
        print("Nem küldtem semmit. Küldéshez: --send")
        return 0
    with F75() as kb:
        kb.write_keymap([bytes(layer) for layer in layers])
    print("Elküldve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
