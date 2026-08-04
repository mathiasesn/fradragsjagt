# AGENTS.md

Operating instructions for coding agents (Claude Code, Codex, Cursor, Copilot, Aider,
Jules, ...) working in this repo. Thin and behavioural by design — see `ARCHI.md` for
architecture depth.

## 1. What this is

`fradragsjagt` is a free, local-first Danish tax tool: the user downloads their own
documents from TastSelv (skat.dk), and the tool parses them locally, calculates tax with
the 2026 rates, and finds probable overlooked `fradrag` (deductions) — with `koersel`
(commuting) deduction as the flagship. It never touches skat.dk itself.

Privacy/scope promise: all processing is local. No cloud calls, no telemetry, no account,
no MitID automation, no auto-filing (`auto-indberetning`) to skat.dk. The user always
fetches their own PDFs and submits their own return.

## 2. Where things live

- `backend/core/` — domain logic: `models.py`, `engine.py`, `rates_2026.py`,
  `parsing.py`, `profile.py`, `report.py`, `fradrag/` (deduction rules).
- `backend/cli/` — thin argparse layer (`cli.main:main`) on top of `core`.
- `backend/tests/` — pytest suite, imports `core.*` directly.
- `.claude/` — agent skills and commands for this repo.
- `specs/` — task specs (e.g. this file's own spec: `specs/agents-md.md`).
- `assets/` — logos and branding assets.
- `ARCHI.md` — full architecture reference (repo root); see section 6 below.

## 3. Commands

All commands below run from `backend/` (`cd backend` first):

```bash
uv run --with pytest --with pypdf python -m pytest -q   # tests
uv run --with ruff ruff check core cli tests            # lint
uv run --with ruff ruff format core cli tests           # format
```

Console script: `fradragsjagt = "cli.main:main"` (install with `pip install -e ".[dev]"`,
then run `fradragsjagt --version`).

## 4. Conventions

- Danish domain naming throughout (`fradrag`, `koersel`, `aarsopgoerelse`,
  `kirkeskat`, ...) — these are code identifiers and legal field names; do not
  translate them.
- `core` must never import `cli`. Dependencies flow one way: `cli` depends on `core`,
  never the reverse.
- All 2026 tax rates/thresholds live only in `backend/core/rates_2026.py` — do not
  hardcode rate numbers elsewhere.
- Ruff: line-length 110, target py310.

### Adding a new deduction rule

1. Create a new file in `backend/core/fradrag/rules/regler/`, e.g. `mit_fradrag.py`,
   with a function decorated `@fradragsregel` (see `registry.py` and existing rules
   such as `fagforening.py` for the pattern — signature
   `(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]`).
2. No registry edit is needed beyond that — rules under `regler/` are auto-discovered
   by `backend/core/fradrag/rules/registry.py` via `pkgutil`.
3. Add a matching `backend/tests/test_<rule>.py` covering the new rule.
4. Run the test/lint commands in section 3 before considering the change done.

## 5. Do not

- Make network calls from `core` or `cli` — this is a local-only tool.
- Automate MitID or any skat.dk login flow.
- Auto-file or auto-submit (`auto-indberetning`) anything to skat.dk. The user always
  reviews and submits themselves.
- Commit tax PDFs, parsed tax data, or any other real user data to the repo.
- Send unmasked CPR numbers to a model — mask CPR before including any user data in a
  prompt.
- Change 2026 rates/thresholds in `rates_2026.py` without a citable skat.dk source.

## 6. Architecture reference

For anything structural or architectural, read `ARCHI.md` rather than asking here again.
Section index:

1. How to Read This Document
2. Overview
3. Technology Stack
4. Project Structure
5. Core Architecture Principles
6. Build System & Toolchain
7. Configuration
8. Data Model (`core/models.py`)
9. Tax Calculation Engine (`core/engine.py` + `rates_2026.py`)
10. Deduction Rules (`core/fradrag/`)
11. PDF Parsing (`core/parsing.py`)
12. Report (`core/report.py`)
13. Claude Code Agent Layer (`.claude/`)
14. Testing
15. Summary & Key Architectural Decisions
