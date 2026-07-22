"""Regel: manglende rejsefradrag (LL §9 A, rubrik 53)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ..registry import _er_lav, fradragsregel

try:  # pragma: no cover - defensiv import
    from ....rates_2026 import REJSE_KOST_SATS, REJSE_LOGI_SATS, REJSEFRADRAG_MAX
except ImportError:
    REJSEFRADRAG_MAX = 31_600.0  # kr/år, rubrik 53, loft for rejsefradrag 2026
    REJSE_KOST_SATS = 574.0  # kr/døgn, kost (best-effort)
    REJSE_LOGI_SATS = 246.0  # kr/døgn, logi (best-effort)


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
            estimeret_skattebesparelse=round(estimeret * 0.26, 2),
            begrundelse=(
                "Din profil angiver rejsedage med overnatning, men der er ikke indberettet "
                "rejsefradrag. Har du haft arbejdsrejser med overnatning og mindst 24 timer "
                "hjemmefra, kan du trække kost og logi fra med standardsatser, op til et loft på "
                f"{REJSEFRADRAG_MAX:,.0f} kr om året."
            ).replace(",", "."),
            saadan_indberetter_du=(
                "Log ind på skat.dk -> Ret årsopgørelsen -> felt/rubrik 53 'Rejsefradrag'. "
                "Kræver dokumentation for antal rejsedage, overnatning og afstand til hjemmet."
            ),
            kilde="skat.dk – Rejsefradrag (LL §9 A), rubrik 53",
            sikkerhed="mulig",
        )
    )

    return forslag
