"""Regel-registret: dekoratoren `@fradragsregel` og auto-discovery af regler.

Hver regelfil under `rules/regler/` importeres automatisk (via pkgutil), og
dekorerede funktioner samles i `REGLER`. Nye regler kan tilføjes ved blot at
oprette en ny fil i `regler/` — ingen delte filer skal redigeres.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Callable

from ...models import FradragsForslag, Profil, Skatteoplysninger

Fradragsregel = Callable[[Skatteoplysninger, Profil], list[FradragsForslag]]

REGLER: list[Fradragsregel] = []

_DISCOVERED = False


def fradragsregel(func: Fradragsregel) -> Fradragsregel:
    """Dekorator: registrerer en regelfunktion i det globale regel-register."""

    REGLER.append(func)
    return func


def _er_lav(vaerdi: float | None, taerskel: float = 0.0) -> bool:
    """True hvis værdien mangler (None) eller er under en given tærskel."""

    return vaerdi is None or vaerdi <= taerskel


def _discover_regler() -> None:
    """Importér alle moduler i `rules/regler/`, så deres @fradragsregel-funktioner
    registreres i REGLER. Idempotent — importerer kun én gang pr. proces."""

    global _DISCOVERED
    if _DISCOVERED:
        return

    from . import regler as regler_pakke

    for modinfo in pkgutil.iter_modules(regler_pakke.__path__):
        importlib.import_module(f"{regler_pakke.__name__}.{modinfo.name}")

    _DISCOVERED = True


def find_oversete_fradrag(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    """Kør alle registrerede regler og saml en liste af foreslåede fradrag.

    Reglerne køres i deterministisk rækkefølge (sorteret efter funktionsnavn).
    """

    _discover_regler()

    forslag: list[FradragsForslag] = []
    for regel in sorted(REGLER, key=lambda r: r.__name__):
        forslag.extend(regel(oplysninger, profil))
    return forslag
