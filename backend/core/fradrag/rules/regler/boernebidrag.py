"""Regel: manglende indberetning af fradrag for betalt børnebidrag (LL §10/§11)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ....rates_2026 import BOERNEBIDRAG_NORMALBIDRAG_AAR
from ..registry import _er_lav, fradragsregel


@fradragsregel
def tjek_boernebidrag(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.betaler_boernebidrag and _er_lav(oplysninger.boernebidrag):
        forslag.append(
            FradragsForslag(
                navn="Børnebidrag (LL §10/§11)",
                felt="56",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Din profil angiver, at du betaler børnebidrag, men der er ikke registreret "
                    "noget fradrag for det. Bidrag, der overstiger normalbidraget "
                    f"(ca. {BOERNEBIDRAG_NORMALBIDRAG_AAR:,.0f} kr pr. barn pr. år), er "
                    "fradragsberettiget. Beløbet afhænger af antal børn og den konkrete "
                    "bidragsaftale/-resolution, så det kan ikke estimeres automatisk her."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Indberet det betalte børnebidrag ud over normalbidraget i rubrik 56 på "
                    "årsopgørelsen. Du skal kunne dokumentere beløbet med en bidragsaftale eller "
                    "en resolution fra Familieretshuset."
                ),
                kilde="skat.dk – Børnebidrag (LL §10/§11), rubrik 56",
                sikkerhed="kræver dokumentation",
            )
        )

    return forslag
