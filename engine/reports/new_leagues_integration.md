# New league integration verification

Status: preflight in progress, no live prediction code changed.

Branch: codex/new-leagues, base origin/main dea160d. No push or merge.

Live source checks on 2026-10-29:

| Code | Betpawa ID | Confirmed competition | ESPN slug | Current football-data distinct teams | ESPN logos returning HTTP 200 |
|---|---:|---|---|---:|---:|
| EREDIV | 12125 | Eredivisie | ned.1 | 18 | 18 |
| JUPILER | 12128 | Pro League | bel.1 | 18 | 18 |
| PRIMEIRA | 12124 | Liga Portugal | por.1 | 18 | 18 |
| SUPERLIG | 12182 | Super Lig | tur.1 | 18 | 18 |

Competition identities were verified by the identified Betpawa categories endpoint. Team names
were fetched from current football-data season CSVs, the identified Betpawa upcoming event-list
endpoint (50 events per competition), and ESPN teams endpoints. Requests to Betpawa were paced
at one second. Each ESPN first-logo URL was fetched and returned HTTP 200.

Historical distinct-team counts from the real study CSVs:

- N1 and P1: 18 in each season 2014/15 through 2026/27.
- B1: 16 in 2014/15 through 2019/20; 18 in 2020/21 through 2022/23; 16 in 2023/24 through
  2025/26; 18 in 2026/27.
- T1: 18 in 2014/15 through 2019/20; 21 in 2020/21; 20 in 2021/22; 19 in 2022/23;
  20 in 2023/24; 19 in 2024/25; 18 in 2025/26 and 2026/27.

The unmodified cached baseline is running. Before/after equality is not yet established.
No new-league prediction, gate, settlement, setup, frontend or regression checks have passed yet.
