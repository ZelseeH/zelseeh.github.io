"""
generuj_zdjecia.py
------------------
Skanuje folder "zdjecia/" i generuje plik zdjecia.js
gotowy do wklejenia na stronę dla Lidii.

Użycie:
    python generuj_zdjecia.py

Skrypt nadpisuje zdjecia.js – najpierw zrób kopię jeśli już
dodawałeś opisy ręcznie.
"""

import os
import re
from pathlib import Path

FOLDER_ZDJECII = "zdjecia"
PLIK_WYJSCIOWY = "zdjecia.js"
ROZSZERZENIA   = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def wyciagnij_rok(nazwa: str) -> str:
    """Próbuje wyciągnąć rok z nazwy pliku, np. IMG_20230814 → 2023."""
    m = re.search(r"(20\d{2}|19\d{2})", nazwa)
    return m.group(1) if m else ""


def zbierz_zdjecia(folder: str) -> list[dict]:
    p = Path(folder)
    if not p.exists():
        print(f"[!] Folder '{folder}/' nie istnieje. Utwórz go i wrzuć tam zdjęcia.")
        return []

    pliki = sorted(
        f for f in p.iterdir()
        if f.is_file() and f.suffix.lower() in ROZSZERZENIA
    )

    if not pliki:
        print(f"[!] W folderze '{folder}/' nie ma żadnych zdjęć.")
        return []

    print(f"[✓] Znaleziono {len(pliki)} zdjęć w '{folder}/'")
    return [
        {
            "src":       f"{folder}/{f.name}",
            "opis":      "",
            "data":      wyciagnij_rok(f.stem),
            "kategoria": "",
        }
        for f in pliki
    ]


def formatuj_wpis(z: dict, idx: int) -> str:
    src       = z["src"]
    opis      = z["opis"]
    data      = z["data"]
    kategoria = z["kategoria"]

    # wyrównaj komentarz z numerem
    nr = f"  /* {idx+1:>3} */"

    return (
        f"{nr} "
        f'{{ src: "{src}", '
        f'opis: "{opis}", '
        f'data: "{data}", '
        f'kategoria: "{kategoria}" }},'
    )


def generuj_js(zdjecia: list[dict]) -> str:
    naglowek = """\
/*
  ============================================================
  zdjecia.js  –  WYGENEROWANE AUTOMATYCZNIE
  ============================================================
  Uzupełnij pola:
    opis      – podpis pod zdjęciem
    data      – rok lub pełna data, np. "lipiec 2022"
    kategoria – do filtrowania, np. "wakacje"  (zostaw "" żeby pominąć)

  Nie zmieniaj pola src – to ścieżka do pliku.
  ============================================================
*/

const ZDJECIA = [
"""
    stopka = """\
];

/*
  KATEGORIE – wpisz tu unikalne wartości z pola "kategoria" wyżej.
  Kolejność = kolejność przycisków filtrów na stronie.
  Zostaw [] żeby wyłączyć filtry.
*/
const KATEGORIE = [
  // "wakacje",
  // "zima",
  // "początki",
];
"""
    wpisy = "\n".join(formatuj_wpis(z, i) for i, z in enumerate(zdjecia))
    return naglowek + wpisy + "\n" + stopka


def main():
    zdjecia = zbierz_zdjecia(FOLDER_ZDJECII)

    if not zdjecia:
        return

    js = generuj_js(zdjecia)

    with open(PLIK_WYJSCIOWY, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"[✓] Zapisano '{PLIK_WYJSCIOWY}' – {len(zdjecia)} wpisów")
    print(f"    Otwórz plik i uzupełnij pola 'opis', 'data', 'kategoria'.")
    print(f"    Potem edytuj tablicę KATEGORIE na dole pliku.")


if __name__ == "__main__":
    main()
