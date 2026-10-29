"""Világítás. A rögzítésekből kiderített szerkezet:

Beállításblokk (0x84 olvasás, 0x04 írás):
  10. bájt: effekt kódja (EFFECTS), 0 = kikapcsolva
  9. bájt: 1, ha a Self-define effekt aktív, egyébként 0
  56 + 2 * effekt: az effekt fényereje, 0-9
  57 + 2 * effekt: felső 4 bit a sebesség (0-4), alsó 4 bit a színhely (0-6),
                   vagy 7 = Colourful (minden színhely)

Színtábla (0x0a írás, 512 bájt): effektenként 7 színhely, egyenként 3 bájt (R, G, B),
az effekt része a 21 * effekt helyen kezdődik. A tábla nem olvasható ki, ezért
a program tartja nyilván (kiinduló állapot: data\\color_table.hex).
"""

from f75.keymap import DATA as DATA_DIR

EFFECTS = {
    "off": 0, "fixed": 1, "respire": 2, "rainbow": 3, "flash_away": 4,
    "raindrops": 5, "ripples": 7, "stars": 8, "snake": 10, "neon": 11,
    "reaction": 12, "sine_wave": 13, "windmill": 15, "waterfall": 16,
    "blossoming": 17, "self_define": 21,
}
EFFECT_NAMES = {code: name for name, code in EFFECTS.items()}

SETTING_SELF_DEFINE = 9
SETTING_EFFECT = 10
MAX_BRIGHTNESS = 9
MAX_SPEED = 4
COLOURFUL = 7

COLOR_TABLE_LEN = 512
COLOR_NAMES = {
    "piros": "ff0000", "zöld": "00ff00", "kék": "0000ff", "sárga": "ffff00",
    "lila": "ff00ff", "türkiz": "00ffff", "fehér": "ffffff", "narancs": "ff8000",
}


def default_color_table():
    return bytearray(bytes.fromhex((DATA_DIR / "color_table.hex").read_text().strip()))


def brightness_index(effect):
    return 56 + 2 * effect


def mode_index(effect):
    return 57 + 2 * effect


def describe(block, color_table):
    """A beállításblokk világítási részének szöveges leírása."""
    effect = block[SETTING_EFFECT]
    name = EFFECT_NAMES.get(effect, f"ismeretlen ({effect})")
    if effect == 0:
        return ["Világítás: kikapcsolva."]
    mode = block[mode_index(effect)]
    slot = mode & 0x0F
    if slot == COLOURFUL:
        color = "Colourful, minden szín"
    else:
        rgb = color_table[21 * effect + 3 * slot:21 * effect + 3 * slot + 3].hex()
        named = next((n for n, v in COLOR_NAMES.items() if v == rgb), None)
        color = f"{named} ({rgb})" if named else rgb
    return [
        f"Effekt: {name}.",
        f"Fényerő: {block[brightness_index(effect)]} a {MAX_BRIGHTNESS}-ből.",
        f"Sebesség: {mode >> 4} a {MAX_SPEED}-ből.",
        f"Szín: {color}.",
    ]


def parse_color(text):
    text = text.lower().lstrip("#")
    text = COLOR_NAMES.get(text, text)
    try:
        rgb = bytes.fromhex(text)
    except ValueError:
        rgb = b""
    if len(rgb) != 3:
        names = ", ".join(COLOR_NAMES)
        raise ValueError(f"Érvénytelen szín. Megadható névvel ({names}, colourful) vagy hat hexadecimális jeggyel, például ff8000.")
    return rgb
