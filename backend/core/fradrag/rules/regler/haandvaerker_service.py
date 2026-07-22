"""Regel: manglende håndværkerfradrag (grønt) og servicefradrag for boligejere."""

from __future__ import annotations

from ....models import FradragsForslag, Profil, Skatteoplysninger
from ....rates_2026 import FRADRAG_VAERDI_PROCENT, HAANDVAERKERFRADRAG_MAX, SERVICEFRADRAG_MAX
from ..registry import _er_lav, fradragsregel, kr


@fradragsregel
def tjek_haandvaerker_service(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if not profil.boligejer:
        return forslag

    if _er_lav(oplysninger.haandvaerkerfradrag):
        forslag.append(
            FradragsForslag(
                navn="Håndværkerfradrag (grønt)",
                felt="460",
                estimeret_fradrag=HAANDVAERKERFRADRAG_MAX,
                estimeret_skattebesparelse=round(HAANDVAERKERFRADRAG_MAX * FRADRAG_VAERDI_PROCENT, 2),
                begrundelse=(
                    "Du er boligejer, men har ikke indberettet håndværkerfradrag. Har du haft "
                    "energi-/klimarenovering udført i 2026 (fx isolering, varmepumpe, "
                    "vinduesudskiftning), kan du trække op til "
                    f"{kr(HAANDVAERKERFRADRAG_MAX)} kr fra pr. person."
                ),
                saadan_indberetter_du=(
                    "Log ind på skat.dk -> Ret årsopgørelsen -> felt 460 'Håndværkerfradrag'. "
                    "Kræver digital betaling til en momsregistreret virksomhed og gemt faktura."
                ),
                kilde="skat.dk – Håndværkerfradrag (grønt fradrag), felt 460",
                sikkerhed="mulig",
            )
        )

    if _er_lav(oplysninger.servicefradrag):
        forslag.append(
            FradragsForslag(
                navn="Servicefradrag",
                felt="461",
                estimeret_fradrag=SERVICEFRADRAG_MAX,
                estimeret_skattebesparelse=round(SERVICEFRADRAG_MAX * FRADRAG_VAERDI_PROCENT, 2),
                begrundelse=(
                    "Du er boligejer, men har ikke indberettet servicefradrag. Har du købt "
                    "rengøring, havearbejde eller børnepasning i hjemmet i 2026, kan du trække "
                    f"op til {kr(SERVICEFRADRAG_MAX)} kr fra pr. person."
                ),
                saadan_indberetter_du=(
                    "Log ind på skat.dk -> Ret årsopgørelsen -> felt 461 'Servicefradrag'. "
                    "Kræver digital betaling til en momsregistreret virksomhed og gemt faktura."
                ),
                kilde="skat.dk – Servicefradrag, felt 461",
                sikkerhed="mulig",
            )
        )

    return forslag
