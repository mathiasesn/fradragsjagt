from fradragsjagt.fradrag.koersel import beregn_koerselsfradrag


def test_kort_pendling_giver_intet_fradrag():
    # 10 km hver vej = 20 km/dag, under 24 km bundgrænse.
    forslag = beregn_koerselsfradrag(
        km_hver_vej=10, arbejdsdage=216, yderkommune=False, aarsindkomst=400_000
    )
    assert forslag.estimeret_fradrag == 0.0
    assert forslag.felt == "51"


def test_normal_pendler():
    # 20 km hver vej = 40 km/dag -> 16 fradragsberettigede km/dag over bundgrænsen.
    forslag = beregn_koerselsfradrag(
        km_hver_vej=20, arbejdsdage=216, yderkommune=False, aarsindkomst=500_000
    )
    forventet = 16 * 2.28 * 216
    assert forslag.estimeret_fradrag == round(forventet, 2)
    assert forslag.estimeret_skattebesparelse > 0
    assert forslag.sikkerhed == "sandsynlig"


def test_over_120_km_graense_bruger_lav_sats():
    # 80 km hver vej = 160 km/dag -> 136 km fradragsberettiget.
    # De første 96 km (120-24) til normal sats, resten (40 km) til lav sats.
    forslag = beregn_koerselsfradrag(
        km_hver_vej=80, arbejdsdage=216, yderkommune=False, aarsindkomst=500_000
    )
    forventet_dagligt = 96 * 2.28 + 40 * 1.14
    forventet = forventet_dagligt * 216
    assert forslag.estimeret_fradrag == round(forventet, 2)


def test_yderkommune_bruger_flad_hoej_sats_uanset_afstand():
    # 80 km hver vej i yderkommune -> hele 136 km til yderkommune-sats, ingen reduktion.
    forslag = beregn_koerselsfradrag(
        km_hver_vej=80, arbejdsdage=216, yderkommune=True, aarsindkomst=500_000
    )
    forventet = 136 * 2.53 * 216
    assert forslag.estimeret_fradrag == round(forventet, 2)


def test_ekstra_befordringsfradrag_for_lav_indkomst():
    forslag_lav = beregn_koerselsfradrag(
        km_hver_vej=20, arbejdsdage=216, yderkommune=False, aarsindkomst=300_000
    )
    forslag_hoej = beregn_koerselsfradrag(
        km_hver_vej=20, arbejdsdage=216, yderkommune=False, aarsindkomst=500_000
    )
    # Lav indkomst under 341.500 kr skal have fuldt ekstra befordringsfradrag oveni.
    assert forslag_lav.estimeret_fradrag > forslag_hoej.estimeret_fradrag


def test_ekstra_befordringsfradrag_udfases_over_top():
    forslag_over_top = beregn_koerselsfradrag(
        km_hver_vej=20, arbejdsdage=216, yderkommune=False, aarsindkomst=391_500
    )
    forslag_lav = beregn_koerselsfradrag(
        km_hver_vej=20, arbejdsdage=216, yderkommune=False, aarsindkomst=300_000
    )
    # Ved/over 391.500 kr er der intet ekstra fradrag, dermed lavere end lavindkomst-tilfældet.
    assert forslag_over_top.estimeret_fradrag < forslag_lav.estimeret_fradrag
