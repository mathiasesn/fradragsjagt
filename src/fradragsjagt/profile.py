"""Lokal profilopsætning (`fradragsjagt setup`).

Alt gemmes lokalt. Intet forlader maskinen.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields

from .models import Civilstand, Profil

DEFAULT_PATH = "profil.json"


def _spoerg(prompt: str, default: str) -> str:
    svar = input(f"{prompt} [{default}]: ").strip()
    return svar or default


def _spoerg_bool(prompt: str, default: bool) -> bool:
    default_str = "j" if default else "n"
    svar = input(f"{prompt} (j/n) [{default_str}]: ").strip().lower()
    if not svar:
        return default
    return svar in ("j", "ja", "y", "yes")


def _spoerg_int(prompt: str, default: int) -> int:
    svar = input(f"{prompt} [{default}]: ").strip()
    if not svar:
        return default
    try:
        return int(svar)
    except ValueError:
        return default


def _spoerg_float(prompt: str, default: float) -> float:
    svar = input(f"{prompt} [{default}]: ").strip()
    if not svar:
        return default
    try:
        return float(svar.replace(",", "."))
    except ValueError:
        return default


def _spoerg_civilstand(default: Civilstand) -> Civilstand:
    svar = input(f"Civilstand (enlig/gift) [{default.value}]: ").strip().lower()
    if not svar:
        return default
    try:
        return Civilstand(svar)
    except ValueError:
        return default


def run_setup(interactive: bool) -> int:
    """Opret en lokal brugerprofil og gem den som profil.json.

    Hvis interactive er False, benyttes fornuftige defaults uden prompts.
    """
    if interactive:
        print("Opsætning af lokal profil til fradragsjagt.")
        print("Intet af det du skriver her sendes nogen steder - alt bliver på din maskine.\n")
        kommune = _spoerg("Hvilken kommune bor du i", "København")
        kirkeskattemedlem = _spoerg_bool("Er du medlem af folkekirken (betaler kirkeskat)", False)
        civilstand = _spoerg_civilstand(Civilstand.ENLIG)
        pendler_km_hver_vej = _spoerg_float("Hvor mange km pendler du hver vej til arbejde", 0.0)
        arbejdsdage_pr_aar = _spoerg_int("Hvor mange arbejdsdage har du pr. år", 216)
        bor_i_yderkommune = _spoerg_bool("Bor du i en yderkommune (forhøjet befordringsfradrag)", False)
        fagforening = _spoerg_bool("Er du medlem af en fagforening", False)
        a_kasse = _spoerg_bool("Er du medlem af en a-kasse", False)
        boligejer = _spoerg_bool("Er du boligejer", False)
        indkomstaar = _spoerg_int("Hvilket indkomstår gælder profilen", 2026)

        profil = Profil(
            kommune=kommune,
            kirkeskattemedlem=kirkeskattemedlem,
            civilstand=civilstand,
            pendler_km_hver_vej=pendler_km_hver_vej,
            arbejdsdage_pr_aar=arbejdsdage_pr_aar,
            bor_i_yderkommune=bor_i_yderkommune,
            fagforening=fagforening,
            a_kasse=a_kasse,
            boligejer=boligejer,
            indkomstaar=indkomstaar,
        )
    else:
        profil = Profil(kommune="København")

    save_profil(profil)

    print(f"\nProfil gemt i {DEFAULT_PATH}.")
    print("Husk: fradragsjagt kører 100% lokalt - dine data forlader ikke denne maskine.")
    return 0


def save_profil(profil: Profil, path: str = DEFAULT_PATH) -> None:
    """Gem en Profil som JSON."""
    data = asdict(profil)
    data["civilstand"] = profil.civilstand.value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_profil(path: str = DEFAULT_PATH) -> Profil:
    """Indlæs en Profil fra JSON. Kaster FileNotFoundError med en klar besked hvis filen mangler."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Ingen profil fundet på '{path}'. Kør 'fradragsjagt setup' først."
        ) from exc

    civilstand = data.get("civilstand", Civilstand.ENLIG.value)
    data["civilstand"] = civilstand if isinstance(civilstand, Civilstand) else Civilstand(civilstand)
    kendte_felter = {f.name for f in fields(Profil)}
    data = {k: v for k, v in data.items() if k in kendte_felter}
    return Profil(**data)
