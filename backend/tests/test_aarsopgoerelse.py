"""Unit-tests for aarsopgoerelse.projicer_aarsopgoerelse."""

from __future__ import annotations

import sys
from pathlib import Path

# Gør 'core'/'cli' importérbare, også når filen køres uden for pytest.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.aarsopgoerelse import projicer_aarsopgoerelse
from core.models import Skatteberegning, Skatteoplysninger


def _beregning(samlet_skat: float) -> Skatteberegning:
    return Skatteberegning(
        personlig_indkomst=450000.0,
        skattepligtig_indkomst=420000.0,
        am_bidrag=36000.0,
        bundskat=50000.0,
        kommuneskat=100000.0,
        kirkeskat=3000.0,
        samlet_skat=samlet_skat,
    )


def test_restskat_naar_beregnet_skat_overstiger_indbetalt():
    oplysninger = Skatteoplysninger(a_skat_indeholdt=100000.0, am_bidrag_indeholdt=30000.0)
    opgoerelse = projicer_aarsopgoerelse(oplysninger, _beregning(150000.0))

    assert opgoerelse.tilstraekkeligt_grundlag is True
    assert opgoerelse.er_restskat is True
    assert opgoerelse.indbetalt_skat == 130000.0
    assert opgoerelse.difference == 20000.0
    assert opgoerelse.beloeb == 20000.0


def test_overskydende_skat_naar_indbetalt_overstiger_beregnet():
    oplysninger = Skatteoplysninger(a_skat_indeholdt=140000.0, am_bidrag_indeholdt=36000.0)
    opgoerelse = projicer_aarsopgoerelse(oplysninger, _beregning(150000.0))

    assert opgoerelse.tilstraekkeligt_grundlag is True
    assert opgoerelse.er_restskat is False
    assert opgoerelse.indbetalt_skat == 176000.0
    assert opgoerelse.difference == -26000.0
    assert opgoerelse.beloeb == 26000.0


def test_utilstraekkeligt_grundlag_naar_begge_indeholdte_felter_mangler():
    oplysninger = Skatteoplysninger()
    opgoerelse = projicer_aarsopgoerelse(oplysninger, _beregning(150000.0))

    assert opgoerelse.tilstraekkeligt_grundlag is False
    assert opgoerelse.indbetalt_skat == 0.0


def test_utilstraekkeligt_grundlag_naar_kun_ét_indeholdt_felt_er_kendt():
    oplysninger = Skatteoplysninger(a_skat_indeholdt=100000.0, am_bidrag_indeholdt=None)
    opgoerelse = projicer_aarsopgoerelse(oplysninger, _beregning(150000.0))

    assert opgoerelse.tilstraekkeligt_grundlag is False
