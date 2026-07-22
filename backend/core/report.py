"""Rapport-stadiet — samler beregning og fradragsforslag til en Markdown-rapport.

Ren funktion `byg_rapport` + IO-wrapper `run_rapport` til CLI'en.
"""

from __future__ import annotations

import json
import os

from . import DISCLAIMER
from .models import FradragsForslag, Profil, Skatteberegning, Skatteoplysninger


def _fmt_kr(beloeb: float) -> str:
    return f"{beloeb:,.0f} kr.".replace(",", ".")


def byg_rapport(
    oplysninger: Skatteoplysninger,
    profil: Profil,
    beregning: Skatteberegning | None,
    forslag: list[FradragsForslag],
) -> str:
    """Byg en samlet Markdown-rapport på dansk. Indeholder aldrig CPR."""

    linjer: list[str] = []
    linjer.append("# fradragsjagt — din rapport")
    linjer.append("")
    linjer.append(f"Kommune: **{profil.kommune}** · Indkomstår: **{profil.indkomstaar}**")
    linjer.append("")

    # Skatteoverblik
    linjer.append("## Skatteoverblik")
    linjer.append("")
    if beregning is not None:
        linjer.append("| Post | Beløb |")
        linjer.append("|---|---|")
        linjer.append(f"| Personlig indkomst | {_fmt_kr(beregning.personlig_indkomst)} |")
        linjer.append(f"| Skattepligtig indkomst | {_fmt_kr(beregning.skattepligtig_indkomst)} |")
        linjer.append(f"| AM-bidrag | {_fmt_kr(beregning.am_bidrag)} |")
        linjer.append(f"| Bundskat | {_fmt_kr(beregning.bundskat)} |")
        linjer.append(f"| Kommuneskat | {_fmt_kr(beregning.kommuneskat)} |")
        linjer.append(f"| Kirkeskat | {_fmt_kr(beregning.kirkeskat)} |")
        if beregning.mellemskat:
            linjer.append(f"| Mellemskat | {_fmt_kr(beregning.mellemskat)} |")
        if beregning.topskat:
            linjer.append(f"| Topskat | {_fmt_kr(beregning.topskat)} |")
        if beregning.top_topskat:
            linjer.append(f"| Ekstra topskat | {_fmt_kr(beregning.top_topskat)} |")
        linjer.append(f"| Beskæftigelsesfradrag | {_fmt_kr(beregning.beskaeftigelsesfradrag)} |")
        linjer.append(f"| Jobfradrag | {_fmt_kr(beregning.jobfradrag)} |")
        linjer.append(f"| Personfradrag (værdi) | {_fmt_kr(beregning.personfradrag_vaerdi)} |")
        linjer.append(f"| **Samlet skat** | **{_fmt_kr(beregning.samlet_skat)}** |")
    else:
        linjer.append("_Skatteberegningen kunne ikke gennemføres (beregningsmodulet mangler eller fejlede)._")
    linjer.append("")

    # Fradragsforslag
    linjer.append("## Sandsynlige oversete fradrag")
    linjer.append("")
    if forslag:
        linjer.append("| Navn | Felt | Estimeret fradrag | Estimeret besparelse | Sikkerhed |")
        linjer.append("|---|---|---|---|---|")
        for f in forslag:
            linjer.append(
                f"| {f.navn} | {f.felt} | {_fmt_kr(f.estimeret_fradrag)} | "
                f"{_fmt_kr(f.estimeret_skattebesparelse)} | {f.sikkerhed} |"
            )
        linjer.append("")

        samlet_besparelse = sum(f.estimeret_skattebesparelse for f in forslag)
        linjer.append(f"**Samlet potentiel skattebesparelse: {_fmt_kr(samlet_besparelse)}**")
        linjer.append("")

        linjer.append("### Sådan indberetter du")
        linjer.append("")
        for f in forslag:
            linjer.append(f"**{f.navn}** (felt {f.felt})")
            linjer.append("")
            linjer.append(f"- Begrundelse: {f.begrundelse}")
            linjer.append(f"- Sådan indberetter du: {f.saadan_indberetter_du}")
            if f.kilde:
                linjer.append(f"- Kilde: {f.kilde}")
            linjer.append(f"- Verificeret: {'ja' if f.verificeret else 'nej'}")
            linjer.append("")
    else:
        linjer.append("Ingen oversete fradrag fundet ud fra de tilgængelige oplysninger.")
        linjer.append("")

    linjer.append("---")
    linjer.append("")
    linjer.append(DISCLAIMER)
    linjer.append("")

    return "\n".join(linjer)


def run_rapport(oplysninger_path: str, out: str) -> int:
    """Indlæs profil + oplysninger, beregn skat, find fradrag, skriv rapport til `out`."""

    if not os.path.exists(oplysninger_path):
        print(
            f"Fandt ikke '{oplysninger_path}'. Kør 'fradragsjagt parse' først for at "
            "oprette skatteoplysninger."
        )
        return 1

    try:
        with open(oplysninger_path, encoding="utf-8") as fh:
            raw = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Kunne ikke læse '{oplysninger_path}': {exc}")
        return 1

    oplysninger = Skatteoplysninger(
        **{k: v for k, v in raw.items() if k in Skatteoplysninger.__dataclass_fields__}
    )

    profil: Profil
    try:
        from .profile import load_profil

        profil = load_profil("profil.json")
    except ImportError:
        print("Bemærk: profil-modulet er endnu ikke tilgængeligt — bruger standardprofil.")
        profil = Profil(kommune="ukendt")
    except (FileNotFoundError, OSError):
        print("Bemærk: ingen lokal profil fundet — bruger standardprofil. Kør 'fradragsjagt setup'.")
        profil = Profil(kommune="ukendt")

    beregning: Skatteberegning | None
    try:
        from .engine import beregn_skat

        beregning = beregn_skat(oplysninger, profil)
    except ImportError:
        print("Bemærk: beregningsmodulet er endnu ikke tilgængeligt — springer skatteoverblik over.")
        beregning = None
    except Exception as exc:  # noqa: BLE001 — degrade gracefully
        print(f"Bemærk: skatteberegning fejlede ({exc}) — springer skatteoverblik over.")
        beregning = None

    forslag: list[FradragsForslag]
    try:
        from .fradrag import find_oversete_fradrag

        forslag = find_oversete_fradrag(oplysninger, profil)
    except ImportError:
        print("Bemærk: fradragstjek-modulet er endnu ikke tilgængeligt — springer fradragstjek over.")
        forslag = []
    except Exception as exc:  # noqa: BLE001 — degrade gracefully
        print(f"Bemærk: fradragstjek fejlede ({exc}) — springer fradragstjek over.")
        forslag = []

    rapport = byg_rapport(oplysninger, profil, beregning, forslag)

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(rapport)

    print(f"Rapport gemt i '{out}'.")
    return 0
