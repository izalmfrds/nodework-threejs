// WebGL context creation and the first draw can exceed an idle callback's
// budget. Keep those one-time tasks out of an active wheel/touch/scroll gesture.
let lastScroll = -Infinity;
const pending = new Set<() => void>();
const markScroll = () => { lastScroll = performance.now(); };
const events = ['wheel', 'touchmove', 'scroll'] as const;
events.forEach(event => window.addEventListener(event, markScroll, { passive: true }));

export function whenScrollIdle(work: () => void) {
  let timer: number | undefined;
  let idle: number | undefined;
  let cancelled = false;
  const cancel = () => {
    cancelled = true;
    if (timer !== undefined) window.clearTimeout(timer);
    if (idle !== undefined) window.cancelIdleCallback(idle);
    pending.delete(cancel);
  };
  const schedule = () => {
    if (cancelled) return;
    const remaining = 180 - (performance.now() - lastScroll);
    if (remaining > 0) {
      timer = window.setTimeout(schedule, remaining);
      return;
    }
    const run = () => {
      if (cancelled) return;
      if (performance.now() - lastScroll < 180) { schedule(); return; }
      pending.delete(cancel);
      work();
    };
    if (typeof window.requestIdleCallback === 'function') idle = window.requestIdleCallback(run, { timeout: 1500 });
    else timer = window.setTimeout(run, 32);
  };
  pending.add(cancel);
  schedule();
  return cancel;
}

import.meta.hot?.dispose(() => {
  events.forEach(event => window.removeEventListener(event, markScroll));
  pending.forEach(cancel => cancel());
});
