# Open source dansk skatteassistent som Claude Code-agent: Feasibility og go-to-market

## TL;DR
- **Teknisk realistisk, men IKKE via automatiseret MitID-login eller API'er til borgerens egne data.** Den eneste lovlige og holdbare arkitektur for et open source-CLI er "bring your own data": brugeren logger selv ind på skat.dk med MitID, henter sin årsopgørelse/forskudsopgørelse/R75 som PDF, og agenten parser filerne lokalt, beregner skat og finder oversete fradrag. Der findes ingen offentlig API til privatpersoners egne skattedata — kun DUPLA/R75-webservices for myndigheder og virksomheder med lovhjemmel og VOCES-certifikat.
- **Markedsvinduet er stærkt.** Skatteguiden (forsiden: "Gør som over 1.000.000 danskere") og TaxHelper tager betaling (TaxHelper: "maks. 30% af den skattebesparelse, du får"; Skatteguiden: 20%/10%/gratis afhængigt af medlemskab, plus abonnement på 79 kr./md) for noget en borger kan gøre gratis på skat.dk — og begge er blevet kritiseret i dansk presse for datahåndtering. Et gratis, privacy-first, lokalt open source-alternativ har en skarp positioneringsvinkel.
- **Lancér omkring årsopgørelsen i marts** (max opmærksomhed), med en teaser i november ifm. forskudsopgørelsen. Følg ai-job-search-mønsteret: MIT-licens, ét skarpt LinkedIn-opslag på dansk, tydelig "kører på din egen maskine"-fortælling, og en klar ansvarsfraskrivelse om at det ikke er autoriseret skatterådgivning.

## Key Findings

### Teknisk feasibility
1. **Ingen borger-API.** Skatteforvaltningens datadeling (DUPLA / R75 "KontrolOplysninger" / eIndkomst) er kun for myndigheder og virksomheder "med hjemmel i relevant lovgivning", som opnår adgang via ansøgning til dataudstilling@ufst.dk, oprettelse som aftalepart, VOCES-certifikat og roller i TastSelv Erhverv. Dette er ikke tilgængeligt for et open source-værktøj til privatpersoner. R75-webservicen (SF1570) udstiller detaljerede indkomst- og kapitaloplysninger til *anvendersystemer* — ikke til borgeren selv.
2. **Rådgiveradgang er den eneste "officielle" tredjepartsvej — og den er problematisk.** Skatteguiden/TaxHelper bruger skat.dk's autorisationsordning ("angiv rådgiver/revisor" via formular 02.052), hvor brugeren giver virksomheden adgang til sine skatteoplysninger. Det kræver, at man er en registreret virksomhed/rådgiver, og det er præcis den model, DR og TV2 har kritiseret på privacy. Et open source-CLI bør IKKE efterligne dette.
3. **MitID kan ikke lovligt automatiseres.** MitID kræver en godkendt broker (12 godkendte brokere ifølge Digitaliseringsstyrelsen), typisk med opstartsbetaling (op mod 50.000 kr.) og månedligt abonnement; det er til at tilbyde login på egne tjenester, ikke til at automatisere login på tredjeparts sites som skat.dk. Programmatisk/scriptet MitID-login mod skat.dk er i strid med vilkår og teknisk spærret.
4. **PDF/eksport-vejen virker.** Borgere kan hente årsopgørelse, forskudsopgørelse og R75/skatteoplysninger som PDF fra TastSelv (Skatteoplysninger → udskriv → gem som PDF). R75 ("skattemappen") indeholder løn, honorarer, renteudgifter, restgæld, aktier, biloplysninger m.m. — netop de data en fradragstjek kræver. Dette er den rene, lovlige input-kanal. R75-data for et givet indkomstår åbnes samtidig med årsopgørelsen midt marts.
5. **Skattemotor er velafgrænset og allerede delvist open source.** Der findes eksisterende GitHub-projekter at lære af/genbruge: **lonklar.dk** (fuld 2026-model med bundskat, kommuneskat, AM-bidrag, personfradrag, beskæftigelsesfradrag, ATP, kirkeskat, pension, befordringsfradrag, fagforening — alle 98 kommuner, open source), **krisztin/danskat** og **DREAMmodel/Skatteberegning**. Bemærk: skat.dk selv har en officiel kørselsfradragsberegner, der kan overføre fradraget direkte til forskuds-/årsopgørelsen.

### 2026-skattetal (til beregningsmotoren)
- **AM-bidrag:** 8%. **Personfradrag:** 54.100 kr. **Bundskat:** 12,01% (sat ned fra 12,22% i 2025).
- **Nyt 2026-system** (erstatter den gamle topskat): Mellemskat 7,5% (personlig indkomst 641.200–777.900 kr. efter AM-bidrag), topskat 7,5% (777.900–2.592.700 kr.), top-topskat 5% (over 2.592.700 kr.). Skatteloft 52,07%. Reformen giver lavere marginalskat for de fleste, men marginalskatten stiger fra 56% til 61% for indkomster over ca. 2.818.000 kr. før AM-bidrag.
- **Kommuneskat:** landsgennemsnit ca. 25,07%; spænder fra ca. 23,4% (fx Vejle) til over 26,3%. **Kirkeskat:** ca. 0,68% (kun folkekirkemedlemmer).
- **Beskæftigelsesfradrag:** 12,75%, maks. 63.300 kr. **Jobfradrag:** 4,50% af indkomst over 235.200 kr., maks. 3.100 kr.

### Fradrag at tjekke (lønmodtager-fokus)
- **Kørselsfradrag/befordringsfradrag 2026:** 2,28 kr./km for 25–120 km, 1,14 kr./km over 120 km; yderkommuner 2,53 kr./km. Kræver over 24 km samlet (over 12 km hver vej). Indberettes IKKE automatisk — den hyppigst oversete post (over 1,1 mio. danskere indtaster den; samlet fradrag nær 24 mia. kr.). **Ekstra befordringsfradrag** for lavere indkomster: skat.dk skriver "Du kan få et ekstra kørselsfradrag, hvis du tjener mindre end 391.500 kr. (før am-bidrag er fratrukket) i 2026 ... Du kan højst få fradrag for 30.800 kr. i 2026 ... Fradraget nedsættes gradvist for indkomster over 341.500 kr. til 391.500 kr." Værdien af fradraget er ifølge Skattestyrelsen "cirka 26 procent" — dvs. et fradrag på 5.000 kr. sparer ca. 1.300 kr. i skat.
- **Håndværkerfradrag:** genindført som "grønt" fradrag 2025–2027, 9.000 kr./person i 2026 (kun energi/klima-arbejde). **Servicefradrag:** 18.300 kr./person i 2026 (rengøring, havearbejde, børnepasning, hårde hvidevare-reparation). Værdi ca. 26%. Indberettes i felt 460 (håndværk) / 461 (service).
- **Gaver/donationer §8A:** maks. 20.000 kr. i 2026 (19.000 kr. i 2025), værdi ca. 26%. Kan ikke overføres mellem ægtefæller.
- **Øvrige:** fagforening/A-kasse, renteudgifter, rejsefradrag, dobbelt husførelse, hjemmearbejde, aktieindkomst (27%/42%), ægtefælleoverførsel af uudnyttet personfradrag.

### Deadlines (skattekalender)
- **Forskudsopgørelse:** klar november; kan justeres løbende.
- **Årsopgørelse:** klar midt marts.
- **Overskydende skat:** udbetales til NemKonto fra ca. 24. april (medio april).
- **Rettefrist:** normalt 1. maj (for 2025 ekstraordinært forlænget til 20. maj 2026). Selvstændige: 1. juli. Efter fristen kan ændringer stadig ske via genoptagelse, men glemte fradrag forælder efter 1. maj i det fjerde år.

### Konkurrenter og positionering
- **Skatteguiden:** stiftet 2017 af Nikolai T. G. Høgskilde; støtte fra Vækstfonden/Innovationsfonden; investering fra Jesper Buch (Løvens Hule, 1,5 mio. kr. for 12,5%). Forsiden hævder "over 1.000.000 danskere" (Facebook-milepæl: "Skatteguiden har nu 1.000.000 brugere registreret") — dette er et kumulativt registreringstal, ikke aktive brugere. Plus-medlemskab 79 kr./md (årsabonnement = 10 måneders pris); indberetning af glemte fradrag koster 20%/10%/gratis afhængigt af medlemskab. Underskud på flere mio. kr. i både 2023 og 2024. I 2021 downloadede 200.000 danskere appen på en uge (DR/TV2), og 6.000 krævede deres data slettet.
- **TaxHelper:** stiftet 2020 af Aske Buemann m.fl.; fee er "no cure, no pay": TaxHelper.dk skriver "Servicen koster maks. 30% af den skattebesparelse, du får. Dvs. hvis du får 1.000 kr. tilbage i skat, så kan du maks. betale 300 kr." (var 10% i 2021). Gns. tilbagebetaling markedsføres som 2.704 kr. Kritiseret på Trustpilot for at tage 30% af differencen selv når de reducerer et skattesmæk ("det virker fuldstændig sindssygt").
- **Kritik-vinklen:** DR (Penge) kørte historien "Her er, hvorfor eksperter i databeskyttelse aldrig kunne finde på at bruge populær skatte-app" med citatet "Det er uigennemsigtigt, hvor længe Skatteguiden gemmer dine data, og hvem de deler oplysningerne med, lyder kritikken." TV2's kilde (DKCERT) sagde tjenesten fik hans "alarmklokker til at ringe." SKAT tilbyder selv gratis fradragsvejledning.

### Traction-mønster (ai-job-search / dansk open source)
- **ai-job-search** (Mads Lorentzen, PhD-geofysiker der mistede sit job og byggede rammeværket over tre måneder) ramte #1 på GitHub Trending (alle sprog) 7. juli 2026 og nåede "20.000+ GitHub stars" (LinkedIn; AgentConn rapporterede "19.5K stars and 5.6K forks" ved trending-tidspunktet). Opskriften: MIT-licens, "kører på din egen maskine", drafter-reviewer agent-mønster, ét stærkt LinkedIn-opslag med en personlig historie ("It got me hired. Now it's yours."), og en eksplicit note om at projektet er uafhængigt og "not affiliated with ... Anthropic."
- **Dansk AI/open source** får dækning i Version2/Ingeniøren; **syv.ai** (DanskGPT — "allerede i brug hos 170.000+ ansatte", Hviske, Plapre) har opbygget rækkevidde på fortællingen "dansk, lokal, GDPR-venlig, ingen data forlader maskinen." Dette er præcis den værdiprofil en skatteassistent bør spejle.

## Details

### Anbefalet MVP-arkitektur
En Claude Code / CLI-agent (fork-venlig, MIT-licens) med denne pipeline:

1. **`/setup`** — brugeren udfylder en lokal profil (kommune, kirkeskattemedlem, civilstand, pendlerafstand, fagforening, boligejer, etc.).
2. **Manuel dataeksport** — guide brugeren til at hente årsopgørelse + forskudsopgørelse + R75 som PDF fra TastSelv. Ingen login-automatisering.
3. **`/parse`** — lokal PDF-parsing af de tre dokumenter til strukturerede felter (rubrik/felt-numre).
4. **`/beregn`** — ren skatteberegningsmotor (Python) med 2026-satser og alle 98 kommuner; genbrug logik fra lonklar.dk.
5. **`/fradragstjek`** — regelbaseret gennemgang af oversete fradrag (drafter-reviewer-mønster: én agent foreslår, én verificerer mod satser/betingelser), med kørselsfradrag som flagskib.
6. **Output** — en rapport med "her er dine sandsynlige oversete fradrag og hvordan du selv indberetter dem på skat.dk (felt X)". **Værktøjet indberetter IKKE for brugeren** — det bevarer den juridiske og etiske adskillelse fra betalingstjenesterne.

**Privacy-design:** Al databehandling lokalt. Hvis Claude API bruges, dokumentér ZDR/7-dages retention og anbefal, at CPR maskeres inden data sendes til modellen. Aldrig cloud-lagring af skattedata. Ingen telemetri. Anbefal at holde repo/data privat, som ai-job-search gør for CV'er.

### Juridiske guardrails
- **Skatterådgivning er ikke en beskyttet titel** for privatpersoner, men **rådgiveransvar** findes: medvirken til urigtige oplysningsskemaer (fx forsætligt eller groft uagtsomt at udfærdige et urigtigt oplysningsskema) kan udløse strafansvar efter skattekontrolloven/straffeloven. Værktøjet skal levere generel information, ikke bindende rådgivning, og brugeren skal selv indberette og bære ansvaret. Brug en disclaimer i stil med skat.dk's egen: "information og generelle råd — ikke individuel skatterådgivning."
- **GDPR:** CPR og skattedata er (særligt) følsomme. Lokal-only-processing minimerer eksponering og gør det til brugeren, ikke projektet, der er dataansvarlig. Klar ansvarsfraskrivelse à la ai-job-search ("uafhængigt open source-projekt, ikke tilknyttet Anthropic eller Skattestyrelsen").
- **Anthropic/Claude:** Claude API har 7-dages retention (standard fra 15. sept. 2025) og ZDR for enterprise; consumer-konti (Free/Pro/Max) har 30-dages retention. Anbefal API-brug med opt-out af træning, og fremhæv i dokumentationen at data kan holdes lokalt eller sendes maskeret.

### Lanceringsplan (bundet til skattekalenderen)
- **November (forskudsopgørelse for 2026 åbner):** soft launch / teaser — "tjek din forskudsopgørelse med det nye 2026-skattesystem (mellemskat/topskat) og undgå skattesmæk." Byg tidlige stjerner og feedback.
- **Midt marts (årsopgørelsen frigives + R75 åbnes):** hovedlancering. Maksimal opmærksomhed i medierne og hos borgerne. LinkedIn-opslag på dansk med personlig historie + pitch til Version2/Ingeniøren og evt. DR Penge (privacy-vinklen spiller godt ind i deres tidligere dækning).
- **Frem til 20. maj / 1. maj (rettefrist):** vedligehold momentum; "sidste chance for at rette din årsopgørelse — gratis, på din egen maskine."

### Navngivning/branding
Følg dansk devtool-mønster: kort, dansk, selvforklarende. Kandidater i stil med "skattehjælper", "fradragstjek", "aarsopgoerelse-agent" eller et ordspil (jf. syv.ai's "Hviske"/"Plapre"). Det virale element er ikke navnet men **fortællingen**: "gratis + open source + kører lokalt + tager ikke en andel af din tilbagebetaling."

## Recommendations
1. **Byg "bring your own PDF"-MVP'en først** med kørselsfradrag som flagskibsfunktion — det er den mest oversete, højest-værdi post, indberettes ikke automatisk, og er præcis den post TaxHelper/Skatteguiden markedsfører sig på.
2. **Genbrug lonklar.dk's 2026-skattemotor** (tjek licens/kredit) fremfor at bygge beregningen fra bunden; valider mod skat.dk's officielle beregnere.
3. **Positionér skarpt mod betalingstjenester:** "De tager op til 30% af din tilbagebetaling — her er et gratis, open source-alternativ, der kører på din egen maskine og aldrig sender dine data væk." Denne vinkel udnytter både pris- og privacy-kritikken af Skatteguiden/TaxHelper.
4. **Lancér midt marts** med ét stærkt LinkedIn-opslag og en ærlig personlig historie (jf. Mads Lorentzen). Undgå overdrevne løfter — ai-job-search vandt netop på "ærligt værktøj, ingen garanti."
5. **Preempt kritik proaktivt:** lokal-only, ingen andel af refusion, tydelig disclaimer om at det ikke er autoriseret rådgivning, ingen MitID-automatisering, og en synlig FAQ om datahåndtering. Dette er dit stærkeste forsvar mod den presse-vinkel, der ramte konkurrenterne.

**Tærskler der ændrer anbefalingen:**
- Hvis Skatteforvaltningen udgiver en egentlig borger-API ("adgang til egne data" for privatpersoner), skift til direkte, samtykke-baseret integration.
- Hvis MitID-broker-reglerne åbner for personlig agent/on-device-brug, genovervej automatiseret hentning.
- Hvis Skatteguiden/TaxHelper skifter til rene abonnements-flatrates og forlader %-modellen, mister "de tager en andel"-vinklen kraft — skift da til privacy/ejerskabs-vinklen alene.

## Caveats
- **Præcise priser** for Skatteguidens Standard- og Studerende-tiers (og alle årsabonnementspriser) er ikke bekræftet i tekstkilder — kun Plus = 79 kr./md og reglen "betal 10 måneder for et år". Skatteguidens indberetningsgebyr (20%/10%/gratis) og TaxHelpers fee (maks. 30%) må ikke forveksles; "maks. 20%" tilhører Skatteguiden, ikke TaxHelper.
- **Brugertal er marketingtal** og varierer mellem sider og datoer (1.000.000 vs. 950.000 vs. tidligere ~800.000); behandl "over 1 mio." som kumulative registreringer, ikke aktive betalende brugere.
- **GitHub-stjernetal for ai-job-search** varierer efter kilde og dato (19,5K ved trending 7. juli 2026; 20.000+ ifølge Lorentzens LinkedIn; enkelte aggregatorer nævner højere tal senere) — brug ~20.000+ som robust nedre grænse.
- **2026-skattesatserne** er bekræftede på tværs af flere kilder (skat.dk, Nordea, Nykredit, Martinsen), men enkelte fradragsudvidelser (fx udvidet beskæftigelsesfradrag for seniorer) afventede endelig lovvedtagelse forventet april 2026 og bør verificeres mod skat.dk/hjaelp/satser før release.
- En specifik Version2- eller Forbrugerrådet Tænk-artikel med den eksplicitte "betal for noget gratis"-vinkel blev ikke lokaliseret; den dokumenterede presse-kritik er primært DR's og TV2's privacy-dækning plus det underliggende faktum, at basal indberetning er gratis på skat.dk.