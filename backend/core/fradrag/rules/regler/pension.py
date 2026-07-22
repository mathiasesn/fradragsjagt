"""Regel: manglende indskud på privat pensionsordning for selvstændige (felt 436)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ..registry import _er_lav, fradragsregel

try:  # pragma: no cover - defensiv import
    from ....rates_2026 import PENSION_FRADRAG_MAX
except ImportError:
    PENSION_FRADRAG_MAX = 66_500.0  # kr., loft for fradrag på ratepension/ophørende livrente 2026


@fradragsregel
def tjek_pensionsindbetaling(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    # Kun konservativt: selvstændige uden arbejdsgiverordning er det klare tilfælde,
    # hvor manglende pensionsindbetaling er værd at flage.
    if not profil.selvstaendig:
        return forslag

    if not _er_lav(oplysninger.pensionsindbetaling):
        return forslag

    forslag.append(
        FradragsForslag(
            navn="Indskud på privat pensionsordning",
            felt="436",
            estimeret_fradrag=0.0,
            estimeret_skattebesparelse=0.0,
            begrundelse=(
                "Du er registreret som selvstændig og har ikke indberettet pensionsindbetaling. "
                "Uden en arbejdsgiveradministreret pensionsordning kan du selv indskyde på en "
                "ratepension eller ophørende livrente og trække det fra, op til et loft på "
                f"{PENSION_FRADRAG_MAX:,.0f} kr om året. Det faktiske fradrag afhænger af, hvor "
                "meget du reelt indbetaler, og er derfor ikke estimeret her."
            ).replace(",", "."),
            saadan_indberetter_du=(
                "Log ind på skat.dk -> Ret årsopgørelsen -> felt 436 'Indskud på pensionsordning'. "
                "Beløbet indberettes normalt automatisk af pensionsselskabet, men bør tjekkes."
            ),
            kilde="skat.dk – Fradrag for pensionsindbetaling, felt 436",
            sikkerhed="mulig",
        )
    )

    return forslag
