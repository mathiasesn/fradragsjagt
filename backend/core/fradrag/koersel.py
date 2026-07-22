"""Beregning af kørselsfradrag (befordringsfradrag) for 2026.

Satser og regler er defineret lokalt her (med kommentar om kilde), og læses
defensivt fra ..rates_2026 hvis det modul findes, så dette modul virker også
hvis det importeres alene uden resten af pakken.

2026-satser (SKAT, kilometersats til befordringsfradrag):
- 0-24 km/dag: intet fradrag (bundgrænse)
- 25-120 km/dag: 2,28 kr/km
- over 120 km/dag: 1,14 kr/km
- yderkommuner: 2,53 kr/km for alle km over bundgrænsen (ingen reduktion over 120 km)
- ekstra befordringsfradrag for lavindkomst: max 30.800 kr/år, for indkomst
  under 391.500 kr (før am-bidrag), aftrappet mellem 341.500-391.500 kr.
"""

from __future__ import annotations

from ..models import FradragsForslag

try:  # pragma: no cover - defensiv import
    from ..rates_2026 import (
        EKSTRA_BEFORDRING_ANDEL,
        EKSTRA_BEFORDRING_INDKOMST_SLUT,
        EKSTRA_BEFORDRING_INDKOMST_START,
        EKSTRA_BEFORDRING_MAX,
        KOERSEL_BUNDGRAENSE_KM,
        KOERSEL_LANG_GRAENSE_KM,
        KOERSEL_SATS_LANG,
        KOERSEL_SATS_NORMAL,
        KOERSEL_SATS_YDERKOMMUNE,
    )
except ImportError:  # rates_2026 findes ikke (endnu) eller mangler felter
    KOERSEL_SATS_NORMAL = 2.28  # kr/km, 25-120 km/dag
    KOERSEL_SATS_LANG = 1.14  # kr/km, over 120 km/dag
    KOERSEL_SATS_YDERKOMMUNE = 2.53  # kr/km, yderkommuner (ingen reduktion over 120 km)
    KOERSEL_BUNDGRAENSE_KM = 24.0  # km/dag (samlet tur/retur) uden fradrag
    KOERSEL_LANG_GRAENSE_KM = 120.0  # km/dag hvor lavere sats starter
    EKSTRA_BEFORDRING_MAX = 30_800.0  # kr/år
    EKSTRA_BEFORDRING_INDKOMST_START = 341_500.0  # kr, aftrapning starter
    EKSTRA_BEFORDRING_INDKOMST_SLUT = 391_500.0  # kr, aftrapning slutter (0 kr herefter)
    EKSTRA_BEFORDRING_ANDEL = 0.64  # andel af almindeligt befordringsfradrag


def _daglig_fradragsberettiget_km(km_hver_vej: float) -> float:
    """Samlet daglig km (tur/retur) ud over bundgrænsen på 24 km."""

    samlet_km = km_hver_vej * 2
    return max(0.0, samlet_km - KOERSEL_BUNDGRAENSE_KM)


def _km_sats_beloeb(fradragsberettiget_km: float, yderkommune: bool) -> float:
    """Beregn kr/dag for den fradragsberettigede del af den daglige kørsel."""

    if yderkommune:
        return fradragsberettiget_km * KOERSEL_SATS_YDERKOMMUNE

    if fradragsberettiget_km <= (KOERSEL_LANG_GRAENSE_KM - KOERSEL_BUNDGRAENSE_KM):
        return fradragsberettiget_km * KOERSEL_SATS_NORMAL

    km_normal = KOERSEL_LANG_GRAENSE_KM - KOERSEL_BUNDGRAENSE_KM
    km_lang = fradragsberettiget_km - km_normal
    return km_normal * KOERSEL_SATS_NORMAL + km_lang * KOERSEL_SATS_LANG


def _ekstra_befordringsfradrag(aarsindkomst: float, kommunalt_fradrag: float) -> float:
    """Ekstra befordringsfradrag for lavindkomster (aftrappet 341.500-391.500 kr).

    Kræver i praksis også mere end 24 km hver vej og medlemskab af visse
    ordninger i nogle tilfælde, men vi holder det simpelt: indkomstbaseret
    aftrapning, som er den del alle kan tjekke selv.
    """

    if aarsindkomst >= EKSTRA_BEFORDRING_INDKOMST_SLUT:
        return 0.0
    if kommunalt_fradrag <= 0:
        return 0.0

    if aarsindkomst <= EKSTRA_BEFORDRING_INDKOMST_START:
        andel = 1.0
    else:
        spaend = EKSTRA_BEFORDRING_INDKOMST_SLUT - EKSTRA_BEFORDRING_INDKOMST_START
        andel = 1.0 - (aarsindkomst - EKSTRA_BEFORDRING_INDKOMST_START) / spaend
        andel = max(0.0, min(1.0, andel))

    return min(EKSTRA_BEFORDRING_MAX, EKSTRA_BEFORDRING_ANDEL * kommunalt_fradrag) * andel


def beregn_koerselsfradrag(
    km_hver_vej: float,
    arbejdsdage: int,
    yderkommune: bool,
    aarsindkomst: float,
) -> FradragsForslag:
    """Beregn befordringsfradrag (rubrik 51) for en pendler i 2026.

    Args:
        km_hver_vej: afstand bopæl -> arbejde, én vej, i km.
        arbejdsdage: antal arbejdsdage pr. år (typisk 216).
        yderkommune: True hvis bopælskommune er en udpeget yderkommune.
        aarsindkomst: personlig indkomst før am-bidrag (bruges til ekstra fradrag).

    Returns:
        FradragsForslag med estimeret_fradrag = normalt + ekstra befordringsfradrag.
    """

    fradragsberettiget_km_pr_dag = _daglig_fradragsberettiget_km(km_hver_vej)

    if fradragsberettiget_km_pr_dag <= 0:
        return FradragsForslag(
            navn="Kørselsfradrag (befordringsfradrag)",
            felt="51",
            estimeret_fradrag=0.0,
            estimeret_skattebesparelse=0.0,
            begrundelse=(
                f"Din daglige transport ({km_hver_vej * 2:.0f} km tur/retur) er under "
                f"bundgrænsen på {KOERSEL_BUNDGRAENSE_KM:.0f} km, så der er ikke ret til "
                "befordringsfradrag."
            ),
            saadan_indberetter_du=("Intet at indberette — afstanden giver ikke ret til fradrag."),
            sikkerhed="sandsynlig",
        )

    dagligt_beloeb = _km_sats_beloeb(fradragsberettiget_km_pr_dag, yderkommune)
    kommunalt_fradrag = dagligt_beloeb * arbejdsdage
    ekstra_fradrag = _ekstra_befordringsfradrag(aarsindkomst, kommunalt_fradrag)
    samlet_fradrag = kommunalt_fradrag + ekstra_fradrag

    # Værdi af fradraget: ca. 26% (bundskat + kommuneskat), groft skøn, ikke marginalskat-præcist.
    skatteværdi = samlet_fradrag * 0.26

    yderkommune_tekst = " (yderkommune-sats)" if yderkommune else ""
    ekstra_tekst = ""
    if ekstra_fradrag > 0:
        ekstra_tekst = (
            f" Derudover kan du være berettiget til ekstra befordringsfradrag for "
            f"lavere indkomster på ca. {ekstra_fradrag:,.0f} kr, da din indkomst er "
            f"under {EKSTRA_BEFORDRING_INDKOMST_SLUT:,.0f} kr.".replace(",", ".")
        )

    begrundelse = (
        f"Med {km_hver_vej:.0f} km hver vej og {arbejdsdage} arbejdsdage om året kan du "
        f"trække {fradragsberettiget_km_pr_dag:.0f} fradragsberettigede km/dag "
        f"(ud over de første {KOERSEL_BUNDGRAENSE_KM:.0f} km){yderkommune_tekst}, "
        f"svarende til ca. {kommunalt_fradrag:,.0f} kr i almindeligt befordringsfradrag.".replace(",", ".")
        + ekstra_tekst
        + " Kørselsfradrag beregnes ikke automatisk af Skattestyrelsen — du skal selv indberette det."
    )

    return FradragsForslag(
        navn="Kørselsfradrag (befordringsfradrag)",
        felt="51",
        estimeret_fradrag=round(samlet_fradrag, 2),
        estimeret_skattebesparelse=round(skatteværdi, 2),
        begrundelse=begrundelse,
        saadan_indberetter_du=(
            "Log ind på skat.dk -> Ret årsopgørelsen/forskudsopgørelsen -> felt 51 "
            "'Befordring' -> indtast afstand hver vej, antal arbejdsdage og evt. "
            "yderkommune. Skat.dk beregner selv det præcise beløb ud fra dine tal."
        ),
        sikkerhed="sandsynlig",
    )
