import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import { mountFactoryScene } from "./scene";
import { whenScrollIdle } from "./scroll-idle";
import "./style.css";

gsap.registerPlugin(ScrollTrigger);

const arrow = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 19 19 5M8 5h11v11"/></svg>`;
const downArrow = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v16m-7-7 7 7 7-7"/></svg>`;

type ProjectKey = "operations" | "dashboard" | "location";
type Project = {
  key: ProjectKey;
  number: string;
  title: string;
  category: string;
};

const projects: Project[] = [
  {
    key: "operations",
    number: "01",
    title: "Operational Management System",
    category: "Connected operations",
  },
  {
    key: "dashboard",
    number: "02",
    title: "Business Dashboard Platform",
    category: "Data & intelligence",
  },
  {
    key: "location",
    number: "03",
    title: "Location Data Management System",
    category: "Location intelligence",
  },
];

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("App root not found");

app.innerHTML = `
  <div class="site-shell">
    <div class="scroll-progress" aria-hidden="true"></div>

    <section class="hero" id="top" aria-labelledby="hero-title">
      <div class="hero-halo" aria-hidden="true"></div>
      <header class="site-header container">
        <a class="wordmark" href="#top" aria-label="Nodeworks home"><img src="${import.meta.env.BASE_URL}nodeworks-mark.svg" width="44" height="44" alt="" />Nodeworks</a>
        <nav class="desktop-nav" aria-label="Main navigation">
          <a href="#work" class="active">Work</a>
          <a href="#services">Services</a>
          <a href="#about">About</a>
          <a href="#insights">Insights</a>
        </nav>
        <a class="header-cta" href="#contact">Let's talk ${arrow}</a>
        <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">
          <span></span><span></span>
        </button>
      </header>

      <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation" hidden>
        <a href="#work">Work</a><a href="#services">Services</a><a href="#about">About</a><a href="#insights">Insights</a><a href="#contact">Let's talk ${arrow}</a>
      </nav>

      <div class="hero-inner container">
        <div class="hero-copy">
          <p class="eyebrow hero-eyebrow">Digital systems for real business</p>
          <h1 id="hero-title"><span>We build what your </span><span class="text-blue">business needs.</span></h1>
        </div>
      </div>
      <div class="hero-stage">
        <div class="hero-orbits" aria-hidden="true"></div>
        <div class="hero-scene" role="group" aria-label="Interactive Nodeworks 3D studio">
          <canvas class="hero-canvas" tabindex="0" role="img" aria-label="3D studio. Drag or use arrow keys to rotate. Press Home to reset the view."></canvas>
        </div>
        <div class="scene-controls" role="group" aria-label="3D view controls">
          <span class="scene-drag-hint">Drag to explore</span><span class="scene-touch-hint">Explore in 3D</span>
          <button type="button" data-scene-view="left" aria-label="Rotate studio left"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m14 7-5 5 5 5"/></svg></button>
          <button type="button" data-scene-view="reset" aria-label="Reset studio view"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 11a8 8 0 1 1 1 5M4 5v6h6"/></svg></button>
          <button type="button" data-scene-view="right" aria-label="Rotate studio right"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m10 7 5 5-5 5"/></svg></button>
        </div>
      </div>
      <div class="hero-actions">
        <a class="button button-primary" href="#work">Explore our work ${arrow}</a>
        <a class="button button-text" href="#services">What we do ${downArrow}</a>
      </div>
    </section>

    <main>
      <section class="work-section section" id="work" aria-labelledby="work-heading">
        <div class="container">
          <div class="section-heading work-heading reveal">
            <div class="section-title-wrap">
              <span class="section-number">01 <i></i></span>
              <h2 id="work-heading">Selected works</h2>
            </div>
            <p class="section-intro">A preview of what’s in progress.<br />Full case studies coming soon.</p>
            <span class="work-availability">Coming soon</span>
          </div>
          <div class="project-grid" id="all-projects">
            ${projects
              .map(
                (project) => `
              <article class="project-card reveal">
                <div class="project-visual project-visual-${project.key}">
                  <img src="${import.meta.env.BASE_URL}images/work/${project.key}.webp" width="880" height="852" loading="lazy" decoding="async" alt="" />
                  <span class="project-number">${project.number}</span>
                  <span class="project-status">Coming soon</span>
                  <div class="project-info">
                    <p class="project-category">${project.category}</p>
                    <h3 class="project-title">${project.title}</h3>
                  </div>
                </div>
                <p class="project-meta">Case study in progress</p>
              </article>
            `,
              )
              .join("")}
          </div>
        </div>
      </section>

      <section class="services-section section" id="services" aria-labelledby="services-heading">
        <div class="container">
          <div class="services-top reveal">
            <div>
              <span class="section-number section-number-light">02 <i></i></span>
              <p class="eyebrow eyebrow-light">What we do</p>
              <h2 id="services-heading">Complex challenges.<br /><em>Clear solutions.</em></h2>
            </div>
            <p>From the first question to the next release, we connect strategy, design, and engineering into systems built to work in the real world.</p>
          </div>
          <div class="service-grid">
            <article class="service-card reveal">
              <div class="service-symbol symbol-platform" aria-hidden="true"><span></span><span></span><span></span></div>
              <span class="service-index">01 / Discover</span>
              <h3>Product strategy</h3>
              <p>Define the right problem, map the opportunity, and give every build a clear direction.</p>
              <span class="service-tag">Research · Roadmaps · Architecture</span>
            </article>
            <article class="service-card reveal">
              <div class="service-symbol symbol-experience" aria-hidden="true"><span></span><span></span><span></span></div>
              <span class="service-index">02 / Design</span>
              <h3>Digital experiences</h3>
              <p>Make complicated workflows feel natural through useful, memorable interfaces.</p>
              <span class="service-tag">UX · UI · Prototypes</span>
            </article>
            <article class="service-card reveal">
              <div class="service-symbol symbol-systems" aria-hidden="true"><span></span><span></span><span></span></div>
              <span class="service-index">03 / Build</span>
              <h3>Connected systems</h3>
              <p>Engineer platforms, integrations, and data foundations that keep moving with you.</p>
              <span class="service-tag">Web · Data · Integrations</span>
            </article>
          </div>
        </div>
      </section>

      <section class="approach-section section" id="about" aria-labelledby="approach-heading">
        <div class="container approach-layout">
          <div class="approach-sticky reveal">
            <span class="section-number">03 <i></i></span>
            <p class="eyebrow">How we think</p>
            <h2 id="approach-heading">Built for the way business <span>actually moves.</span></h2>
            <p>Great digital products are never isolated screens. They connect people, decisions, and operations in a way that makes the whole business stronger.</p>
            <a class="inline-link" href="#contact">Start a conversation ${arrow}</a>
          </div>
          <div class="approach-steps">
            <article class="approach-step reveal"><span>01</span><div><h3>Understand the real work</h3><p>We start with the people, processes, and constraints behind the brief.</p></div></article>
            <article class="approach-step reveal"><span>02</span><div><h3>Design the whole system</h3><p>Interfaces, data, and technology are considered together from day one.</p></div></article>
            <article class="approach-step reveal"><span>03</span><div><h3>Build, learn, improve</h3><p>We ship in useful increments and keep refining what matters most.</p></div></article>
            <div class="approach-blueprint" aria-hidden="true"><span class="blueprint-ring ring-one"></span><span class="blueprint-ring ring-two"></span><span class="blueprint-core">N</span><span class="blueprint-dot dot-one"></span><span class="blueprint-dot dot-two"></span><span class="blueprint-dot dot-three"></span></div>
          </div>
        </div>
      </section>

      <section class="insights-section section" id="insights" aria-labelledby="insights-heading">
        <div class="container">
          <div class="section-heading insights-heading reveal">
            <div class="section-title-wrap"><span class="section-number">04 <i></i></span><h2 id="insights-heading">Ideas in motion</h2></div>
            <p class="section-intro">A few principles behind the way<br />we make digital work harder.</p>
          </div>
          <div class="insight-grid">
            <article class="insight-card reveal"><span class="insight-label">Perspective / 01</span><div class="insight-art insight-art-one" aria-hidden="true"><span></span><span></span><span></span></div><h3>Build around the work, not the tool.</h3><p>Technology creates value when it fits the decisions people need to make.</p></article>
            <article class="insight-card reveal"><span class="insight-label">Perspective / 02</span><div class="insight-art insight-art-two" aria-hidden="true"><span></span><span></span><span></span></div><h3>Good systems make room to grow.</h3><p>Clear foundations help teams move faster as their needs change.</p></article>
          </div>
        </div>
      </section>

      <section class="contact-section" id="contact" aria-labelledby="contact-heading">
        <div class="container contact-layout reveal">
          <div><span class="eyebrow eyebrow-light">Have a challenge in mind?</span><h2 id="contact-heading">Let's build<br /><span>what's next.</span></h2></div>
          <div class="contact-side"><p>Tell us what you are working on. The best ideas usually start with a conversation.</p><a class="contact-button" href="mailto:hello@nodeworks.studio?subject=Let%27s%20build%20something">Start a conversation ${arrow}</a><span>Concept contact address for this design demo</span></div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container footer-top"><a class="wordmark" href="#top">NODEWORKS<span>.</span></a><p>Digital systems for real business.</p><a href="#top">Back to top ${arrow}</a></div>
      <div class="container footer-bottom"><span>© ${new Date().getFullYear()} Nodeworks. Concept website.</span><span>Strategy · Design · Technology</span></div>
    </footer>
  </div>


`;

const canvas = document.querySelector<HTMLCanvasElement>(".hero-canvas");
if (!canvas) throw new Error("Hero canvas not found");
const cleanups: Array<() => void> = [];

const menuToggle = document.querySelector<HTMLButtonElement>(".menu-toggle");
const mobileNav = document.querySelector<HTMLElement>(".mobile-nav");
function setMenu(open: boolean) {
  if (!menuToggle || !mobileNav) return;
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  mobileNav.hidden = !open;
  document.body.classList.toggle("menu-open", open);
  syncScrollLock();
}
menuToggle?.addEventListener("click", () =>
  setMenu(menuToggle.getAttribute("aria-expanded") !== "true"),
);
mobileNav
  ?.querySelectorAll("a")
  .forEach((link) => link.addEventListener("click", () => setMenu(false)));
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});

const reduceMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;
let lenis: Lenis | undefined;
function syncScrollLock() {
  if (document.body.classList.contains("menu-open")) lenis?.stop();
  else lenis?.start();
}
const scrollEasing = (t: number) => 1 - Math.pow(1 - t, 4);
lenis = new Lenis({
  duration: 1.45,
  easing: scrollEasing,
  smoothWheel: true,
  wheelMultiplier: 0.9,
  respectReducedMotion: true,
});
lenis.on("scroll", ScrollTrigger.update);
const tickSmoothScroll = (time: number) => lenis?.raf(time * 1000);
gsap.ticker.add(tickSmoothScroll);
gsap.ticker.lagSmoothing(0);

function onAnchorClick(event: MouseEvent) {
  if (
    event.defaultPrevented ||
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey
  )
    return;
  const link =
    event.target instanceof Element
      ? event.target.closest<HTMLAnchorElement>('a[href^="#"]')
      : null;
  if (
    !link ||
    link.hasAttribute("download") ||
    (link.target && link.target !== "_self")
  )
    return;
  const target = document.getElementById(
    decodeURIComponent(link.hash.slice(1)),
  );
  if (!target || !lenis) return;
  event.preventDefault();
  if (window.location.hash !== link.hash)
    history.pushState(null, "", link.hash);
  lenis.resize();
  lenis.scrollTo(target, { duration: 1.6, easing: scrollEasing });
}
document.addEventListener("click", onAnchorClick);

if (!reduceMotion) {
  gsap.fromTo(
    ".hero-eyebrow, #hero-title, .hero-description, .hero-actions",
    { autoAlpha: 0, y: 30 },
    {
      autoAlpha: 1,
      y: 0,
      duration: 0.85,
      stagger: 0.085,
      ease: "power3.out",
      delay: 0.1,
    },
  );
  gsap.fromTo(
    ".hero-scene",
    { autoAlpha: 0, y: 18 },
    { autoAlpha: 1, y: 0, duration: 1.35, ease: "power2.out", delay: 0.15 },
  );

  gsap.utils.toArray<HTMLElement>(".reveal").forEach((element) => {
    gsap.fromTo(
      element,
      { autoAlpha: 0, y: 32 },
      {
        autoAlpha: 1,
        y: 0,
        duration: 0.8,
        ease: "power2.out",
        scrollTrigger: { trigger: element, start: "top 90%", once: true },
      },
    );
  });
}

const progress = document.querySelector<HTMLElement>(".scroll-progress");
ScrollTrigger.create({
  start: 0,
  end: "max",
  onUpdate: (self) => {
    if (progress) progress.style.transform = `scaleX(${self.progress})`;
  },
});

const navLinks = document.querySelectorAll<HTMLAnchorElement>(".desktop-nav a");
const sectionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      navLinks.forEach((link) =>
        link.classList.toggle("active", link.hash === `#${entry.target.id}`),
      );
    });
  },
  { rootMargin: "-30% 0px -60% 0px" },
);
document
  .querySelectorAll<HTMLElement>("main section[id]")
  .forEach((section) => sectionObserver.observe(section));

window.addEventListener("load", () => ScrollTrigger.refresh(), { once: true });

// Model framing can resize the hero after its GLBs load or the viewport changes.
let cancelLayoutRefresh = () => {};
const heroLayoutObserver = new ResizeObserver(() => {
  cancelLayoutRefresh();
  cancelLayoutRefresh = whenScrollIdle(() => {
    lenis?.resize();
    ScrollTrigger.refresh();
  });
});
heroLayoutObserver.observe(document.querySelector(".hero")!);

// The hero is the only WebGL canvas; project previews are static local images.
const cancelSceneInitialization = whenScrollIdle(() =>
  cleanups.push(mountFactoryScene(canvas)),
);

import.meta.hot?.dispose(() => {
  cancelSceneInitialization();
  cancelLayoutRefresh();
  heroLayoutObserver.disconnect();
  cleanups.forEach((cleanup) => cleanup());
  gsap.ticker.remove(tickSmoothScroll);
  document.removeEventListener("click", onAnchorClick);
  lenis?.destroy();
  sectionObserver.disconnect();
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
});
