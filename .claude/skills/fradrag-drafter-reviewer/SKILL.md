---
name: fradrag-drafter-reviewer
description: Drafter-reviewer-mønster til at foreslå og verificere sandsynlige oversete skattefradrag ud fra en brugers parsede skatteoplysninger og profil. Brug når /fradragstjek skal sanity-checke fund fra den deterministiske Python-kerne, eller når nye kandidat-fradrag skal foreslås og valideres mod 2026-reglerne, før de vises til brugeren.
---

# Fradrag drafter-reviewer

Dette skill lægger et lille to-rolle-lag oven på den deterministiske Python-kerne
(`fradragsjagt fradragstjek`). Formålet er IKKE at erstatte den deterministiske
logik, men at fange kandidat-fradrag den ikke fanger, og — vigtigst — at
verificere alt før det præsenteres for brugeren som en anbefaling.

## Grundprincipper (ufravigelige)

- **Kun lokale data.** Alt arbejde sker på data der allerede ligger lokalt
  (`skatteoplysninger.json`, `profil.json`). Der skal ikke og må ikke hentes
  eller sendes data til eksterne tjenester.
- **Masker CPR før noget sendes til modellen.** Hvis rå PDF-tekst eller
  R75-uddrag skal læses ind i konteksten, skal CPR-numre (og andre direkte
  identifikatorer) fjernes/masken først. `Skatteoplysninger`- og
  `FradragsForslag`-modellerne indeholder i forvejen ikke CPR — bevar det sådan.
- **Opfind aldrig beløb.** Ethvert kronebeløb i et forslag skal kunne
  udledes direkte af tal, der findes i brugerens egne parsede data
  (`skatteoplysninger.json`) eller profil (`profil.json`). Gæt eller
  "typiske" beløb er ikke tilladt.
- **Citér altid skat.dk-feltet.** Hvert forslag skal angive det konkrete
  felt/rubrik-nummer (fx felt 460, rubrik 51) fra `FradragsForslag.felt`.
- **Indberet aldrig for brugeren.** Værktøjet foreslår og forklarer — det
  udfylder eller sender aldrig noget til skat.dk. Det er altid brugeren, der
  indberetter og bærer ansvaret.

## Rollerne

### DRAFTER

Foreslår kandidat-fradrag ud fra brugerens parsede `Skatteoplysninger` og
`Profil`. For hvert kandidat-fradrag skal DRAFTER angive:

- `navn` — kort dansk navn på fradraget.
- `felt` — skat.dk felt/rubrik-nummer.
- `estimeret_fradrag` — beregnet direkte fra brugerens egne tal.
- `estimeret_skattebesparelse` — estimat, typisk fradrag × marginalskat eller ~26%.
- `begrundelse` — hvorfor DRAFTER tror dette er overset, med reference til
  de konkrete data-felter det er udledt fra.
- `saadan_indberetter_du` — konkret vejledning til TastSelv-feltet.

DRAFTER må foreslå bredt — det er REVIEWERs job at sortere fra.

### REVIEWER

Går hvert forslag fra DRAFTER igennem mod 2026-satser og -grænser, se
`reviewer-checklist.md`. For hvert forslag:

- Verificér at beløbet faktisk kan udledes af brugerens data (ingen opfundne tal).
- Verificér at eventuelle grænser/tærskler (kørselsafstand, bundfradrag,
  indkomstlofter osv.) er overholdt.
- Sæt `verificeret = true` kun hvis forslaget består alle relevante tjek.
- Sæt `verificeret = false` og forklar hvorfor, hvis forslaget er
  uunderbygget, overtræder en tærskel, eller mangler dokumentation i data.
- Afvis (fjern helt) forslag der er rene gæt uden belæg i brugerens data.

Kun forslag REVIEWER har set igennem, må vises til brugeren som "sandsynlige
oversete fradrag". Uverificerede forslag kan stadig vises, men skal tydeligt
markeres som ikke-verificerede, med `sikkerhed`-feltet sat til `"mulig"` eller
`"kræver dokumentation"` snarere end `"sandsynlig"`.

## Reference

Se `reviewer-checklist.md` i denne mappe for de konkrete 2026-tærskler
REVIEWER skal tjekke imod.
