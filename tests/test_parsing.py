import pytest

from fradragsjagt.parsing import _parse_dkk, detect_dokumenttype, parse_skattetekst


@pytest.mark.parametrize(
    ("tekst", "forventet"),
    [
        ("1.234.567,89", 1234567.89),
        ("0,00", 0.0),
        ("-123,45", -123.45),
        ("1.000", 1000.0),
        ("42", 42.0),
        ("-1.234,00", -1234.0),
    ],
)
def test_parse_dkk(tekst, forventet):
    assert _parse_dkk(tekst) == pytest.approx(forventet)


def test_parse_skattetekst_aarsopgoerelse():
    tekst = """
    Årsopgørelse 2025

    Lønindkomst mv.               350.000,00 kr.
    AM-bidrag                      28.000,00 kr.
    A-skat                         85.000,00 kr.
    Renteudgifter                   12.500,50 kr.
    Befordring                       8.200,00 kr.
    Fagforening                      4.500,00 kr.
    """
    resultat = parse_skattetekst(tekst)

    assert resultat.loen == pytest.approx(350000.00)
    assert resultat.am_bidrag_indeholdt == pytest.approx(28000.00)
    assert resultat.a_skat_indeholdt == pytest.approx(85000.00)
    assert resultat.renteudgifter == pytest.approx(12500.50)
    assert resultat.befordringsfradrag == pytest.approx(8200.00)
    assert resultat.fagforening_a_kasse == pytest.approx(4500.00)

    # Ikke nævnt i teksten -> forbliver None
    assert resultat.haandvaerkerfradrag is None
    assert resultat.servicefradrag is None
    assert resultat.gaver_almenvelgoerende is None
    assert resultat.pensionsindbetaling is None
    assert resultat.aktieindkomst is None

    assert resultat.raw["dokumenttype"] == "aarsopgoerelse"


def test_parse_skattetekst_forskudsopgoerelse_gaver_og_service():
    tekst = """
    Forskudsopgørelse 2026

    Gaver til almenvelgørende foreninger    1.200,00 kr.
    Servicefradrag                            5.000,00 kr.
    Håndværkerfradrag                         3.300,00 kr.
    """
    resultat = parse_skattetekst(tekst)

    assert resultat.gaver_almenvelgoerende == pytest.approx(1200.00)
    assert resultat.servicefradrag == pytest.approx(5000.00)
    assert resultat.haandvaerkerfradrag == pytest.approx(3300.00)
    assert resultat.loen is None
    assert resultat.raw["dokumenttype"] == "forskudsopgoerelse"


def test_parse_skattetekst_masks_cpr():
    tekst = "Navn: Test Testesen\nCPR: 010190-1234\nLønindkomst mv.  100.000,00 kr."
    resultat = parse_skattetekst(tekst)

    assert resultat.raw.get("cpr") == "(CPR maskeret)"
    assert "010190-1234" not in str(resultat.raw)


def test_parse_skattetekst_absent_fields_stay_none():
    resultat = parse_skattetekst("Der er intet relevant indhold i denne tekst.")
    assert resultat.loen is None
    assert resultat.renteudgifter is None
    assert resultat.befordringsfradrag is None
    assert resultat.raw == {}


def test_detect_dokumenttype_r75():
    assert detect_dokumenttype("Dette er en R75 udskrift fra skat.dk") == "r75"


def test_detect_dokumenttype_ukendt():
    assert detect_dokumenttype("Ukendt dokument") == "ukendt"
