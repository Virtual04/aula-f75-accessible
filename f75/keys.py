"""Gombnevek. Minden név a magyar kiosztás szerint értendő: a "z" az a gomb,
amelyik magyar kiosztásban Z-t ír, a "0" az 1-es melletti gomb, és így tovább.

PHYSICAL: a billentyűzet fizikai gombjai, név -> mátrixhely.
A mátrixhelyek a gyári program KB.ini fájljából, az í és az ű próbával kiderítve.

Egy kiosztás-bejegyzés 4 bájt: típus, módosítóbitek, 16 bites kód.
  típus 0x00: billentyű (HID-kód), módosítóbitekkel együtt
  típus 0x02: médiagomb (HID consumer kód)
  típus 0x0d: Fn
"""

PHYSICAL = {
    "esc": 0, "f1": 12, "f2": 18, "f3": 24, "f4": 30, "f5": 36, "f6": 42,
    "f7": 48, "f8": 54, "f9": 60, "f10": 66, "f11": 72, "f12": 78,
    "tekerő": 84,
    "0": 1, "1": 7, "2": 13, "3": 19, "4": 25, "5": 31, "6": 37, "7": 43,
    "8": 49, "9": 55, "ö": 61, "ü": 67, "ó": 73, "backspace": 79, "delete": 85,
    "tab": 2, "q": 8, "w": 14, "e": 20, "r": 26, "t": 32, "z": 38, "u": 44,
    "i": 50, "o": 56, "p": 62, "ő": 68, "ú": 74, "pgup": 86,
    "capslock": 3, "a": 9, "s": 15, "d": 21, "f": 27, "g": 33, "h": 39,
    "j": 45, "k": 51, "l": 57, "é": 63, "á": 69, "ű": 75, "enter": 81,
    "pgdn": 87,
    "lshift": 4, "í": 76, "y": 10, "x": 16, "c": 22, "v": 28, "b": 34,
    "n": 40, "m": 46, ",": 52, ".": 58, "-": 64, "rshift": 70, "up": 82,
    "end": 88,
    "lctrl": 5, "lwin": 11, "lalt": 17, "space": 35, "altgr": 53, "fn": 59,
    "left": 77, "down": 83, "right": 89,
}

# A magyar billentyűzeten a szóköz után AltGr és Fn van. A gyári program ANSI táblája
# ugyanide Fn-t és jobb Ctrl-t ír; a mi gyári táblánk (data\factory_keymap.hex) a magyart.

# Az ANSI kiosztás \ gombjának helye (80). A magyar billentyűzeten nincs ilyen
# fizikai gomb, de a gyári tábla tartalmazza, ezért érintetlenül hagyjuk.

MODIFIERS = {
    "lctrl": 0x01, "lshift": 0x02, "lalt": 0x04, "lwin": 0x08,
    "rctrl": 0x10, "rshift": 0x20, "altgr": 0x40, "rwin": 0x80,
}
MODIFIER_ALIASES = {"ctrl": "lctrl", "shift": "lshift", "alt": "lalt", "win": "lwin", "ralt": "altgr"}

KEYCODES = {
    **{chr(ord("a") + i): 0x04 + i for i in range(26)},
    "z": 0x1C, "y": 0x1D,  # magyar QWERTZ
    **{str(i): 0x1D + i for i in range(1, 10)},
    "0": 0x35, "ö": 0x27, "ü": 0x2D, "ó": 0x2E, "ő": 0x2F, "ú": 0x30,
    "é": 0x33, "á": 0x34, "ű": 0x32, "í": 0x64, ",": 0x36, ".": 0x37, "-": 0x38,
    "enter": 0x28, "esc": 0x29, "backspace": 0x2A, "tab": 0x2B, "space": 0x2C,
    "capslock": 0x39,
    **{f"f{i}": 0x39 + i for i in range(1, 13)},
    **{f"f{i}": 0x5B + i for i in range(13, 25)},
    "printscreen": 0x46, "scrolllock": 0x47, "pause": 0x48, "insert": 0x49,
    "home": 0x4A, "pgup": 0x4B, "delete": 0x4C, "end": 0x4D, "pgdn": 0x4E,
    "right": 0x4F, "left": 0x50, "down": 0x51, "up": 0x52,
    "numlock": 0x53, "numslash": 0x54, "numstar": 0x55, "numminus": 0x56, "numplus": 0x57,
    "numenter": 0x58, **{f"num{i}": 0x58 + i for i in range(1, 10)},
    "num0": 0x62, "numdot": 0x63, "menu": 0x65,
}

MEDIA = {
    "next": 0x00B5, "prev": 0x00B6, "stop": 0x00B7, "playpause": 0x00CD,
    "mute": 0x00E2, "volup": 0x00E9, "voldown": 0x00EA,
    "mail": 0x018A, "calculator": 0x0192, "mycomputer": 0x0194, "browser": 0x0223,
}

TYPE_KEY = 0x00
TYPE_MEDIA = 0x02
TYPE_SYSTEM = 0x07  # a billentyűzet saját funkciói
TYPE_LIGHT = 0x08  # világításvezérlés
TYPE_FN = 0x0D
FN2_ENTRY = bytes([TYPE_FN, 0x01, 0, 0])  # a gyári programból rögzítve

# A billentyűzet saját funkciói. A zárolások a gyári program Commands füléről rögzítve,
# a többi a gyári FN1 réteg helyei és a kézikönyv alapján.
SPECIAL = {
    "lock_win": bytes([TYPE_SYSTEM, 0, 0, 0x01]),
    "lock_keyboard": bytes([TYPE_SYSTEM, 0, 0, 0x02]),
    "bt1": bytes([TYPE_SYSTEM, 0, 0, 0x05]),
    "bt2": bytes([TYPE_SYSTEM, 0, 0, 0x06]),
    "bt3": bytes([TYPE_SYSTEM, 0, 0, 0x07]),
    "2.4g": bytes([TYPE_SYSTEM, 0, 0, 0x08]),
    "mode_windows": bytes([TYPE_SYSTEM, 0, 0, 0x18]),
    "mode_android": bytes([TYPE_SYSTEM, 0, 0, 0x19]),
    "mode_mac": bytes([TYPE_SYSTEM, 0, 0, 0x1A]),
    "battery": bytes([TYPE_SYSTEM, 0, 0, 0x11]),  # Fn+B: töltöttség kijelzése a fényekkel
    "light_brighter": bytes([TYPE_LIGHT, 0x03, 0x01, 0]),
    "light_darker": bytes([TYPE_LIGHT, 0x03, 0x02, 0]),
    "light_faster": bytes([TYPE_LIGHT, 0x04, 0x01, 0]),
    "light_slower": bytes([TYPE_LIGHT, 0x04, 0x02, 0]),
    "knob": bytes([TYPE_SYSTEM, 0, 0, 0x1D]),  # a tekerő gyári lenyomás-funkciója (módváltás, némítás)
}
# Csak kiírásra: célként nem adható meg, mert egy véletlen leütés mindent töröl.
DECODE_ONLY = {"factory_reset": bytes([TYPE_SYSTEM, 0, 0, 0x04])}
_SPECIAL_NAMES = {entry: name for name, entry in {**SPECIAL, **DECODE_ONLY}.items()}


class UnknownKey(ValueError):
    pass


def physical_index(name):
    name = name.lower()
    if name not in PHYSICAL:
        raise UnknownKey(f"Ismeretlen gomb: {name}. A gombnevek listája: f75 keys")
    return PHYSICAL[name]


def encode(target):
    """Célnév -> 4 bájtos bejegyzés. Kombináció is lehet, például ctrl+shift+esc."""
    target = target.lower()
    if target in ("none", "semmi"):
        return bytes(4)
    if target == "fn":
        return bytes([TYPE_FN, 0, 0, 0])
    if target == "fn2":
        return FN2_ENTRY
    if target in SPECIAL:
        return SPECIAL[target]
    if target in MEDIA:
        code = MEDIA[target]
        return bytes([TYPE_MEDIA, 0, code >> 8, code & 0xFF])
    *mods, key = target.split("+")
    bits = 0
    for mod in mods:
        mod = MODIFIER_ALIASES.get(mod, mod)
        if mod not in MODIFIERS:
            raise UnknownKey(f"Ismeretlen módosító: {mod}")
        bits |= MODIFIERS[mod]
    if key in MODIFIERS or key in MODIFIER_ALIASES:
        return bytes([TYPE_KEY, bits | MODIFIERS[MODIFIER_ALIASES.get(key, key)], 0, 0])
    if key not in KEYCODES:
        raise UnknownKey(f"Ismeretlen cél: {key}. A célnevek listája: f75 keys")
    return bytes([TYPE_KEY, bits, 0, KEYCODES[key]])


_KEY_NAMES = {code: name for name, code in reversed(KEYCODES.items())}
_MEDIA_NAMES = {code: name for name, code in MEDIA.items()}
_MOD_NAMES = {bit: name for name, bit in MODIFIERS.items()}


def decode(entry):
    """4 bájtos bejegyzés -> olvasható név. Ismeretlen bejegyzésnél a nyers bájtok."""
    kind, bits, hi, lo = entry
    code = (hi << 8) | lo
    entry = bytes(entry)
    if entry == bytes(4):
        return "semmi"
    if entry in _SPECIAL_NAMES:
        return _SPECIAL_NAMES[entry]
    if kind == TYPE_FN and not (bits or code):
        return "fn"
    if entry == FN2_ENTRY:
        return "fn2"
    if kind == TYPE_MEDIA and not bits and code in _MEDIA_NAMES:
        return _MEDIA_NAMES[code]
    # Billentyű: a kód a 4. bájtban áll, a gyári program kombinációinál a 3.-ban.
    keycodes = [c for c in (hi, lo) if c]
    if kind == TYPE_KEY and all(c in _KEY_NAMES for c in keycodes):
        parts = [_MOD_NAMES[b] for b in sorted(_MOD_NAMES) if bits & b]
        parts += [_KEY_NAMES[c] for c in keycodes]
        return "+".join(parts)
    return "nyers " + entry.hex(" ")


# Olvasható magyar nevek a grafikus felülethez.
_LABELS = {
    "esc": "Esc", "tekerő": "Tekerő lenyomása", "backspace": "Backspace", "delete": "Delete",
    "tab": "Tab", "capslock": "Caps Lock", "enter": "Enter", "space": "Szóköz",
    "lshift": "Bal Shift", "rshift": "Jobb Shift", "lctrl": "Bal Ctrl", "rctrl": "Jobb Ctrl",
    "lalt": "Bal Alt", "altgr": "AltGr", "lwin": "Bal Windows-gomb", "rwin": "Jobb Windows-gomb",
    "fn": "Fn", "fn2": "FN2-gomb (nyomva tartva az FN2 réteg)", "semmi": "Semmi (kikapcsolt gomb)",
    "pgup": "Page Up", "pgdn": "Page Down", "home": "Home", "end": "End", "insert": "Insert",
    "up": "Fel nyíl", "down": "Le nyíl", "left": "Balra nyíl", "right": "Jobbra nyíl",
    "printscreen": "Print Screen", "scrolllock": "Scroll Lock", "pause": "Pause", "menu": "Helyi menü gomb",
    "numlock": "Num Lock", "numslash": "Num /", "numstar": "Num *", "numminus": "Num -",
    "numplus": "Num +", "numenter": "Num Enter", "numdot": "Num ,",
    "ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "win": "Windows-gomb", "ralt": "AltGr",
    "next": "Következő szám", "prev": "Előző szám", "stop": "Lejátszás leállítása",
    "playpause": "Lejátszás vagy szünet", "mute": "Némítás", "volup": "Hangerő fel",
    "voldown": "Hangerő le", "mail": "Levelezőprogram", "calculator": "Számológép",
    "mycomputer": "Sajátgép", "browser": "Böngésző kezdőlap",
    "lock_win": "Windows-gomb tiltása", "lock_keyboard": "Billentyűzet zárolása",
    "bt1": "Bluetooth 1. eszköz", "bt2": "Bluetooth 2. eszköz", "bt3": "Bluetooth 3. eszköz",
    "2.4g": "2,4 GHz-es vevő", "mode_windows": "Windows-mód", "mode_android": "Android-mód",
    "mode_mac": "Mac-mód", "battery": "Akkumulátor töltöttsége (fényekkel)",
    "light_brighter": "Világítás világosabb", "light_darker": "Világítás sötétebb",
    "light_faster": "Világítás gyorsabb", "light_slower": "Világítás lassabb",
    "knob": "Tekerő gyári funkciója (módváltás, némítás)",
    "factory_reset": "Gyári visszaállítás (nyomva tartva)",
}


def label(name):
    """Egy gomb- vagy célnév olvasható alakja; kombinációknál részenként."""
    if name in _LABELS:
        return _LABELS[name]
    if "+" in name and not name.startswith("nyers"):
        return "+".join(label(part) for part in name.split("+"))
    if len(name) == 1:
        return name.upper()
    if name.startswith("num") and name[3:].isdigit():
        return f"Num {name[3:]}"
    return name[0].upper() + name[1:]


def target_catalog():
    """A gombra tehető funkciók (csoport, olvasható név, célnév) listája."""
    items = [("Billentyű", label(n), n) for n in KEYCODES]
    items += [("Módosító", label(n), n) for n in MODIFIERS]
    items += [("Médiagomb", label(n), n) for n in MEDIA]
    items += [("Billentyűzet funkció", label(n), n) for n in SPECIAL]
    items += [("Egyéb", label(n), n) for n in ("fn", "fn2", "semmi")]
    return items
