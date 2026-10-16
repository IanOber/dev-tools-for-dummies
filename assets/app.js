/* The most powerful dev tools: page behaviour.
   No dependencies. Everything here is an enhancement; the page reads fine without it. */
(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const root = document.documentElement;
  const body = document.body;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
  };

  const slides = $$('main > .slide');
  const total = slides.length;
  const pad2 = (n) => String(n).padStart(2, '0');
  const mmss = (s) => `${Math.floor(s / 60)}:${pad2(Math.floor(s % 60))}`;
  const toSeconds = (t) => { const [m, s] = (t || '0:00').split(':').map(Number); return m * 60 + (s || 0); };

  /* ───────────── rail: git-graph nav ───────────── */
  const rail = $('#rail');
  const graph = $('[data-graph]');
  const graphLine = $('[data-graph-progress]');
  const chapterEls = $$('.chapter', rail);
  const linkFor = new Map();
  $$('a[href^="#"]', rail).forEach((a) => {
    const id = a.getAttribute('href').slice(1);
    // the chapter link and the first branch link can point at the same slide; the branch link wins for "current"
    if (!linkFor.has(id) || a.closest('.branch')) linkFor.set(id, a);
  });
  const progressBar = $('[data-progress]');
  const nowTitle = $('[data-now-title]');
  const nowCount = $('[data-now-count]');

  let current = -1;
  let userMoved = false;

  function offsetTop() {
    return parseFloat(getComputedStyle(root).getPropertyValue('--top-offset')) || 0;
  }

  function setCurrent(i) {
    if (i === current) return;
    const prev = current;
    current = i;
    const s = slides[i];
    const chapter = s.dataset.chapter;

    chapterEls.forEach((c) => {
      const idx = chapterEls.indexOf(c);
      const curIdx = chapterEls.findIndex((x) => x.dataset.chapter === chapter);
      c.classList.toggle('is-current', idx === curIdx);
      c.classList.toggle('is-past', idx < curIdx);
    });
    slides.forEach((sl, j) => {
      const a = linkFor.get(sl.id);
      if (!a) return;
      a.classList.toggle('is-seen', j < i);
      if (j === i) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });

    // the line fills down to whichever dot is current
    const target = linkFor.get(s.id);
    if (target) {
      const g = graph.getBoundingClientRect();
      const t = target.getBoundingClientRect();
      graphLine.style.height = `${Math.max(0, t.top - g.top + Math.min(t.height, 30) / 2 - 14)}px`;
      // keep the active link inside the rail's visible area
      const r = rail.getBoundingClientRect();
      if (t.top < r.top + 80) rail.scrollTop -= r.top + 80 - t.top;
      else if (t.bottom > r.bottom - 90) rail.scrollTop += t.bottom - (r.bottom - 90);
    }

    nowTitle.textContent = s.dataset.title;
    nowCount.textContent = `${s.dataset.n} / ${pad2(total)}`;
    if (userMoved && prev !== -1 && history.replaceState) {
      history.replaceState(null, '', `#${s.id}`);
    }
    onSlideChange(i);
  }

  let ticking = false;
  function measure() {
    ticking = false;
    const o = offsetTop();
    const line = o + innerHeight * 0.38;
    let cur = 0;
    for (let i = 0; i < total; i++) {
      const r = slides[i].getBoundingClientRect();
      if (r.top <= line) cur = i;
      if (i > 0) slides[i].classList.toggle('is-stuck', r.top < o - 8);
    }
    if (innerHeight + scrollY >= root.scrollHeight - 4) cur = total - 1;
    setCurrent(cur);
    const max = root.scrollHeight - innerHeight;
    progressBar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
  }
  function onScroll() {
    userMoved = true;
    if (!ticking) { ticking = true; requestAnimationFrame(measure); }
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', () => { current = -1; measure(); });

  /* ───────────── mobile menu ───────────── */
  const menuBtn = $('[data-menu]');
  const scrim = $('[data-scrim]');
  function setMenu(open) {
    body.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
  }
  menuBtn.addEventListener('click', () => setMenu(!body.classList.contains('menu-open')));
  scrim.addEventListener('click', () => setMenu(false));
  rail.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });

  /* ───────────── copy prompt buttons ───────────── */
  $$('[data-copy]').forEach((btn) => {
    const label = btn.textContent;
    btn.addEventListener('click', async () => {
      const text = btn.dataset.copy;
      try {
        await navigator.clipboard.writeText(text);
      } catch (e) {
        const ta = document.createElement('textarea');
        ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch (err) { /* nothing else to try */ }
        ta.remove();
      }
      btn.textContent = 'Copied';
      btn.classList.add('is-done');
      setTimeout(() => { btn.textContent = label; btn.classList.remove('is-done'); }, 1400);
    });
  });

  /* ───────────── setup steps: tick them off ───────────── */
  $$('[data-steps]').forEach((box) => {
    const boxes = $$('input[type="checkbox"]', box);
    const tally = $('[data-tally]', box);
    const update = () => {
      const n = boxes.filter((b) => b.checked).length;
      tally.textContent = n === 0 ? '' : n === boxes.length ? 'All done. Next task, same loop.' : `${n} of ${boxes.length} done`;
    };
    boxes.forEach((b) => b.addEventListener('change', update));
    update();
  });

  /* ───────────── video: load YouTube only when asked ───────────── */
  $$('.video[data-yt]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const box = document.createElement('div');
      box.className = 'video';
      const f = document.createElement('iframe');
      f.src = `https://www.youtube-nocookie.com/embed/${btn.dataset.yt}?autoplay=1&rel=0`;
      f.title = btn.dataset.title;
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      box.appendChild(f);
      btn.replaceWith(box);
    });
  });

  /* ───────────── permissions table ───────────── */
  const modes = $('[data-modes]');
  if (modes) {
    const rows = $$('tbody tr', modes);
    const toggle = (row) => row.classList.toggle('is-pick');
    rows.forEach((row) => {
      row.addEventListener('click', () => toggle(row));
      row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(row); } });
    });
    const runit = $('[data-runit]');
    runit.addEventListener('click', () => {
      const mine = rows.filter((r) => r.dataset.mode === 'accept' || r.dataset.mode === 'bypass');
      const already = mine.every((r) => r.classList.contains('is-pick')) && rows.filter((r) => r.classList.contains('is-pick')).length === mine.length;
      rows.forEach((r) => r.classList.toggle('is-pick', !already && mine.includes(r)));
    });
  }

  /* ───────────── point-at-it demo ───────────── */
  const demo = $('[data-demo]');
  if (demo) {
    const page = $('[data-page]', demo);
    const els = $$('.m-el', page);
    const chat = $('[data-chat]', demo);
    const marksEl = $('[data-marks]', demo);
    const toolBtns = $$('.tool', demo);
    const addBtn = $('[data-add]', demo);
    const defaultHint = 'Click the heading, the paragraph or the button.';
    const hint = $('.hint', chat);
    let tool = 'select';
    let sel = null;
    let drawing = null;

    const say = (cls, html) => {
      const p = document.createElement('p');
      p.className = cls;
      p.innerHTML = html;
      chat.appendChild(p);
      const bubbles = $$('p:not(.hint)', chat);
      if (bubbles.length > 4) bubbles[0].remove();
    };
    const nameOf = (el) => el.dataset.label.toLowerCase();
    const select = (el) => {
      sel = el;
      els.forEach((e) => { e.classList.toggle('is-selected', e === el); e.setAttribute('aria-pressed', String(e === el)); });
      hint.textContent = el ? `Selected: ${nameOf(el)}. Now say what to change.` : defaultHint;
    };

    els.forEach((el) => {
      el.addEventListener('click', () => { if (tool === 'select') select(el); });
      el.addEventListener('keydown', (e) => {
        if ((e.key === 'Enter' || e.key === ' ') && tool === 'select') { e.preventDefault(); select(el); }
      });
    });

    toolBtns.forEach((b) => b.addEventListener('click', () => {
      tool = b.dataset.tool;
      toolBtns.forEach((x) => { const on = x === b; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', String(on)); });
      page.dataset.tool = tool;
    }));

    page.addEventListener('pointerdown', (e) => {
      if (tool === 'select') return;
      const r = page.getBoundingClientRect();
      const x = e.clientX - r.left; const y = e.clientY - r.top;
      const m = document.createElement('div');
      m.className = `mark mark--${tool}`;
      m.style.cssText = `left:${x}px;top:${y}px;width:0;height:0`;
      marksEl.appendChild(m);
      drawing = { m, x, y, r };
      page.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    page.addEventListener('pointermove', (e) => {
      if (!drawing) return;
      const { m, x, y, r } = drawing;
      const cx = Math.max(0, Math.min(r.width, e.clientX - r.left));
      const cy = Math.max(0, Math.min(r.height, e.clientY - r.top));
      m.style.left = `${Math.min(x, cx)}px`; m.style.top = `${Math.min(y, cy)}px`;
      m.style.width = `${Math.abs(cx - x)}px`; m.style.height = `${Math.abs(cy - y)}px`;
    });
    const endDraw = () => {
      if (!drawing) return;
      const { m } = drawing;
      drawing = null;
      if (m.offsetWidth < 10 || m.offsetHeight < 10) { m.remove(); return; }
      addBtn.disabled = false;
      hint.textContent = 'Marked. Click Add to chat to send it.';
    };
    page.addEventListener('pointerup', endDraw);
    page.addEventListener('pointercancel', endDraw);

    addBtn.addEventListener('click', () => {
      const marks = $$('.mark', marksEl);
      if (!marks.length) return;
      const r = marks[marks.length - 1].getBoundingClientRect();
      const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      const target = hit && hit.closest ? hit.closest('.m-el') : null;
      if (target) select(target);
      say('me', `<b>markup</b>${marks.length} ${marks.length === 1 ? 'shape' : 'shapes'} on the ${target ? nameOf(target) : 'page'}`);
      say('ai', target ? `Got it. Say what to change about the ${nameOf(target)}.` : 'Got it. Say what to change.');
      marks.forEach((m) => m.remove());
      addBtn.disabled = true;
      toolBtns[0].click();
    });

    $$('[data-ask]', demo).forEach((b) => b.addEventListener('click', () => {
      const kind = b.dataset.ask;
      if (kind !== 'match' && !sel) {
        hint.textContent = 'Pick something first: click the heading, the paragraph or the button.';
        return;
      }
      if (kind === 'bigger') {
        say('me', `<b>${nameOf(sel)}</b>make this bigger`);
        if (sel.classList.contains('fx-big')) say('ai', `The ${nameOf(sel)} is already one size up. Say how much more.`);
        else { sel.classList.add('fx-big'); say('ai', `Done. The ${nameOf(sel)} is one size up. Check the preview.`); }
      } else if (kind === 'tight') {
        say('me', `<b>${nameOf(sel)}</b>tighten the spacing here`);
        if (sel.classList.contains('fx-tight')) say('ai', `The ${nameOf(sel)} is already tight. Say how much more.`);
        else { sel.classList.add('fx-tight'); say('ai', `Tightened the spacing around the ${nameOf(sel)}.`); }
      } else {
        say('me', 'match the frame');
        if (page.classList.contains('fx-match')) say('ai', 'Already matches. Point at what still looks off.');
        else { page.classList.add('fx-match'); say('ai', 'Matched the Figma frame: lighter heading, squarer button, more room between them.'); }
      }
    }));

    $('[data-reset]', demo).addEventListener('click', () => {
      els.forEach((e) => e.classList.remove('fx-big', 'fx-tight'));
      page.classList.remove('fx-match');
      marksEl.innerHTML = '';
      addBtn.disabled = true;
      $$('p:not(.hint)', chat).forEach((p) => p.remove());
      select(null);
      toolBtns[0].click();
    });
  }

  /* ───────────── branch diagram ───────────── */
  const diagram = $('[data-diagram]');
  if (diagram) {
    if ('IntersectionObserver' in window && !reduceMotion) {
      const io = new IntersectionObserver((entries) => {
        if (entries.some((e) => e.isIntersecting)) { diagram.classList.add('is-in'); io.disconnect(); }
      }, { threshold: 0.35 });
      io.observe(diagram);
    } else {
      diagram.classList.add('is-in');
    }
    const terms = $$('.term[data-for]');
    let pinned = null;
    const hl = (k) => {
      diagram.classList.toggle('is-hl', !!k);
      $$('[data-term]', diagram).forEach((g) => g.classList.toggle('hl', g.dataset.term === k));
      terms.forEach((t) => t.classList.toggle('is-on', t.dataset.for === pinned));
    };
    terms.forEach((t) => {
      const k = t.dataset.for;
      t.addEventListener('mouseenter', () => hl(k));
      t.addEventListener('mouseleave', () => hl(pinned));
      t.addEventListener('focus', () => hl(k));
      t.addEventListener('blur', () => hl(pinned));
      t.addEventListener('click', () => { pinned = pinned === k ? null : k; hl(pinned); });
      t.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); t.click(); } });
    });
  }

  /* ───────────── one feature: play the loop ───────────── */
  const feature = $('[data-feature]');
  if (feature) {
    const items = $$('li', feature);
    const btn = $('[data-loop]');
    let timer = null;
    let i = 0;
    const stop = () => {
      clearInterval(timer); timer = null;
      feature.classList.remove('is-playing');
      items.forEach((li) => li.classList.remove('is-lit'));
      btn.textContent = 'Play the loop';
      btn.setAttribute('aria-pressed', 'false');
    };
    const tick = () => {
      items.forEach((li, j) => li.classList.toggle('is-lit', j === i));
      i = (i + 1) % items.length;
    };
    btn.addEventListener('click', () => {
      if (timer) { stop(); return; }
      i = 0; tick();
      feature.classList.add('is-playing');
      timer = setInterval(tick, 1500);
      btn.textContent = 'Stop';
      btn.setAttribute('aria-pressed', 'true');
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver((entries) => { if (timer && !entries.some((e) => e.isIntersecting)) stop(); }).observe(feature);
    }
  }

  /* ───────────── presenter mode ───────────── */
  const hudN = $('[data-hud-n]');
  const hudSlide = $('[data-hud-slide]');
  const hudBudget = $('[data-hud-budget]');
  const hudTotal = $('[data-hud-total]');
  const timerBtn = $('[data-timer]');
  const notesBox = $('[data-notes]');
  const notesTitle = $('[data-notes-title]');
  const notesTime = $('[data-notes-time]');
  const notesBody = $('[data-notes-body]');
  const notesNext = $('[data-notes-next]');
  const keysModal = $('[data-keys-modal]');
  const fsBtn = $('[data-fs]');

  const clock = { running: false, last: 0, total: 0, slide: 0, id: null };
  let presenting = false;
  let wakeLock = null;

  function renderClock() {
    hudSlide.textContent = mmss(clock.slide);
    hudTotal.textContent = mmss(clock.total);
    hudSlide.parentElement.classList.toggle('is-over', clock.slide > toSeconds(slides[Math.max(0, current)].dataset.time));
  }
  function tickClock() {
    const now = Date.now();
    if (clock.running) {
      const dt = (now - clock.last) / 1000;
      clock.total += dt; clock.slide += dt;
    }
    clock.last = now;
    renderClock();
  }
  function setClockRunning(on) {
    clock.running = on;
    clock.last = Date.now();
    timerBtn.textContent = on ? 'Pause' : 'Resume';
  }

  function renderNotes() {
    const s = slides[Math.max(0, current)];
    const src = $('.slide__notes', s);
    notesTitle.textContent = `${s.dataset.n} · ${s.dataset.title}`;
    notesTime.textContent = `about ${s.dataset.time}`;
    notesBody.innerHTML = src ? src.innerHTML : '';
    const nx = slides[current + 1];
    notesNext.textContent = nx ? `Next: ${nx.dataset.title}` : 'Last slide.';
  }

  function onSlideChange(i) {
    hudN.textContent = pad2(i + 1);
    hudBudget.textContent = slides[i].dataset.time;
    clock.slide = 0;
    renderClock();
    renderNotes();
  }

  async function requestWake() {
    try { if ('wakeLock' in navigator) wakeLock = await navigator.wakeLock.request('screen'); } catch (e) { wakeLock = null; }
  }
  function releaseWake() { try { if (wakeLock) wakeLock.release(); } catch (e) { /* already released */ } wakeLock = null; }

  function present(on) {
    if (on === presenting) return;
    presenting = on;
    body.classList.toggle('is-presenting', on);
    $$('[data-present]').forEach((b) => b.setAttribute('aria-pressed', String(on)));
    setMenu(false);
    if (on) {
      if (!clock.id) clock.id = setInterval(tickClock, 250);
      setClockRunning(true);
      renderClock();
      requestWake();
      // line the current slide up with the top of the screen so snap points agree
      requestAnimationFrame(() => slides[Math.max(0, current)].scrollIntoView({ block: 'start', behavior: 'auto' }));
    } else {
      setClockRunning(false);
      releaseWake();
      if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    }
  }

  function go(i) {
    const n = Math.max(0, Math.min(total - 1, i));
    slides[n].scrollIntoView({ block: 'start' });
  }
  const step = (d) => go((current < 0 ? 0 : current) + d);

  $$('[data-present]').forEach((b) => b.addEventListener('click', () => present(!presenting)));
  timerBtn.addEventListener('click', () => setClockRunning(!clock.running));
  $('[data-reset-clock]').addEventListener('click', () => { clock.total = 0; clock.slide = 0; clock.last = Date.now(); renderClock(); });
  $('[data-notes-toggle]').addEventListener('click', () => body.classList.toggle('show-notes'));
  fsBtn.addEventListener('click', toggleFullscreen);
  $$('[data-keys]').forEach((b) => b.addEventListener('click', () => keysModal.classList.add('is-open')));
  keysModal.addEventListener('click', (e) => { if (e.target === keysModal) keysModal.classList.remove('is-open'); });
  document.addEventListener('fullscreenchange', () => { fsBtn.firstChild.textContent = document.fullscreenElement ? 'Exit fullscreen ' : 'Fullscreen '; });
  document.addEventListener('visibilitychange', () => { if (presenting && document.visibilityState === 'visible') requestWake(); });

  function toggleFullscreen() {
    if (document.fullscreenElement) { document.exitFullscreen().catch(() => {}); return; }
    if (root.requestFullscreen) root.requestFullscreen().catch(() => {});
  }

  addEventListener('keydown', (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const t = e.target;
    if (t.closest && t.closest('input[type="text"], input[type="search"], textarea, select, [contenteditable]')) return;
    const k = e.key;

    if (k === 'Escape') {
      if (keysModal.classList.contains('is-open')) keysModal.classList.remove('is-open');
      else if (body.classList.contains('menu-open')) setMenu(false);
      else if (presenting && !document.fullscreenElement) present(false);
      return;
    }
    if (k === '?') { keysModal.classList.toggle('is-open'); e.preventDefault(); return; }
    if (k === 'p' || k === 'P') { present(!presenting); e.preventDefault(); return; }
    if (k === 'j' || k === 'J') { step(1); e.preventDefault(); return; }
    if (k === 'k' || k === 'K') { step(-1); e.preventDefault(); return; }
    if (!presenting) return;

    const onControl = t.closest && t.closest('button, a, input, [role="button"]');
    if (k === 'ArrowRight' || k === 'PageDown' || (k === ' ' && !onControl)) { step(1); e.preventDefault(); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { step(-1); e.preventDefault(); }
    else if (k === 'Home') { go(0); e.preventDefault(); }
    else if (k === 'End') { go(total - 1); e.preventDefault(); }
    else if (k === 'n' || k === 'N') { body.classList.toggle('show-notes'); e.preventDefault(); }
    else if (k === 'f' || k === 'F') { toggleFullscreen(); e.preventDefault(); }
  });

  // a deep link (#figma) should land on the slide at once, not glide there from the cover
  const hashSlide = location.hash && slides.find((sl) => sl.id === location.hash.slice(1));
  const snapToHash = () => {
    root.style.scrollBehavior = 'auto';
    hashSlide.scrollIntoView({ block: 'start' });
    requestAnimationFrame(() => { root.style.scrollBehavior = ''; });
  };
  if (hashSlide) {
    snapToHash();
    // fonts and images can nudge the layout; settle once more if the viewer hasn't moved yet
    addEventListener('load', () => {
      if (Math.abs(hashSlide.getBoundingClientRect().top - offsetTop()) < 400) snapToHash();
    }, { once: true });
  }

  // first paint of nav state, once everything above exists
  measure();

  // a link with ?present starts the talk straight away
  if (/[?&]present\b/.test(location.search)) present(true);

  // the one thing remembered per viewer: whether the notes drawer was open
  if (store.get('devtools-notes') === '1') body.classList.add('show-notes');
  new MutationObserver(() => store.set('devtools-notes', body.classList.contains('show-notes') ? '1' : '0'))
    .observe(body, { attributes: true, attributeFilter: ['class'] });
})();
