"""Regel: uudnyttet fremført tab på aktier i reguleret marked (ABL §13 A)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ..registry import _er_lav, fradragsregel


@fradragsregel
def _tjek_aktietab(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.har_aktietab and _er_lav(oplysninger.aktietab_fremfoert):
        forslag.append(
            FradragsForslag(
                navn="Tab på aktier i reguleret marked (fremførsel)",
                felt="67",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Du har angivet, at du har haft et tab på aktier i et reguleret marked, men der "
                    "er ikke registreret et fremført tab i rubrik 67. Et tab, der ikke kan modregnes i "
                    "årets gevinster eller udbytter, kan fremføres og modregnes i fremtidig "
                    "aktieindkomst — men kun hvis tabet blev indberettet til Skattestyrelsen i det år, "
                    "det opstod (kildekravet). Tjek på skat.dk, om et ældre tab nogensinde er blevet "
                    "registreret, da det ellers ikke kan udnyttes senere."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Se rubrik 66/67 på din årsopgørelse under 'Aktier og investeringsbeviser'. Er "
                    "tabet ikke registreret, kan du kontakte Skattestyrelsen for at få det efterangivet "
                    "for det år, tabet opstod."
                ),
                kilde="skat.dk – Tab på aktier i reguleret marked (ABL §13 A), rubrik 66/67",
                sikkerhed="kræver dokumentation",
            )
        )

    return forslag
