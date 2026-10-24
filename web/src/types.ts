export type MarketKey =
  | "home_win" | "draw" | "away_win"
  | "over_0.5" | "over_1.5" | "over_2.5" | "over_3.5" | "under_2.5" | "under_3.5"
  | "btts_yes" | "btts_no"
  | "home_1up" | "away_1up" | "home_first" | "away_first";

export interface MarketPrediction {
  market: MarketKey;
  label: string;
  probability: number;          // final: model blended with bookmaker market
  model_probability: number;
  market_probability: number | null;
  fair_odds: number;
}

export interface Fixture {
  id: number;
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  round: string;
  expected_goals: [number, number];
  top_scorelines: { score: string; probability: number }[];
  has_market_odds: boolean;
  markets: MarketPrediction[];
}

export interface SlipLeg {
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  market: MarketKey;
  label: string;
  probability: number;
  estimated_odds: number;
  fair_odds: number;
  won?: boolean | null;
}

export interface Slip {
  total_odds: number;
  win_probability: number;
  legs: SlipLeg[];
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

export interface Predictions {
  generated_at: string;
  round: string | null;
  model: { training_last_date: string; market_blend_model_weight: number; retail_margin: number };
  backtest: Record<TierName, BacktestTier>;
  fixtures: Fixture[];
  slips: Partial<Record<TierName, Slip>>;
  history: HistoryEntry[];
  results: Result[];
  archive: ArchiveDay[];
  live_record: LiveRecord;
}

export interface ArchiveDay { date: string; fixtures: number; settled: number }

export interface LiveRecord {
  matches: number;
  result_hit_rate?: number;
  log_loss?: number | null;
  market_log_loss?: number | null;
  confident_picks?: number;
  confident_hit_rate?: number | null;
}

export interface ArchivedFixture {
  date: string;
  time: string;
  kickoff_utc: string;
  home: string;
  away: string;
  expected_goals: [number, number];
  markets: { market: MarketKey; label: string; probability: number; market_probability: number | null }[];
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
  stake: number;
  savedAt: string;
}
