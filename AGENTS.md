# Instructions for Codex and other agents

Before doing anything in this repository, read **PROJECT.md** completely. It holds the owner's
rules, the goals, how the system works, the current status and the open tasks.

Rules for Codex in particular:
- Work on a separate branch; never push to or merge into `main` (Claude Code reviews and merges).
- Do not change anything that affects predictions (engine models, calibration, data) unless the
  prompt explicitly says so.
- After every change, update PROJECT.md in the same commit (status, open tasks, change log).
- The owner's rules in PROJECT.md are non-negotiable: accuracy first, consistency, decisions
  supported by data, no mistakes.
