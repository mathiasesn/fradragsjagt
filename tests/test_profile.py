import pytest

from fradragsjagt.models import Civilstand, Profil
from fradragsjagt.profile import load_profil, run_setup, save_profil


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "profil.json")
    profil = Profil(
        kommune="Aarhus",
        kirkeskattemedlem=True,
        civilstand=Civilstand.GIFT,
        pendler_km_hver_vej=25.0,
        arbejdsdage_pr_aar=210,
        bor_i_yderkommune=True,
        fagforening=True,
        a_kasse=True,
        boligejer=True,
        indkomstaar=2026,
    )
    save_profil(profil, path)
    loaded = load_profil(path)

    assert loaded == profil
    assert isinstance(loaded.civilstand, Civilstand)


def test_load_missing_raises_clear_error(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    with pytest.raises(FileNotFoundError):
        load_profil(path)


def test_run_setup_non_interactive(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc = run_setup(interactive=False)
    assert rc == 0

    loaded = load_profil("profil.json")
    assert isinstance(loaded, Profil)
    assert isinstance(loaded.civilstand, Civilstand)
    assert loaded.indkomstaar == 2026


def test_run_setup_interactive_prompts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    answers = iter(
        [
            "Odense",  # kommune
            "j",  # kirkeskattemedlem
            "gift",  # civilstand
            "30",  # pendler_km_hver_vej
            "200",  # arbejdsdage_pr_aar
            "n",  # bor_i_yderkommune
            "j",  # fagforening
            "j",  # a_kasse
            "n",  # boligejer
            "2026",  # indkomstaar
        ]
    )
    monkeypatch.setattr("builtins.input", lambda *_args, **_kwargs: next(answers))

    rc = run_setup(interactive=True)
    assert rc == 0

    loaded = load_profil("profil.json")
    assert loaded.kommune == "Odense"
    assert loaded.kirkeskattemedlem is True
    assert loaded.civilstand == Civilstand.GIFT
    assert loaded.pendler_km_hver_vej == 30.0
    assert loaded.arbejdsdage_pr_aar == 200
    assert loaded.bor_i_yderkommune is False
    assert loaded.fagforening is True
    assert loaded.a_kasse is True
    assert loaded.boligejer is False
