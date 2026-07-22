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


def test_flagger_dobbelt_husfoerelse_naar_profil_angiver_det():
    profil = _profil(dobbelt_husfoerelse=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert any("obbelt husførelse" in n for n in navne)
    for f in forslag:
        assert f.kilde


def test_ingen_dobbelt_husfoerelse_forslag_uden_profilflag():
    profil = _profil()
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert not any("obbelt husførelse" in n for n in navne)


def test_ingen_dobbelt_husfoerelse_forslag_hvis_allerede_indberettet():
    profil = _profil(dobbelt_husfoerelse=True)
    oplysninger = Skatteoplysninger(dobbelt_husfoerelse_fradrag=5_000.0)

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert not any("obbelt husførelse" in n for n in navne)
