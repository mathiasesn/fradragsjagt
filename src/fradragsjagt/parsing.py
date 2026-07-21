"""PDF-parsing af årsopgørelse / forskudsopgørelse / R75 (`fradragsjagt parse`).

Alt sker lokalt. CPR-numre gemmes eller logges aldrig.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, fields

from .models import Skatteoplysninger

# Dansk CPR-mønster: DDMMYY-XXXX (maskeres, gemmes aldrig).
_CPR_RE = re.compile(r"\b\d{6}-?\d{4}\b")

# Dansk talformat: punktum som tusindeadskiller, komma som decimaltegn.
_DKK_RE = re.compile(r"-?[\d.]+(?:,\d+)?")


def _parse_dkk(s: str) -> float:
    """Konverter et dansk formateret beløb (fx '1.234.567,89' eller '-123,45') til float."""
    s = s.strip()
    negativ = s.startswith("-")
    s = s.lstrip("-").strip()
    s = s.replace(".", "").replace(",", ".")
    val = float(s)
    return -val if negativ else val


# Felt-label -> (attribut på Skatteoplysninger, rubrik/felt-nummer til raw dict)
_FELT_MOENSTRE: list[tuple[str, str, str]] = [
    (r"L[øo]nindkomst(?:\s*mv\.?)?[^\d\-]*?(-?[\d.]+,\d{2})\s*(?:kr\.?)?", "loen", "11"),
    (r"AM-bidrag[^\d\-]*?(-?[\d.]+,\d{2})", "am_bidrag_indeholdt", "am_bidrag"),
    (r"A-skat[^\d\-]*?(-?[\d.]+,\d{2})", "a_skat_indeholdt", "a_skat"),
    (r"Renteudgifter[^\d\-]*?(-?[\d.]+,\d{2})", "renteudgifter", "41"),
    (
        r"(?:Fagforening|Kontingent til fagforening)[^\d\-]*?(-?[\d.]+,\d{2})",
        "fagforening_a_kasse",
        "50",
    ),
    (r"Befordring(?:sfradrag)?[^\d\-]*?(-?[\d.]+,\d{2})", "befordringsfradrag", "51"),
    (r"H[åa]ndv[æe]rkerfradrag[^\d\-]*?(-?[\d.]+,\d{2})", "haandvaerkerfradrag", "460"),
    (r"Servicefradrag[^\d\-]*?(-?[\d.]+,\d{2})", "servicefradrag", "461"),
    (
        r"Gaver til (?:almenvelg[øo]rende|godk[eæ]ndte foreninger)[^\d\-]*?(-?[\d.]+,\d{2})",
        "gaver_almenvelgoerende",
        "55",
    ),
    (r"Pensionsindbetaling[^\d\-]*?(-?[\d.]+,\d{2})", "pensionsindbetaling", "pension"),
    (r"Aktieindkomst[^\d\-]*?(-?[\d.]+,\d{2})", "aktieindkomst", "aktie"),
]

_DOKUMENTTYPE_RE = {
    "aarsopgoerelse": re.compile(r"[ÅA]rsopg[øo]relse", re.IGNORECASE),
    "forskudsopgoerelse": re.compile(r"Forskudsopg[øo]relse", re.IGNORECASE),
    "r75": re.compile(r"\bR75\b"),
}


def detect_dokumenttype(text: str) -> str:
    for navn, mønster in _DOKUMENTTYPE_RE.items():
        if mønster.search(text):
            return navn
    return "ukendt"


def parse_skattetekst(text: str) -> Skatteoplysninger:
    """Ren, testbar parser: udtræk skatteoplysninger fra tekst.

    CPR-numre maskeres og gemmes ikke.
    """
    raw: dict = {}
    if _CPR_RE.search(text):
        raw["cpr"] = "(CPR maskeret)"

    værdier: dict[str, float] = {}
    for mønster, attribut, feltnr in _FELT_MOENSTRE:
        m = re.search(mønster, text)
        if m:
            try:
                værdien = _parse_dkk(m.group(1))
            except ValueError:
                continue
            værdier[attribut] = værdien
            raw[feltnr] = værdien

    dokumenttype = detect_dokumenttype(text)
    if dokumenttype != "ukendt":
        raw["dokumenttype"] = dokumenttype

    return Skatteoplysninger(raw=raw, **værdier)


def _merge(base: Skatteoplysninger, ny: Skatteoplysninger) -> Skatteoplysninger:
    """Flet ny ind i base; ikke-None-felter i ny overskriver base."""
    for felt in fields(Skatteoplysninger):
        if felt.name == "raw":
            continue
        ny_værdi = getattr(ny, felt.name)
        if ny_værdi is not None:
            setattr(base, felt.name, ny_værdi)
    base.raw.update(ny.raw)
    return base


def parse_documents(paths: list[str], out: str) -> int:
    """Parse en eller flere PDF'er, flet felter, og gem som JSON."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Fejl: pypdf er ikke installeret. Kør 'pip install pypdf'.")
        return 1

    samlet = Skatteoplysninger()
    fundet_noget = False

    for path in paths:
        try:
            reader = PdfReader(path)
        except FileNotFoundError:
            print(f"Fejl: filen '{path}' blev ikke fundet.")
            return 1
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Fejl: kunne ikke læse '{path}': {exc}")
            return 1

        tekst = "\n".join(page.extract_text() or "" for page in reader.pages)
        oplysninger = parse_skattetekst(tekst)
        samlet = _merge(samlet, oplysninger)
        fundet_noget = True

    if not fundet_noget:
        print("Ingen PDF'er blev behandlet.")
        return 1

    data = asdict(samlet)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Skatteoplysninger gemt i {out}.\n")
    print("Fundne felter:")
    for felt in fields(Skatteoplysninger):
        if felt.name == "raw":
            continue
        værdi = getattr(samlet, felt.name)
        status = f"{værdi} kr." if værdi is not None else "ikke fundet"
        print(f"  - {felt.name}: {status}")

    return 0
