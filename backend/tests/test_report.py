"""Unit-tests for report.byg_rapport — bruger håndbyggede modelinstanser."""

from __future__ import annotations

import pytest

from core import DISCLAIMER
from core.models import (
    Civilstand,
    FradragsForslag,
    Profil,
    Skatteberegning,
    Skatteoplysninger,
)
from core.report import byg_rapport


def _profil() -> Profil:
    return Profil(
        kommune="Aarhus",
        kirkeskattemedlem=True,
        civilstand=Civilstand.ENLIG,
        pendler_km_hver_vej=30,
        arbejdsdage_pr_aar=216,
        bor_i_yderkommune=False,
        fagforening=True,
        a_kasse=True,
        boligejer=False,
        indkomstaar=2026,
    )


def _oplysninger() -> Skatteoplysninger:
    return Skatteoplysninger(loen=450000.0)


def _beregning() -> Skatteberegning:
    return Skatteberegning(
        personlig_indkomst=450000.0,
        skattepligtig_indkomst=420000.0,
        am_bidrag=36000.0,
        bundskat=50000.0,
        kommuneskat=100000.0,
        kirkeskat=3000.0,
        beskaeftigelsesfradrag=45000.0,
        jobfradrag=2500.0,
        personfradrag_vaerdi=12000.0,
        samlet_skat=150000.0,
    )


def _forslag() -> list[FradragsForslag]:
    return [
        FradragsForslag(
            navn="Befordringsfradrag",
            felt="51",
            estimeret_fradrag=10000.0,
            estimeret_skattebesparelse=2600.0,
            begrundelse="Du pendler 30 km hver vej og har ikke selvangivet befordringsfradrag.",
            saadan_indberetter_du="Indtast beløbet i felt 51 på TastSelv.",
            sikkerhed="sandsynlig",
            verificeret=True,
        ),
        FradragsForslag(
            navn="Håndværkerfradrag",
            felt="460",
            estimeret_fradrag=9000.0,
            estimeret_skattebesparelse=2340.0,
            begrundelse="Håndværkerudgifter fundet i dine data uden tilsvarende fradrag.",
            saadan_indberetter_du="Indtast beløbet i felt 460 på TastSelv.",
            sikkerhed="mulig",
            verificeret=False,
        ),
    ]


def test_byg_rapport_indeholder_forslag_og_felter():
    rapport = byg_rapport(_oplysninger(), _profil(), _beregning(), _forslag())

    assert "Befordringsfradrag" in rapport
    assert "51" in rapport
    assert "Håndværkerfradrag" in rapport
    assert "460" in rapport


def test_byg_rapport_samlet_besparelse_er_korrekt():
    rapport = byg_rapport(_oplysninger(), _profil(), _beregning(), _forslag())

    # 2600 + 2340 = 4940
    assert "4.940 kr." in rapport


def test_byg_rapport_indeholder_disclaimer():
    rapport = byg_rapport(_oplysninger(), _profil(), _beregning(), _forslag())

    assert DISCLAIMER in rapport


def test_byg_rapport_uden_cpr():
    rapport = byg_rapport(_oplysninger(), _profil(), _beregning(), _forslag())

    assert "cpr" not in rapport.lower()


def test_byg_rapport_uden_beregning_degraderer_paent():
    rapport = byg_rapport(_oplysninger(), _profil(), None, [])

    assert "kunne ikke gennemføres" in rapport
    assert DISCLAIMER in rapport


@pytest.mark.parametrize(
    ("a_skat", "am_bidrag", "forventet_overskrift"),
    [
        (100000.0, 30000.0, "Forventet restskat: 20.000 kr."),
        (140000.0, 36000.0, "Forventet overskydende skat: 26.000 kr."),
    ],
)
def test_byg_rapport_viser_projiceret_aarsopgoerelse(a_skat, am_bidrag, forventet_overskrift):
    oplysninger = Skatteoplysninger(
        loen=450000.0, a_skat_indeholdt=a_skat, am_bidrag_indeholdt=am_bidrag
    )

    rapport = byg_rapport(oplysninger, _profil(), _beregning(), _forslag())

    assert "Tidlig årsopgørelse" in rapport
    assert forventet_overskrift in rapport


def test_byg_rapport_utilstraekkeligt_grundlag_for_aarsopgoerelse():
    rapport = byg_rapport(_oplysninger(), _profil(), _beregning(), _forslag())

    assert "Tidlig årsopgørelse" in rapport
    assert "kan ikke projiceres" in rapport
