"""Regel: manglende indberetning af fagforenings- og a-kasse-kontingent."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ..registry import _er_lav, fradragsregel


@fradragsregel
def tjek_fagforening(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if (profil.fagforening or profil.a_kasse) and _er_lav(oplysninger.fagforening_a_kasse):
        forslag.append(
            FradragsForslag(
                navn="Fagforening og A-kasse-kontingent",
                felt="50/52",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Din profil angiver medlemskab af fagforening og/eller a-kasse, men der er "
                    "ikke registreret et fradrag for kontingent. Fagforeningskontingent og "
                    "a-kasse-kontingent er fradragsberettiget."
                ),
                saadan_indberetter_du=(
                    "Indberettes normalt automatisk af fagforeningen/a-kassen i rubrik 50/52. "
                    "Mangler det på din årsopgørelse, kan du selv tilføje beløbet på skat.dk."
                ),
                kilde="skat.dk – Fagligt kontingent og A-kasse, rubrik 50/52",
                sikkerhed="mulig",
            )
        )

    return forslag
