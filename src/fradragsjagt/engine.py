"""Skatteberegningsmotor for indkomståret 2026.

`beregn_skat` er en ren funktion (ingen I/O, ingen netværk, deterministisk):
den tager en `Skatteoplysninger` og en `Profil` og returnerer en
`Skatteberegning`.

Forenklet beregningsmodel (dokumenteret her, ikke gemt hemmeligt):

  1. personlig_indkomst = løn (rubrik 11), 0 hvis ikke oplyst.
  2. am_bidrag = personlig_indkomst * 8%.
  3. personlig_indkomst_efter_am = personlig_indkomst - am_bidrag.
     Dette grundlag bruges til beskæftigelsesfradrag, jobfradrag og til
     mellemskat/topskat/top-topskat (progressionsgrænserne gælder personlig
     indkomst efter AM-bidrag, ekskl. evt. positiv nettokapitalindkomst, som
     ikke er modelleret her).
  4. beskæftigelsesfradrag = min(12,75% * grundlag, 63.300 kr.)
  5. jobfradrag = min(4,50% * max(grundlag - 235.200, 0), 3.100 kr.)
  6. skattepligtig_indkomst (grundlag for bundskat/kommuneskat/kirkeskat)
     = max(personlig_indkomst_efter_am - beskæftigelsesfradrag - jobfradrag
           - personfradrag, 0)
  7. bundskat/kommuneskat/kirkeskat beregnes af skattepligtig_indkomst.
  8. mellemskat/topskat/top-topskat beregnes progressivt af
     personlig_indkomst_efter_am (personfradraget påvirker ikke disse
     trin i denne forenklede model — det er en kendt forenkling).

Skatteloftet (52,07%) håndhæves IKKE som en fuld marginalskats-cap i denne
version — det noteres i `detaljer` som en advarsel, hvis den beregnede
marginalskat overstiger loftet. Dette er en bevidst forenkling og bør
udbygges, hvis præcis marginalskat er kritisk.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from . import rates_2026 as rates
from .models import Profil, Skatteberegning, Skatteoplysninger


def beregn_skat(oplysninger: Skatteoplysninger, profil: Profil) -> Skatteberegning:
    """Beregn 2026-skat ud fra parsede skatteoplysninger og brugerprofil."""

    personlig_indkomst = oplysninger.loen or 0.0

    am_bidrag = personlig_indkomst * rates.AM_BIDRAG_PCT / 100.0
    personlig_indkomst_efter_am = personlig_indkomst - am_bidrag

    beskaeftigelsesfradrag = min(
        personlig_indkomst_efter_am * rates.BESKAEFTIGELSESFRADRAG_PCT / 100.0,
        rates.BESKAEFTIGELSESFRADRAG_MAKS,
    )
    beskaeftigelsesfradrag = max(beskaeftigelsesfradrag, 0.0)

    jobfradrag_grundlag = max(personlig_indkomst_efter_am - rates.JOBFRADRAG_BUNDGRAENSE, 0.0)
    jobfradrag = min(
        jobfradrag_grundlag * rates.JOBFRADRAG_PCT / 100.0,
        rates.JOBFRADRAG_MAKS,
    )

    skattepligtig_indkomst = max(
        personlig_indkomst_efter_am - beskaeftigelsesfradrag - jobfradrag - rates.PERSONFRADRAG,
        0.0,
    )

    sats = rates.kommunesats(profil.kommune)

    bundskat = skattepligtig_indkomst * rates.BUNDSKAT_PCT / 100.0
    kommuneskat = skattepligtig_indkomst * sats.kommuneskat_pct / 100.0
    kirkeskat = (
        skattepligtig_indkomst * sats.kirkeskat_pct / 100.0
        if profil.kirkeskattemedlem
        else 0.0
    )

    mellemskat_grundlag = max(
        min(personlig_indkomst_efter_am, rates.MELLEMSKAT_TOPGRAENSE) - rates.MELLEMSKAT_BUNDGRAENSE,
        0.0,
    )
    mellemskat = mellemskat_grundlag * rates.MELLEMSKAT_PCT / 100.0

    topskat_grundlag = max(
        min(personlig_indkomst_efter_am, rates.TOPSKAT_TOPGRAENSE) - rates.TOPSKAT_BUNDGRAENSE,
        0.0,
    )
    topskat = topskat_grundlag * rates.TOPSKAT_PCT / 100.0

    top_topskat_grundlag = max(personlig_indkomst_efter_am - rates.TOP_TOPSKAT_BUNDGRAENSE, 0.0)
    top_topskat = top_topskat_grundlag * rates.TOP_TOPSKAT_PCT / 100.0

    personfradrag_vaerdi = rates.PERSONFRADRAG * (
        rates.BUNDSKAT_PCT
        + sats.kommuneskat_pct
        + (sats.kirkeskat_pct if profil.kirkeskattemedlem else 0.0)
    ) / 100.0

    samlet_skat = (
        am_bidrag
        + bundskat
        + kommuneskat
        + kirkeskat
        + mellemskat
        + topskat
        + top_topskat
    )

    marginalskat_uden_kirke_pct = (
        rates.BUNDSKAT_PCT
        + sats.kommuneskat_pct
        + (rates.MELLEMSKAT_PCT if mellemskat_grundlag > 0 else 0.0)
        + (rates.TOPSKAT_PCT if topskat_grundlag > 0 else 0.0)
        + (rates.TOP_TOPSKAT_PCT if top_topskat_grundlag > 0 else 0.0)
    )
    skatteloft_overskredet = marginalskat_uden_kirke_pct > rates.SKATTELOFT_PCT

    detaljer = {
        "kommune": sats.kommune,
        "kommuneskat_pct": sats.kommuneskat_pct,
        "kirkeskat_pct": sats.kirkeskat_pct if profil.kirkeskattemedlem else 0.0,
        "personlig_indkomst_efter_am": personlig_indkomst_efter_am,
        "marginalskat_uden_kirke_pct": marginalskat_uden_kirke_pct,
        "skatteloft_overskredet": skatteloft_overskredet,
    }
    if skatteloft_overskredet:
        detaljer["advarsel"] = (
            f"Beregnet marginalskat ({marginalskat_uden_kirke_pct:.2f}%) overstiger "
            f"skatteloftet på {rates.SKATTELOFT_PCT}% — denne forenklede model "
            "håndhæver ikke skatteloftet som en reel cap."
        )

    return Skatteberegning(
        personlig_indkomst=personlig_indkomst,
        skattepligtig_indkomst=skattepligtig_indkomst,
        am_bidrag=am_bidrag,
        bundskat=bundskat,
        kommuneskat=kommuneskat,
        kirkeskat=kirkeskat,
        mellemskat=mellemskat,
        topskat=topskat,
        top_topskat=top_topskat,
        beskaeftigelsesfradrag=beskaeftigelsesfradrag,
        jobfradrag=jobfradrag,
        personfradrag_vaerdi=personfradrag_vaerdi,
        samlet_skat=samlet_skat,
        detaljer=detaljer,
    )


def _profil_fra_json(data: dict) -> Profil:
    civilstand = data.get("civilstand", "enlig")
    from .models import Civilstand

    return Profil(
        kommune=data.get("kommune", ""),
        kirkeskattemedlem=data.get("kirkeskattemedlem", False),
        civilstand=Civilstand(civilstand) if not isinstance(civilstand, Civilstand) else civilstand,
        pendler_km_hver_vej=data.get("pendler_km_hver_vej", 0.0),
        arbejdsdage_pr_aar=data.get("arbejdsdage_pr_aar", 216),
        bor_i_yderkommune=data.get("bor_i_yderkommune", False),
        fagforening=data.get("fagforening", False),
        a_kasse=data.get("a_kasse", False),
        boligejer=data.get("boligejer", False),
        indkomstaar=data.get("indkomstaar", 2026),
    )


def _oplysninger_fra_json(data: dict) -> Skatteoplysninger:
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
    }
    kwargs = {felt: data[felt] for felt in kendte_felter if felt in data}
    raw = data.get("raw", {})
    return Skatteoplysninger(raw=raw, **kwargs)


def run_beregn(oplysninger_path: str, profil_path: str = "profil.json") -> int:
    """Indlæs profil + skatteoplysninger fra JSON, beregn skat og udskriv resultatet.

    Returnerer 0 ved succes, 1 hvis en påkrævet fil mangler eller ikke kan
    læses/parses.
    """

    op_path = Path(oplysninger_path)
    pr_path = Path(profil_path)

    if not pr_path.exists():
        print(
            f"Fejl: kunne ikke finde profilfilen '{pr_path}'. "
            "Kør 'fradragsjagt setup' for at oprette den.",
            file=sys.stderr,
        )
        return 1

    if not op_path.exists():
        print(
            f"Fejl: kunne ikke finde skatteoplysninger-filen '{op_path}'. "
            "Kør 'fradragsjagt parse' for at oprette den.",
            file=sys.stderr,
        )
        return 1

    try:
        profil_data = json.loads(pr_path.read_text(encoding="utf-8"))
        profil = _profil_fra_json(profil_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Fejl: kunne ikke læse profilfilen '{pr_path}': {e}", file=sys.stderr)
        return 1

    try:
        op_data = json.loads(op_path.read_text(encoding="utf-8"))
        oplysninger = _oplysninger_fra_json(op_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Fejl: kunne ikke læse skatteoplysninger-filen '{op_path}': {e}", file=sys.stderr)
        return 1

    beregning = beregn_skat(oplysninger, profil)

    print("Skatteberegning 2026 (estimat)")
    print("=" * 40)
    print(f"Kommune:                    {beregning.detaljer.get('kommune')}")
    print(f"Personlig indkomst:         {beregning.personlig_indkomst:,.0f} kr.")
    print(f"AM-bidrag (8%):             {beregning.am_bidrag:,.0f} kr.")
    print(f"Beskæftigelsesfradrag:      {beregning.beskaeftigelsesfradrag:,.0f} kr.")
    print(f"Jobfradrag:                 {beregning.jobfradrag:,.0f} kr.")
    print(f"Personfradrag (skatteværdi):{beregning.personfradrag_vaerdi:,.0f} kr.")
    print(f"Skattepligtig indkomst:     {beregning.skattepligtig_indkomst:,.0f} kr.")
    print("-" * 40)
    print(f"Bundskat:                   {beregning.bundskat:,.0f} kr.")
    print(f"Kommuneskat:                {beregning.kommuneskat:,.0f} kr.")
    print(f"Kirkeskat:                  {beregning.kirkeskat:,.0f} kr.")
    print(f"Mellemskat:                 {beregning.mellemskat:,.0f} kr.")
    print(f"Topskat:                    {beregning.topskat:,.0f} kr.")
    print(f"Top-topskat:                {beregning.top_topskat:,.0f} kr.")
    print("-" * 40)
    print(f"Samlet skat i alt:          {beregning.samlet_skat:,.0f} kr.")
    if beregning.detaljer.get("skatteloft_overskredet"):
        print()
        print(f"Advarsel: {beregning.detaljer.get('advarsel')}")
    print()
    print(
        "Dette er et estimat baseret på forenklede 2026-satser. "
        "Ikke autoriseret skatterådgivning — verificér altid mod skat.dk."
    )

    return 0
