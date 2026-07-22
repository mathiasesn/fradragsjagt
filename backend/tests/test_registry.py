from core.fradrag.rules import REGLER, find_oversete_fradrag
from core.fradrag.rules.registry import _discover_regler
from core.models import Civilstand, Profil, Skatteoplysninger


def _profil(**overrides):
    defaults = dict(
        kommune="Aarhus",
        kirkeskattemedlem=False,
        civilstand=Civilstand.ENLIG,
        pendler_km_hver_vej=25.0,
        arbejdsdage_pr_aar=216,
        bor_i_yderkommune=False,
        fagforening=True,
        a_kasse=False,
        boligejer=True,
        indkomstaar=2026,
    )
    defaults.update(overrides)
    return Profil(**defaults)


def test_regler_er_registreret_og_ikke_tom():
    _discover_regler()
    assert REGLER, "REGLER bør indeholde de migrerede regler"
    navne = {r.__name__ for r in REGLER}
    forventede = {
        "tjek_koersel",
        "tjek_haandvaerker_service",
        "tjek_gaver",
        "tjek_fagforening",
    }
    assert forventede.issubset(navne)


def test_auto_discovery_indlaeser_alle_moduler_i_regler():
    import pkgutil

    from core.fradrag.rules import regler as regler_pakke

    modul_navne = {m.name for m in pkgutil.iter_modules(regler_pakke.__path__)}
    forventede = {"koersel", "haandvaerker_service", "gaver", "fagforening"}
    assert forventede.issubset(modul_navne)


def test_migrerede_forslag_har_ikke_tom_kilde():
    profil = _profil()
    oplysninger = Skatteoplysninger(loen=450_000)

    forslag = find_oversete_fradrag(oplysninger, profil)
    assert forslag
    for f in forslag:
        assert f.kilde, f"Forslag '{f.navn}' mangler kilde"


def test_determinisme_samme_raekkefoelge_ved_flere_kald():
    profil = _profil()
    oplysninger = Skatteoplysninger(loen=450_000)

    forslag1 = find_oversete_fradrag(oplysninger, profil)
    forslag2 = find_oversete_fradrag(oplysninger, profil)

    navne1 = [f.navn for f in forslag1]
    navne2 = [f.navn for f in forslag2]
    assert navne1 == navne2
