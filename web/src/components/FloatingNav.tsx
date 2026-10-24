import { useCallback, useLayoutEffect, useRef, useState } from "react";

interface NavItem<T extends string> {
  id: T;
  label: string;
  icon: string;
}

export function FloatingNav<T extends string>({ items, active, onSelect }: {
  items: readonly NavItem<T>[];
  active: T;
  onSelect: (id: T) => void;
}) {
  const rail = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<T, HTMLButtonElement>());
  const [indicator, setIndicator] = useState({ left: 0, width: 0 });

  const measure = useCallback(() => {
    const container = rail.current;
    const button = buttons.current.get(active);
    if (!container || !button) return;
    const containerBox = container.getBoundingClientRect();
    const buttonBox = button.getBoundingClientRect();
    setIndicator({ left: buttonBox.left - containerBox.left, width: buttonBox.width });
  }, [active]);

  useLayoutEffect(() => {
    measure();
    const observer = new ResizeObserver(measure);
    if (rail.current) observer.observe(rail.current);
    window.addEventListener("resize", measure);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [measure, items.length]);

  return (
    <nav data-floating-nav aria-label="Primary" className="glass-strong floating-nav">
      <div ref={rail} className="relative flex">
        <span aria-hidden className="floating-nav-indicator"
          style={{ width: indicator.width, transform: `translateX(${indicator.left}px)`, opacity: indicator.width ? 1 : 0 }} />
        {items.map((item) => (
          <button key={item.id} ref={(node) => {
            if (node) buttons.current.set(item.id, node);
            else buttons.current.delete(item.id);
          }} onClick={() => onSelect(item.id)} aria-current={active === item.id ? "page" : undefined}
            className={`relative z-10 flex min-h-14 flex-1 flex-col items-center justify-center gap-0.5 rounded-full px-1 text-[10px] font-semibold transition-colors ${active === item.id ? "text-accent" : "text-ink-3"}`}>
            <svg viewBox="0 0 24 24" className="h-[21px] w-[21px]" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d={item.icon} />
            </svg>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
