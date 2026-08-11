(function () {
  'use strict';

  const tripsGrid  = document.getElementById('tripsGrid');
  const viewer     = document.getElementById('viewer');
  const viewerGrid = document.getElementById('viewerGrid');
  const viewerName = document.getElementById('viewerName');
  const viewerDate = document.getElementById('viewerDate');
  const backBtn    = document.getElementById('backBtn');

  const lb    = document.getElementById('lb');
  const lbImg = document.getElementById('lbImg');
  let lbList  = [];
  let lbIdx   = 0;

  /* ── RENDER BLOCZKÓW ────────────────────────────────────── */
  function renderTiles() {
    tripsGrid.innerHTML = '';

    if (!WYJAZDY.length) {
      tripsGrid.innerHTML = '<p style="color:#888">Brak wyjazdów – uruchom generuj_galerie.py</p>';
      return;
    }

    WYJAZDY.forEach((wyjazd, idx) => {
      const tile = document.createElement('div');
      tile.className = 'trip-tile';

      const img = document.createElement('img');
      img.src = (wyjazd.zdjecia[0] && wyjazd.zdjecia[0].thumb) || '';
      img.alt = wyjazd.nazwa;
      img.loading = 'lazy';
      tile.appendChild(img);

      const body = document.createElement('div');
      body.className = 'trip-tile-body';
      body.innerHTML = `
        <div class="trip-tile-name">${wyjazd.nazwa}</div>
        <div class="trip-tile-date">${wyjazd.data}</div>
        <div class="trip-tile-count">📷 ${wyjazd.zdjecia.length} zdjęć</div>
      `;
      tile.appendChild(body);

      tile.addEventListener('click', () => openViewer(idx));
      tripsGrid.appendChild(tile);
    });
  }

  /* ── WIDOK ZDJĘĆ Z WYJAZDU ──────────────────────────────── */
  function openViewer(idx) {
    const wyjazd = WYJAZDY[idx];

    viewerName.textContent = wyjazd.nazwa;
    viewerDate.textContent = wyjazd.data;

    viewerGrid.innerHTML = '';
    wyjazd.zdjecia.forEach((zdj, i) => {
      const img = document.createElement('img');
      img.src = zdj.thumb;          // mała, szybka miniaturka w siatce
      img.loading = 'lazy';
      img.addEventListener('click', () => openLightbox(wyjazd.zdjecia, i));
      viewerGrid.appendChild(img);
    });

    document.body.classList.add('viewer-open');
    viewer.classList.add('open');
    window.scrollTo(0, 0);
  }

  function closeViewer() {
    document.body.classList.remove('viewer-open');
    viewer.classList.remove('open');
  }

  backBtn.addEventListener('click', closeViewer);

  /* ── LIGHTBOX (wersja "full" – ok. 1600px) ───────────────── */
  function openLightbox(list, idx) {
    lbList = list;
    lbIdx  = idx;
    setLightboxImage();
    lb.classList.add('open');
  }

  function setLightboxImage() {
    lbImg.src = lbList[lbIdx].full;
  }

  function closeLightbox() { lb.classList.remove('open'); }
  function nextPhoto() { lbIdx = (lbIdx + 1) % lbList.length; setLightboxImage(); }
  function prevPhoto() { lbIdx = (lbIdx - 1 + lbList.length) % lbList.length; setLightboxImage(); }

  document.getElementById('lbClose').addEventListener('click', closeLightbox);
  document.getElementById('lbNext').addEventListener('click', nextPhoto);
  document.getElementById('lbPrev').addEventListener('click', prevPhoto);
  lb.addEventListener('click', e => { if (e.target === lb) closeLightbox(); });

  document.addEventListener('keydown', e => {
    if (lb.classList.contains('open')) {
      if (e.key === 'Escape')     closeLightbox();
      if (e.key === 'ArrowRight') nextPhoto();
      if (e.key === 'ArrowLeft')  prevPhoto();
      return;
    }
    if (viewer.classList.contains('open') && e.key === 'Escape') {
      closeViewer();
    }
  });

  /* ── START ───────────────────────────────────────────────── */
  renderTiles();

})();
