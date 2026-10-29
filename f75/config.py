"""A konfiguráció: a gyári beállításhoz képesti eltérések.

A billentyűzetből nem lehet kiolvasni a beállításokat, ezért a program itt
tartja nyilván őket. Formátum (JSON):

    {"version": 1, "keymap": {"default": {"capslock": "esc"}, "fn1": {}, "fn2": {}},
     "sleep": 10}

A "sleep" percben értendő, 0 = kikapcsolva. Ha hiányzik, az alvást nem módosítjuk.
A "debounce" a pergésmentesítés fokozata, 1-5.
A "tap" a Tap réteg érzékenysége, 10-127, 0 = kikapcsolva.
A "macros" a makrók: {"név": {"text": "szöveg"}} vagy {"név": {"steps": "ctrl+c 500ms ctrl+v"}}.
A sorrendjük adja a sorszámukat. Gombra a "macro:név" céllal kerülnek, opcionálisan
":3" (ismétlésszám), ":held" (amíg nyomva tartod) vagy ":untilkey" (a következő leütésig).
A "light" a világítás: {"effect": "neon", "brightness": 9, "speed": 4, "color": "colourful"}.
A "colors" a teljes színtábla hexadecimálisan, mert az nem olvasható ki a billentyűzetből.
"""

import json
import os
from pathlib import Path

from f75 import keys, lighting, macros
from f75.keymap import LAYER_NAMES, factory_layers

EDITABLE_LAYERS = ["default", "fn1", "fn2", "tap"]
# A gyári program csúszkájának értékei percben (KB.ini: SleepUI / SleepHW), 0 = kikapcsolva
SLEEP_MINUTES = [0, 1, 1.5, 2, 3, 4, 5, 10, 15, 20]
DEBOUNCE_STAGES = range(1, 6)
TAP_SENSITIVITY = range(10, 128)  # 0 = kikapcsolva
STATE_FILE = Path(os.environ.get("APPDATA", Path.home())) / "F75Konfig" / "allapot.json"


def empty():
    return {"version": 1, "keymap": {layer: {} for layer in EDITABLE_LAYERS}, "macros": {}}


def validate(config):
    """Ellenőrzi a fájlból betöltött konfigurációt. Hibánál UnknownKey vagy ValueError."""
    if config.get("version") != 1:
        raise ValueError("Ismeretlen konfigurációs verzió.")
    config.setdefault("macros", {})
    for name, macro in config["macros"].items():
        if not name or len(name) > macros.MAX_NAME:
            raise ValueError(f"A makró neve 1-{macros.MAX_NAME} karakter lehet: {name!r}")
        macros.events_of(macro)
    if config["macros"]:
        macros.build_blob(config["macros"])
    for layer, mapping in config.get("keymap", {}).items():
        if layer not in EDITABLE_LAYERS:
            raise ValueError(f"Ismeretlen réteg: {layer}")
        for key, target in mapping.items():
            keys.physical_index(key)
            encode_target(config, target)
    for layer in EDITABLE_LAYERS:
        config.setdefault("keymap", {}).setdefault(layer, {})
    if "sleep" in config and config["sleep"] not in SLEEP_MINUTES:
        raise ValueError(f"Érvénytelen alvási idő: {config['sleep']}")
    if "debounce" in config and config["debounce"] not in DEBOUNCE_STAGES:
        raise ValueError(f"Érvénytelen pergésmentesítési fokozat: {config['debounce']}")
    if "tap" in config and config["tap"] != 0 and config["tap"] not in TAP_SENSITIVITY:
        raise ValueError(f"Érvénytelen Tap-érzékenység: {config['tap']}")
    if "colors" in config:
        table = bytes.fromhex(config["colors"])
        if len(table) != lighting.COLOR_TABLE_LEN or table[506:508] != b"\x5a\xa5":
            raise ValueError("Hibás színtábla a konfigurációban.")
    if "light" in config:
        light = config["light"]
        if light.get("effect") not in lighting.EFFECTS:
            raise ValueError(f"Ismeretlen effekt: {light.get('effect')}")
        if light["effect"] != "off":
            if light.get("brightness") not in range(lighting.MAX_BRIGHTNESS + 1):
                raise ValueError("Érvénytelen fényerő a konfigurációban.")
            if light.get("speed") not in range(lighting.MAX_SPEED + 1):
                raise ValueError("Érvénytelen sebesség a konfigurációban.")
            if light.get("color") != "colourful":
                lighting.parse_color(light.get("color", ""))
    return config


def encode_target(config, target):
    """Célnév -> 4 bájtos bejegyzés; a makrókhoz a konfiguráció makrólistája kell."""
    if macros.parse_target(target):
        return macros.entry(target, list(config.get("macros", {})))
    return keys.encode(target)


def describe_target(target):
    if macros.parse_target(target):
        return macros.describe_target(target)
    return keys.decode(keys.encode(target))


def macro_users(config, name):
    """Azok a (réteg, gomb) párok, amelyekre az adott makró ki van osztva."""
    return [(layer, key) for layer, mapping in config["keymap"].items() for key, target in mapping.items()
            if (macros.parse_target(target) or ("",))[0] == name]


def color_table(config):
    if "colors" in config:
        return bytearray(bytes.fromhex(config["colors"]))
    return lighting.default_color_table()


def read(path):
    with open(path, encoding="utf-8") as f:
        return validate(json.load(f))


def write(config, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_state():
    return read(STATE_FILE) if STATE_FILE.exists() else empty()


def save_state(config):
    write(config, STATE_FILE)


def build_layers(config):
    """A gyári tábla és az eltérések alapján a billentyűzetre küldendő négy réteg."""
    layers = factory_layers()
    for layer, mapping in config["keymap"].items():
        table = layers[LAYER_NAMES.index(layer)]
        for key, target in mapping.items():
            i = keys.physical_index(key)
            table[i * 4:i * 4 + 4] = encode_target(config, target)
    # Az FN2-gomb a gyári programhoz hasonlóan az FN1 és az FN2 rétegen is FN2 marad,
    # hacsak ott mást nem adtak meg rá.
    for key, target in config["keymap"]["default"].items():
        if encode_target(config, target) == keys.FN2_ENTRY:
            i = keys.physical_index(key)
            for layer in ("fn1", "fn2"):
                if key not in config["keymap"][layer]:
                    layers[LAYER_NAMES.index(layer)][i * 4:i * 4 + 4] = keys.FN2_ENTRY
    return [bytes(layer) for layer in layers]
