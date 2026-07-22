"""Regel: manglende indberetning af gaver til almennyttige foreninger (§8A)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ..registry import _er_lav, fradragsregel

try:  # pragma: no cover - defensiv import
    from ....rates_2026 import GAVER_8A_MAX
except ImportError:
    GAVER_8A_MAX = 20_000.0  # kr/person 2026, §8A gaver, rubrik 55


@fradragsregel
def tjek_gaver(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.stoetter_velgoerenhed and _er_lav(oplysninger.gaver_almenvelgoerende):
        forslag.append(
            FradragsForslag(
                navn="Gaver til almennyttige foreninger (§8A)",
                felt="55",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Du har ikke indberettet gaver til godkendte foreninger. Har du doneret til "
                    "fx en velgørenhedsorganisation i 2026, kan du trække det fra med op til "
                    f"{GAVER_8A_MAX:,.0f} kr pr. person (kan ikke overføres mellem ægtefæller). "
                    "De fleste foreninger indberetter selv beløbet automatisk."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Tjek felt/rubrik 55 på din årsopgørelse — indberettes normalt automatisk af "
                    "foreningen. Mangler det, kan du selv rette det på skat.dk under 'Gaver til "
                    "godkendte foreninger'."
                ),
                kilde="skat.dk – Gaver til godkendte foreninger (§8A), rubrik 55",
                sikkerhed="kræver dokumentation",
            )
        )

    return forslag
