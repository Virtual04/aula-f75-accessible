# Az AULA F75 konfigurációs protokollja

Az USB-felvételekből (captures mappa) visszafejtve. Firmware: V11.0.4.

## Csatorna

- USB 258a:010c, 1-es interfész, a 0xFF00 usage page-ű gyűjtemények közül a Col06 (520 bájtos feature report).
- Minden parancs egy 520 bájtos feature report, azonosítója 6.
- Fejléc, 8 bájt: 06, parancs, index, 00, 01, 00, hossz kisebb helyiértékű bájtja, hossz nagyobb helyiértékű bájtja. Utána az adat, a végén nullákkal kitöltve.
- Olvasásnál a gép elküldi a kérést (SET_REPORT), majd visszaolvassa a választ (GET_REPORT). A válasz fejléce ugyanaz, mint a kérésé.
- Két küldés között legalább 0,1 másodpercet várni kell, a program 0,25-öt vár. Gyorsabb küldésnél a billentyűzet egyszer újracsatlakozott.

## Parancsok

- 82, index 1, hossz 6: azonosítás. A válasz végén 03 00 00 00 00 cd, ez a gyári program Dev\kb\1\KB.ini fájljának Psd sora.
- 03, index 0-3, hossz 512: a gombkiosztás írása, rétegenként (0 Default, 1 FN1, 2 FN2, 3 Tap). A gyári program csak a megváltozott rétegeket küldi. Kiolvasni nem lehet.
- 84, index 0, hossz 128: a beállításblokk kiolvasása.
- 04, index 0, hossz 128: a beállításblokk írása.
- 0A, index 0, hossz 512: az effektek színtáblájának írása. A gyári program minden világítás-mentés után küldi.
- 05, index 0, hossz = az adat hossza: az összes makró (lásd lent). A gyári program a gombkiosztás után küldi, ha van makró gombon.
- 06, index 0, hossz 384: gombonkénti színek (Self-define effekt), gombonként 3 bájt. Nincs beépítve.

## Gombkiosztás

- Rétegenként 128 bejegyzés, egyenként 4 bájt, a mátrix sorrendjében. A 127. bejegyzés mindig 00 00 5a a5.
- A mátrixhely: oszlop * 6 + sor. A helyek a KB.ini fájlból valók, az ISO-gombok próbával kiderítve: 75 = ű, 76 = í.
- A magyar billentyűzeten az 53-as hely AltGr, az 59-es Fn. A gyári program ide Fn-t és jobb Ctrl-t ír.
- Egy bejegyzés: típus, módosítóbitek, két kódbájt.
  - 00: billentyű. Módosítóbitek: 01 bal Ctrl, 02 bal Shift, 04 bal Alt, 08 bal Win, 10 jobb Ctrl, 20 jobb Shift, 40 AltGr, 80 jobb Win. A HID-billentyűkód a 4. bájtban áll; a gyári program kombinációinál a 3.-ban.
  - 02: médiagomb, a HID consumer kód a 3. és a 4. bájtban.
  - 03: makró. 03, mód (01 ismétlésszámszor, 02 a következő leütésig, 04 amíg nyomva tartod), ismétlésszám, a makró sorszáma.
  - 07: a billentyűzet saját funkciói. 01 Windows-gomb tiltása, 02 billentyűzet zárolása, 04 gyári visszaállítás, 05-07 Bluetooth 1-3, 08 2,4 GHz, 18 Windows-mód, 19 Android-mód, 1a Mac-mód, 1d a tekerő lenyomása. Ismeretlen: 0a (Fn+G), 11 (Fn+B).
  - 08: világításvezérlés. 03 01 világosabb, 03 02 sötétebb, 04 01 és 04 02 valószínűleg gyorsabb és lassabb. Ismeretlen: 02 00 (Fn+Tab), 00 01 (Fn+bal Shift).
  - 0d 00 00 00: Fn. 0d 01 00 00: FN2 (az FN2 réteget kapcsolja be). A gyári program az FN2-gombot a Default, az FN1 és az FN2 rétegen is ugyanarra a helyre írja.

## Beállításblokk (128 bájt)

- 3: pergésmentesítés, a fokozat mínusz egy (0-4).
- 9: 1, ha a Self-define effekt aktív.
- 10: a fényeffekt kódja. 0 ki, 1 fixed, 2 respire, 3 rainbow, 4 flash_away, 5 raindrops, 7 ripples, 8 stars, 10 snake, 11 neon, 12 reaction, 13 sine_wave, 15 windmill, 16 waterfall, 17 blossoming, 21 self_define.
- 22: a Tap réteg érzékenysége, 10-127, 0 = kikapcsolva. Bekapcsolva a Tap rétegen kiosztott gomb rövid leütésre a Tap réteg funkcióját adja (felengedéskor, ismétlés nélkül), nyomva tartva a Default rétegét. Az érték a rövid leütés időkorlátja: 10-nél 0,5 mp már nyomva tartás, 69-nél 1 mp még rövid leütés.
- 24: alvási idő, a perc kétszerese. 0 = kikapcsolva.
- 56 + 2 * effekt: az effekt fényereje, 0-9.
- 57 + 2 * effekt: a felső 4 bit a sebesség (0-4), az alsó 4 bit a használt színhely (0-6), vagy 7 = Colourful.
- 126-127: 5a a5.

A gyári program a blokk más bájtjait is felülírja a saját állapotából. Ez a program csak a módosítandó bájtot változtatja.

## Makrók (05-ös parancs)

- Fejléc: makrónként 2 bájt kezdőhely és 2 bájt hossz, kisebb helyiérték elöl. A kezdőhely az adat elejétől számít.
- Makrónként: 1 bájt névhossz (bájtban), a név UTF-16LE kódolással, majd a lépések.
- Lépés, 4 bájt: jelző (00 lenyomás, 80 felengedés, +10 a módosítóbillentyűknél, HID e0-e7), várakozás ezredmásodpercben 2 bájton (nagyobb helyiérték elöl!), HID-billentyűkód.
- A sorszám a makró helye a csomagban.
- 512 bájtnál nagyobb makróadatot nem rögzítettünk; lehet, hogy a parancs indexe a folytatásra szolgál.
- A gyári program makrószerkesztőben történő mentéskor semmit nem küld.

## Színtábla (512 bájt)

- Effektenként 7 színhely, egyenként 3 bájt (R, G, B). Az effekt része a 21 * effekt helyen kezdődik.
- 506-507: 5a a5.
- Kiolvasni nem lehet, ezért a program nyilvántartja.
