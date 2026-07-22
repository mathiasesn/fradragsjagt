"""Regel: manglende indberetning af fradrag for dobbelt husførelse."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ....rates_2026 import DOBBELT_HUSFOERELSE_SATS_PR_UGE
from ..registry import _er_lav, fradragsregel


@fradragsregel
def tjek_dobbelt_husfoerelse(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.dobbelt_husfoerelse and _er_lav(oplysninger.dobbelt_husfoerelse_fradrag):
        forslag.append(
            FradragsForslag(
                navn="Dobbelt husførelse",
                felt="58",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Din profil angiver dobbelt husførelse, men der er ikke registreret noget "
                    "fradrag for det. Standardsatsen er "
                    f"{DOBBELT_HUSFOERELSE_SATS_PR_UGE:,.0f} kr pr. uge. Det kræver, at du har "
                    "midlertidigt arbejde mindst 5 km fra din sædvanlige bopæl og opretholder "
                    "dobbelt husstand. Antal uger kan ikke estimeres automatisk her."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Indberet fradraget under øvrige lønmodtagerudgifter (felt 58) på "
                    "årsopgørelsen. Du skal kunne dokumentere det midlertidige arbejdssted og "
                    "den dobbelte husførelse."
                ),
                kilde="skat.dk – Dobbelt husførelse, felt 58",
                sikkerhed="mulig",
            )
        )

    return forslag
