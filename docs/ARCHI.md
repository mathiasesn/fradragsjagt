# fradragsjagt Architecture Documentation

> Generated: 2026-07-22 · Commit: d31cf74 · Version: 0.1.0
> Re-read this file at the start of any session touching this codebase. Update it when the architecture changes (new major dependency, restructured layer, changed convention).

## 1. How to Read This Document

This is the architecture memory for **fradragsjagt** — a free, open-source, **local-only** Danish tax-deduction assistant. It is written for AI coding agents and new human contributors: read it once instead of re-globbing the tree.

The codebase is small (~1400 lines of Python across `backend/`) and in **Danish** — identifiers, comments, docstrings, and all user-facing strings are Danish. Match that when writing code. The domain is Danish personal income tax for **income year 2026**.

Two hard truths govern everything here and are repeated in the summary: **(1) no tax data ever leaves the machine** — no network calls, no telemetry, no accounts; **(2) the tool never files to skat.dk for the user** — it explains *which field* to fill, the user files it themselves and owns the result.

## 2. Overview

The populære Danish tax apps take up to 30% of a refund for something a user can do for free on skat.dk. `fradragsjagt` is the free alternative: the user downloads their own documents from TastSelv (MitID login, done by the user — never automated), and the tool parses them **locally**, computes 2026 tax, and flags **likely overlooked deductions** (*oversete fradrag*), with the commuter deduction (*kørselsfradrag*) as the flagship.

The system is a **CLI pipeline** plus a thin **Claude Code agent layer**:

```
setup  →  parse  →  beregn  →  fradragstjek  →  rapport
```

- `setup` — create a local profile JSON (municipality, church tax, commute km, homeowner, union, etc.).
- `parse` — extract structured fields from user-supplied TastSelv PDFs into `skatteoplysninger.json` (CPR masked, never stored).
- `beregn` — compute 2026 tax from the parsed fields + profile.
- `fradragstjek` — run deterministic rules to find overlooked deductions.
- `rapport` — assemble everything into one Markdown report.

The Python core is deterministic and authoritative. The Claude agent layer (`.claude/`) sits *on top* as a drafter-reviewer that proposes extra candidate deductions and verifies every one against 2026 thresholds before it is shown — it never replaces the deterministic logic.

## 3. Technology Stack

- **Language:** Python `>=3.10` (`from __future__ import annotations` used throughout; `X | Y` unions and `list[...]` generics are fine).
- **Runtime dependency:** `pypdf>=4.0` — the only production dependency, used solely in `core/parsing.py` for PDF text extraction. Imported lazily inside functions so the rest of the tool works without it.
- **Dev dependencies:** `pytest>=8.0`, `ruff>=0.5`.
- **Build backend:** `hatchling` (packages `core` and `cli` into the wheel).
- **Tooling runner:** [`uv`](https://docs.astral.sh/uv/) — all dev/CI commands run through `uv run --with ...`.
- **No frameworks.** Pure stdlib otherwise: `argparse`, `dataclasses`, `enum`, `csv`, `json`, `re`, `pathlib`.

## 4. Project Structure

```
fradragsjagt/
  README.md                 # root: full intro, disclaimer, privacy, TODO landscape
  LICENSE                   # MIT
  .pre-commit-config.yaml   # ruff check + format hooks (backend-only)
  .github/workflows/ci.yml  # lint + test, working-directory: backend
  backend/                  # ALL Python lives here
    pyproject.toml          # package metadata, ruff/pytest config, console script
    uv.lock
    README.md               # backend dev commands
    core/                   # shared domain logic (the authority)
      __init__.py           # __version__, DISCLAIMER constant
      models.py             # dataclasses: the contract between every module
      engine.py             # 2026 tax calculation (pure beregn_skat + run_beregn IO wrapper)
      rates_2026.py         # all 2026 rates/thresholds + kommunesats() CSV lookup
      parsing.py            # PDF → Skatteoplysninger (CPR-masking)
      aarsopgoerelse.py     # projicer_aarsopgoerelse: estimerer restskat/overskydende skat
      profile.py            # setup wizard + save/load Profil JSON
      report.py             # byg_rapport (pure) + run_rapport IO wrapper
      fradrag/
        __init__.py         # run_fradragstjek + re-exports
        koersel.py          # kørselsfradrag (flagship commuter deduction)
        rules.py            # rule-based drafter: find_oversete_fradrag
      data/
        kommuneskat_2026.csv  # PARTIAL municipal tax table (~32 of 98 kommuner)
    tests/                  # pytest suite, one test_*.py per core module
  specs/                    # design notes / spec docs (not shipped)
  .claude/                  # Claude Code agent layer
    commands/fradragstjek.md
    skills/fradrag-drafter-reviewer/{SKILL.md,reviewer-checklist.md}
    settings.local.json
```

Organizing principle: **`core` is shared domain logic; `cli` is a thin argparse shell over it.** A future `api/` layer (FastAPI) is intended to be added as a sibling of `cli/` reusing `core` the same way. Nothing in `cli` should contain business logic.

Note: git status may still show a recent move from the old `src/fradragsjagt/` layout to `backend/{core,cli}` — the `backend/` layout is canonical.

## 5. Core Architecture Principles

1. **Local-only, always.** No module makes network calls or writes telemetry. `.gitignore` blocks all user data (`*.pdf`, `skatteoplysninger.json`, `profil.json`, `fradragsjagt-rapport.md`, `.fradragsjagt/`). Never introduce a dependency or code path that phones home.
2. **Never invent an amount.** Every kroner figure in a deduction suggestion must be derivable from the user's own parsed data or profile. No "typical" or guessed values. This is enforced in the rules and re-stated as an inviolable rule for the agent layer.
3. **CPR is never stored or logged.** `parsing.py` masks CPR (`(CPR maskeret)`) on sight; the `Skatteoplysninger` and `FradragsForslag` models deliberately hold no direct identifiers. Keep it that way.
4. **Pure core, thin IO shell.** The heavy logic is pure functions — `beregn_skat` (engine), `byg_rapport` (report), `parse_skattetekst` (parsing), `beregn_koerselsfradrag` / `find_oversete_fradrag` (fradrag). Each has a `run_*` wrapper that does file IO, prints, and returns an exit code. Tests target the pure functions.
5. **Cite the skat.dk field.** Every deduction suggestion carries the concrete field/rubrik number (e.g. felt 460, rubrik 51) so the user can find and file it.
6. **Never file for the user.** The tool proposes and explains; the user always files on skat.dk and bears responsibility. No NemKonto, no power-of-attorney (form 02.052) — deliberately *not* the payment-services model.
7. **Degrade gracefully.** `report.py` wraps each stage (profile / engine / fradrag) in try/except so a missing or failing module still produces a partial report rather than crashing.

## 6. Build System & Toolchain

All Python commands run from **`backend/`** (that is where `pyproject.toml`, `uv.lock`, and CI's `working-directory` point). Copied verbatim from `backend/README.md` and `.github/workflows/ci.yml`:

```bash
# tests
uv run --with pytest --with pypdf python -m pytest -q

# lint
uv run --with ruff ruff check core cli tests

# format (check-only, as CI runs it)
uv run --with ruff ruff format --check core cli tests

# install the console script for manual use
pip install -e ".[dev]"
fradragsjagt --version
```

- **Console script:** `fradragsjagt = "cli.main:main"` (from `pyproject.toml [project.scripts]`).
- **pytest config:** `testpaths = ["tests"]`, `pythonpath = ["."]` — so tests import `core.*` / `cli.*` with `backend/` as root.
- **ruff:** `line-length = 110`, `target-version = "py310"`.
- **CI** (`.github/workflows/ci.yml`): two jobs — `lint` (ruff check + format --check) and `test` (pytest) — both `working-directory: backend`, using `astral-sh/setup-uv@v5`. Runs on push to `main` and all PRs.
- **pre-commit** (`.pre-commit-config.yaml`): ruff check (`--fix`) and format via `uv run --project backend`, plus stock hygiene hooks. `typos` is deliberately omitted (Danish → false positives).

## 7. Configuration

There is no config file or env-var layer — configuration is **local JSON produced by the tool itself**, plus compile-time rate constants.

- **`profil.json`** (default path `profil.json`, `core/profile.py:DEFAULT_PATH`) — the user profile from `setup`. Schema = the `Profil` dataclass. `civilstand` is serialized as its enum `.value`.
- **`skatteoplysninger.json`** (default from CLI `--input`) — parsed tax fields. Schema = `Skatteoplysninger` dataclass (`asdict`); `None` means "not parsed" (distinct from `0`).
- **CLI flags** (see `cli/main.py`): `--input`, `--out`, `--non-interactive` (setup). Every subcommand defaults these so the pipeline works with zero flags.
- **2026 rates/thresholds** live as module constants in `core/rates_2026.py` — the single source of truth for tax numbers. Duplicated as defensive fallbacks in `fradrag/koersel.py` and `fradrag/rules.py` (guarded `try: from ..rates_2026 import ... except ImportError`) so those modules work standalone. **If you change a rate, change it in `rates_2026.py` AND the two fallback blocks**, and mirror the threshold in `.claude/skills/fradrag-drafter-reviewer/reviewer-checklist.md`.

## 8. Data Model (`core/models.py`)

`models.py` is the contract between every module. All amounts are DKK. No model holds CPR. Dataclasses:

- **`Civilstand`** — `str, Enum`: `ENLIG` | `GIFT`.
- **`Profil`** — local user profile: `kommune`, `kirkeskattemedlem`, `civilstand`, commute (`pendler_km_hver_vej`, `arbejdsdage_pr_aar=216`, `bor_i_yderkommune`), memberships (`fagforening`, `a_kasse`, `boligejer`), `indkomstaar=2026`.
- **`Skatteoplysninger`** — parsed tax fields, all `Optional[float]` defaulting to `None` (so the engine distinguishes 0 from unknown). Field comments carry the skat.dk rubrik/felt number (e.g. `loen` = rubrik 11, `befordringsfradrag` = rubrik 51). Has a `raw: dict` for other parsed fields and a **`from_dict` classmethod** that keeps only known dataclass fields (forward-compatible; unknown keys ignored). Prefer `from_dict` when loading JSON.
- **`Skatteberegning`** — engine output: personlig/skattepligtig indkomst, am_bidrag, bundskat, kommuneskat, kirkeskat, mellemskat/topskat/top_topskat, beskæftigelsesfradrag, jobfradrag, personfradrag_vaerdi, samlet_skat, and a free-form `detaljer: dict`.
- **`FradragsForslag`** — one overlooked-deduction suggestion: `navn`, `felt`, `estimeret_fradrag`, `estimeret_skattebesparelse`, `begrundelse`, `saadan_indberetter_du`, `sikkerhed` (`"mulig"` | `"sandsynlig"` | `"kræver dokumentation"`), `verificeret` (set by the reviewer agent).
- **`TidligAarsopgoerelse`** — output of `projicer_aarsopgoerelse`: projiceret restskat/overskydende skat (`difference`, `er_restskat`, `beloeb`) plus `tilstraekkeligt_grundlag` (requires both `a_skat_indeholdt` and `am_bidrag_indeholdt`).

## 9. Tax Calculation Engine (`core/engine.py` + `rates_2026.py`)

`beregn_skat(oplysninger, profil) -> Skatteberegning` is a **pure, deterministic** function (no IO). The model is **deliberately simplified** and documents its own simplifications in the module docstring. Sequence:

1. `personlig_indkomst = loen or 0`.
2. `am_bidrag = 8%` of that.
3. Base for progression = `personlig_indkomst_efter_am` (after AM-bidrag).
4. `beskæftigelsesfradrag = min(12.75% × base, 63,300)`.
5. `jobfradrag = min(4.5% × max(base − 235,200, 0), 3,100)`.
6. `skattepligtig_indkomst = max(base − beskæftigelsesfradrag − jobfradrag − personfradrag(54,100), 0)`.
7. Bundskat (12.01%) / kommuneskat / kirkeskat computed on `skattepligtig_indkomst`.
8. Mellemskat / topskat / top-topskat computed progressively on `personlig_indkomst_efter_am` (new 2026 reform brackets: mellem 7.5% 641,200–777,900; top 7.5% 777,900–2,592,700; top-top 5% above).

**Known simplifications (do not treat the engine as authoritative tax):** the *skatteloft* (52.07%) is a soft warning in `detaljer["advarsel"]`, **not** an enforced marginal-rate cap; net capital income is not modeled; personfradrag does not reduce the mellem/top brackets. These are called out in the docstring and README TODO.

`rates_2026.py` holds every rate/threshold as a named constant with a sourcing comment. **All 2026 numbers are best-effort projections** and are flagged as such — they must be verified against skat.dk before real use. `kommunesats(kommune)` looks up the municipality in `data/kommuneskat_2026.csv` (case-insensitive) and **falls back to the national average** (`GENNEMSNITLIG_KOMMUNESKAT_PCT = 25.07`, kirke 0.68) for unknown kommuner — the CSV covers only ~32 of 98 municipalities.

## 10. Deduction Rules (`core/fradrag/`)

The deterministic "drafter" pass. `find_oversete_fradrag(oplysninger, profil) -> list[FradragsForslag]` (`fradrag/rules.py`) runs conservative, independent rule functions and concatenates their suggestions. Each rule only fires when the profile clearly indicates it, and every suggestion sets a `sikkerhed` level. Current rules:

- **`_tjek_koersel`** — the flagship. Delegates to `beregn_koerselsfradrag` (`fradrag/koersel.py`), which applies the 24 km/day bundgrænse (round-trip), tiered km rates (2.28 normal / 1.14 over 120 km / 2.53 yderkommune-flat), and an income-tapered *ekstra befordringsfradrag* for low incomes (341,500–391,500 kr taper). Suppressed if already reported at ≥95% of the computed amount.
- **`_tjek_haandvaerker_service`** — homeowners only: håndværkerfradrag (felt 460, max 9,000) and servicefradrag (felt 461, max 18,300) if not already present.
- **`_tjek_gaver`** — §8A charitable gifts (rubrik 55, max 20,000), marked `"kræver dokumentation"`.
- **`_tjek_fagforening`** — union / a-kasse dues (rubrik 50/52) if profile says member but no deduction present.

Deduction *value* is estimated crudely as ~26% (`FRADRAG_VAERDI_PROCENT`, roughly bund + kommuneskat), not precise marginal rate. **To add a rule:** write a `_tjek_*` helper returning `list[FradragsForslag]`, add it to `find_oversete_fradrag`, cite the skat.dk field, keep amounts derived from real data, and add a threshold entry to the reviewer checklist.

## 11. PDF Parsing (`core/parsing.py`)

`parse_skattetekst(text) -> Skatteoplysninger` is the pure, testable parser; `parse_documents(paths, out)` is the IO wrapper (lazy-imports `pypdf`). Details:

- CPR (`\b\d{6}-?\d{4}\b`) is detected and replaced with `(CPR maskeret)` in `raw` — never the real number.
- Danish number format is assumed: `.` = thousands separator, `,` = decimal (`_parse_dkk`). All user-facing amounts are printed back in this format via `f"{x:,.0f}".replace(",", ".")` — a repeated idiom across the codebase.
- `_FELT_MOENSTRE` maps regex label patterns → (`Skatteoplysninger` attribute, rubrik/felt key). `detect_dokumenttype` classifies årsopgørelse / forskudsopgørelse / R75.
- Multiple PDFs are merged with `_merge` (non-`None` fields in the newer doc win; `raw` dicts update).

## 12. Report (`core/report.py`)

`byg_rapport(oplysninger, profil, beregning, forslag) -> str` builds the Danish Markdown report (skatteoverblik table + "Tidlig årsopgørelse" section, projected restskat/overskydende skat via `aarsopgoerelse.py` + overlooked-deductions table + "sådan indberetter du" section + `DISCLAIMER`). It **never contains CPR**. `run_rapport` is the IO wrapper that loads inputs and, per principle #7, degrades gracefully if profile/engine/fradrag are unavailable — producing a partial report with a note rather than failing.

## 13. Claude Code Agent Layer (`.claude/`)

A thin two-role layer *on top of* the deterministic core — it augments, never replaces it.

- **`commands/fradragstjek.md`** — the `/fradragstjek` slash command: run `fradragsjagt beregn`, then `fradragsjagt fradragstjek`, then invoke the skill to draft + verify extra candidates, then `fradragsjagt rapport`, then present, clearly labeling each suggestion `verificeret: ja/nej`.
- **`skills/fradrag-drafter-reviewer/SKILL.md`** — the drafter-reviewer pattern. **DRAFTER** proposes candidate deductions broadly from the user's local data; **REVIEWER** verifies each against 2026 thresholds and sets `verificeret`. Inviolable rules mirror the core principles: local data only, mask CPR before anything reaches the model, never invent amounts, always cite the skat.dk field, never file for the user.
- **`skills/fradrag-drafter-reviewer/reviewer-checklist.md`** — the concrete 2026 thresholds REVIEWER checks against. **Keep this in sync with `rates_2026.py`.**

If you use the agent layer on real data: mask CPR first, and use an account/API with training opted out.

## 14. Testing

pytest suite in `backend/tests/`, one `test_*.py` per core module (`engine`, `koersel`, `parsing`, `profile`, `report`, `rules`). Tests import `core.*` (root = `backend/`, via `pythonpath = ["."]`) and target the **pure** functions. When adding logic, add or extend the matching `test_*.py`; keep tests deterministic and offline (they already are).

## 15. Summary & Key Architectural Decisions

An agent must not violate these:

- **No network, no telemetry, no accounts.** Tax data never leaves the machine. Don't add a dependency or path that phones home. User data stays git-ignored.
- **Never file to skat.dk for the user.** Suggest and explain (cite the field); the user files and owns the result. No power-of-attorney model.
- **Never invent a kroner amount.** Every figure must derive from the user's own parsed data or profile.
- **CPR is never stored or logged.** Keep models identifier-free; keep the masking in `parsing.py`.
- **Everything is Danish** — identifiers, comments, strings. All amounts are DKK, formatted with `.` thousands / `,` decimal.
- **`core` = pure domain logic + thin `run_*` IO shells; `cli` = thin argparse.** No business logic in `cli`. A future `api/` reuses `core` the same way.
- **`rates_2026.py` is the single source of truth for tax numbers** — but the two fallback blocks in `fradrag/` and the reviewer checklist must be updated in lockstep.
- **The engine is deliberately simplified** (soft skatteloft, no capital income, projected 2026 rates). Treat it as an estimate; it is not authoritative tax advice.
- **All 2026 rates are unverified projections** and the kommune table covers only ~32/98 municipalities (national-average fallback). See README TODO before broad release.
- **Run Python tooling from `backend/` via `uv`.** Tests offline & deterministic.
