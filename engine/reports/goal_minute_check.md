# Task 19 — Goal-Minute Accuracy Check (Understat vs ESPN)

## 1. Sample & Pre-Registered Gate Decision

- **Compared sample**: **332 goals** across **73 matches** spanning all **5 main leagues** (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) and **3 seasons** (`2023/24`, `2024/25`, `2025/26`).
- **10-minute window (`00:01-09:59`, ESPN `period == 1` and `clock.value < 600.0` seconds)**: Under mapping `Understat minute <= 9`, agreement is **332 / 332 (100.00%)** (gate threshold `>= 98.00%` -> **PASS**).
- **Chronological goal order (when `goals.parquet` is sorted by `minute`)**: Full match goal-scoring team sequence agrees with ESPN in **73 / 73 matches (100.00%)**, and first-goal team agrees in **73 / 73 (100.00%)** (gate threshold `>= 99.00%` -> **PASS**).
- **Overall Task 19 Verdict**: **PASS** — Understat processed goal minutes may be used in Task 20 with `minute <= 9` for the `00:01-09:59` 10-minute window and `goals.parquet` sorted by `minute` for first-goal order.

## 2. Exact Minute Mapping & Stoppage-Time Storage

1. **Regular-time goals (`clock.displayValue` without `+`)**: Understat stores **0-indexed completed minutes**: `minute = floor(seconds / 60) = display_minute - 1`. Across `296` regular-time goals, **293 / 296 (98.99%)** match `floor(seconds / 60)` exactly, and the remaining **3** differ by `-1` minute.
2. **First-half stoppage goals (`45'+x'` in `period == 1`)**: ESPN sets `clock.value = 2700.0` for all first-half stoppage goals and records `+x'` in `clock.displayValue`. Understat stores them as **`minute = 45 + x - 1 = 44 + x`** (`45'+1' -> 45`, `45'+2' -> 46`, ..., `45'+6' -> 50`). Across `16` first-half stoppage goals, **16 / 16 (100.00%)** match `44 + x` exactly. Because `45'+2'` (`minute = 46`) collides numerically with a second-half 47th-minute goal (`46:00-46:59`, `minute = 46`), half-time markets must be settled from `ht_home_goals`/`ht_away_goals` (`HTHG`/`HTAG`), never by filtering `minute <= 45`.
3. **Second-half stoppage goals (`90'+x'` in `period == 2`)**: ESPN sets `clock.value = 5400.0` and records `+x'` in `clock.displayValue`. Understat stores them as **`minute = 90 + x - 1 = 89 + x`** (`90'+1' -> 90`, ..., `90'+12' -> 101`). Across `20` second-half stoppage goals, **20 / 20 (100.00%)** match `89 + x` exactly.
4. **Row order in `goals.parquet`**: Raw `goals.parquet` stores all `home` goals before `away` goals (raw row order agrees with ESPN in only `21 / 73` = `28.77%` of matches). Sorting `goals.parquet` by `minute` restores chronological order in **`73 / 73` (`100.00%`)** of compared matches.

## 3. Sample Breakdown by League and Season

| League | Season | Date | Matches | Goals | `< 10:00` Agreement (`us <= 9`) | Sorted Goal Order Agreement |
|---|---|---|---:|---:|---:|---:|
| `EPL` | `2023/24` | `2024-05-19` | 5 | 24 | 24/24 (100.0%) | 5/5 (100.0%) |
| `EPL` | `2024/25` | `2024-12-04` | 5 | 23 | 23/23 (100.0%) | 5/5 (100.0%) |
| `EPL` | `2025/26` | `2026-01-07` | 5 | 22 | 22/22 (100.0%) | 5/5 (100.0%) |
| `LALIGA` | `2023/24` | `2024-05-19` | 5 | 24 | 24/24 (100.0%) | 5/5 (100.0%) |
| `LALIGA` | `2024/25` | `2025-05-18` | 5 | 21 | 21/21 (100.0%) | 5/5 (100.0%) |
| `LALIGA` | `2025/26` | `2026-05-23` | 5 | 19 | 19/19 (100.0%) | 5/5 (100.0%) |
| `SERIEA` | `2023/24` | `2023-09-17` | 4 | 20 | 20/20 (100.0%) | 4/4 (100.0%) |
| `SERIEA` | `2024/25` | `2025-05-18` | 4 | 17 | 17/17 (100.0%) | 4/4 (100.0%) |
| `SERIEA` | `2025/26` | `2026-05-17` | 5 | 16 | 16/16 (100.0%) | 5/5 (100.0%) |
| `BUNDES` | `2023/24` | `2024-05-18` | 5 | 24 | 24/24 (100.0%) | 5/5 (100.0%) |
| `BUNDES` | `2024/25` | `2025-05-17` | 5 | 22 | 22/22 (100.0%) | 5/5 (100.0%) |
| `BUNDES` | `2025/26` | `2026-05-16` | 5 | 23 | 23/23 (100.0%) | 5/5 (100.0%) |
| `LIGUE1` | `2023/24` | `2024-04-28` | 5 | 26 | 26/26 (100.0%) | 5/5 (100.0%) |
| `LIGUE1` | `2024/25` | `2025-05-17` | 5 | 26 | 26/26 (100.0%) | 5/5 (100.0%) |
| `LIGUE1` | `2025/26` | `2025-10-29` | 5 | 25 | 25/25 (100.0%) | 5/5 (100.0%) |
| **Total** | **3 seasons** | **15 matchdays** | **73** | **332** | **332/332 (100.00%)** | **73/73 (100.00%)** |

## 4. Agreement Summary by Goal Category

| Category | Goals | Formula Tested | Exact Match | Off by -1 min | `< 10:00` Agreement (`us <= 9`) | Naive `us <= 10` Agreement |
|---|---:|---|---:|---:|---:|---:|
| Regular time (no `+`) | 296 | `floor(seconds / 60)` | 293/296 (98.99%) | 3 | 296/296 (100.00%) | 294/296 (99.32%) |
| First-half stoppage (`45'+x'`) | 16 | `44 + x` | 16/16 (100.00%) | 0 | 16/16 (100.00%) | 16/16 (100.00%) |
| Second-half stoppage (`90'+x'`) | 20 | `89 + x` | 20/20 (100.00%) | 0 | 20/20 (100.00%) | 20/20 (100.00%) |
| All compared goals | 332 | Combined mapping | 329/332 (99.10%) | 3 | 332/332 (100.00%) | 330/332 (99.40%) |

## 5. Boundary Verification Around 10:00 (`480s` to `720s`, Period 1)

| League | Date | Match | Team | ESPN Seconds | ESPN Display | `< 10:00` (`< 600s`) | Understat `minute` | `minute <= 9` | `minute <= 10` |
|---|---|---|---|---:|---|---:|---:|---:|---:|
| `EPL` | `2024-05-19` | Crystal Palace vs Aston Villa | `home` | `505.0` | `9'` | `Yes` | `8` | `Yes` | `Yes` |
| `LIGUE1` | `2024-04-28` | Rennes vs Brest | `home` | `513.0` | `9'` | `Yes` | `8` | `Yes` | `Yes` |
| `LALIGA` | `2025-05-18` | Celta vs Vallecano | `home` | `552.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `BUNDES` | `2026-05-16` | Bayern Munich vs FC Koln | `home` | `562.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `LALIGA` | `2025-05-18` | Ath Madrid vs Betis | `home` | `566.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `EPL` | `2024-12-04` | Everton vs Wolves | `home` | `568.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `LIGUE1` | `2025-05-17` | St Etienne vs Toulouse | `away` | `573.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `BUNDES` | `2026-05-16` | Ein Frankfurt vs Stuttgart | `away` | `576.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `LALIGA` | `2025-05-18` | Sociedad vs Girona | `away` | `577.0` | `10'` | `Yes` | `9` | `Yes` | `Yes` |
| `EPL` | `2024-12-04` | Southampton vs Chelsea | `home` | `608.0` | `11'` | `No` | `10` | `No` | `Yes` |
| `LIGUE1` | `2024-04-28` | Rennes vs Brest | `away` | `646.0` | `11'` | `No` | `10` | `No` | `Yes` |
| `LALIGA` | `2026-05-23` | Real Madrid vs Ath Bilbao | `home` | `715.0` | `12'` | `No` | `11` | `No` | `No` |

## 6. All First-Half Stoppage Goals (`45'+x'`)

| League | Date | Match | Team | ESPN Seconds | ESPN Display | Formula `44 + x` | Understat `minute` |
|---|---|---|---|---:|---|---:|---:|
| `BUNDES` | `2025-05-17` | Freiburg vs Ein Frankfurt | `away` | `2700.0` | `45'+4'` | `48` | `48` |
| `BUNDES` | `2026-05-16` | Ein Frankfurt vs Stuttgart | `away` | `2700.0` | `45'+4'` | `48` | `48` |
| `EPL` | `2024-05-19` | Luton vs Fulham | `home` | `2700.0` | `45'+1'` | `45` | `45` |
| `EPL` | `2024-05-19` | Luton vs Fulham | `away` | `2700.0` | `45'+3'` | `47` | `47` |
| `EPL` | `2026-01-07` | Newcastle vs Leeds | `away` | `2700.0` | `45'+5'` | `49` | `49` |
| `LALIGA` | `2024-05-19` | Villarreal vs Real Madrid | `away` | `2700.0` | `45'+2'` | `46` | `46` |
| `LALIGA` | `2025-05-18` | Ath Madrid vs Betis | `home` | `2700.0` | `45'+3'` | `47` | `47` |
| `LALIGA` | `2025-05-18` | Barcelona vs Villarreal | `home` | `2700.0` | `45'+5'` | `49` | `49` |
| `LALIGA` | `2025-05-18` | Celta vs Vallecano | `away` | `2700.0` | `45'+2'` | `46` | `46` |
| `LALIGA` | `2026-05-23` | Betis vs Levante | `away` | `2700.0` | `45'+1'` | `45` | `45` |
| `LALIGA` | `2026-05-23` | Real Madrid vs Ath Bilbao | `away` | `2700.0` | `45'+1'` | `45` | `45` |
| `LIGUE1` | `2025-05-17` | Marseille vs Rennes | `home` | `2700.0` | `45'+1'` | `45` | `45` |
| `LIGUE1` | `2025-10-29` | Nantes vs Monaco | `home` | `2700.0` | `45'+6'` | `50` | `50` |
| `SERIEA` | `2023-09-17` | Frosinone vs Sassuolo | `home` | `2700.0` | `45'+4'` | `48` | `48` |
| `SERIEA` | `2025-05-18` | Inter vs Lazio | `home` | `2700.0` | `45'+2'` | `46` | `46` |
| `SERIEA` | `2026-05-17` | Cagliari vs Torino | `home` | `2700.0` | `45'+2'` | `46` | `46` |

## 7. Every Disagreement Example

### 7.1 Disagreements on `< 10:00` Window Under Verified Mapping (`minute <= 9`)

- **None** (`0 / 332` disagreements). Every goal with `espn_seconds < 600.0` in Period 1 has `Understat minute <= 9`, and every goal with `espn_seconds >= 600.0` has `Understat minute >= 10`.

### 7.2 Disagreements on `< 10:00` Window If Naive `minute <= 10` Were Used

| League | Date | Match | Team | ESPN Seconds | ESPN Display | Understat `minute` | Reason |
|---|---|---|---|---:|---|---:|---|
| `EPL` | `2024-12-04` | Southampton vs Chelsea | `home` | `608.0` | `11'` | `10` | Scored in 11th display minute (`10:00-10:59`), stored as 0-indexed minute `10` |
| `LIGUE1` | `2024-04-28` | Rennes vs Brest | `away` | `646.0` | `11'` | `10` | Scored in 11th display minute (`10:00-10:59`), stored as 0-indexed minute `10` |

### 7.3 Disagreements on Chronological Goal Order (`goals.parquet` Sorted by `minute`)

- **None** (`0 / 73` matches). When sorted by `minute`, `goals.parquet` reproduces ESPN's exact scoring-team sequence in all 73 matches.

### 7.4 Regular-Time Minute Formula Disagreements (`us_minute != floor(espn_seconds / 60)`)

| League | Date | Match | Team | ESPN Seconds | ESPN Display | `floor(seconds / 60)` | Understat `minute` | Difference |
|---|---|---|---|---:|---|---:|---:|---:|
| `EPL` | `2024-05-19` | Luton vs Fulham | `away` | `4081.0` | `69'` | `68` | `67` | `-1` |
| `SERIEA` | `2023-09-17` | Roma vs Empoli | `home` | `4740.0` | `79'` | `79` | `78` | `-1` |
| `SERIEA` | `2026-05-17` | Cagliari vs Torino | `away` | `2220.0` | `37'` | `37` | `36` | `-1` |
