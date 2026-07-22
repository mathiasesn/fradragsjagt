"""Unit-tests for aarsopgoerelse.projicer_aarsopgoerelse."""

from __future__ import annotations

import pytest

from core.aarsopgoerelse import projicer_aarsopgoerelse
from core.models import Skatteberegning, Skatteoplysninger


def _beregning(samlet_skat: float) -> Skatteberegning:
    """Kun `samlet_skat` indgår i projektionen — de øvrige poster er irrelevante her."""
    return Skatteberegning(
        personlig_indkomst=0.0,
        skattepligtig_indkomst=0.0,
        am_bidrag=0.0,
        bundskat=0.0,
        kommuneskat=0.0,
        kirkeskat=0.0,
        samlet_skat=samlet_skat,
    )


@pytest.mark.parametrize(
    ("a_skat", "am_bidrag", "forventet_indbetalt", "forventet_difference", "forventet_restskat"),
    [
        # Beregnet skat (150.000) overstiger det indeholdte -> restskat.
        (100000.0, 30000.0, 130000.0, 20000.0, True),
        # Det indeholdte overstiger den beregnede skat -> overskydende skat.
        (140000.0, 36000.0, 176000.0, -26000.0, False),
    ],
)
def test_projektion_udleder_restskat_og_overskydende_skat(
    a_skat, am_bidrag, forventet_indbetalt, forventet_difference, forventet_restskat
):
    oplysninger = Skatteoplysninger(a_skat_indeholdt=a_skat, am_bidrag_indeholdt=am_bidrag)

    opgoerelse = projicer_aarsopgoerelse(oplysninger, _beregning(150000.0))

    assert opgoerelse is not None
    assert opgoerelse.indbetalt_skat == forventet_indbetalt
    assert opgoerelse.difference == forventet_difference
    assert opgoerelse.er_restskat is forventet_restskat
    assert opgoerelse.beloeb == abs(forventet_difference)


@pytest.mark.parametrize(
    ("a_skat", "am_bidrag"),
    [
        (None, None),  # intet indeholdt kendt
        (100000.0, None),  # kun A-skat kendt
        (None, 30000.0),  # kun AM-bidrag kendt
    ],
)
def test_utilstraekkeligt_grundlag_giver_ingen_projektion(a_skat, am_bidrag):
    """Begge indeholdte beløb skal være kendt — ellers ville `indbetalt` mangle
    en komponent og give en misvisende restskat."""
    oplysninger = Skatteoplysninger(a_skat_indeholdt=a_skat, am_bidrag_indeholdt=am_bidrag)

    assert projicer_aarsopgoerelse(oplysninger, _beregning(150000.0)) is None
