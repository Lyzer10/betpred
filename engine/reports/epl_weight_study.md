# EPL model weight study (PROJECT.md task 4, pre-registered)

Legs: 4,919 EPL slip-market legs, 2025/26 onwards, 137 match days.

| Procedure | Weights by season | Mean log loss |
|---|---|---:|
| V (test-era only, live) | {'2025/26': 0.35000000000000003, '2026/27': 0.2} | 0.61285 |
| A (validation + test-era) | {'2024/25': 0.0, '2025/26': 0.05, '2026/27': 0.05} | 0.61252 |

V - A: +0.00033 (95% CI -0.00166 to +0.00231). **Decision: keep V (current live).**

Gates (task-1 rules, reported only): V: over_0.5 INSUFFICIENT, under_2.5 FAIL; A: over_0.5 INSUFFICIENT
