# AULA F75 konfigurátor

Akadálymentes beállítóprogram az AULA F75 billentyűzethez, a gyári program helyett. Vak felhasználó számára készült, képernyőolvasóval (NVDA) jól használható: a grafikus felülete natív Windows-vezérlőkből áll, a parancssoros változat minden kimenete egyszerű szöveg.

Funkciók: gombkiosztás négy rétegen (Default, FN1, FN2, Tap), makrók, alvási idő, pergésmentesítés, Tap (kettős funkció), világítás, mentés és betöltés fájlba. A magyar ISO kiosztást helyesen kezeli, a gyári programmal ellentétben.

## English summary

An accessible replacement for the AULA F75 keyboard's vendor configuration software, made by and for a blind user. It works well with screen readers (NVDA): the GUI uses native Windows controls (wxPython), and there is a plain-text command-line tool. Features: key remapping on all four layers, macros, sleep time, debounce, tap/hold dual function, lighting, and saving/loading the configuration as JSON. The protocol was reverse engineered from USB captures; see `research/protokoll.md` (Hungarian). The user interface is Hungarian, and key names follow the Hungarian ISO layout; other layouts and firmware versions are untested.

## Figyelmeztetés

- Ez nem az AULA hivatalos programja, és a gyártó nem támogatja. Mindenki a saját felelősségére használja.
- Csak a magyar ISO kiosztású AULA F75-tel (USB 258a:010c), V11.0.4-es firmware-rel próbáltuk ki. Más változatokkal és firmware-ekkel nem biztos, hogy működik.
- A program csak beállításokat küld a billentyűzetnek, firmware-t soha nem ír.
- Vészmegoldás: az Fn és az Esc 3 másodpercig nyomva tartva visszaállítja a billentyűzet gyári állapotát.

## Letöltés és telepítés

A telepítő a GitHub Releases oldalán tölthető le. Rendszergazdai jogot nem kér. Mivel nincs digitálisan aláírva, a Windows SmartScreen figyelmeztethet: ilyenkor a „További információ”, majd a „Futtatás mindenképp” választandó.

Telepítés után a program a Start menüből indul („AULA F75 beállítások”). Ha a telepítéskor bejelölted, az `f75` parancs bármelyik parancssorból elérhető.

## Fontos tudnivalók

- A billentyűzetnek vezetékes módban kell lennie, a kapcsoló középső állásában.
- A gyári program ne fusson egyszerre ezzel a programmal.
- A gyári program minden mentéskor ANSI kiosztást ír a billentyűzetre, ezzel elrontja a magyar kiosztást: az í, az ű, az AltGr és az Fn rossz helyre kerül. Ha mégis használtad, utána futtasd le: `f75 apply`
- Vészmegoldás: az Fn és az Esc 3 másodpercig nyomva tartva visszaállítja a billentyűzet gyári állapotát.

## A grafikus felület

Az ablaknak három füle van, a fülek között Ctrl+Tab-bal lehet váltani. Minden módosítás után az ablak alján rövid visszajelzés jelenik meg, amelyet az NVDA magától felolvas.

- **Gombkiosztás:** a Réteg mezőben (Alt+R) választható ki a réteg, alatta a Gombok listában (Alt+G) soronként egy gomb látható, mellette a funkciója, és hogy gyári vagy átírt.
  - Enter: a gomb átírása. A megnyíló ablakban a keresőmezőbe gépelve szűkül a funkciók listája; kombináció (például ctrl+shift+esc) is megadható, makrónál az ismétlés is beállítható.
  - Delete: a gomb visszaállítása gyárira.
  - A Minden gyárira gomb az egész kiosztást visszaállítja, előtte rákérdez.
- **Makrók:** a makrók listája, Új szövegmakró, Új lépésmakró, Szerkesztés, Törlés és Lépések megjelenítése gombokkal. A makrót a Gombkiosztás fülön lehet gombra tenni.
- **Beállítások:** alvási idő, pergésmentesítés, Tap, és a világítás (be/ki, effekt, fényerő, sebesség, szín). Az Alkalmazás gomb küldi el őket, a Kiolvasás a billentyűzetből gomb betölti az aktuális állapotot.
- **Fájl menü:** Mentés fájlba (Ctrl+S), Betöltés fájlból (Ctrl+O), Gombkiosztás újraküldése (Ctrl+R).

## Parancssoros használat

A telepített változatnál az `f75` parancs bárhonnan kiadható. A forráskódból futtatva a projektmappában kell kiadni, PowerShellben `.\` előtaggal, például `.\f75 show`. A grafikus felület forrásból az `f75gui` paranccsal indul.

## Gombkiosztás

- `f75 remap capslock esc`: a Caps Lock Escape lesz, a Default rétegen.
- `f75 remap f1 mute --layer fn1`: az Fn+F1 némít. A réteg lehet default, fn1, fn2 vagy tap.
- `f75 remap capslock ctrl+shift+esc`: kombináció is megadható, pluszjellel.
- `f75 remap capslock fn2`: a Caps Lock FN2-gomb lesz. Nyomva tartva az FN2 réteg kapcsol be, amelyet a `--layer fn2` kapcsolóval lehet kiosztani. A gyári billentyűzeten nincs FN2-gomb.
- `f75 remap capslock capslock --layer tap`: kettős funkció. Ha a Tap be van kapcsolva, a gomb rövid leütésre a Tap réteg funkcióját adja, nyomva tartva a Default rétegét. Például a `f75 remap capslock fn2` paranccsal együtt a Caps Lock röviden leütve Caps Lock, nyomva tartva FN2-gomb. A rövid leütés funkciója csak a gomb felengedésekor megy ki.
- `f75 reset capslock`: egy gomb visszaállítása gyárira. Rétegnél itt is használható a `--layer`.
- `f75 reset`: a teljes gombkiosztás visszaállítása gyárira, minden rétegen.
- `f75 show`: az átírt gombok listája.
- `f75 show --all --layer fn1`: egy réteg összes gombja, soronként egy.
- `f75 keys`: a gombok és a rájuk tehető funkciók neve.
- `f75 apply`: a program által nyilvántartott gombkiosztás újraküldése.

A gombnevek a magyar kiosztás szerint értendők: a `z` az a gomb, amelyik Z-t ír, a `0` az 1-es melletti gomb, az ékezetes betűk a saját nevükön szerepelnek. A szóköz utáni két gomb neve `altgr` és `fn`, a tekerő lenyomásáé `tekerő`.

A gombkiosztást a billentyűzetből nem lehet kiolvasni, ezért a program nyilvántartja, mit írtál át. A nyilvántartás helye: `%APPDATA%\F75Konfig\allapot.json`.

## Makrók

- `f75 macro text koszon "Üdvözlettel, User"`: makró, amely begépeli a szöveget a magyar kiosztás szerint, ékezetekkel, nagybetűkkel és a gyakori jelekkel (például @, #, €).
- `f75 macro set masol ctrl+c 500ms ctrl+v`: makró gombokból és kombinációkból, szóközzel elválasztva. Az `500ms` szünet.
- `f75 macro list`: a makrók listája, és hogy melyik gombon vannak.
- `f75 macro show koszon`: egy makró lépései.
- `f75 macro delete koszon`: makró törlése. Csak akkor lehet, ha egyik gombon sincs rajta.
- `f75 remap j macro:koszon --layer fn1`: a makró gombra tétele, itt az Fn+J-re.
  - `--repeat 3`: háromszor fut le.
  - `--while-held`: addig ismétlődik, amíg nyomva tartod a gombot.
  - `--until-key`: addig ismétlődik, amíg meg nem nyomsz egy másik gombot.

Az összes makró együtt legfeljebb 512 bájt lehet, ez nagyjából 100 begépelt karakter. A nagybetűk és a jelek kétszer annyi helyet foglalnak, mint a kisbetűk.

## Alvás, pergésmentesítés, világítás

Ezek a billentyűzetben tárolódnak, és kiolvashatók.

- `f75 sleep`: az alvási idő lekérdezése. Csak vezeték nélküli módban érvényes.
- `f75 sleep 10`: az alvási idő percben. Lehetséges: 1; 1,5; 2; 3; 4; 5; 10; 15; 20.
- `f75 sleep off`: az alvás kikapcsolása.
- `f75 debounce`: a pergésmentesítés lekérdezése.
- `f75 debounce 3`: a pergésmentesítés fokozata, 1 és 5 között.
- `f75 tap`: a Tap (kettős funkció) lekérdezése.
- `f75 tap 40`: a Tap bekapcsolása, érzékenysége 10 és 127 között. Minél nagyobb a szám, annál hosszabb ideig számít egy leütés rövidnek. 10-nél fél másodperc már nyomva tartásnak számít, 69-nél egy másodperc még rövid leütésnek.
- `f75 tap off`, `f75 tap on`: a Tap ki- és bekapcsolása.
- `f75 light`: a világítás lekérdezése.
- `f75 light effect neon`: effekt választása. Az effektek: off, fixed, respire, rainbow, flash_away, raindrops, ripples, stars, snake, neon, reaction, sine_wave, windmill, waterfall, blossoming, self_define.
- `f75 light brightness 5`: fényerő, 0 és 9 között.
- `f75 light speed 2`: sebesség, 0 és 4 között.
- `f75 light color piros`: szín névvel (piros, zöld, kék, sárga, lila, türkiz, fehér, narancs), hexadecimálisan (például ff8000), vagy `colourful` a többszínű módhoz.
- `f75 light off`, `f75 light on`: a világítás ki- és bekapcsolása.

A fényerő, a sebesség és a szín mindig az éppen kiválasztott effektre vonatkozik.

## Mentés és betöltés

- `f75 save beallitasaim.json`: minden beállítás mentése fájlba.
- `f75 load beallitasaim.json`: minden beállítás betöltése fájlból és elküldése a billentyűzetre.

## Futtatás forráskódból

Python 3.14 kell hozzá. A projektmappában:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## A projekt felépítése

- `f75`: maga a program.
- `tools`: a protokoll visszafejtéséhez használt eszközök (USB-rögzítés, a gyári program vezérlése, elemzés).
- `research`: a visszafejtett protokoll leírása (`research\protokoll.md`). A gyári program fájljai szerzői jogi okokból nincsenek a tárolóban; a fejlesztéshez a gyári program `Dev\kb` mappájából a `research\gyari` mappába lehet másolni őket.
- `captures`: az USB-felvételek. A leütéseket a rögzítő kiszűri belőlük.

## Telepítő készítése

Kell hozzá a PyInstaller (`.venv\Scripts\python.exe -m pip install pyinstaller`) és az Inno Setup 6 (`winget install JRSoftware.InnoSetup --scope user`). Utána a projektmappában:

```
packaging\build.cmd
```

Az eredmény: `build\installer\AULA_F75_beallitasok_telepito_1.0.0.exe`.

## Licenc

MIT, lásd a `LICENSE` fájlt.
