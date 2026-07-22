"""Delte datamodeller — kontrakten mellem alle moduler i fradragsjagt.

Alle beløb er i danske kroner (DKK) medmindre andet er angivet.
Ingen af disse modeller må indeholde CPR eller andre direkte identifikatorer.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Optional


class Civilstand(str, Enum):
    ENLIG = "enlig"
    GIFT = "gift"


@dataclass
class Profil:
    """Lokal brugerprofil (fra `fradragsjagt setup`). Gemmes lokalt som JSON."""

    kommune: str
    kirkeskattemedlem: bool = False
    civilstand: Civilstand = Civilstand.ENLIG
    # Pendling
    pendler_km_hver_vej: float = 0.0
    arbejdsdage_pr_aar: int = 216
    bor_i_yderkommune: bool = False
    # Medlemskaber / status
    fagforening: bool = False
    a_kasse: bool = False
    boligejer: bool = False
    stoetter_velgoerenhed: bool = False
    indkomstaar: int = 2026
    # Fase 2-felter (bruges af kommende regler)
    betaler_boernebidrag: bool = False
    dobbelt_husfoerelse: bool = False
    rejsedage_med_overnatning: int = 0
    selvstaendig: bool = False
    har_aktietab: bool = False


@dataclass
class Skatteoplysninger:
    """Strukturerede felter parset fra årsopgørelse / forskudsopgørelse / R75.

    Feltnavne følger så vidt muligt skat.dk's rubrik-/feltnumre i kommentarer.
    Værdier er None hvis de ikke kunne parses (så motoren kan skelne 0 fra ukendt).
    """

    loen: Optional[float] = None  # rubrik 11
    am_bidrag_indeholdt: Optional[float] = None
    a_skat_indeholdt: Optional[float] = None
    renteudgifter: Optional[float] = None  # rubrik 41
    fagforening_a_kasse: Optional[float] = None  # rubrik 50/52
    befordringsfradrag: Optional[float] = None  # rubrik 51
    haandvaerkerfradrag: Optional[float] = None  # felt 460
    servicefradrag: Optional[float] = None  # felt 461
    gaver_almenvelgoerende: Optional[float] = None  # §8A, rubrik 55
    pensionsindbetaling: Optional[float] = None
    aktieindkomst: Optional[float] = None
    rejsefradrag: Optional[float] = None  # rubrik 53
    boernebidrag: Optional[float] = None  # betalt børnebidrag, rubrik 56
    dobbelt_husfoerelse_fradrag: Optional[float] = None
    aktietab_fremfoert: Optional[float] = None  # rubrik 67
    raw: dict = field(default_factory=dict)  # øvrige rå felter, felt-nr -> værdi

    @classmethod
    def from_dict(cls, data: dict) -> "Skatteoplysninger":
        """Byg fra en parset JSON-dict. Kendte felter (inkl. 'raw') udledes fra
        dataklassen selv, så nye felter automatisk understøttes; ukendte nøgler
        ignoreres."""
        kendte = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in kendte})


@dataclass
class Skatteberegning:
    """Resultat af skattemotoren for et givet indkomstår."""

    personlig_indkomst: float
    skattepligtig_indkomst: float
    am_bidrag: float
    bundskat: float
    kommuneskat: float
    kirkeskat: float
    mellemskat: float = 0.0
    topskat: float = 0.0
    top_topskat: float = 0.0
    beskaeftigelsesfradrag: float = 0.0
    jobfradrag: float = 0.0
    personfradrag_vaerdi: float = 0.0
    samlet_skat: float = 0.0
    detaljer: dict = field(default_factory=dict)


@dataclass
class TidligAarsopgoerelse:
    """Projiceret restskat/overskydende skat, udledt af en `Skatteberegning`
    og den indeholdte skat i `Skatteoplysninger`. Rent rapport-view — påvirker
    ikke selve skatteberegningen."""

    samlet_beregnet_skat: float
    indbetalt_skat: float
    difference: float  # samlet_beregnet_skat - indbetalt_skat
    er_restskat: bool
    beloeb: float  # abs(difference)
    tilstraekkeligt_grundlag: bool


@dataclass
class FradragsForslag:
    """Ét oversete-fradrag-forslag fundet af fradragstjekket."""

    navn: str
    felt: str  # skat.dk felt/rubrik-nummer til selvangivelse
    estimeret_fradrag: float  # kr. der kan trækkes fra
    estimeret_skattebesparelse: float  # ca. 26% eller marginalskat
    begrundelse: str
    saadan_indberetter_du: str
    sikkerhed: str = "mulig"  # "mulig" | "sandsynlig" | "kræver dokumentation"
    kilde: str = ""  # proveniens, fx "skat.dk – Befordringsfradrag (LL §9 C), rubrik 51"
    verificeret: bool = False  # sat af reviewer-agenten
