"""
edytor_zdjec.py
---------------
GUI do przeglądania i opisywania zdjęć.
Odpal z folderu repozytorium:

    python edytor_zdjec.py

Przy starcie wczytuje istniejący zdjecia.js (zachowuje opisy).
Na koniec kliknij "Zapisz zdjecia.js".
"""

import re
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

FOLDER       = "zdjecia"
PLIK_JS      = "zdjecia.js"
ROZSZERZENIA = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
MAX_W, MAX_H = 820, 520


# ── parsowanie istniejącego zdjecia.js ───────────────────────

def wczytaj_istniejacy_js(plik: str) -> dict[str, dict]:
    """
    Zwraca słownik {src: {opis, data, kategoria}}
    parsowany regexpem z istniejącego zdjecia.js.
    """
    p = Path(plik)
    if not p.exists():
        return {}

    wynik = {}
    # dopasuj każdą linię z { src: "...", opis: "...", data: "...", kategoria: "..." }
    wzorzec = re.compile(
        r'src:\s*"([^"]*)"'
        r'.*?opis:\s*"([^"]*)"'
        r'.*?data:\s*"([^"]*)"'
        r'.*?kategoria:\s*"([^"]*)"',
        re.DOTALL
    )
    tekst = p.read_text(encoding="utf-8")
    for m in wzorzec.finditer(tekst):
        src, opis, data, kat = m.group(1), m.group(2), m.group(3), m.group(4)
        wynik[src] = {"opis": opis, "data": data, "kategoria": kat}

    return wynik


# ── skanowanie folderu ────────────────────────────────────────

def wyciagnij_rok(nazwa: str) -> str:
    m = re.search(r"(20\d{2}|19\d{2})", nazwa)
    return m.group(1) if m else ""


def wczytaj_zdjecia() -> list[dict]:
    """
    Skanuje folder zdjecia/, a istniejące dane z zdjecia.js
    nadpisują puste pola – zachowując już wpisane opisy.
    """
    p = Path(FOLDER)
    if not p.exists():
        return []

    pliki = sorted(
        f for f in p.iterdir()
        if f.is_file() and f.suffix.lower() in ROZSZERZENIA
    )

    istniejace = wczytaj_istniejacy_js(PLIK_JS)
    n_wczytanych = sum(1 for v in istniejace.values() if v["opis"] or v["kategoria"])

    lista = []
    for f in pliki:
        src = f"{FOLDER}/{f.name}"
        zapisane = istniejace.get(src, {})
        lista.append({
            "src":       src,
            "opis":      zapisane.get("opis", ""),
            "data":      zapisane.get("data", "") or wyciagnij_rok(f.stem),
            "kategoria": zapisane.get("kategoria", ""),
        })

    if istniejace:
        print(f"[✓] Wczytano {len(istniejace)} wpisów z {PLIK_JS} "
              f"({n_wczytanych} z opisem/kategorią)")

    return lista


# ── zapis ─────────────────────────────────────────────────────

def zbierz_kategorie(zdjecia: list[dict]) -> list[str]:
    seen: list[str] = []
    for z in zdjecia:
        k = z.get("kategoria", "").strip()
        if k and k not in seen:
            seen.append(k)
    return seen


def formatuj_wpis(z: dict, idx: int) -> str:
    def uciec(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')
    return (
        f'  /* {idx+1:>3} */ '
        f'{{ src: "{uciec(z["src"])}", '
        f'opis: "{uciec(z["opis"])}", '
        f'data: "{uciec(z["data"])}", '
        f'kategoria: "{uciec(z["kategoria"])}" }},'
    )


def zapisz_js(zdjecia: list[dict], plik: str):
    kategorie = zbierz_kategorie(zdjecia)
    kat_str = "\n".join(f'  "{k}",' for k in kategorie) or "  // brak kategorii"

    naglowek = (
        "/*\n"
        "  ============================================================\n"
        "  zdjecia.js  –  edytowane przez edytor_zdjec.py\n"
        "  ============================================================\n"
        "*/\n\n"
        "const ZDJECIA = [\n"
    )
    wpisy  = "\n".join(formatuj_wpis(z, i) for i, z in enumerate(zdjecia))
    stopka = (
        "\n];\n\n"
        "const KATEGORIE = [\n"
        + kat_str + "\n"
        "];\n"
    )

    with open(plik, "w", encoding="utf-8") as f:
        f.write(naglowek + wpisy + stopka)


# ── skalowanie obrazu ─────────────────────────────────────────

def scaluj(img, max_w, max_h):
    w, h = img.size
    skala = min(max_w / w, max_h / h, 1.0)
    if skala < 1.0:
        img = img.resize((int(w * skala), int(h * skala)), Image.LANCZOS)
    return img


# ── GUI ───────────────────────────────────────────────────────

class Edytor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Edytor zdjęć – galeria Lidii")
        self.configure(bg="#2b2118")
        self.resizable(True, True)

        self.zdjecia  = wczytaj_zdjecia()
        self.idx      = 0
        self._img_ref = None

        if not self.zdjecia:
            messagebox.showerror(
                "Brak zdjęć",
                f"Nie znaleziono zdjęć w folderze '{FOLDER}/'.\n"
                "Uruchom skrypt z folderu repozytorium."
            )
            self.destroy()
            return

        self._buduj_ui()
        self._pokaz(0)

        self.bind("<Left>",  lambda e: self._poprzednie())
        self.bind("<Right>", lambda e: self._nastepne())
        self.bind("<Return>", lambda e: self._fokus_opis())

    # ── UI ────────────────────────────────────────────────────

    def _buduj_ui(self):
        # pasek górny
        top = tk.Frame(self, bg="#2b2118", pady=6)
        top.pack(fill="x", padx=12)

        self.lbl_licznik = tk.Label(
            top, text="", bg="#2b2118", fg="#c4a882",
            font=("Helvetica", 11)
        )
        self.lbl_licznik.pack(side="left")

        self.lbl_plik = tk.Label(
            top, text="", bg="#2b2118", fg="#8b6342",
            font=("Helvetica", 10)
        )
        self.lbl_plik.pack(side="left", padx=16)

        # wskaźnik zapisania
        self.lbl_status = tk.Label(
            top, text="", bg="#2b2118", fg="#5c9e5c",
            font=("Helvetica", 10, "bold")
        )
        self.lbl_status.pack(side="right", padx=8)

        btn_zapisz = tk.Button(
            top, text="💾  Zapisz zdjecia.js",
            command=self._zapisz,
            bg="#5c3d1e", fg="#f5f0e8",
            activebackground="#8b6342", activeforeground="#fff",
            relief="flat", padx=14, pady=4, cursor="hand2",
            font=("Helvetica", 10, "bold")
        )
        btn_zapisz.pack(side="right")

        # podgląd
        self.canvas = tk.Canvas(
            self, width=MAX_W, height=MAX_H,
            bg="#1a110a", highlightthickness=0
        )
        self.canvas.pack(pady=(4, 0))

        if not PIL_OK:
            self.canvas.create_text(
                MAX_W // 2, MAX_H // 2,
                text="Zainstaluj Pillow:\npip install pillow",
                fill="#8b6342", font=("Helvetica", 13), justify="center"
            )

        # pasek nawigacji
        nav = tk.Frame(self, bg="#2b2118")
        nav.pack(pady=6)

        s = dict(bg="#3d2812", fg="#f5f0e8",
                  activebackground="#5c3d1e", activeforeground="#fff",
                  relief="flat", width=5, cursor="hand2",
                  font=("Helvetica", 18))
        tk.Button(nav, text="‹", command=self._poprzednie, **s).pack(side="left", padx=6)
        tk.Button(nav, text="›", command=self._nastepne,   **s).pack(side="left", padx=6)

        # formularz
        form = tk.Frame(self, bg="#2b2118", padx=16, pady=8)
        form.pack(fill="x")

        lbl  = dict(bg="#2b2118", fg="#c4a882", font=("Helvetica", 10), anchor="w")
        ent  = dict(bg="#3d2812", fg="#f5f0e8", insertbackground="#f5f0e8",
                    relief="flat", font=("Helvetica", 11),
                    highlightthickness=1, highlightcolor="#8b6342",
                    highlightbackground="#5c3d1e")

        tk.Label(form, text="Opis / podpis", **lbl).grid(row=0, column=0, sticky="w", pady=4)
        self.ent_opis = tk.Entry(form, **ent, width=56)
        self.ent_opis.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Data / rok",    **lbl).grid(row=1, column=0, sticky="w", pady=4)
        self.ent_data = tk.Entry(form, **ent, width=56)
        self.ent_data.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        tk.Label(form, text="Kategoria",     **lbl).grid(row=2, column=0, sticky="w", pady=4)
        self.ent_kat = tk.Entry(form, **ent, width=56)
        self.ent_kat.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        form.columnconfigure(1, weight=1)

        self.lbl_kat_hint = tk.Label(
            form, text="", bg="#2b2118", fg="#5c3d1e",
            font=("Helvetica", 9), anchor="w"
        )
        self.lbl_kat_hint.grid(row=3, column=1, sticky="w", padx=(8, 0))

        # skróty
        tk.Label(
            self,
            text="← → nawigacja    Enter → skocz do opisu    "
                 "Ctrl+S → zapisz    zapis auto przy każdym przejściu",
            bg="#2b2118", fg="#5c3d1e", font=("Helvetica", 9)
        ).pack(pady=(2, 10))

        # Ctrl+S
        self.bind("<Control-s>", lambda e: self._zapisz())

    # ── logika ────────────────────────────────────────────────

    def _pokaz(self, idx: int):
        self.idx = idx
        z = self.zdjecia[idx]

        self.lbl_licznik.config(text=f"{idx + 1} / {len(self.zdjecia)}")
        self.lbl_plik.config(text=z["src"])
        self.lbl_status.config(text="")

        # podgląd obrazu
        self.canvas.delete("all")
        if PIL_OK:
            try:
                img = Image.open(z["src"])
                img = scaluj(img, MAX_W, MAX_H)
                self._img_ref = ImageTk.PhotoImage(img)
                self.canvas.create_image(MAX_W // 2, MAX_H // 2,
                                          anchor="center", image=self._img_ref)
            except Exception as exc:
                self.canvas.create_text(
                    MAX_W // 2, MAX_H // 2,
                    text=f"Nie można wczytać:\n{exc}",
                    fill="#8b6342", font=("Helvetica", 11), justify="center"
                )

        # wypełnij pola — blokuj trackingi zdarzeń podczas wypełniania
        self.ent_opis.delete(0, "end");  self.ent_opis.insert(0, z.get("opis", ""))
        self.ent_data.delete(0, "end");  self.ent_data.insert(0, z.get("data", ""))
        self.ent_kat.delete(0,  "end");  self.ent_kat.insert(0,  z.get("kategoria", ""))

        # podpowiedź kategorii
        uzyte = zbierz_kategorie(self.zdjecia)
        if uzyte:
            self.lbl_kat_hint.config(text="użyte: " + ",  ".join(uzyte))
        else:
            self.lbl_kat_hint.config(text="")

    def _zapisz_pole_biezacego(self):
        """Zapisz wartości pól do listy w pamięci (nie do pliku)."""
        z = self.zdjecia[self.idx]
        z["opis"]      = self.ent_opis.get().strip()
        z["data"]      = self.ent_data.get().strip()
        z["kategoria"] = self.ent_kat.get().strip()

    def _poprzednie(self):
        self._zapisz_pole_biezacego()
        self._pokaz((self.idx - 1) % len(self.zdjecia))

    def _nastepne(self):
        self._zapisz_pole_biezacego()
        self._pokaz((self.idx + 1) % len(self.zdjecia))

    def _fokus_opis(self):
        self.ent_opis.focus_set()
        self.ent_opis.icursor("end")

    def _zapisz(self):
        self._zapisz_pole_biezacego()
        try:
            zapisz_js(self.zdjecia, PLIK_JS)
            self.lbl_status.config(text="✓ zapisano")
            self.after(3000, lambda: self.lbl_status.config(text=""))
            print(f"[✓] Zapisano {PLIK_JS} ({len(self.zdjecia)} zdjęć)")
        except Exception as exc:
            messagebox.showerror("Błąd zapisu", str(exc))


# ── start ─────────────────────────────────────────────────────

if __name__ == "__main__":
    app = Edytor()
    app.mainloop()
