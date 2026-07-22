# fradragsjagt — backend

Python-koden bag `fradragsjagt`. Se projektets [rod-README](../README.md) for den fulde
introduktion, ansvarsfraskrivelse og brugervejledning.

## Struktur

```
backend/
  core/    # domænelogik: models, engine, rates_2026, parsing, profile, report, fradrag/
           #   + core/data/kommuneskat_2026.csv (pakkes med i wheel'en)
  cli/     # tyndt argparse-lag (cli.main:main) oven på core
  tests/   # pytest-suite (importerer core.*)
```

Et kommende `api/`-lag (FastAPI) kan tilføjes som en søskende-pakke ved siden af `cli/`,
og genbruger `core` på samme måde som CLI'en gør.

## Udvikling

Projektet bruger [uv](https://docs.astral.sh/uv/). Kør alle kommandoer fra `backend/`:

```bash
uv run --with pytest --with pypdf python -m pytest -q   # tests
uv run --with ruff ruff check core cli tests            # lint
uv run --with ruff ruff format core cli tests           # format
```

Installér CLI'en som konsol-script:

```bash
pip install -e ".[dev]"
fradragsjagt --version
```
