from core.fradrag.rules import find_oversete_fradrag
from core.models import Civilstand, Profil, Skatteoplysninger


def _profil(**overrides):
    defaults = dict(
        kommune="Aarhus",
        kirkeskattemedlem=False,
        civilstand=Civilstand.ENLIG,
        pendler_km_hver_vej=0.0,
        arbejdsdage_pr_aar=216,
        bor_i_yderkommune=False,
        fagforening=False,
        a_kasse=False,
        boligejer=False,
        indkomstaar=2026,
    )
    defaults.update(overrides)
    return Profil(**defaults)


def test_flagger_aktietab_naar_har_tab_men_intet_fremfoert():
    profil = _profil(har_aktietab=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert any("ktier" in n and "tab" in n.lower() for n in navne)


def test_ingen_aktietab_forslag_uden_tab_i_profil():
    profil = _profil(har_aktietab=False)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert not any("ktier" in n for n in navne)


def test_ingen_aktietab_forslag_hvis_allerede_registreret():
    profil = _profil(har_aktietab=True)
    oplysninger = Skatteoplysninger(aktietab_fremfoert=5_000.0)

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert not any("ktier" in n for n in navne)


def test_alle_forslag_har_kilde():
    profil = _profil(har_aktietab=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    assert all(f.kilde for f in forslag)
