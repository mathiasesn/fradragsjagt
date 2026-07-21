"""Regelbaseret drafter-pas: gennemgår profil + skatteoplysninger og foreslår
oversete fradrag. Hver regel er konservativ — den foreslår kun noget, hvis
profilen tydeligt peger på det (fx pendling registreret), og markerer altid
"sikkerhed" så brugeren ved hvor sikker vurderingen er.

Satser læses defensivt fra ..rates_2026 hvis muligt, ellers lokale fallbacks
(kommenteret nedenfor).
"""

from __future__ import annotations

try:  # pragma: no cover - defensiv import
    from ..rates_2026 import (
        HAANDVAERKERFRADRAG_MAX,
        SERVICEFRADRAG_MAX,
        GAVER_8A_MAX,
    )
except ImportError:
    HAANDVAERKERFRADRAG_MAX = 9_000.0  # kr/person 2026, grønt håndværkerfradrag, felt 460
    SERVICEFRADRAG_MAX = 18_300.0  # kr/person 2026, servicefradrag, felt 461
    GAVER_8A_MAX = 20_000.0  # kr/person 2026, §8A gaver, rubrik 55

# Grov værdi af et fradrag: ca. bundskat + kommuneskat, uden topskat/mellemskat-præcision.
FRADRAG_VAERDI_PROCENT = 0.26

from ..models import FradragsForslag, Profil, Skatteoplysninger
from .koersel import beregn_koerselsfradrag


def _er_lav(vaerdi: float | None, taerskel: float = 0.0) -> bool:
    """True hvis værdien mangler (None) eller er under en given tærskel."""

    return vaerdi is None or vaerdi <= taerskel


def _tjek_koersel(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if profil.pendler_km_hver_vej <= 0:
        return forslag

    aarsindkomst = oplysninger.loen or 0.0
    beregnet = beregn_koerselsfradrag(
        km_hver_vej=profil.pendler_km_hver_vej,
        arbejdsdage=profil.arbejdsdage_pr_aar,
        yderkommune=profil.bor_i_yderkommune,
        aarsindkomst=aarsindkomst,
    )

    if beregnet.estimeret_fradrag <= 0:
        return forslag

    indberettet = oplysninger.befordringsfradrag or 0.0
    if indberettet >= beregnet.estimeret_fradrag * 0.95:
        # Allerede indberettet i nogenlunde rigtig størrelsesorden.
        return forslag

    forslag.append(beregnet)
    return forslag


def _tjek_haandvaerker_service(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
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
                    f"{HAANDVAERKERFRADRAG_MAX:,.0f} kr fra pr. person."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Log ind på skat.dk -> Ret årsopgørelsen -> felt 460 'Håndværkerfradrag'. "
                    "Kræver digital betaling til en momsregistreret virksomhed og gemt faktura."
                ),
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
                    f"op til {SERVICEFRADRAG_MAX:,.0f} kr fra pr. person."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Log ind på skat.dk -> Ret årsopgørelsen -> felt 461 'Servicefradrag'. "
                    "Kræver digital betaling til en momsregistreret virksomhed og gemt faktura."
                ),
                sikkerhed="mulig",
            )
        )

    return forslag


def _tjek_gaver(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if _er_lav(oplysninger.gaver_almenvelgoerende):
        forslag.append(
            FradragsForslag(
                navn="Gaver til almennyttige foreninger (§8A)",
                felt="55",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Du har ikke indberettet gaver til godkendte foreninger. Har du doneret til "
                    "fx en velgørenhedsorganisation i 2026, kan du trække det fra med op til "
                    f"{GAVER_8A_MAX:,.0f} kr pr. person (kan ikke overføres mellem ægtefæller). "
                    "De fleste foreninger indberetter selv beløbet automatisk."
                ).replace(",", "."),
                saadan_indberetter_du=(
                    "Tjek felt/rubrik 55 på din årsopgørelse — indberettes normalt automatisk af "
                    "foreningen. Mangler det, kan du selv rette det på skat.dk under 'Gaver til "
                    "godkendte foreninger'."
                ),
                sikkerhed="kræver dokumentation",
            )
        )

    return forslag


def _tjek_fagforening(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    forslag: list[FradragsForslag] = []

    if (profil.fagforening or profil.a_kasse) and _er_lav(oplysninger.fagforening_a_kasse):
        forslag.append(
            FradragsForslag(
                navn="Fagforening og A-kasse-kontingent",
                felt="50/52",
                estimeret_fradrag=0.0,
                estimeret_skattebesparelse=0.0,
                begrundelse=(
                    "Din profil angiver medlemskab af fagforening og/eller a-kasse, men der er "
                    "ikke registreret et fradrag for kontingent. Fagforeningskontingent og "
                    "a-kasse-kontingent er fradragsberettiget."
                ),
                saadan_indberetter_du=(
                    "Indberettes normalt automatisk af fagforeningen/a-kassen i rubrik 50/52. "
                    "Mangler det på din årsopgørelse, kan du selv tilføje beløbet på skat.dk."
                ),
                sikkerhed="mulig",
            )
        )

    return forslag


def find_oversete_fradrag(oplysninger: Skatteoplysninger, profil: Profil) -> list[FradragsForslag]:
    """Kør alle regler og saml en liste af foreslåede, sandsynligvis oversete fradrag."""

    forslag: list[FradragsForslag] = []
    forslag.extend(_tjek_koersel(oplysninger, profil))
    forslag.extend(_tjek_haandvaerker_service(oplysninger, profil))
    forslag.extend(_tjek_gaver(oplysninger, profil))
    forslag.extend(_tjek_fagforening(oplysninger, profil))
    return forslag
