// Edusoft site behaviour: nav, copy logins, tabs + filters, card tilt, quick look, intro video, count-up.
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const UR = document.documentElement.lang === 'ur';
  const L = (en, ur) => UR ? ur : en;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

  // mobile nav
  const nav = $('.nav');
  $('.burger')?.addEventListener('click', () => nav.classList.toggle('open'));
  $$('.nav-links a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));

  // copy demo logins
  const toast = $('#toast');
  let tt;
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); }
    catch {
      const t = document.createElement('textarea');
      t.value = text; document.body.appendChild(t); t.select();
      document.execCommand('copy'); t.remove();
    }
    toast.querySelector('span').textContent = L(`Copied "${text}"`, `کاپی ہو گیا: ${text}`);
    toast.classList.add('show');
    clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('show'), 1800);
  }
  document.addEventListener('click', e => {
    const c = e.target.closest('[data-copy]');
    if (c) { e.preventDefault(); e.stopPropagation(); copy(c.dataset.copy); }
  });

  // cards rise in, staggered (CSS animation, always ends visible)
  function reveal(cards) {
    if (calm) return;
    cards.forEach((c, i) => {
      c.classList.remove('rise'); void c.offsetWidth;
      c.style.animationDelay = `${Math.min(i, 9) * 40}ms`;
      c.classList.add('rise');
    });
  }
  reveal($$('.card'));

  // tilt + spotlight following the cursor
  if (finePointer && !calm) {
    document.addEventListener('pointermove', e => {
      const c = e.target.closest?.('.card');
      if (!c) return;
      const r = c.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      c.style.setProperty('--mx', `${x * 100}%`); c.style.setProperty('--my', `${y * 100}%`);
      c.style.setProperty('--ry', `${(x - .5) * 6}deg`); c.style.setProperty('--rx', `${(.5 - y) * 5}deg`);
    });
    document.addEventListener('pointerout', e => {
      const c = e.target.closest?.('.card');
      if (c && !c.contains(e.relatedTarget)) { c.style.setProperty('--rx', '0deg'); c.style.setProperty('--ry', '0deg'); }
    });
  }

  // intro video: sound button + modal
  $('.intro-video .sound')?.addEventListener('click', ev => {
    ev.stopPropagation();
    const v = $('.intro-video video');
    v.muted = false; v.currentTime = 0; v.controls = true; v.play();
    ev.currentTarget.remove();
  });
  const modal = $('#vmodal');
  if (modal) {
    const open = () => {
      const f = $('iframe[data-src]', modal); if (f) f.src = f.dataset.src;
      modal.showModal(); $('video', modal)?.play();
    };
    const close = () => {
      $('video', modal)?.pause();
      const f = $('iframe[data-src]', modal); if (f) f.src = '';
      modal.close();
    };
    $$('[data-open-video]').forEach(b => b.addEventListener('click', open));
    // clicking the placeholder (no real video yet) also opens the modal
    $('.intro-video .vslot')?.addEventListener('click', open);
    $('.vclose', modal).addEventListener('click', close);
    modal.addEventListener('click', ev => { if (ev.target === modal) close(); });
    modal.addEventListener('cancel', () => $('video', modal)?.pause());
  }

  // product page: real screenshots with tabs, auto-rotating until the visitor picks one
  $$('[data-screens]').forEach(m => {
    const imgs = $$('.shots img', m), btns = $$('.stabs button', m);
    if (imgs.length < 2) return;
    let i = 0, timer;
    const show = n => { i = n; imgs.forEach((x, k) => x.classList.toggle('on', k === n)); btns.forEach((x, k) => x.classList.toggle('on', k === n)); };
    btns.forEach((b, k) => b.addEventListener('click', () => { clearInterval(timer); show(k); }));
    if (!calm) timer = setInterval(() => show((i + 1) % imgs.length), 4500);
  });

  // count-up numbers in the "at a glance" band
  $$('[data-count]').forEach(el => {
    const end = +el.dataset.count, suf = el.dataset.suffix || '';
    if (calm || !('IntersectionObserver' in window)) return;
    const ob = new IntersectionObserver(([en]) => {
      if (!en.isIntersecting) return;
      ob.disconnect();
      const t0 = performance.now(), dur = 900;
      const step = t => {
        const k = Math.min((t - t0) / dur, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3))) + suf;
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
    ob.observe(el);
  });

  // ---------------------------------------------------------------- home page only
  const bento = $('#bento');
  const tabsEl = $('.tabs');
  if (!bento || !tabsEl) return;
  const cards = $$('.card', bento);
  let type = 'web', ind = 'all';

  const bar = $('.ind-bar', tabsEl);
  function moveBar() {
    const on = $('button.on', tabsEl);
    if (!on || !bar) return;
    bar.style.width = on.offsetWidth + 'px';
    bar.style.transform = UR ? `translateX(${-(tabsEl.clientWidth - on.offsetLeft - on.offsetWidth - 5)}px)` : `translateX(${on.offsetLeft - 5}px)`;
  }

  function apply() {
    const shown = [];
    cards.forEach(c => {
      const ok = c.dataset.type === type && (type !== 'web' || ind === 'all' || c.dataset.ind === ind);
      c.hidden = !ok;
      if (ok) shown.push(c);
    });
    reveal(shown);
    $$('button[data-view]', tabsEl).forEach(b => { const on = b.dataset.view === type; b.classList.toggle('on', on); b.setAttribute('aria-selected', on); });
    $$('#chips [data-filter]').forEach(b => b.classList.toggle('on', b.dataset.filter === ind));
    $('#chips').hidden = type !== 'web';
    moveBar();
  }
  $$('button[data-view]', tabsEl).forEach(b => b.addEventListener('click', () => { type = b.dataset.view; ind = 'all'; apply(); }));
  $$('#chips [data-filter]').forEach(b => b.addEventListener('click', () => { ind = b.dataset.filter; apply(); }));
  addEventListener('resize', moveBar);
  document.fonts?.ready.then(moveBar);

  function fromHash() { if (location.hash === '#apps') { type = 'android'; ind = 'all'; apply(); } }
  addEventListener('hashchange', fromHash);
  apply(); fromHash();

  // quick look panel
  const data = JSON.parse($('#peek-data').textContent);
  const pk = $('#peek');
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
  let lastFocus;
  function openPeek(id) {
    const p = data[id]; if (!p) return;
    lastFocus = document.activeElement;
    pk.style.setProperty('--c', p.color);
    $('.pp-img img', pk).src = p.img; $('.pp-img img', pk).alt = p.name;
    $('.pp-body', pk).innerHTML = `
      <span class="badge-ind"><i class="fas ${p.icon}"></i>${esc(p.ind)}</span>
      <h3>${esc(p.name)}</h3>
      <span class="tl">${esc(p.tagline)}</span>
      <p>${esc(p.intro)}</p>
      <ul class="pp-feats">${p.features.map(([t, d]) => `<li><i class="fas fa-check"></i><span><b>${esc(t)}</b>${esc(d)}</span></li>`).join('')}</ul>
      ${p.user ? `<div class="logrow">
        <button class="cred" data-copy="${esc(p.user)}">${L('user', 'یوزر')} <code>${esc(p.user)}</code> <i class="far fa-copy"></i></button>
        <button class="cred" data-copy="${esc(p.pass)}">${L('pass', 'پاس')} <code>${esc(p.pass)}</code> <i class="far fa-copy"></i></button>
      </div>` : '<div class="logrow"><span class="cred soon"><i class="far fa-clock"></i> ' + L('Demo link coming soon', 'ڈیمو لنک جلد آ رہا ہے') + '</span></div>'}`;
    $('.pp-acts', pk).innerHTML = `
      <a class="btn demo" href="${esc(p.demo)}" ${p.demoBlank ? 'target="_blank" rel="noopener"' : ''} ${p.apk ? 'download' : ''}>${esc(p.demoLabel)}</a>
      <a class="btn btn-light" href="${esc(p.page)}">${L('Full details', 'مکمل تفصیل')}</a>`;
    pk.classList.add('open'); pk.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    $('.pp-close', pk).focus();
  }
  function closePeek() {
    pk.classList.remove('open'); pk.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    lastFocus?.focus();
  }
  $$('[data-peek]').forEach(b => b.addEventListener('click', e => { e.preventDefault(); openPeek(b.dataset.peek); }));
  $$('[data-peek-close]', pk).forEach(b => b.addEventListener('click', closePeek));
  addEventListener('keydown', e => { if (e.key === 'Escape' && pk.classList.contains('open')) closePeek(); });
})();
