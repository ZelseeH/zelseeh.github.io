(function () {
  'use strict';

  /* ============================================================
     POMOCNICZE
     ============================================================ */
  function getYearRange(lista) {
    const lata = lista
      .map(z => {
        const m = (z.data || '').match(/\d{4}/);
        return m ? parseInt(m[0]) : null;
      })
      .filter(Boolean);
    if (!lata.length) return '';
    const min = Math.min(...lata);
    const max = Math.max(...lata);
    return min === max ? String(min) : min + ' – ' + max;
  }

  /* ============================================================
     INICJALIZACJA OKŁADKI
     ============================================================ */
  function initCover() {
    const yearsEl = document.getElementById('coverYears');
    if (!yearsEl) return;
    const zakres = getYearRange(ZDJECIA);
    yearsEl.textContent = zakres || '';
  }

  /* ============================================================
     STOPKA
     ============================================================ */
  function initFooter() {
    const el = document.getElementById('footerText');
    if (!el) return;
    el.textContent = 'dla Lidii, z całego serca ♡';
  }

  /* ============================================================
     FILTRY
     ============================================================ */
  let aktywnaKategoria = 'wszystkie';

  function initFilters() {
    const bar = document.getElementById('filterBar');
    if (!bar) return;

    // jeśli KATEGORIE jest puste lub brak danych z kategoriami – ukryj pasek
    const uzytKategorie = typeof KATEGORIE !== 'undefined' && KATEGORIE.length;
    if (!uzytKategorie) {
      bar.style.display = 'none';
      return;
    }

    const wszystkie = ['wszystkie', ...KATEGORIE];
    wszystkie.forEach(kat => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (kat === 'wszystkie' ? ' active' : '');
      btn.textContent = kat === 'wszystkie' ? 'wszystkie' : kat;
      btn.dataset.kat = kat;
      btn.addEventListener('click', () => {
        aktywnaKategoria = kat;
        bar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderGrid();
      });
      bar.appendChild(btn);
    });
  }

  /* ============================================================
     GALERIA
     ============================================================ */
  let widoczneZdjecia = [];

  function renderGrid() {
    const grid = document.getElementById('photoGrid');
    if (!grid) return;

    widoczneZdjecia = ZDJECIA.filter(z => {
      if (aktywnaKategoria === 'wszystkie') return true;
      return (z.kategoria || '') === aktywnaKategoria;
    }).filter(z => z.src); // pomiń puste src

    grid.innerHTML = '';

    if (!widoczneZdjecia.length) {
      const empty = document.createElement('p');
      empty.className = 'photo-empty';
      empty.textContent = 'Brak zdjęć w tej kategorii.';
      grid.appendChild(empty);
      return;
    }

    widoczneZdjecia.forEach((zdj, idx) => {
      const card = document.createElement('div');
      card.className = 'photo-card';
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'button');
      card.setAttribute('aria-label', zdj.opis || ('zdjęcie ' + (idx + 1)));

      const imgWrap = document.createElement('div');
      imgWrap.className = 'photo-card-img-wrap';

      const img = document.createElement('img');
      img.className = 'photo-card-img';
      img.src = zdj.src;
      img.alt = zdj.opis || '';
      img.loading = 'lazy';

      imgWrap.appendChild(img);
      card.appendChild(imgWrap);

      if (zdj.opis) {
        const cap = document.createElement('p');
        cap.className = 'photo-card-caption';
        cap.textContent = zdj.opis;
        card.appendChild(cap);
      }

      if (zdj.data) {
        const dt = document.createElement('p');
        dt.className = 'photo-card-date';
        dt.textContent = zdj.data;
        card.appendChild(dt);
      }

      card.addEventListener('click', () => openLightbox(idx));
      card.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') openLightbox(idx);
      });

      grid.appendChild(card);
    });
  }

  /* ============================================================
     LIGHTBOX
     ============================================================ */
  let lbIdx = 0;

  function openLightbox(idx) {
    lbIdx = idx;
    updateLightbox();
    const lb = document.getElementById('lightbox');
    lb.classList.add('open');
    lb.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    const lb = document.getElementById('lightbox');
    lb.classList.remove('open');
    lb.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  function updateLightbox() {
    const zdj = widoczneZdjecia[lbIdx];
    if (!zdj) return;
    document.getElementById('lightboxImg').src = zdj.src;
    document.getElementById('lightboxImg').alt = zdj.opis || '';
    const cap = [];
    if (zdj.opis) cap.push(zdj.opis);
    if (zdj.data) cap.push(zdj.data);
    document.getElementById('lightboxCaption').textContent = cap.join('  ·  ');
  }

  function prevPhoto() {
    lbIdx = (lbIdx - 1 + widoczneZdjecia.length) % widoczneZdjecia.length;
    updateLightbox();
  }

  function nextPhoto() {
    lbIdx = (lbIdx + 1) % widoczneZdjecia.length;
    updateLightbox();
  }

  function initLightbox() {
    document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
    document.getElementById('lightboxPrev').addEventListener('click', prevPhoto);
    document.getElementById('lightboxNext').addEventListener('click', nextPhoto);

    document.getElementById('lightbox').addEventListener('click', function (e) {
      if (e.target === this) closeLightbox();
    });

    document.addEventListener('keydown', e => {
      const lb = document.getElementById('lightbox');
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape')      closeLightbox();
      if (e.key === 'ArrowLeft')   prevPhoto();
      if (e.key === 'ArrowRight')  nextPhoto();
    });

    // swipe na telefonie
    let touchStartX = 0;
    document.getElementById('lightbox').addEventListener('touchstart', e => {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });
    document.getElementById('lightbox').addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) > 50) dx < 0 ? nextPhoto() : prevPhoto();
    }, { passive: true });
  }

  /* ============================================================
     SPRAWDZENIE LISTY ZDJĘĆ
     ============================================================ */
  function checkZdjeciaList() {
    if (typeof ZDJECIA === 'undefined' || !ZDJECIA.length) {
      console.warn('[galeria] Brak listy zdjęć – uzupełnij plik zdjecia.js');
      return false;
    }
    const realne = ZDJECIA.filter(z => z.src);
    if (!realne.length) {
      console.info('[galeria] Lista zdjęć jest pusta (tylko placeholdery) – dodaj zdjęcia do folderu i uzupełnij zdjecia.js');
    }
    return true;
  }

  /* ============================================================
     START
     ============================================================ */
  document.addEventListener('DOMContentLoaded', () => {
    checkZdjeciaList();
    initCover();
    initFooter();
    initFilters();
    renderGrid();
    initLightbox();
  });

})();


/* ============================================================
   ODTWARZACZ MUZYKI
   Odpala się przy pierwszym dotknięciu/kliknięciu strony.
   ============================================================ */
(function () {
  const audio    = document.getElementById('muzyka');
  const btn      = document.getElementById('playerBtn');
  const icon     = document.getElementById('playerIcon');
  const titleEl  = document.getElementById('playerTitle');
  const progress = document.getElementById('playerProgress');
  const player   = document.getElementById('player');

  if (!audio || !btn) return;

  // Nazwa piosenki z atrybutu data lub z nazwy pliku
  const TYTUL = audio.dataset.title || 'muzyka.mp3';

  let started = false;
  let granie  = false;

  function aktualizujIcon() {
    icon.textContent = granie ? '⏸' : '♪';
  }

  function aktualizujPasek() {
    if (!audio.duration) return;
    const pct = (audio.currentTime / audio.duration) * 100;
    progress.style.width = pct + '%';
  }

  function startMuzyki() {
    if (started) return;
    started = true;
    audio.volume = 0.7;
    audio.play().then(() => {
      granie = true;
      aktualizujIcon();
      titleEl.textContent = '♩ ' + TYTUL;
    }).catch(() => {
      // zablokowane mimo kliknięcia – nic nie rób
    });
  }

  // pierwsze kliknięcie / dotknięcie gdziekolwiek
  function onFirstInteraction() {
    startMuzyki();
    document.removeEventListener('click',      onFirstInteraction);
    document.removeEventListener('touchstart', onFirstInteraction);
    document.removeEventListener('keydown',    onFirstInteraction);
  }

  document.addEventListener('click',      onFirstInteraction, { once: false });
  document.addEventListener('touchstart', onFirstInteraction, { once: false, passive: true });
  document.addEventListener('keydown',    onFirstInteraction, { once: false });

  // przycisk pauzy/play
  btn.addEventListener('click', function (e) {
    e.stopPropagation(); // nie triggeruje onFirstInteraction drugi raz
    if (!started) { startMuzyki(); return; }
    if (granie) {
      audio.pause();
      granie = false;
    } else {
      audio.play();
      granie = true;
    }
    aktualizujIcon();
  });

  // pasek postępu
  audio.addEventListener('timeupdate', aktualizujPasek);

  // po załadowaniu metadanych – pokaż tytuł
  audio.addEventListener('loadedmetadata', () => {
    titleEl.textContent = '♩ ' + TYTUL;
  });

  // lekkie przyciemnienie playera kiedy się nie dzieje nic
  setTimeout(() => { player.style.opacity = '0.55'; }, 4000);
  player.addEventListener('mouseenter', () => { player.style.opacity = '1'; });
  player.addEventListener('mouseleave', () => { if (!granie) player.style.opacity = '0.55'; else player.style.opacity = '0.85'; });
})();
