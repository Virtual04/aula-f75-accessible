"""Gombkiosztás-táblák. Egy réteg 128 bejegyzés, egyenként 4 bájt:
típus, módosítóbitek, 16 bites kód (nagy helyiérték elöl).

A gyári tábla a gyári program mentéséből származik (research\\02_payloads.hex),
kiegészítve a magyar ISO kiosztás két gombjával, amelyeket a gyári program kihagy:
75-ös mátrixhely = ISO # (magyarul ű), 76-os mátrixhely = ISO \\ (magyarul í).
A szóköz utáni két gomb (53, 59) a magyar billentyűzeten AltGr és Fn; a gyári program
ide Fn-t és jobb Ctrl-t ír.
"""

from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"

LAYER_NAMES = ["default", "fn1", "fn2", "tap"]


def factory_layers():
    lines = (DATA / "factory_keymap.hex").read_text().split()
    return [bytearray(bytes.fromhex(line)) for line in lines]
