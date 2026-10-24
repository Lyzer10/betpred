import { useState } from "react";
import { shortName } from "./lib";

// Premier League's public badge CDN, by club id (checked image by image).
const PL_BADGE_IDS: Record<string, number> = {
  Arsenal: 3, "Aston Villa": 7, Bournemouth: 91, Brentford: 94, Brighton: 36, Chelsea: 8, Coventry: 9,
  "Crystal Palace": 31, Everton: 11, Fulham: 54, Hull: 88, Ipswich: 40, Leeds: 2, Liverpool: 14,
  "Manchester City": 43, "Manchester United": 1, Newcastle: 4, "Nottingham Forest": 17, Sunderland: 56,
  Tottenham: 6, "West Ham": 21, Wolves: 39, Burnley: 90, Leicester: 13, Southampton: 20,
};

const badgeUrl = (team: string) =>
  PL_BADGE_IDS[team] ? `https://resources.premierleague.com/premierleague/badges/50/t${PL_BADGE_IDS[team]}.png` : null;

/** Club badge; falls back to the team's initials when there is no image or it fails to load. */
export function TeamBadge({ team, size = 28 }: { team: string; size?: number }) {
  const [failed, setFailed] = useState(false);
  const url = badgeUrl(team);
  if (url && !failed) {
    return (
      <img src={url} alt="" width={size} height={size} loading="lazy" onError={() => setFailed(true)}
        className="shrink-0 object-contain" style={{ width: size, height: size }} />
    );
  }
  return (
    <span aria-hidden className="inline-flex shrink-0 items-center justify-center rounded-full bg-surface-2 font-bold tracking-wide text-ink-2"
      style={{ width: size, height: size, fontSize: Math.max(size * 0.32, 8) }}>
      {shortName(team)}
    </span>
  );
}

/** Small flags for league headers (plain shapes: no external images). */
export function Flag({ country, width = 28 }: { country: string; width?: number }) {
  const h = Math.round(width * 2 / 3);
  const box = { width, height: h, className: "shrink-0 rounded-[3px] ring-1 ring-border" };
  switch (country) {
    case "England":
      return <svg viewBox="0 0 30 20" {...box}><rect width="30" height="20" fill="#fff" /><rect x="12.5" width="5" height="20" fill="#ce1124" /><rect y="7.5" width="30" height="5" fill="#ce1124" /></svg>;
    case "Spain":
      return <svg viewBox="0 0 30 20" {...box}><rect width="30" height="20" fill="#aa151b" /><rect y="5" width="30" height="10" fill="#f1bf00" /></svg>;
    case "Italy":
      return <svg viewBox="0 0 30 20" {...box}><rect width="10" height="20" fill="#009246" /><rect x="10" width="10" height="20" fill="#fff" /><rect x="20" width="10" height="20" fill="#ce2b37" /></svg>;
    case "Germany":
      return <svg viewBox="0 0 30 20" {...box}><rect width="30" height="7" fill="#000" /><rect y="6.6" width="30" height="6.8" fill="#dd0000" /><rect y="13.3" width="30" height="6.7" fill="#ffce00" /></svg>;
    case "France":
      return <svg viewBox="0 0 30 20" {...box}><rect width="10" height="20" fill="#002395" /><rect x="10" width="10" height="20" fill="#fff" /><rect x="20" width="10" height="20" fill="#ed2939" /></svg>;
    default:
      return <svg viewBox="0 0 30 20" {...box}><rect width="30" height="20" fill="currentColor" opacity="0.15" /></svg>;
  }
}
