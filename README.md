<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo/logo-light.svg">
    <img src="assets/logo/logo-light.svg" alt="fradragsjagt" width="360">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/mathiasesn/fradragsjagt/actions/workflows/ci.yml"><img src="https://github.com/mathiasesn/fradragsjagt/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/ruff-lint%20%2B%20format-261230.svg?logo=ruff&logoColor=white" alt="Ruff">
  <img src="https://img.shields.io/badge/skatteår-2026-2ea44f.svg" alt="Skatteår 2026">
  <img src="https://img.shields.io/badge/privacy-100%25%20lokal-success.svg" alt="100% lokal">
</p>

# fradragsjagt 🔍

**Gratis, open source, lokal dansk fradrags- og skatteassistent. Kører på din egen maskine — og sender aldrig dine data væk.**

De populære skatte-apps tager op til **30% af din tilbagebetaling** for noget, du selv kan gøre gratis på skat.dk. `fradragsjagt` er et gratis alternativ: du henter selv dine dokumenter fra TastSelv, og værktøjet parser dem **lokalt**, beregner din skat med **2026-satserne** og finder sandsynlige **oversete fradrag** — med kørselsfradraget som flagskib.

- 🔒 **Privacy-first** — al databehandling sker lokalt. Ingen cloud, ingen telemetri, ingen konto.
- 💸 **Ingen andel af din refusion** — det er gratis. For altid.
- 🧾 **Du indberetter selv** — værktøjet fortæller dig *hvilket felt* på skat.dk, men indberetter aldrig for dig.
- 🛠️ **Open source (MIT)** — fork den, læs koden, verificér beregningerne selv.

## Sådan virker det

```
setup  →  parse  →  beregn  →  fradragstjek  →  rapport
```

1. **`fradragsjagt setup`** — opret en lokal profil (kommune, kirkeskat, civilstand, pendlerafstand, fagforening, boligejer).
2. **Hent dine dokumenter selv** fra [TastSelv](https://www.skat.dk): log ind med MitID, og gem **årsopgørelse**, **forskudsopgørelse** og **R75/skatteoplysninger** som PDF. *(fradragsjagt automatiserer aldrig MitID-login — det er hverken lovligt eller nødvendigt.)*
3. **`fradragsjagt parse dine-pdfer.pdf`** — parser PDF'erne til strukturerede felter, lokalt.
4. **`fradragsjagt beregn`** — beregner din skat med 2026-satser. Kommuneskat for en række kommuner er indbygget; ukendte kommuner bruger landsgennemsnittet, indtil den fulde 98-kommuners-tabel er komplet.
5. **`fradragsjagt fradragstjek`** — gennemgår dine data for oversete fradrag (drafter-reviewer-mønster: én agent foreslår, én verificerer).
6. **`fradragsjagt rapport`** — samler alt til én rapport: *"her er dine sandsynlige oversete fradrag, og sådan indberetter du dem selv (felt X)."*

## Installation

Python-koden bor i `backend/`. Installér CLI'en derfra:

```bash
cd backend
pip install -e ".[dev]"
fradragsjagt --version
```

## Projektstruktur

```
backend/
  core/    # domænelogik: skatteberegning, satser, fradragsregler, parsing, rapport
  cli/     # tyndt argparse-lag oven på core
  tests/   # pytest-suite
frontend/  # (muligt senere)
.claude/   # Claude Code agent-lag (skills, kommandoer)
```

`core` er delt domænelogik; `cli` er et tyndt lag ovenpå. Et kommende `api/`-lag (FastAPI)
kan tilføjes ved siden af `cli/` og genbruge `core`. Se [`backend/README.md`](backend/README.md)
for udvikler-kommandoer.

## Claude Code agent-lag

Ud over CLI'en kan `fradragsjagt` køres som en Claude Code-agent. `.claude/`-mappen indeholder skills, der driver drafter-reviewer-gennemgangen af dine fradrag oven på den deterministiske Python-motor.

## Privatliv & sikkerhed

- Skattedata forlader **aldrig** din maskine. `.gitignore` blokerer PDF'er og parsede data fra git.
- Bruger du Claude Code-laget, så **maskér dit CPR** før data sendes til modellen, og brug en konto/API med træning fravalgt.
- Ingen NemKonto, ingen fuldmagt, ingen rådgiveradgang (formular 02.052). Vi efterligner **ikke** betalingstjenesternes fuldmagtsmodel.

## Fremtidigt arbejde / To-do

Roadmap og kendte MVP-begrænsninger spores som [GitHub issues](https://github.com/mathiasesn/fradragsjagt/issues) — se labels `roadmap`, `ingestion` og `mvp-begrænsning`.

Retningslinjen for alt planlagt arbejde: vi bygger **beregning og fradragsfund** der ikke kræver et live SKAT-datafeed, og hvor vores styrke — *"vi viser dig reglen og feltet"* — slår de kommercielle apps' black box. Vi bygger **ikke** realtids-dataindhentning eller auto-indberetning; det bryder med projektets løfte om lokal, privatlivsførst, du-indberetter-selv.

## Ansvarsfraskrivelse

fradragsjagt er et **uafhængigt open source-projekt** og er **ikke tilknyttet Skattestyrelsen, skat.dk eller Anthropic**. Værktøjet giver **generel information og overslag — ikke individuel eller bindende skatterådgivning**. Du skal selv indberette på skat.dk og bærer selv ansvaret for rigtigheden af dine oplysninger. Verificér altid mod [skat.dk](https://www.skat.dk) før du indberetter.

## Licens

MIT — se [LICENSE](LICENSE).
