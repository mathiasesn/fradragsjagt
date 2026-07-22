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


def test_flagger_pension_for_selvstaendig_uden_indbetaling():
    profil = _profil(selvstaendig=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert any("ension" in n for n in navne)

    pension_forslag = [f for f in forslag if "ension" in f.navn]
    for f in pension_forslag:
        assert f.kilde


def test_ingen_pension_forslag_naar_ikke_selvstaendig():
    profil = _profil(selvstaendig=False)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert not any("ension" in n for n in navne)
