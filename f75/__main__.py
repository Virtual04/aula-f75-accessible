"""AULA F75 konfigurátor, parancssoros változat.

    f75 remap capslock esc                 gomb átírása (alapból a default rétegen)
    f75 remap f1 mute --layer fn1          gomb átírása az FN1 rétegen
    f75 remap capslock ctrl+shift+esc      kombináció is lehet
    f75 reset capslock                     egy gomb vissza gyárira
    f75 reset                              minden vissza gyárira, minden rétegen
    f75 show                               az átírt gombok listája
    f75 show --all --layer fn1             egy réteg összes gombja
    f75 keys                               a használható gomb- és célnevek
    f75 sleep                              az alvási idő lekérdezése
    f75 sleep 10 / f75 sleep off           alvási idő percben, vagy kikapcsolás
    f75 macro text koszon "Üdvözlettel, User"  makró, amely begépeli a szöveget
    f75 macro set masol ctrl+c 500ms ctrl+v    makró gombokból és szünetekből
    f75 macro list / show NÉV / delete NÉV
    f75 remap f12 macro:koszon [--repeat 3 | --while-held | --until-key]
    f75 debounce / f75 debounce 3         pergésmentesítés lekérdezése, beállítása (1-5)
    f75 tap / f75 tap 69 / f75 tap off     a Tap réteg lekérdezése, érzékenysége, kikapcsolása
    f75 light                              a világítás lekérdezése
    f75 light effect neon                  effekt választása
    f75 light brightness 5                 fényerő 0-9
    f75 light speed 2                      sebesség 0-4
    f75 light color piros / ff8000 / colourful
    f75 light off / f75 light on
    f75 save fajl.json / f75 load fajl.json
    f75 apply                              a nyilvántartott gombkiosztás újraküldése
"""

import argparse
import sys

from f75 import actions, config, keys, lighting, macros
from f75.actions import send, set_light, set_setting, set_sleep, sleep_text, tap_text
from f75.device import F75, SETTING_DEBOUNCE, SETTING_SLEEP, SETTING_TAP, DeviceNotFound
from f75.keymap import LAYER_NAMES


def commit(cfg, message):
    actions.commit(cfg)
    print(message)


def cmd_remap(args):
    key, target = args.key.lower(), args.target
    if not target.startswith("macro:"):
        target = target.lower()
    options = [o for o in (args.repeat and str(args.repeat), args.while_held and "held",
                           args.until_key and "untilkey") if o]
    if options:
        if not target.startswith("macro:") or len(options) > 1:
            raise ValueError("A --repeat, --while-held és --until-key közül egy adható meg, és csak makróhoz.")
        target = f"{target}:{options[0]}"
    keys.physical_index(key)
    cfg = config.load_state()
    config.encode_target(cfg, target)
    cfg["keymap"][args.layer][key] = target
    commit(cfg, f"Kész: a {key} gomb a {args.layer} rétegen mostantól: {config.describe_target(target)}.")


def cmd_reset(args):
    cfg = config.load_state()
    if args.key is None:
        cfg["keymap"] = config.empty()["keymap"]
        commit(cfg, "A teljes gombkiosztás visszaállt a gyárira, minden rétegen. A makrók megmaradtak, "
                    "de egyik gombon sincsenek rajta.")
        return
    key = args.key.lower()
    keys.physical_index(key)
    if cfg["keymap"][args.layer].pop(key, None) is None:
        print(f"A {key} gomb a {args.layer} rétegen már eddig is a gyári beállításon volt.")
        return
    commit(cfg, f"Kész: a {key} gomb a {args.layer} rétegen visszaállt a gyárira.")


def cmd_show(args):
    cfg = config.load_state()
    if args.all:
        layer = args.layer
        table = config.build_layers(cfg)[LAYER_NAMES.index(layer)]
        print(f"A {layer} réteg összes gombja, a billentyűzet sorrendjében:")
        for key, i in keys.PHYSICAL.items():
            if key in cfg["keymap"][layer]:
                print(f"{key}: {config.describe_target(cfg['keymap'][layer][key])}, átírva")
            else:
                print(f"{key}: {keys.decode(table[i * 4:i * 4 + 4])}")
        return
    changed = [(layer, key, target) for layer in config.EDITABLE_LAYERS
               for key, target in cfg["keymap"][layer].items()]
    if not changed:
        print("Nincs átírt gomb, minden a gyári beállításon van.")
    else:
        print(f"Átírt gombok száma: {len(changed)}.")
        for layer, key, target in changed:
            print(f"{layer} réteg, {key}: {config.describe_target(target)}")
    print("Megjegyzés: ez a program nyilvántartása. Ha a billentyűzetet a gyári programmal vagy "
          "Fn+Esc-pel módosítottad, az f75 apply újra ezt küldi el.")


def cmd_keys(args):
    print("Gombok, amelyek rajta vannak a billentyűzeten. Ezeket lehet átírni:")
    print(", ".join(keys.PHYSICAL))
    print()
    print("Amit egy gombra rá lehet tenni. Ezek nem fizikai gombok, hanem amit a gomb a gépnek küld.")
    print("Billentyűk:")
    print(", ".join(keys.KEYCODES))
    print()
    print("Módosítók:")
    print(", ".join([*keys.MODIFIERS, *keys.MODIFIER_ALIASES]))
    print()
    print("Médiagombok:")
    print(", ".join(keys.MEDIA))
    print()
    print("A billentyűzet saját funkciói (Windows-gomb tiltása, zárolás, Bluetooth-hely, 2,4 GHz, "
          "rendszermód, világítás):")
    print(", ".join(keys.SPECIAL))
    print()
    print("Egyéb: fn, fn2, semmi. Kombináció pluszjellel: ctrl+c, ctrl+shift+esc, win+e.")
    print("Az fn2 gomb nyomva tartása az FN2 réteget kapcsolja be.")


def cmd_sleep(args):
    with F75() as kb:
        if args.minutes is None:
            current = kb.read_settings()[SETTING_SLEEP] / 2
            print(f"Alvási idő: {sleep_text(current)}. Csak vezeték nélküli módban érvényes.")
            return
        value = args.minutes.lower().replace(",", ".")
        minutes = 0 if value in ("off", "ki") else float(value)
        if minutes not in config.SLEEP_MINUTES:
            allowed = ", ".join(sleep_text(m) for m in config.SLEEP_MINUTES[1:])
            raise ValueError(f"Ez az érték nem választható. Lehetséges: off, {allowed}.")
        set_sleep(kb, minutes)
    cfg = config.load_state()
    cfg["sleep"] = minutes
    config.save_state(cfg)
    print(f"Kész: alvási idő: {sleep_text(minutes)}. Csak vezeték nélküli módban érvényes.")


def cmd_macro(args):
    cfg = config.load_state()
    action, name = args.action, args.name
    if action == "list":
        if not cfg["macros"]:
            print("Nincs makró.")
        for n, macro in cfg["macros"].items():
            kind = f'szöveg: {macro["text"]}' if "text" in macro else f'lépések: {macro["steps"]}'
            used = ", ".join(f"{k} ({layer})" for layer, k in config.macro_users(cfg, n)) or "nincs gombon"
            print(f"{n}: {kind}. Gombon: {used}.")
        return
    if not name:
        raise ValueError(f"Hiányzik a makró neve: f75 macro {action} NÉV")
    if action == "show":
        if name not in cfg["macros"]:
            raise ValueError(f"Nincs ilyen makró: {name}")
        for line in macros.describe_events(macros.events_of(cfg["macros"][name])):
            print(line)
        return
    if action == "delete":
        if name not in cfg["macros"]:
            raise ValueError(f"Nincs ilyen makró: {name}")
        users = config.macro_users(cfg, name)
        if users:
            listed = ", ".join(f"{k} ({layer})" for layer, k in users)
            raise ValueError(f"A makró gombon van: {listed}. Előbb állítsd vissza: f75 reset GOMB")
        del cfg["macros"][name]
        message = f"A {name} makró törölve."
    else:
        content = " ".join(args.content)
        if not content:
            raise ValueError(f"Hiányzik a makró tartalma: f75 macro {action} {name} ...")
        cfg["macros"][name] = {"text": content} if action == "text" else {"steps": content}
        config.validate(cfg)
        events = macros.events_of(cfg["macros"][name])
        message = f"A {name} makró elmentve, {len(events)} lépés."
    if config.macro_users(cfg, name) or action == "delete":
        commit(cfg, message + " A billentyűzetre is elküldve.")
    else:
        config.save_state(cfg)
        print(message + f" Gombra tenni így lehet: f75 remap GOMB macro:{name}")


def cmd_debounce(args):
    with F75() as kb:
        if args.stage is None:
            print(f"Pergésmentesítés: {kb.read_settings()[SETTING_DEBOUNCE] + 1}. fokozat az 5-ből.")
            return
        if not args.stage.isdigit() or int(args.stage) not in config.DEBOUNCE_STAGES:
            raise ValueError("A pergésmentesítés fokozata 1 és 5 közötti egész szám lehet.")
        stage = int(args.stage)
        set_setting(kb, SETTING_DEBOUNCE, stage - 1)
    cfg = config.load_state()
    cfg["debounce"] = stage
    config.save_state(cfg)
    print(f"Kész: pergésmentesítés: {stage}. fokozat.")


def cmd_tap(args):
    with F75() as kb:
        if args.value is None:
            print(f"Tap réteg: {tap_text(kb.read_settings()[SETTING_TAP])}.")
            return
        value = args.value.lower()
        if value in ("off", "ki"):
            sensitivity = 0
        elif value in ("on", "be"):
            sensitivity = config.load_state().get("tap") or 69
        elif value.isdigit() and int(value) in config.TAP_SENSITIVITY:
            sensitivity = int(value)
        else:
            raise ValueError("A Tap érzékenysége 10 és 127 közötti egész szám lehet, vagy on, vagy off.")
        set_setting(kb, SETTING_TAP, sensitivity)
    cfg = config.load_state()
    cfg["tap"] = sensitivity
    config.save_state(cfg)
    print(f"Kész: Tap réteg: {tap_text(sensitivity)}.")


def cmd_light(args):
    cfg = config.load_state()
    with F75() as kb:
        if args.action is None:
            block = kb.read_settings()
            for line in lighting.describe(block, config.color_table(cfg)):
                print(line)
            return
        action, value = args.action.lower(), args.value
        if action in ("off", "ki"):
            set_light(kb, cfg, effect="off")
        elif action in ("on", "be"):
            last = cfg.get("light", {}).get("effect", "off")
            set_light(kb, cfg, effect=last if last != "off" else "neon")
        elif value is None:
            raise ValueError(f"Hiányzik az érték: f75 light {action} ÉRTÉK")
        elif action == "effect":
            if value.lower() not in lighting.EFFECTS:
                raise ValueError("Ismeretlen effekt. Lehetséges: " + ", ".join(lighting.EFFECTS))
            set_light(kb, cfg, effect=value.lower())
        elif action == "brightness":
            set_light(kb, cfg, brightness=parse_range(value, lighting.MAX_BRIGHTNESS, "fényerő"))
        elif action == "speed":
            set_light(kb, cfg, speed=parse_range(value, lighting.MAX_SPEED, "sebesség"))
        elif action == "color":
            value = value.lower()
            if value != "colourful":
                lighting.parse_color(value)
            set_light(kb, cfg, color=value)
        else:
            raise ValueError("Ismeretlen világítás-parancs. Lehetséges: effect, brightness, speed, color, on, off")
        block = kb.read_settings()
        print("Kész. A billentyűzet szerint most:")
        for line in lighting.describe(block, config.color_table(cfg)):
            print(line)
    config.save_state(cfg)


def parse_range(text, maximum, label):
    if not text.isdigit() or int(text) > maximum:
        raise ValueError(f"A {label} 0 és {maximum} közötti egész szám lehet.")
    return int(text)


def cmd_save(args):
    cfg = config.load_state()
    try:
        with F75() as kb:
            cfg.update(actions.read_settings(kb, cfg))
            cfg["colors"] = config.color_table(cfg).hex()
    except (DeviceNotFound, OSError):
        print("A billentyűzet nem érhető el, az alvást és a világítást a nyilvántartásból mentem.")
    config.write(cfg, args.file)
    print(f"A konfiguráció elmentve: {args.file}")


def cmd_load(args):
    cfg = config.read(args.file)
    send(cfg, with_settings=True)
    config.save_state(cfg)
    print(f"A konfiguráció betöltve és elküldve: {args.file}")


def cmd_apply(args):
    # Csak a gombkiosztás: a világítás, az alvás és a pergésmentesítés a billentyűzetben
    # tárolódik, és közben Fn-kombinációkkal is változhatott, ezért azokhoz nem nyúlunk.
    send(config.load_state())
    print("A nyilvántartott gombkiosztás elküldve a billentyűzetre.")


def main():
    parser = argparse.ArgumentParser(prog="f75", description="AULA F75 konfigurátor")
    sub = parser.add_subparsers(dest="command", required=True)
    layer_arg = dict(choices=config.EDITABLE_LAYERS, default="default", help="réteg: default, fn1, fn2 vagy tap")

    p = sub.add_parser("remap", help="gomb átírása")
    p.add_argument("key")
    p.add_argument("target")
    p.add_argument("--layer", **layer_arg)
    p.add_argument("--repeat", type=int, help="makró: ennyiszer fusson le (1-255)")
    p.add_argument("--while-held", action="store_true", help="makró: ismétlés, amíg nyomva tartod")
    p.add_argument("--until-key", action="store_true", help="makró: ismétlés a következő leütésig")
    p.set_defaults(func=cmd_remap)

    p = sub.add_parser("macro", help="makrók: list, show, text, set, delete")
    p.add_argument("action", choices=["list", "show", "text", "set", "delete"])
    p.add_argument("name", nargs="?")
    p.add_argument("content", nargs="*")
    p.set_defaults(func=cmd_macro)

    p = sub.add_parser("reset", help="egy gomb vagy minden visszaállítása gyárira")
    p.add_argument("key", nargs="?")
    p.add_argument("--layer", **layer_arg)
    p.set_defaults(func=cmd_reset)

    p = sub.add_parser("show", help="az átírt gombok, vagy --all esetén egy réteg összes gombja")
    p.add_argument("--all", action="store_true")
    p.add_argument("--layer", **layer_arg)
    p.set_defaults(func=cmd_show)

    sub.add_parser("keys", help="a használható nevek").set_defaults(func=cmd_keys)

    p = sub.add_parser("sleep", help="alvási idő lekérdezése vagy beállítása (perc, vagy off)")
    p.add_argument("minutes", nargs="?")
    p.set_defaults(func=cmd_sleep)

    p = sub.add_parser("debounce", help="pergésmentesítés lekérdezése vagy beállítása (1-5)")
    p.add_argument("stage", nargs="?")
    p.set_defaults(func=cmd_debounce)

    p = sub.add_parser("tap", help="a Tap réteg lekérdezése, be- és kikapcsolása, érzékenysége (10-127)")
    p.add_argument("value", nargs="?")
    p.set_defaults(func=cmd_tap)

    p = sub.add_parser("light", help="világítás: effect, brightness, speed, color, on, off")
    p.add_argument("action", nargs="?")
    p.add_argument("value", nargs="?")
    p.set_defaults(func=cmd_light)

    p = sub.add_parser("save", help="konfiguráció mentése fájlba")
    p.add_argument("file")
    p.set_defaults(func=cmd_save)

    p = sub.add_parser("load", help="konfiguráció betöltése fájlból és elküldése")
    p.add_argument("file")
    p.set_defaults(func=cmd_load)

    sub.add_parser("apply", help="a nyilvántartott gombkiosztás újraküldése").set_defaults(func=cmd_apply)

    args = parser.parse_args()
    try:
        args.func(args)
    except (DeviceNotFound, keys.UnknownKey, ValueError, OSError) as e:
        print(f"Hiba: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
