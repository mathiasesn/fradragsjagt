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


def test_flagger_manglende_koerselsfradrag():
    profil = _profil(pendler_km_hver_vej=25)
    oplysninger = Skatteoplysninger(loen=450_000)

    forslag = find_oversete_fradrag(oplysninger, profil)

    navne = [f.navn for f in forslag]
    assert any("ørsel" in n or "efordring" in n for n in navne)


def test_ingen_koersel_forslag_hvis_allerede_indberettet():
    profil = _profil(pendler_km_hver_vej=25)
    # Beregn hvad der forventes, og indberet nogenlunde det samme.
    from core.fradrag.koersel import beregn_koerselsfradrag

    beregnet = beregn_koerselsfradrag(25, 216, False, 450_000)
    oplysninger = Skatteoplysninger(loen=450_000, befordringsfradrag=beregnet.estimeret_fradrag)

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert not any("Kørsel" in n for n in navne)


def test_ingen_koersel_forslag_uden_pendling_i_profil():
    profil = _profil(pendler_km_hver_vej=0.0)
    oplysninger = Skatteoplysninger(loen=450_000)

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert not any("Kørsel" in n for n in navne)


def test_flagger_haandvaerker_og_service_for_boligejer():
    profil = _profil(boligejer=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert any("Håndværker" in n for n in navne)
    assert any("Service" in n for n in navne)


def test_flagger_fagforening_naar_medlem_men_intet_indberettet():
    profil = _profil(fagforening=True)
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert any("agforening" in n for n in navne)


def test_flagger_gaver_naar_intet_indberettet():
    profil = _profil()
    oplysninger = Skatteoplysninger()

    forslag = find_oversete_fradrag(oplysninger, profil)
    navne = [f.navn for f in forslag]
    assert any("Gaver" in n for n in navne)
