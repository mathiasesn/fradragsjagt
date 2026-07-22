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


def test_flagger_rejsefradrag_naar_rejsedage_men_intet_indberettet():
    profil = _profil(rejsedage_med_overnatning=10)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert any("ejsefradrag" in n for n in navne)

    rejse_forslag = [f for f in forslag if "ejsefradrag" in f.navn]
    for f in rejse_forslag:
        assert f.kilde


def test_ingen_rejsefradrag_forslag_uden_rejsedage_i_profil():
    profil = _profil(rejsedage_med_overnatning=0)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert not any("ejsefradrag" in n for n in navne)
