export type MarketKey =
  | "home_win" | "draw" | "away_win"
  | "over_0.5" | "over_1.5" | "over_2.5" | "over_3.5" | "under_2.5" | "under_3.5"
  | "btts_yes" | "btts_no"
  | "home_1up" | "away_1up" | "home_first" | "away_first"
  | "double_1x" | "double_x2" | "double_12";

export interface MarketPrediction {
  market: MarketKey;
  label: string;
  probability: number;          // final: model blended with bookmaker market
  model_probability: number;
  market_probability: number | null;
  fair_odds: number;
  betpawa_odds: number | null;
}

export interface League { code: string; name: string; country: string }

export const PREMIER_LEAGUE: League = { code: "EPL", name: "Premier League", country: "England" };

export interface Fixture {
  id: number;
  league?: League;
  mode?: "blended" | "market";   // market: calibrated bookmaker consensus (no model edge in that league)
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  day: string;                   // match day in the user's time zone (EAT)
  expected_goals: [number, number];
  top_scorelines: { score: string; probability: number }[];
  has_market_odds: boolean;
  markets: MarketPrediction[];
}

export interface SlipLeg {
  league?: League;
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  market: MarketKey;
  label: string;
  probability: number;
  estimated_odds: number | null;
  betpawa_odds: number | null;
  fair_odds: number;
  price_warning?: boolean;
  won?: boolean | null;
}

export interface ValuePick extends SlipLeg {
  edge: number;
  kelly: number;
}

export interface Slip {
  total_odds: number;
  win_probability: number;
  legs: SlipLeg[];
  odds_source?: "betpawa" | "estimated";
  expected_value?: number;
  kelly?: number;
  price_warning?: boolean;
  flexi?: { min_correct: number; probability: number }[];   // SportyBet Flexi: P(at least k of n win)
  locked?: boolean;              // first match under way: frozen and tracked
  status?: "won" | "lost" | "pending";
}

export interface HistoryEntry extends Slip {
  round: string;
  tier: TierName;
  generated_at: string;
  status: "won" | "lost" | "pending";
}

export type TierName = "safe" | "medium" | "big";

export interface BacktestTier {
  slips: number;
  win_rate: number;
  predicted_win_rate: number;
  average_odds: number;
}

export interface Result {
  date: string;
  home: string;
  away: string;
  score: [number, number];
  outcomes: Record<MarketKey, boolean>;
}

export interface DayBets {
  date: string;
  fixtures: number[];
  value_picks: ValuePick[];
  slips: Partial<Record<TierName, Slip>>;
}

export interface Predictions {
  generated_at: string;
  time_zone: string;
  model: { training_last_date: string; market_blend_model_weight: number; retail_margin: number };
  backtest: Record<TierName, BacktestTier>;
  fixtures: Fixture[];
  days: DayBets[];
  value_rules?: { min_edge: number; min_probability: number };
  history: HistoryEntry[];
  results: Result[];
  archive: ArchiveDay[];
  live_record: LiveRecord;
  health?: Health;
}

export type HealthStatus = "ok" | "watch" | "warning" | "insufficient";

export interface Health {
  status: HealthStatus;
  stake_factor: number;          // multiply every recommended stake by this
  checks: { name: string; status: HealthStatus; detail: string }[];
}

export interface ArchiveDay { date: string; fixtures: number; settled: number }

export interface LiveRecord {
  matches: number;
  result_hit_rate?: number;
  log_loss?: number | null;
  market_log_loss?: number | null;
  confident_picks?: number;
  confident_hit_rate?: number | null;
  value_bets?: number;
  value_bets_won?: number;
  value_roi?: number | null;
}

export interface ArchivedFixture {
  league?: League;
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  expected_goals: [number, number];
  markets: { market: MarketKey; label: string; probability: number; market_probability: number | null; betpawa_odds?: number | null }[];
  result?: { score: [number, number]; outcomes: Record<MarketKey, boolean> };
}

export interface ArchiveSnapshot {
  date: string;
  generated_at: string;
  fixtures: ArchivedFixture[];
  slips: Partial<Record<TierName, Slip>>;
}

export interface SavedPick {
  id: string;
  fixtureKey: string;           // date|home|away
  date: string;
  home: string;
  away: string;
  market: MarketKey;
  label: string;
  probability: number;
  odds: number;
  stake: number;                // TSh
  savedAt: string;
}
