"""Tests for core.engine (2026 skatteberegning)."""

from __future__ import annotations

import pytest

from core.engine import beregn_skat
from core.models import Profil, Skatteoplysninger


TOLERANCE = 5.0  # kr.


def _profil(**overrides) -> Profil:
    defaults = dict(kommune="Aarhus", kirkeskattemedlem=True)
    defaults.update(overrides)
    return Profil(**defaults)


def test_lav_indkomst_under_alle_progressive_graenser():
    """200.000 kr. i løn — under mellemskattens bundgrænse (641.200 kr.)."""
    profil = _profil()
    oplysninger = Skatteoplysninger(loen=200_000)

    b = beregn_skat(oplysninger, profil)

    assert b.personlig_indkomst == 200_000
    assert b.am_bidrag == pytest.approx(16_000.0, abs=TOLERANCE)
    # personlig_indkomst_efter_am = 184.000
    assert b.beskaeftigelsesfradrag == pytest.approx(23_460.0, abs=TOLERANCE)  # 12.75% * 184.000
    assert b.jobfradrag == 0.0  # under jobfradragets bundgrænse på 235.200
    assert b.mellemskat == 0.0
    assert b.topskat == 0.0
    assert b.top_topskat == 0.0
    assert b.skattepligtig_indkomst == pytest.approx(106_440.0, abs=TOLERANCE)
    assert b.bundskat == pytest.approx(12_783.4, abs=TOLERANCE)
    assert b.kommuneskat == pytest.approx(25_971.4, abs=TOLERANCE)
    assert b.kirkeskat == pytest.approx(755.7, abs=TOLERANCE)
    assert b.samlet_skat == pytest.approx(55_510.5, abs=TOLERANCE)
    assert b.detaljer["skatteloft_overskredet"] is False


def test_mellemindkomst_paye_case():
    """450.000 kr. i løn — typisk lønmodtager, over jobfradragets bundgrænse
    men under mellemskattens bundgrænse."""
    profil = _profil()
    oplysninger = Skatteoplysninger(loen=450_000)

    b = beregn_skat(oplysninger, profil)

    assert b.am_bidrag == pytest.approx(36_000.0, abs=TOLERANCE)
    # personlig_indkomst_efter_am = 414.000
    assert b.beskaeftigelsesfradrag == pytest.approx(52_785.0, abs=TOLERANCE)  # 12.75% * 414.000
    assert b.jobfradrag == pytest.approx(
        3_100.0, abs=TOLERANCE
    )  # rammer maks (4,5% * (414.000-235.200) > 3.100)
    assert b.mellemskat == 0.0
    assert b.topskat == 0.0
    assert b.skattepligtig_indkomst == pytest.approx(304_015.0, abs=TOLERANCE)
    assert b.bundskat == pytest.approx(36_512.2, abs=TOLERANCE)
    assert b.kommuneskat == pytest.approx(74_179.7, abs=TOLERANCE)
    assert b.kirkeskat == pytest.approx(2_158.5, abs=TOLERANCE)
    assert b.samlet_skat == pytest.approx(148_850.4, abs=TOLERANCE)


def test_hoej_indkomst_udloeser_mellem_og_topskat():
    """1.200.000 kr. i løn — udløser både mellemskat og topskat, men ikke
    top-topskat (personlig indkomst efter AM under 2.592.700 kr.)."""
    profil = _profil()
    oplysninger = Skatteoplysninger(loen=1_200_000)

    b = beregn_skat(oplysninger, profil)

    assert b.am_bidrag == pytest.approx(96_000.0, abs=TOLERANCE)
    # personlig_indkomst_efter_am = 1.104.000
    assert b.beskaeftigelsesfradrag == pytest.approx(63_300.0, abs=TOLERANCE)  # rammer maks
    assert b.jobfradrag == pytest.approx(3_100.0, abs=TOLERANCE)  # rammer maks
    # mellemskat: (777.900 - 641.200) * 7.5% = 10.252,5
    assert b.mellemskat == pytest.approx(10_252.5, abs=TOLERANCE)
    # topskat: (1.104.000 - 777.900) * 7.5% = 24.457,5
    assert b.topskat == pytest.approx(24_457.5, abs=TOLERANCE)
    assert b.top_topskat == 0.0
    assert b.skattepligtig_indkomst == pytest.approx(983_500.0, abs=TOLERANCE)
    assert b.samlet_skat == pytest.approx(495_785.2, abs=TOLERANCE)


def test_top_topskat_udloeses_over_2592700():
    """3.000.000 kr. i personlig indkomst efter AM (dvs. høj løn) skal
    udløse top-topskat på 5%."""
    profil = _profil(kirkeskattemedlem=False)
    oplysninger = Skatteoplysninger(loen=3_300_000)  # efter 8% AM ~ 3.036.000

    b = beregn_skat(oplysninger, profil)

    assert b.top_topskat > 0.0
    grundlag_efter_am = b.detaljer["personlig_indkomst_efter_am"]
    forventet_top_topskat = max(grundlag_efter_am - 2_592_700.0, 0.0) * 0.05
    assert b.top_topskat == pytest.approx(forventet_top_topskat, abs=TOLERANCE)
    assert b.kirkeskat == 0.0  # ikke medlem af folkekirken


def test_ukendt_kommune_bruger_landsgennemsnit_fallback():
    from core.rates_2026 import (
        GENNEMSNITLIG_KIRKESKAT_PCT,
        GENNEMSNITLIG_KOMMUNESKAT_PCT,
    )

    profil = _profil(kommune="Ukendtby")
    oplysninger = Skatteoplysninger(loen=400_000)

    b = beregn_skat(oplysninger, profil)

    assert b.detaljer["kommuneskat_pct"] == GENNEMSNITLIG_KOMMUNESKAT_PCT
    assert b.detaljer["kirkeskat_pct"] == GENNEMSNITLIG_KIRKESKAT_PCT


def test_manglende_loen_giver_nul_skat():
    profil = _profil()
    oplysninger = Skatteoplysninger()  # loen = None

    b = beregn_skat(oplysninger, profil)

    assert b.personlig_indkomst == 0
    assert b.am_bidrag == 0.0
    assert b.samlet_skat == 0.0


def test_run_beregn_returnerer_1_hvis_fil_mangler(tmp_path):
    from core.engine import run_beregn

    manglende = tmp_path / "findes-ikke.json"
    profil_fil = tmp_path / "profil.json"
    profil_fil.write_text('{"kommune": "Aarhus"}', encoding="utf-8")

    resultat = run_beregn(str(manglende), profil_path=str(profil_fil))
    assert resultat == 1


def test_run_beregn_returnerer_1_hvis_profil_mangler(tmp_path):
    from core.engine import run_beregn

    op_fil = tmp_path / "oplysninger.json"
    op_fil.write_text('{"loen": 300000}', encoding="utf-8")
    manglende_profil = tmp_path / "findes-ikke-profil.json"

    resultat = run_beregn(str(op_fil), profil_path=str(manglende_profil))
    assert resultat == 1


def test_run_beregn_succes(tmp_path, capsys):
    from core.engine import run_beregn

    profil_fil = tmp_path / "profil.json"
    profil_fil.write_text('{"kommune": "Aarhus", "kirkeskattemedlem": true}', encoding="utf-8")
    op_fil = tmp_path / "oplysninger.json"
    op_fil.write_text('{"loen": 400000}', encoding="utf-8")

    resultat = run_beregn(str(op_fil), profil_path=str(profil_fil))
    assert resultat == 0

    captured = capsys.readouterr()
    assert "Skatteberegning 2026" in captured.out
    assert "Samlet skat i alt" in captured.out
