"""Billentyűzetműveletek, amelyeket a parancssoros és a grafikus felület is használ."""

from f75 import config, lighting, macros
from f75.device import F75, SETTING_DEBOUNCE, SETTING_SLEEP, SETTING_TAP


def send(cfg, with_settings=False):
    """A gombkiosztás és a makrók elküldése; with_settings esetén a konfigurációban
    szereplő alvás, pergésmentesítés, Tap és világítás is."""
    with F75() as kb:
        kb.write_keymap(config.build_layers(cfg))
        if cfg["macros"]:
            kb.write_macros(macros.build_blob(cfg["macros"]))
        if with_settings and "sleep" in cfg:
            set_sleep(kb, cfg["sleep"])
        if with_settings and "debounce" in cfg:
            set_setting(kb, SETTING_DEBOUNCE, cfg["debounce"] - 1)
        if with_settings and "tap" in cfg:
            set_setting(kb, SETTING_TAP, cfg["tap"])
        if with_settings and "light" in cfg:
            apply_light(kb, cfg)


def commit(cfg):
    """A gombkiosztás elküldése és a nyilvántartás mentése."""
    send(cfg)
    config.save_state(cfg)


def set_setting(kb, index, value):
    """Egyetlen bájt módosítása a beállításblokkban: kiolvasás, módosítás, visszaírás."""
    block = kb.read_settings()
    block[index] = value
    kb.write_settings(block)


def set_sleep(kb, minutes):
    set_setting(kb, SETTING_SLEEP, int(minutes * 2))


def read_settings(kb, cfg):
    """A billentyűzetben tárolt beállítások a konfigurációs fájl formájában."""
    block = kb.read_settings()
    return {
        "sleep": block[SETTING_SLEEP] / 2,
        "debounce": block[SETTING_DEBOUNCE] + 1,
        "tap": block[SETTING_TAP],
        "light": light_from_block(block, config.color_table(cfg)),
    }


def light_from_block(block, table):
    """A billentyűzet aktuális világítása a konfigurációs fájl formájában."""
    effect = block[lighting.SETTING_EFFECT]
    name = lighting.EFFECT_NAMES.get(effect)
    if name is None:
        raise ValueError(f"Ismeretlen effektkód a billentyűzetben: {effect}")
    if effect == 0:
        return {"effect": "off"}
    mode = block[lighting.mode_index(effect)]
    slot = mode & 0x0F
    color = "colourful" if slot == lighting.COLOURFUL else \
        table[21 * effect + 3 * slot:21 * effect + 3 * slot + 3].hex()
    return {"effect": name, "brightness": block[lighting.brightness_index(effect)],
            "speed": mode >> 4, "color": color}


def set_light(kb, cfg, effect=None, brightness=None, speed=None, color=None):
    """Kiolvassa a beállításblokkot, módosítja a világítást, visszaírja, és elküldi a színtáblát,
    ahogy a gyári program. A konfigurációban frissíti a világítást és a színtáblát."""
    block = kb.read_settings()
    table = config.color_table(cfg)
    if effect is not None:
        block[lighting.SETTING_EFFECT] = lighting.EFFECTS[effect]
        block[lighting.SETTING_SELF_DEFINE] = 1 if effect == "self_define" else 0
    code = block[lighting.SETTING_EFFECT]
    if code == 0 and (brightness, speed, color) != (None, None, None):
        raise ValueError("A világítás ki van kapcsolva. Előbb kapcsold be.")
    if brightness is not None:
        block[lighting.brightness_index(code)] = brightness
    if speed is not None:
        i = lighting.mode_index(code)
        block[i] = (speed << 4) | (block[i] & 0x0F)
    if color is not None:
        i = lighting.mode_index(code)
        if color == "colourful":
            block[i] = (block[i] & 0xF0) | lighting.COLOURFUL
        else:
            table[21 * code:21 * code + 3] = lighting.parse_color(color)
            block[i] = block[i] & 0xF0
    kb.write_settings(block)
    if code != lighting.EFFECTS["self_define"]:
        kb.write_colors(table)
    cfg["colors"] = table.hex()
    cfg["light"] = light_from_block(block, table)
    return block, table


def apply_light(kb, cfg):
    light = cfg["light"]
    if light["effect"] == "off":
        set_light(kb, cfg, effect="off")
    else:
        set_light(kb, cfg, effect=light["effect"], brightness=light["brightness"],
                  speed=light["speed"], color=light["color"])


def sleep_text(minutes):
    return "kikapcsolva" if minutes == 0 else f"{minutes:g} perc".replace(".", ",")


def tap_text(value):
    return "kikapcsolva" if value == 0 else f"bekapcsolva, érzékenység {value} (10-127)"
