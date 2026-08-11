"""
generuj_galerie.py
-------------------
Skanuje folder ze zdjęciami z wyjazdów, generuje zmniejszone
wersje (miniaturki + wersje do podglądu) i buduje wyjazdy.js
automatycznie na podstawie nazw folderów.

STRUKTURA WEJŚCIOWA (Ty tworzysz):

    surowe/
      Zakopane_10.08.2026/
        IMG_0001.jpg
        IMG_0002.jpg
        ...
      Gdansk_15.06.2026/
        IMG_0100.jpg
        ...

Nazwa folderu = "Miejscowość_data" (ostatni "_" oddziela datę).

STRUKTURA WYJŚCIOWA (skrypt tworzy obok siebie):

    zdjecia/
      Zakopane_10.08.2026/
        thumb/   ← małe, do siatki (ok. 480px, szybkie)
        full/    ← średnie, do podglądu (ok. 1600px)
    wyjazdy.js   ← nadpisany automatycznie

Użycie:
    pip install pillow
    python generuj_galerie.py

Bezpiecznie odpalać wielokrotnie – nadpisuje tylko to co trzeba.
"""

import re
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Brak biblioteki Pillow. Zainstaluj: pip install pillow")
    raise SystemExit(1)

SRC_DIR   = Path("surowe")      # tu wrzucasz foldery z oryginałami
OUT_ZDJ   = Path("zdjecia")     # tu lądują przeskalowane wersje
OUT_JS    = Path("wyjazdy.js")

THUMB_WIDTH = 480    # szerokość miniaturki w siatce
FULL_WIDTH  = 3200   # szerokość wersji do lightboxa
THUMB_QUALITY = 78
FULL_QUALITY  = 88

ROZSZERZENIA = {".jpg", ".jpeg", ".png", ".webp"}


def parsuj_nazwe_folderu(nazwa: str):
    """'Zakopane_10.08.2026' -> ('Zakopane', '10.08.2026')"""
    if "_" in nazwa:
        miejsce, data = nazwa.rsplit("_", 1)
        miejsce = miejsce.replace("_", " ")
    else:
        miejsce, data = nazwa, ""
    return miejsce, data


def przeskaluj_i_zapisz(sciezka_zrodlowa: Path, sciezka_docelowa: Path, szerokosc: int, jakosc: int):
    sciezka_docelowa.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(sciezka_zrodlowa) as img:
        img = ImageOps.exif_transpose(img)   # popraw obrót ze zdjęć z telefonu
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        w, h = img.size
        if w > szerokosc:
            nowa_h = int(h * (szerokosc / w))
            img = img.resize((szerokosc, nowa_h), Image.LANCZOS)

        img.save(sciezka_docelowa, "JPEG", quality=jakosc, optimize=True)


def main():
    if not SRC_DIR.exists():
        print(f"[!] Nie znaleziono folderu '{SRC_DIR}/'.")
        print(f"    Utwórz go i wrzuć podfoldery typu 'Zakopane_10.08.2026/' ze zdjęciami.")
        return

    foldery = sorted(f for f in SRC_DIR.iterdir() if f.is_dir())
    if not foldery:
        print(f"[!] Folder '{SRC_DIR}/' jest pusty.")
        return

    wyjazdy = []
    laczny_rozmiar_bajty = 0

    for folder in foldery:
        miejsce, data = parsuj_nazwe_folderu(folder.name)
        pliki = sorted(
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in ROZSZERZENIA
        )

        if not pliki:
            print(f"[!] Pominięto '{folder.name}' – brak zdjęć.")
            continue

        print(f"[·] {folder.name}  ({len(pliki)} zdjęć)")

        zdjecia_wpisy = []
        for plik in pliki:
            docelowy_thumb = OUT_ZDJ / folder.name / "thumb" / (plik.stem + ".jpg")
            docelowy_full  = OUT_ZDJ / folder.name / "full"  / (plik.stem + ".jpg")

            przeskaluj_i_zapisz(plik, docelowy_thumb, THUMB_WIDTH, THUMB_QUALITY)
            przeskaluj_i_zapisz(plik, docelowy_full,  FULL_WIDTH,  FULL_QUALITY)

            laczny_rozmiar_bajty += docelowy_thumb.stat().st_size
            laczny_rozmiar_bajty += docelowy_full.stat().st_size

            zdjecia_wpisy.append({
                "thumb": str(docelowy_thumb).replace("\\", "/"),
                "full":  str(docelowy_full).replace("\\", "/"),
            })

        wyjazdy.append({
            "nazwa": miejsce,
            "data": data,
            "zdjecia": zdjecia_wpisy,
        })

    zapisz_js(wyjazdy)

    mb = laczny_rozmiar_bajty / (1024 * 1024)
    print(f"\n[✓] Gotowe. {len(wyjazdy)} wyjazdów, przeskalowane zdjęcia: {mb:.1f} MB")
    print(f"    Zapisano '{OUT_JS}' i folder '{OUT_ZDJ}/'.")
    if mb > 900:
        print("    [!] Zbliżasz się do limitu 1GB na repozytorium GitHub Pages.")


def js_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def zapisz_js(wyjazdy: list[dict]):
    linie = ["const WYJAZDY = [\n"]
    for w in wyjazdy:
        linie.append(f'  {{\n    nazwa: "{js_string(w["nazwa"])}",\n    data: "{js_string(w["data"])}",\n    zdjecia: [\n')
        for z in w["zdjecia"]:
            linie.append(f'      {{ thumb: "{z["thumb"]}", full: "{z["full"]}" }},\n')
        linie.append("    ]\n  },\n")
    linie.append("];\n")

    OUT_JS.write_text("".join(linie), encoding="utf-8")


if __name__ == "__main__":
    main()
