"""Satser og grænser for indkomståret 2026.

Kilder / grundlag (bør verificeres mod skat.dk / SKM ved sæsonstart, da de
endelige 2026-tal først offentliggøres officielt sent på året):

  - AM-bidrag: 8% af personlig indkomst (arbejdsmarkedsbidragsloven, uændret
    sats gennem mange år).
  - Personfradrag 2026: 54.100 kr. (fremskrevet, jf. den løbende regulering
    Skattestyrelsen offentliggør hvert efterår for det kommende indkomstår).
  - Bundskat: 12,01% af personlig indkomst + evt. positiv nettokapitalindkomst
    over bundskattens grundlag, her forenklet til personlig indkomst efter
    AM-bidrag (skattepligtig indkomst-grundlag), jf. gældende praksis.
  - Nyt 2026-mellem-/topskattesystem (skattereform 2024, ikrafttræden 2026):
      * Mellemskat 7,5% mellem 641.200 og 777.900 kr.
      * Topskat 7,5% mellem 777.900 og 2.592.700 kr.
      * Top-topskat 5% over 2.592.700 kr.
    (Grundlaget er personlig indkomst efter AM-bidrag, evt. + positiv
    nettokapitalindkomst — her forenklet til personlig indkomst efter AM-bidrag.)
  - Skatteloft (samlet marginalskat af arbejdsindkomst, ekskl. kirkeskat):
    52,07%.
  - Kommuneskat: landsgennemsnit ca. 25,07% for 2026 (bruges som fallback for
    kommuner, der ikke findes i core/data/kommuneskat_2026.csv).
  - Kirkeskat: landsgennemsnit ca. 0,68%, opkræves kun for medlemmer af
    folkekirken.
  - Beskæftigelsesfradrag: 12,75% af arbejdsindkomst, maks. 63.300 kr.
  - Jobfradrag: 4,50% af arbejdsindkomst over 235.200 kr., maks. 3.100 kr.

ALLE tal ovenfor er bedste-indsats-fremskrivninger og skal krydstjekkes mod
de officielle 2026-satser på skat.dk, når Skattestyrelsen har offentliggjort
dem endeligt.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

# --- AM-bidrag -------------------------------------------------------------
AM_BIDRAG_PCT = 8.0  # % af personlig indkomst

# --- Personfradrag -----------------------------------------------------------
PERSONFRADRAG = 54_100.0  # kr., 2026

# --- Bundskat ----------------------------------------------------------------
BUNDSKAT_PCT = 12.01  # % af personlig indkomst (efter AM-bidrag)

# --- Mellemskat / topskat / top-topskat (nyt 2026-system) -------------------
MELLEMSKAT_PCT = 7.5
MELLEMSKAT_BUNDGRAENSE = 641_200.0
MELLEMSKAT_TOPGRAENSE = 777_900.0  # = topskattens bundgrænse

TOPSKAT_PCT = 7.5
TOPSKAT_BUNDGRAENSE = 777_900.0
TOPSKAT_TOPGRAENSE = 2_592_700.0  # = top-topskattens bundgrænse

TOP_TOPSKAT_PCT = 5.0
TOP_TOPSKAT_BUNDGRAENSE = 2_592_700.0

# --- Skatteloft ---------------------------------------------------------------
SKATTELOFT_PCT = 52.07  # maks. samlet marginalskat af arbejdsindkomst (ekskl. kirkeskat)

# --- Kommune-/kirkeskat fallback (landsgennemsnit) ----------------------------
GENNEMSNITLIG_KOMMUNESKAT_PCT = 25.07
GENNEMSNITLIG_KIRKESKAT_PCT = 0.68

# --- Beskæftigelsesfradrag -----------------------------------------------------
BESKAEFTIGELSESFRADRAG_PCT = 12.75
BESKAEFTIGELSESFRADRAG_MAKS = 63_300.0

# --- Jobfradrag -----------------------------------------------------------------
JOBFRADRAG_PCT = 4.50
JOBFRADRAG_BUNDGRAENSE = 235_200.0
JOBFRADRAG_MAKS = 3_100.0

# --- Kørselsfradrag (befordringsfradrag) -----------------------------------------
# Kilde: skat.dk, kilometersatser til befordringsfradrag 2026 (bør verificeres).
KOERSEL_SATS_NORMAL = 2.28  # kr/km, 25-120 km/dag
KOERSEL_SATS_LANG = 1.14  # kr/km, over 120 km/dag
KOERSEL_SATS_YDERKOMMUNE = 2.53  # kr/km, yderkommuner (ingen reduktion over 120 km)
KOERSEL_BUNDGRAENSE_KM = 24.0  # km/dag (samlet tur/retur) uden fradrag
KOERSEL_LANG_GRAENSE_KM = 120.0  # km/dag hvor lavere sats starter

# --- Ekstra befordringsfradrag for lavindkomst ------------------------------------
# Kilde: skat.dk, ekstra befordringsfradrag for lav indkomst (bør verificeres).
EKSTRA_BEFORDRING_MAX = 30_800.0  # kr/år, loft over det ekstra fradrag
EKSTRA_BEFORDRING_INDKOMST_START = 341_500.0  # kr, aftrapning starter
EKSTRA_BEFORDRING_INDKOMST_SLUT = 391_500.0  # kr, aftrapning slutter (0 kr herefter)
# Andel af det almindelige befordringsfradrag, der udgør grundlaget for det
# ekstra fradrag, før loft og aftrapning. Bør verificeres mod skat.dk.
EKSTRA_BEFORDRING_ANDEL = 0.64

# --- Håndværkerfradrag / servicefradrag / gaver (§8A) ------------------------------
HAANDVAERKERFRADRAG_MAX = 9_000.0  # kr/person 2026, grønt håndværkerfradrag, felt 460
SERVICEFRADRAG_MAX = 18_300.0  # kr/person 2026, servicefradrag, felt 461
GAVER_8A_MAX = 20_000.0  # kr/person 2026, §8A gaver, rubrik 55

# --- Grov fradragsværdi (bundskat + kommuneskat, ikke marginalskat-præcist) --------
FRADRAG_VAERDI_PROCENT = 0.26

# --- Fase 2: rejse-, børnebidrags-, dobbelt husførelse- og pensionsfradrag ---------
# Alle satser nedenfor er bedste-indsats-fremskrivninger og skal verificeres mod de
# officielle 2026-satser på skat.dk, når Skattestyrelsen har offentliggjort dem endeligt.
REJSEFRADRAG_MAX = 31_600.0  # kr/år, rubrik 53, loft for rejsefradrag 2026
REJSE_KOST_SATS = 574.0  # kr/døgn, kost (best-effort)
REJSE_LOGI_SATS = 246.0  # kr/døgn, logi (best-effort)
DOBBELT_HUSFOERELSE_SATS_PR_UGE = 508.0  # kr/uge, standardsats (best-effort)
BOERNEBIDRAG_NORMALBIDRAG_AAR = 20_856.0  # kr/år, normalbidrag 2026 (best-effort);
# fradrag gælder betalt bidrag ud over grundbeløbet.
PENSION_FRADRAG_MAX = 66_500.0  # kr., loft for fradrag på ratepension/ophørende livrente 2026 (best-effort)


@dataclass(frozen=True)
class KommuneSats:
    kommune: str
    kommuneskat_pct: float
    kirkeskat_pct: float


_CSV_PATH = Path(__file__).resolve().parent / "data" / "kommuneskat_2026.csv"


def _load_kommunesatser(csv_path: Path = _CSV_PATH) -> Dict[str, KommuneSats]:
    """Indlæs den partielle kommuneskat-tabel fra CSV.

    Kommuner der ikke findes i filen, håndteres ikke her — kald
    `kommunesats(kommune)` for opslag med fallback til landsgennemsnittet.
    """
    satser: Dict[str, KommuneSats] = {}
    if not csv_path.exists():
        return satser
    with csv_path.open(encoding="utf-8") as f:
        # Filter kommentarlinjer (starter med '#') før CSV-parsing.
        linjer = [linje for linje in f if not linje.lstrip().startswith("#")]
    reader = csv.DictReader(linjer)
    for row in reader:
        navn = row["kommune"].strip()
        satser[navn.lower()] = KommuneSats(
            kommune=navn,
            kommuneskat_pct=float(row["kommuneskat_pct"]),
            kirkeskat_pct=float(row["kirkeskat_pct"]),
        )
    return satser


KOMMUNESATSER: Dict[str, KommuneSats] = _load_kommunesatser()


def kommunesats(kommune: str) -> KommuneSats:
    """Slå kommuneskat/kirkeskat op for en kommune.

    Falder tilbage til landsgennemsnittet (GENNEMSNITLIG_KOMMUNESKAT_PCT /
    GENNEMSNITLIG_KIRKESKAT_PCT), hvis kommunen ikke findes i den partielle
    CSV-tabel. Fallback markeres ikke fejlagtigt som en kendt kommune.
    """
    fundet = KOMMUNESATSER.get(kommune.strip().lower())
    if fundet is not None:
        return fundet
    return KommuneSats(
        kommune=kommune,
        kommuneskat_pct=GENNEMSNITLIG_KOMMUNESKAT_PCT,
        kirkeskat_pct=GENNEMSNITLIG_KIRKESKAT_PCT,
    )
