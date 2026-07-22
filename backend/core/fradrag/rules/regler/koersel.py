"""Regel: manglende eller for lavt indberettet kørselsfradrag (befordringsfradrag)."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ...koersel import beregn_koerselsfradrag
from ..registry import fradragsregel


@fradragsregel
def tjek_koersel(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.pendler_km_hver_vej <= 0:
        return forslag

    aarsindkomst = oplysninger.loen or 0.0
    beregnet = beregn_koerselsfradrag(
        km_hver_vej=profil.pendler_km_hver_vej,
        arbejdsdage=profil.arbejdsdage_pr_aar,
        yderkommune=profil.bor_i_yderkommune,
        aarsindkomst=aarsindkomst,
    )

    if beregnet.estimeret_fradrag <= 0:
        return forslag

    indberettet = oplysninger.befordringsfradrag or 0.0
    if indberettet >= beregnet.estimeret_fradrag * 0.95:
        # Allerede indberettet i nogenlunde rigtig størrelsesorden.
        return forslag

    beregnet.kilde = "skat.dk – Befordringsfradrag (LL §9 C), rubrik 51"
    forslag.append(beregnet)
    return forslag
