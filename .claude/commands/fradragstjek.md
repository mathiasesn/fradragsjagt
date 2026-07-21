---
description: Kør den deterministiske skatteberegning og find sandsynlige oversete fradrag, verificeret af drafter-reviewer-skillet.
---

# /fradragstjek

Kør den deterministiske Python-kerne, og brug derefter drafter-reviewer-skillet
til at sanity-checke fundene, før de præsenteres for brugeren.

## Trin

1. Kør skatteberegningen:
   ```bash
   fradragsjagt beregn --input skatteoplysninger.json
   ```

2. Kør det deterministiske fradragstjek:
   ```bash
   fradragsjagt fradragstjek --input skatteoplysninger.json
   ```

3. Brug skillet `fradrag-drafter-reviewer` til at:
   - Maskere CPR og andre direkte identifikatorer, hvis noget rå data skal ses igennem.
   - Lade DRAFTER-rollen foreslå yderligere kandidat-fradrag ud fra brugerens
     parsede data og profil (`skatteoplysninger.json`, `profil.json`).
   - Lade REVIEWER-rollen verificere hvert forslag mod 2026-satser og -grænser
     (se `.claude/skills/fradrag-drafter-reviewer/reviewer-checklist.md`),
     og afvise alt der ikke kan understøttes af tallene i data.

4. Kør den samlede rapport, som inkluderer både det deterministiske
   fradragstjek og de verificerede forslag:
   ```bash
   fradragsjagt rapport --input skatteoplysninger.json --out fradragsjagt-rapport.md
   ```

5. Præsenter rapporten for brugeren. Nævn tydeligt hvilke forslag der er
   `verificeret: ja` vs. `nej`, og mind om at fradragsjagt aldrig indberetter
   på brugerens vegne — brugeren skal selv indtaste beløbene på skat.dk.
