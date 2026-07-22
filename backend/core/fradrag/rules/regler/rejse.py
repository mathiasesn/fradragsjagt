"""Regel: manglende rejsefradrag (LL §9 A, rubrik 53)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ....rates_2026 import (
    FRADRAG_VAERDI_PROCENT,
    REJSE_KOST_SATS,
    REJSE_LOGI_SATS,
    REJSEFRADRAG_MAX,
)
from ..registry import _er_lav, fradragsregel, kr


@fradragsregel
def tjek_rejsefradrag(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.rejsedage_med_overnatning <= 0:
        return forslag

    if not _er_lav(oplysninger.rejsefradrag):
        return forslag

    estimeret = min(
        profil.rejsedage_med_overnatning * (REJSE_KOST_SATS + REJSE_LOGI_SATS),
        REJSEFRADRAG_MAX,
    )

    forslag.append(
        FradragsForslag(
            navn="Rejsefradrag (LL §9 A)",
            felt="53",
            estimeret_fradrag=round(estimeret, 2),
            estimeret_skattebesparelse=round(estimeret * FRADRAG_VAERDI_PROCENT, 2),
            begrundelse=(
                "Din profil angiver rejsedage med overnatning, men der er ikke indberettet "
                "rejsefradrag. Har du haft arbejdsrejser med overnatning og mindst 24 timer "
                "hjemmefra, kan du trække kost og logi fra med standardsatser, op til et loft på "
                f"{kr(REJSEFRADRAG_MAX)} kr om året."
            ),
            saadan_indberetter_du=(
                "Log ind på skat.dk -> Ret årsopgørelsen -> felt/rubrik 53 'Rejsefradrag'. "
                "Kræver dokumentation for antal rejsedage, overnatning og afstand til hjemmet."
            ),
            kilde="skat.dk – Rejsefradrag (LL §9 A), rubrik 53",
            sikkerhed="mulig",
        )
    )

    return forslag
