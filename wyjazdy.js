/*
  ============================================================
  wyjazdy.js  –  tutaj dodajesz kolejne wyjazdy
  ============================================================

  Każdy wyjazd to obiekt:
    nazwa   – nazwa miejsca
    data    – data wyjazdu
    zdjecia – lista linków do zdjęć (z archive.org/download/... )

  Pierwsze zdjęcie z listy staje się miniaturką bloczka.

  Żeby dodać nowy wyjazd, skopiuj cały blok { ... } poniżej,
  zmień nazwa/data i wklej linki do zdjęć z nowego archiwum.
  ============================================================
*/

const WYJAZDY = [

  {
    nazwa: "Zakopane",
    data: "10.08.2026",
    zdjecia: [
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_082115130.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_082122138.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_084459465.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_084624786.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_093207461.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_093832097.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_094114281.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_095451949.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_095515194.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_100538892.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_101046821.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_101058030.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_110718242.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_111441318.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_111450873.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_111943260.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_122233801.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_122242275.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_122247073.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_122254587.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_132150743.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_132157236.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_132215988.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_134927279.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_135217763.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_135222200.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_145053667.jpg",
      "https://archive.org/download/img-20260810-122254587/IMG_20260810_145059683.jpg",
    ]
  },

  // ── kolejny wyjazd, przykład ──────────────────────────────
  // {
  //   nazwa: "Gdańsk",
  //   data: "15.06.2026",
  //   zdjecia: [
  //     "https://archive.org/download/TWOJE-ID/plik1.jpg",
  //     "https://archive.org/download/TWOJE-ID/plik2.jpg",
  //   ]
  // },

];
