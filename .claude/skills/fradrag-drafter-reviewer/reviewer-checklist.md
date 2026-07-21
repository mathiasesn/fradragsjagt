# Reviewer-checkliste: 2026-tærskler

Konkret liste REVIEWER skal tjekke hvert kandidat-fradrag imod, før
`verificeret` sættes til `true`. Tal er 2026-satser og kan ændre sig — hold
denne fil opdateret hvis `rates_2026.py` opdateres.

## Befordringsfradrag (kørsel)

- **Bundgrænse:** kun kørsel ud over 24 km pr. dag (tur/retur) giver fradrag.
  Under 24 km/dag samlet: intet fradrag.
- **25–120 km/dag:** 2,28 kr./km.
- **Over 120 km/dag:** 1,14 kr./km (halv sats).
- **Yderkommune-tillæg:** hvis brugeren bor i en yderkommune
  (`profil.bor_i_yderkommune`), gælder 2,53 kr./km i stedet for reduktionen
  over 120 km — dvs. ingen nedsættelse for yderkommune-bosatte.
- Beregn ud fra `profil.pendler_km_hver_vej` og `profil.arbejdsdage_pr_aar` —
  brug aldrig et gættet antal arbejdsdage.
- Felt: **rubrik 51**.

## Ekstra befordringsfradrag for lav indkomst

- Gælder kun hvis personlig indkomst er **under 391.500 kr.**
- Aftrappes lineært i indkomstintervallet **341.500–391.500 kr.** (fuldt
  fradrag under 341.500, nul ved 391.500 og derover).
- Tjek `beregning.personlig_indkomst` eller `oplysninger.loen`, hvis
  beregning ikke er tilgængelig.

## Håndværkerfradrag

- **Felt 460.**
- Maks. fradragsberettiget beløb: **9.000 kr.** pr. person pr. år.
- Skal være dokumenteret arbejdsløn til håndværksydelser i eget/forældres
  hjem — ikke materialer.
- Afvis hvis det angivne beløb overstiger loftet uden forklaring, eller hvis
  der ikke er belæg for udgiften i data.

## Servicefradrag

- **Felt 461.**
- Maks. fradragsberettiget beløb: **18.300 kr.** pr. person pr. år.
- Gælder rengøring, børnepasning m.v. i hjemmet.

## Gaver til almenvelgørende foreninger (§8A)

- **Rubrik 55.**
- Maks. fradrag: **20.000 kr.** pr. person pr. år.
- Kun foreninger godkendt efter §8A tæller — REVIEWER kan ikke selv
  verificere godkendelsesstatus, så marker som `"kræver dokumentation"`
  medmindre brugerens data allerede bekræfter godkendt forening.

## Generelt for alle forslag

- Estimeret fradrag skal kunne genfindes i `oplysninger` eller `profil` —
  aldrig en antaget "gennemsnitsdansker"-værdi.
- Hvis et forslag kræver information der ikke findes i brugerens lokale
  data (fx dokumentation for en udgift), sæt `sikkerhed = "kræver
  dokumentation"` og `verificeret = false`.
- Estimeret skattebesparelse bør afspejle en rimelig marginalskat/AM-bidrag-
  antagelse (~26–56%), ikke en vilkårlig procentsats.
