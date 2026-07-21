"""fradragstjek — finder sandsynligvis oversete fradrag ud fra profil + oplysninger."""

from __future__ import annotations

import json
import os

from ..models import Skatteoplysninger
from ..profile import load_profil
from .koersel import beregn_koerselsfradrag
from .rules import find_oversete_fradrag

__all__ = ["find_oversete_fradrag", "beregn_koerselsfradrag", "run_fradragstjek"]


def _load_oplysninger(path: str) -> Skatteoplysninger:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    kendte_felter = {
        "loen",
        "am_bidrag_indeholdt",
        "a_skat_indeholdt",
        "renteudgifter",
        "fagforening_a_kasse",
        "befordringsfradrag",
        "haandvaerkerfradrag",
        "servicefradrag",
        "gaver_almenvelgoerende",
        "pensionsindbetaling",
        "aktieindkomst",
        "raw",
    }
    kwargs = {k: v for k, v in data.items() if k in kendte_felter}
    return Skatteoplysninger(**kwargs)


def run_fradragstjek(oplysninger_path: str, profil_path: str = "profil.json") -> int:
    """Kør fradragstjekket: indlæs profil + oplysninger, find oversete fradrag, print dem.

    Returns:
        0 ved succes, 1 hvis nødvendige filer mangler.
    """

    if not os.path.exists(profil_path):
        print(
            f"Fandt ingen lokal profil ('{profil_path}'). Kør 'fradragsjagt setup' først."
        )
        return 1

    if not os.path.exists(oplysninger_path):
        print(
            f"Fandt ingen skatteoplysninger ('{oplysninger_path}'). "
            "Kør 'fradragsjagt parse' først for at generere filen."
        )
        return 1

    try:
        profil = load_profil(profil_path)
    except (json.JSONDecodeError, OSError, ValueError, TypeError, FileNotFoundError) as e:
        print(f"Kunne ikke læse profilen '{profil_path}': {e}")
        return 1

    try:
        oplysninger = _load_oplysninger(oplysninger_path)
    except (json.JSONDecodeError, OSError, ValueError, TypeError) as e:
        print(f"Kunne ikke læse skatteoplysninger '{oplysninger_path}': {e}")
        return 1

    forslag = find_oversete_fradrag(oplysninger, profil)

    if not forslag:
        print("Fradragstjek: Fandt ingen tydeligt oversete fradrag ud fra din profil.")
        return 0

    print(f"Fradragstjek: Fandt {len(forslag)} muligt(e) oversete fradrag:\n")
    samlet_besparelse = 0.0
    for i, f in enumerate(forslag, start=1):
        print(f"{i}. {f.navn} (felt {f.felt}) — sikkerhed: {f.sikkerhed}")
        if f.estimeret_fradrag:
            print(f"   Estimeret fradrag: {f.estimeret_fradrag:,.0f} kr".replace(",", "."))
        if f.estimeret_skattebesparelse:
            print(
                f"   Estimeret skattebesparelse: {f.estimeret_skattebesparelse:,.0f} kr".replace(
                    ",", "."
                )
            )
        print(f"   Begrundelse: {f.begrundelse}")
        print(f"   Sådan indberetter du: {f.saadan_indberetter_du}\n")
        samlet_besparelse += f.estimeret_skattebesparelse

    print(f"Samlet estimeret skattebesparelse: {samlet_besparelse:,.0f} kr".replace(",", "."))
    print(
        "\nHusk: Dette er et estimat, ikke bindende skatterådgivning. "
        "Du skal selv indberette på skat.dk."
    )
    return 0
