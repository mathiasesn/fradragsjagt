# Backlog

Planlagt arbejde for `fradragsjagt`. Prioriteret roadmap øverst, kendte MVP-begrænsninger nederst.

Retningslinjen for hele backloggen: vi bygger **beregning og fradragsfund** der ikke kræver et live SKAT-datafeed, og hvor vores styrke — *"vi viser dig reglen og feltet"* — slår de kommercielle apps' black box. Vi bygger **ikke** realtids-dataindhentning eller auto-indberetning; det bryder med projektets løfte om lokal, privatlivsførst, du-indberetter-selv.

---

## Roadmap

### 1. Udvid fradrags-regelregister 🟢 *(kerne)*

Byg `fradragstjek` ud fra dagens kørselsfradrag-flagskib til et bredt regelregister med per-regel proveniens og felt-nummer på skat.dk.

Kandidat-regler:
- Håndværkerfradrag / servicefradrag
- Gaver til godkendte foreninger
- A-kasse / fagforeningskontingent *(delvist på plads)*
- Børnebidrag
- Dobbelt husførelse
- Rejsefradrag
- Indskud på pension
- Tab på aktier (fremførsel)

- **Pro:** projektets flagskib og differentiator — vi viser reglen, ikke en black box.
- **Con:** regelvedligehold pr. skatteår er den løbende omkostning.
- **Design:** `rules/`-register hvor hver regel bærer proveniens (kilde på skat.dk) + felt-nummer, så rapporten kan sige *"indberet i felt X, jf. kilde Y"*.

### 2. Tidlig årsopgørelse 🟢

Rapportvisning oven på den eksisterende motor: projekteret restskat / overskydende skat.

- **Pro:** næsten gratis givet `engine.py`; stærkt headline-output til `rapport`.
- **Con:** nøjagtighed afhænger af komplet input — kræver tydelig *"estimat"*-forbehold.
- **Design:** ren rapport-view over eksisterende beregning. Ingen ny domænelogik.

### 3. Skattetrin-beregning 🟢

Marginalskat + afstand til topskattegrænsen, oven på `rates_2026.py`.

- **Pro:** triviel tilføjelse; muliggør optimeringsråd (*"du er X kr fra topskat"*).
- **Con:** giver kun mening som *beregning*, ikke som løbende *monitor* — drop monitor-framingen.
- **Design:** statisk funktion; ingen datafeed nødvendig.

### 4. Forskudstjek 🟡→🟢

Diff mellem forskudsopgørelse og faktisk/forventet indkomst → hvilket felt brugeren selv skal rette.

- **Pro:** høj værdi i praksis (undgår restskat); passer til *"vi fortæller dig hvilket felt."*
- **Con:** uden live-indkomst hviler vi på brugerens egne estimater.
- **Design:** diff-rapport, **ikke** automatisk indberetning. Vi parser allerede forskudsopgørelsen.

### 6. Grounded AI-assistent 🟡

Udvid drafter-reviewer-skillet til et *"spørg om dine skatteoplysninger"*-Q&A.

- **Pro:** naturlig forlængelse af Claude-agent-laget; stærk UX-differentiator.
- **Con:** hallucinationsrisiko på skatteret = ansvar. Skal grundes i regelregisteret + citater.
- **Design:** grundede, citerede svar **kun** over vores verificerede regler — ikke åben-ende. Bygges forsigtigt.

> **Bevidst udeladt fra roadmap** (anti-tese for et lokalt, du-indberetter-selv-værktøj): Indkomstoverblik (kræver live eIndkomst) og Skat på Autopilot (auto-indberetning). Aktier-portefølje, SU-fribeløb og "min skat i samfundet" er parkeret til evt. senere moduler / web-frontend.

---

## Dataindhentning (ingestion)

De kommercielle apps får deres data via **fuldmagt/rådgiveradgang** (formular 02.052) + system-integration (eIndkomst, R75) — en *persistent* fuldmagt er det, der giver dem "live" monitorering. Vi bygger **ikke** den model: al automatiseret indhentning kræver enten en persistent fuldmagt (som vi bevidst afviser) eller MitID-session-styring (ulovligt/ToS-brud). Vi læser **de samme autoritative artefakter** — R75, årsopgørelse, forskudsopgørelse — men brugeren eksporterer dem selv.

Målet er derfor ikke en *datapipe*, men en **ingestion-normalizer**: gør den manuelle eksport-sti så friktionsfri som et API, og giv hvert nedstrøms-feature (regelregister, tidlig årsopgørelse, forskudstjek) et rent, proveniens-mærket input. Tiers:

### T0. PDF-parsing 🟢 *(på plads)*

`parse` udtrækker felter fra eksporterede PDF'er lokalt (`parsing.py`: `parse_skattetekst`, `_FELT_MOENSTRE`, `_merge`), maskerer CPR og gemmer som JSON.

- **Status:** implementeret. Regex-baseret felt-udtræk + dokumenttype-detektion (årsopgørelse / forskud / R75).
- **Con:** regex mod PDF-tekstlayout er skørt — brydes når skat.dk ændrer opsætning.

### T1. Strukturerede eksporter 🟢

Ingestér mere maskinvenlige eksporter, ikke kun PDF-tekst. TastSelv tilbyder R75/skatteoplysninger i mere strukturerede formater; parse dem direkte i stedet for at regex'e renderet PDF-tekst.

- **Pro:** dramatisk mere robust end PDF-layout-regex; færre parser-brud pr. skatteår.
- **Con:** kræver at kortlægge det strukturerede felt-skema → vores `Skatteoplysninger`.
- **Design:** ny parser bag samme `parse_skattetekst`-kontrakt; PDF-stien bliver fallback.

### T2. Guidet eksport-wizard 🟢

Fortæl brugeren præcist hvilken TastSelv-menusti + hvilken "download"-knap pr. dokument, og verificér filen når den lægges ind.

- **Pro:** ren UX, nul automatisering — passer perfekt til du-henter-selv-løftet.
- **Con:** vedligehold af menu-stier når skat.dk's UI ændrer sig.
- **Design:** CLI-flow der lister de tre dokumenter, viser sti-instruktion, og kører `detect_dokumenttype` på hver droppet fil for at bekræfte at det rigtige dokument blev hentet.

### T3. Normaliseret ingestion med proveniens 🟢 *(arkitektonisk nøgle)*

Ét normaliseret skema som R75, årsopgørelse, forskud og manuel `setup` alle fødes ind i — med **proveniens pr. felt** (`kilde: R75 felt 201`).

I dag bærer `Skatteoplysninger.raw` kun `feltnr -> værdi`; der er ingen kilde-mærkning af *hvilket dokument* et felt kom fra, og `_merge` lader bare senere dokumenter overskrive tidligere uden at spore konflikter.

- **Pro:** fælles substrat under regelregister (1), tidlig årsopgørelse (2) og forskudstjek (4) — alle kræver rene, kilde-mærkede felter. Samme abstraktion uanset om bytes kom fra PDF (T0) eller struktureret eksport (T1).
- **Con:** kræver en refaktor af `Skatteoplysninger` + `_merge` (og de moduler der læser dem).
- **Design:** pr.-felt `(værdi, kilde-dokument, felt-nr)` i stedet for flad `raw`-dict. `_merge` sporer konflikter (samme felt, forskellig værdi fra to dokumenter) i stedet for tavst at overskrive. Rapporten kan så sige *"felt X = Y kr., jf. din R75."*

---

## Kendte MVP-begrænsninger

Dette er en tidlig MVP. Kendte begrænsninger og planlagte forbedringer:

- [ ] **Fuld kommunetabel** — kun ~32 af 98 kommuner har indbygget skatteprocent i dag; ukendte kommuner falder tilbage på landsgennemsnittet. Komplettér tabellen før bred udgivelse.
- [ ] **Verificér 2026-satser mod skat.dk** — alle 2026-tal (inkl. faktoren på 0,64 for ekstra befordringsfradrag) er *best-effort fremskrivninger* og er markeret i koden. De skal verificeres mod skat.dk's officielle udmelding, før nogen indberetter for alvor.
- [ ] **Fuld progressiv skattemodel** — skattemotoren er forenklet: skatteloftet er i dag en blød advarsel, ikke et hårdt loft, og det progressive grundlag er en tilnærmelse. Se noter i `engine.py`.
- [ ] **Øvrige fradrag** — `renteudgifter`, `aktieindkomst` (aktieindkomstbeskatning), `civilstand` (ægtefælleoverførsel) og rejsefradrag parses/indsamles, men indgår endnu ikke i beregningen.

Bidrag er velkomne — se koden, verificér beregningerne, og åbn gerne en PR.
