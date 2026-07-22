"""Tidlig årsopgørelse — projicerer restskat eller overskydende skat.

`projicer_aarsopgoerelse` er en ren funktion (ingen I/O): den sammenholder
den beregnede samlede skat (`Skatteberegning.samlet_skat`, som inkluderer
AM-bidrag) med den indeholdte skat (A-skat + AM-bidrag) fra
`Skatteoplysninger`, og udleder om der forventes restskat eller
overskydende skat. En fuld projektion kræver begge indeholdte beløb
(A-skat OG AM-bidrag) — mangler ét af dem, er grundlaget ikke
tilstrækkeligt.

Bemærk: dag-til-dag rente og procenttillæg på restskat (jf. skat.dk's regler
for betaling efter fristen) modelleres IKKE her — dette er et rent estimat
baseret på de kendte beløb, ikke en fuld årsopgørelse.
"""

from __future__ import annotations

from .models import Skatteberegning, Skatteoplysninger, TidligAarsopgoerelse


def projicer_aarsopgoerelse(
    oplysninger: Skatteoplysninger, beregning: Skatteberegning
) -> TidligAarsopgoerelse | None:
    """Byg en `TidligAarsopgoerelse` ud fra parsede oplysninger og en
    gennemført skatteberegning. Estimat — ingen rente/procenttillæg.

    Returnerer None, hvis grundlaget er utilstrækkeligt: begge indeholdte
    beløb (A-skat OG AM-bidrag) skal være kendt, ellers ville `indbetalt`
    mangle en komponent og give en misvisende restskat.
    """

    if oplysninger.a_skat_indeholdt is None or oplysninger.am_bidrag_indeholdt is None:
        return None

    return TidligAarsopgoerelse(
        samlet_beregnet_skat=beregning.samlet_skat,
        indbetalt_skat=oplysninger.a_skat_indeholdt + oplysninger.am_bidrag_indeholdt,
    )
