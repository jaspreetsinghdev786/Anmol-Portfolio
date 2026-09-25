import { CLIPS, CATEGORIES, media, timecode, shortDur } from "./clips.js";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const finePointer = matchMedia("(hover: hover) and (pointer: fine)").matches;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- media helpers ---------- */

// Preview <video> that only fetches once it is first played.
function previewVideo(slug) {
  const v = document.createElement("video");
  v.muted = true;
  v.loop = true;
  v.playsInline = true;
  v.preload = "none";
  v.setAttribute("aria-hidden", "true");
  v.dataset.src = media(slug).preview;
  return v;
}

function poster(slug, alt = "") {
  const img = new Image();
  img.src = media(slug).poster;
  img.alt = alt;
  img.loading = "lazy";
  img.decoding = "async";
  return img;
}

function play(video) {
  if (!video) return;
  if (!video.src && video.dataset.src) video.src = video.dataset.src;
  const p = video.play();
  if (p) p.catch(() => {}); // autoplay can be refused; the poster stays visible
}

function pause(video) {
  if (video && !video.paused) video.pause();
}

/* ---------- hero stack ---------- */

const HERO = ["tonino-02", "herds-of-comedy-01", "dodo"];
const heroStack = $(".hero__stack");
HERO.forEach((slug) => {
  const clip = CLIPS.find((c) => c.slug === slug);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "phone";
  btn.dataset.cursor = "";
  btn.setAttribute("aria-label", `Play ${clip.title}`);
  const v = previewVideo(slug);
  v.poster = media(slug).poster;
  const tag = document.createElement("span");
  tag.className = "phone__tag";
  tag.innerHTML = `<span>${CATEGORIES[clip.cat]}</span><span>${shortDur(clip.dur)}</span>`;
  btn.append(v, tag);
  btn.addEventListener("click", () => openPlayer(clip, CLIPS));
  heroStack.append(btn);
  if (!reduceMotion) play(v);
});

/* ---------- timeline strip ---------- */

const FEATURED = CLIPS.filter((c) => c.featured);
const stripTrack = $(".strip__track");
FEATURED.forEach((clip) => {
  const li = document.createElement("li");
  li.className = "strip__clip";
  const btn = document.createElement("button");
  btn.type = "button";
  btn.dataset.cursor = "";
  btn.setAttribute("aria-label", `Play ${clip.title}`);
  const label = document.createElement("span");
  label.className = "clip-label";
  label.innerHTML = `<strong>${clip.title}</strong><span>${CATEGORIES[clip.cat]} · ${shortDur(clip.dur)}</span>`;
  li.append(poster(clip.slug), previewVideo(clip.slug), label, btn);
  btn.addEventListener("click", () => openPlayer(clip, FEATURED));
  stripTrack.append(li);
});

/* ---------- work grid + filters ---------- */

const grid = $(".grid");
const cards = CLIPS.map((clip) => {
  const li = document.createElement("li");
  li.className = "card" + (clip.landscape ? " card--wide" : "");
  li.dataset.cat = clip.cat;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.dataset.cursor = "";
  btn.setAttribute("aria-label", `Play ${clip.title}, ${shortDur(clip.dur)}`);
  const mediaBox = document.createElement("div");
  mediaBox.className = "card__media";
  const dur = document.createElement("span");
  dur.className = "card__dur";
  dur.textContent = shortDur(clip.dur);
  mediaBox.append(poster(clip.slug), previewVideo(clip.slug), dur);
  const info = document.createElement("div");
  info.className = "card__info";
  info.innerHTML = `<h3 class="card__title">${clip.title}</h3><span class="card__cat">${CATEGORIES[clip.cat]}</span>`;
  btn.append(mediaBox, info);
  btn.addEventListener("click", () => openPlayer(clip, visibleClips()));
  li.append(btn);
  grid.append(li);
  return { li, clip, video: $("video", mediaBox) };
});

function setPlaying(card, on) {
  card.li.classList.toggle("is-playing", on);
  on ? play(card.video) : pause(card.video);
}

if (finePointer) {
  cards.forEach((card) => {
    card.li.addEventListener("pointerenter", () => setPlaying(card, true));
    card.li.addEventListener("pointerleave", () => setPlaying(card, false));
  });
} else if (!reduceMotion) {
  // touch: play only the most visible card, so a dense grid isn't decoding
  // half a dozen videos at once on a phone
  const ratios = new Map();
  let playing = null;
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => ratios.set(e.target, e.intersectionRatio));
      let best = null, bestR = 0.6;
      cards.forEach((c) => {
        const r = ratios.get(c.li) || 0;
        if (!c.li.hidden && r > bestR) { bestR = r; best = c; }
      });
      if (best === playing) return;
      if (playing) setPlaying(playing, false);
      playing = best;
      if (playing) setPlaying(playing, true);
    },
    { threshold: [0, 0.6, 0.8, 1] }
  );
  cards.forEach((c) => io.observe(c.li));
}

const filters = $(".filters");
const filterDefs = [["all", "All", CLIPS.length]].concat(
  Object.entries(CATEGORIES).map(([k, name]) => [k, name, CLIPS.filter((c) => c.cat === k).length])
);
filterDefs.forEach(([key, name, count], i) => {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "filter";
  b.dataset.filter = key;
  b.setAttribute("aria-pressed", String(i === 0));
  b.innerHTML = `${name}<sup>${String(count).padStart(2, "0")}</sup>`;
  filters.append(b);
});
filters.addEventListener("click", (e) => {
  const b = e.target.closest(".filter");
  if (!b) return;
  $$(".filter", filters).forEach((f) => f.setAttribute("aria-pressed", String(f === b)));
  const key = b.dataset.filter;
  const shown = cards.filter((c) => key === "all" || c.clip.cat === key);
  cards.forEach((c) => {
    c.li.hidden = !shown.includes(c);
    if (c.li.hidden) setPlaying(c, false);
  });
  if (window.gsap && !reduceMotion) {
    gsap.fromTo(shown.map((c) => c.li), { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.03, ease: "power3.out", clearProps: "transform,opacity" });
  }
  window.ScrollTrigger?.refresh();
});

function visibleClips() {
  return cards.filter((c) => !c.li.hidden).map((c) => c.clip);
}

/* ---------- player ---------- */

const dialog = $(".player");
const pVideo = $(".player__video", dialog);
let queue = [];
let current = 0;

function load(clip) {
  const m = media(clip.slug);
  pVideo.poster = m.poster;
  pVideo.src = m.full;
  dialog.classList.toggle("is-wide", !!clip.landscape);
  pVideo.style.setProperty("--ar", clip.landscape ? "16 / 9" : "9 / 16");
  $("#player-title").textContent = clip.title;
  $("[data-player-cat]", dialog).textContent = CATEGORIES[clip.cat];
  $("[data-player-dur]", dialog).textContent = `Duration ${timecode(clip.dur)}`;
  play(pVideo);
}

function openPlayer(clip, list) {
  queue = list;
  current = Math.max(0, list.indexOf(clip));
  $$("video").forEach((v) => v !== pVideo && pause(v));
  load(queue[current]);
  if (!dialog.open) dialog.showModal();
  lenis?.stop();
}

function step(dir) {
  current = (current + dir + queue.length) % queue.length;
  load(queue[current]);
}

$("[data-player-prev]").addEventListener("click", () => step(-1));
$("[data-player-next]").addEventListener("click", () => step(1));
$("[data-player-close]").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); }); // backdrop
dialog.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") step(1);
  if (e.key === "ArrowLeft") step(-1);
});
dialog.addEventListener("close", () => {
  pVideo.pause();
  pVideo.removeAttribute("src");
  pVideo.load();
  lenis?.start();
  if (!reduceMotion) $$(".phone video").forEach(play);
});

/* ---------- header: running timecode + scroll progress ---------- */

const tcEl = $("[data-tc]");
const t0 = performance.now();
(function tick(now) {
  tcEl.textContent = timecode((now - t0) / 1000);
  requestAnimationFrame(tick);
})(t0);
$("[data-year]").textContent = new Date().getFullYear();

/* ---------- custom cursor ---------- */

const cursor = $(".cursor");
if (finePointer && window.gsap) {
  const xTo = gsap.quickTo(cursor, "x", { duration: 0.35, ease: "power3" });
  const yTo = gsap.quickTo(cursor, "y", { duration: 0.35, ease: "power3" });
  addEventListener("pointermove", (e) => { xTo(e.clientX); yTo(e.clientY); }, { passive: true });
  document.addEventListener("pointerover", (e) => {
    cursor.classList.toggle("is-on", !!e.target.closest("[data-cursor]"));
  });
}

/* ---------- motion ---------- */

let lenis = null;

if (window.gsap && window.ScrollTrigger) {
  gsap.registerPlugin(ScrollTrigger, window.SplitText);

  // header progress bar tracks the whole page
  gsap.to(".bar__progress", {
    scaleX: 1, ease: "none",
    scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 0.3 },
  });

  const mm = gsap.matchMedia();

  mm.add("(prefers-reduced-motion: no-preference)", () => {
    lenis = new Lenis({ lerp: 0.1 });
    lenis.on("scroll", ScrollTrigger.update);
    const raf = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);

    // split headings: lines masked, words rise with a slight 3D tilt
    $$("[data-split]").forEach((el) => {
      const inHero = !!el.closest(".hero");
      SplitText.create(el, {
        type: "lines,words",
        linesClass: "split-line",
        autoSplit: true,
        onSplit: (self) => gsap.from(self.words, {
          yPercent: 110, rotationX: -40, transformOrigin: "50% 100% -20px",
          duration: 1, ease: "expo.out", stagger: 0.05,
          delay: inHero ? 0.15 : 0,
          scrollTrigger: inHero ? undefined : { trigger: el, start: "top 85%", once: true },
        }),
      });
    });

    gsap.from(".hero__lede, .hero__actions, .hero__copy .eyebrow", { opacity: 0, y: 20, duration: 0.9, stagger: 0.08, delay: 0.5, ease: "power3.out" });
    gsap.from(".phone", { opacity: 0, y: 80, rotation: 0, duration: 1.2, stagger: 0.12, delay: 0.3, ease: "expo.out" });
    gsap.from(".hero__stats > div", { opacity: 0, y: 16, duration: 0.8, stagger: 0.08, delay: 0.8, ease: "power3.out" });

    // phones drift apart as the hero leaves
    gsap.to(".phone:nth-child(1)", { yPercent: -18, rotation: -14, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 1 } });
    gsap.to(".phone:nth-child(3)", { yPercent: -30, rotation: 13, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: 1 } });

    // timeline strip: pin and scrub the track under a fixed playhead
    const viewport = $(".strip__viewport");
    const clipsEls = $$(".strip__clip");
    const stripTc = $("[data-strip-tc]");
    let live = null;
    const distance = () => stripTrack.scrollWidth - innerWidth;

    // Runs off the track tween, not the ScrollTrigger, so it follows where the
    // clips actually are while scrub is still easing toward the scroll position.
    const starts = FEATURED.map((_, i) => FEATURED.slice(0, i).reduce((s, c) => s + c.dur, 0));
    const syncPlayhead = () => {
      const mid = innerWidth / 2;
      let best = 0, bestD = Infinity, frac = 0;
      clipsEls.forEach((el, i) => {
        const r = el.getBoundingClientRect();
        const d = Math.abs(r.left + r.width / 2 - mid);
        if (d < bestD) { bestD = d; best = i; frac = gsap.utils.clamp(0, 1, (mid - r.left) / r.width); }
      });
      stripTc.textContent = timecode(starts[best] + frac * FEATURED[best].dur);
      const el = clipsEls[best];
      if (el === live) return;
      if (live) { live.classList.remove("is-live"); pause($("video", live)); }
      live = el;
      live.classList.add("is-live");
      play($("video", live));
    };

    gsap.to(stripTrack, {
      x: () => -distance(),
      ease: "none",
      onUpdate: syncPlayhead,
      scrollTrigger: {
        trigger: ".strip",
        start: "bottom bottom",
        end: () => "+=" + distance(),
        pin: true,
        scrub: 1,
        invalidateOnRefresh: true,
        onToggle: (self) => {
          if (self.isActive) syncPlayhead();
          else if (live) { pause($("video", live)); live.classList.remove("is-live"); live = null; }
        },
      },
    });

    // ruler scrolls with the track, slower, for depth
    gsap.to(".strip__ruler", {
      backgroundPositionX: () => -distance() * 0.5 + "px",
      ease: "none",
      scrollTrigger: { trigger: ".strip", start: "bottom bottom", end: () => "+=" + distance(), scrub: 1, invalidateOnRefresh: true },
    });

    // grid cards rise in batches
    ScrollTrigger.batch(".card", {
      start: "top 92%",
      once: true,
      onEnter: (els) => gsap.from(els, { opacity: 0, y: 40, duration: 0.8, stagger: 0.06, ease: "power3.out" }),
    });

    gsap.from(".edl li", {
      opacity: 0, x: -30, duration: 0.8, stagger: 0.08, ease: "power3.out",
      scrollTrigger: { trigger: ".edl", start: "top 80%", once: true },
    });

    return () => { lenis.destroy(); lenis = null; };
  });

  mm.add("(prefers-reduced-motion: reduce)", () => {
    $(".strip").classList.add("is-static");
  });

  addEventListener("load", () => ScrollTrigger.refresh());
  document.fonts?.ready.then(() => ScrollTrigger.refresh());
} else {
  $(".strip").classList.add("is-static");
}
