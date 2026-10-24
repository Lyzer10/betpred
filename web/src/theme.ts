// Light / dark / follow-the-phone. Stored per device; applied before the first paint.
export type Theme = "auto" | "light" | "dark";
const THEME_KEY = "pl-predictor:theme";

export function loadTheme(): Theme {
  try {
    const value = localStorage.getItem(THEME_KEY);
    return value === "light" || value === "dark" ? value : "auto";
  } catch {
    return "auto";
  }
}

export function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "auto") root.removeAttribute("data-theme");
  else root.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* storage unavailable: theme lasts for this visit */
  }
}

export const NEXT_THEME: Record<Theme, Theme> = { auto: "light", light: "dark", dark: "auto" };
