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
4. **`fradragsjagt beregn`** — beregner din skat med 2026-satser for alle 98 kommuner.
5. **`fradragsjagt fradragstjek`** — gennemgår dine data for oversete fradrag (drafter-reviewer-mønster: én agent foreslår, én verificerer).
6. **`fradragsjagt rapport`** — samler alt til én rapport: *"her er dine sandsynlige oversete fradrag, og sådan indberetter du dem selv (felt X)."*

## Installation

```bash
pip install -e ".[dev]"
fradragsjagt --version
```

## Claude Code agent-lag

Ud over CLI'en kan `fradragsjagt` køres som en Claude Code-agent. `.claude/`-mappen indeholder skills, der driver drafter-reviewer-gennemgangen af dine fradrag oven på den deterministiske Python-motor.

## Privatliv & sikkerhed

- Skattedata forlader **aldrig** din maskine. `.gitignore` blokerer PDF'er og parsede data fra git.
- Bruger du Claude Code-laget, så **maskér dit CPR** før data sendes til modellen, og brug en konto/API med træning fravalgt.
- Ingen NemKonto, ingen fuldmagt, ingen rådgiveradgang (formular 02.052). Vi efterligner **ikke** betalingstjenesternes fuldmagtsmodel.

## Ansvarsfraskrivelse

fradragsjagt er et **uafhængigt open source-projekt** og er **ikke tilknyttet Skattestyrelsen, skat.dk eller Anthropic**. Værktøjet giver **generel information og overslag — ikke individuel eller bindende skatterådgivning**. Du skal selv indberette på skat.dk og bærer selv ansvaret for rigtigheden af dine oplysninger. Verificér altid mod [skat.dk](https://www.skat.dk) før du indberetter.

## Licens

MIT — se [LICENSE](LICENSE).
