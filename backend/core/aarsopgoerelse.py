"""Tidlig årsopgørelse — projicerer restskat eller overskydende skat.

`projicer_aarsopgoerelse` er en ren funktion (ingen I/O): den sammenholder
den beregnede samlede skat (`Skatteberegning.samlet_skat`, som inkluderer
AM-bidrag) med den indeholdte skat (A-skat + AM-bidrag) fra
`Skatteoplysninger`, og udleder om der forventes restskat eller
overskydende skat.

Bemærk: dag-til-dag rente og procenttillæg på restskat (jf. skat.dk's regler
for betaling efter fristen) modelleres IKKE her — dette er et rent estimat
baseret på de kendte beløb, ikke en fuld årsopgørelse.
"""

from __future__ import annotations

from .models import Skatteberegning, Skatteoplysninger, TidligAarsopgoerelse


def projicer_aarsopgoerelse(
    oplysninger: Skatteoplysninger, beregning: Skatteberegning
) -> TidligAarsopgoerelse:
    """Byg en `TidligAarsopgoerelse` ud fra parsede oplysninger og en
    gennemført skatteberegning. Estimat — ingen rente/procenttillæg."""

    tilstraekkeligt_grundlag = (
        oplysninger.a_skat_indeholdt is not None or oplysninger.am_bidrag_indeholdt is not None
    )
    indbetalt = (oplysninger.a_skat_indeholdt or 0.0) + (oplysninger.am_bidrag_indeholdt or 0.0)
    difference = beregning.samlet_skat - indbetalt

    return TidligAarsopgoerelse(
        samlet_beregnet_skat=beregning.samlet_skat,
        indbetalt_skat=indbetalt,
        difference=difference,
        er_restskat=difference > 0,
        beloeb=abs(difference),
        tilstraekkeligt_grundlag=tilstraekkeligt_grundlag,
    )
