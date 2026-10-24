// Short "why this bet" lines for a slip pick, from the model's own numbers for that match.
import { odds, pct } from "./lib";
import type { Fixture, MarketKey } from "./types";

export function explainPick(market: MarketKey, fixture: Fixture): string[] {
  const m = Object.fromEntries(fixture.markets.map((x) => [x.market, x]));
  const p = (k: MarketKey) => m[k]?.probability ?? 0;
  const [xh, xa] = fixture.expected_goals;
  const total = (xh + xa).toFixed(1);
  const scores = fixture.top_scorelines.slice(0, 2).map((s) => s.score).join(", ");
  const home = fixture.home, away = fixture.away;
  const lines: string[] = [];

  switch (market) {
    case "home_1up":
    case "away_1up": {
      const isHome = market === "home_1up";
      const [team, opp, xt, xo] = isHome ? [home, away, xh, xa] : [away, home, xa, xh];
      lines.push(`${team} expected ${xt.toFixed(1)} goals vs ${opp} ${xo.toFixed(1)}.`);
      lines.push(`${team} score first ${pct(p(isHome ? "home_first" : "away_first"))} and lead at some point ${pct(p(market))} of the time: a 1Up pays even if they don't win.`);
      break;
    }
    case "over_0.5":
    case "over_1.5":
    case "over_2.5":
    case "over_3.5": {
      const need = Number(market.split("_")[1]) + 0.5;
      lines.push(`Expected ${total} goals in total (${home} ${xh.toFixed(1)}, ${away} ${xa.toFixed(1)}).`);
      lines.push(`${pct(p(market))} chance of ${need}+ goals. Likeliest scores: ${scores}.`);
      break;
    }
    case "under_2.5":
    case "under_3.5": {
      const most = Number(market.split("_")[1]) - 0.5;
      lines.push(`Only ${total} goals expected in total (${home} ${xh.toFixed(1)}, ${away} ${xa.toFixed(1)}).`);
      lines.push(`${pct(p(market))} chance of ${most} goals or fewer. Likeliest scores: ${scores}.`);
      break;
    }
    case "home_win":
    case "away_win": {
      const isHome = market === "home_win";
      const [team, opp] = isHome ? [home, away] : [away, home];
      lines.push(`${team} ${(isHome ? xh : xa).toFixed(1)} vs ${opp} ${(isHome ? xa : xh).toFixed(1)} expected goals.`);
      lines.push(`${team} win ${pct(p(market))}, draw ${pct(p("draw"))}, ${opp} win ${pct(p(isHome ? "away_win" : "home_win"))}.`);
      break;
    }
    case "double_1x":
    case "double_x2":
    case "double_12": {
      const loses = market === "double_1x" ? `${away} win` : market === "double_x2" ? `${home} win` : "a draw";
      const loseKey: MarketKey = market === "double_1x" ? "away_win" : market === "double_x2" ? "home_win" : "draw";
      lines.push(`${home} ${xh.toFixed(1)} vs ${away} ${xa.toFixed(1)} expected goals.`);
      lines.push(`Covers two of three results (${pct(p(market))}); it only loses on ${loses} (${pct(p(loseKey))}).`);
      break;
    }
    default:
      lines.push(`${pct(p(market))} chance by our model.`);
  }

  const pick = m[market];
  if (pick?.market_probability != null) {
    const gap = pick.model_probability - pick.market_probability;
    lines.push(Math.abs(gap) < 0.03
      ? `Bookmakers agree: they make it ${pct(pick.market_probability)}.`
      : `Our model says ${pct(pick.model_probability)}, bookmakers ${pct(pick.market_probability)}: final ${pct(pick.probability)} blends both.`);
  }
  if (pick?.betpawa_odds != null) {
    const value = pick.probability * pick.betpawa_odds - 1;
    lines.push(`Betpawa ${odds(pick.betpawa_odds)} vs fair ${odds(pick.fair_odds)}: ${value >= 0.03 ? `pays ${pct(value)} more than it should` : value > -0.03 ? "about a fair price" : "priced below fair"}.`);
  }
  return lines;
}
