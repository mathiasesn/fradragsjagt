"""Kommandolinje-indgang for fradragsjagt.

Pipeline:  setup -> parse -> beregn -> fradragstjek -> rapport

Alle underkommandoer arbejder lokalt. Ingen netværkskald, ingen telemetri.
"""

from __future__ import annotations

import argparse
import sys

from core import DISCLAIMER, __version__


def _cmd_setup(args: argparse.Namespace) -> int:
    from core.profile import run_setup

    return run_setup(interactive=not args.non_interactive)


def _cmd_parse(args: argparse.Namespace) -> int:
    from core.parsing import parse_documents

    return parse_documents(paths=args.pdf, out=args.out)


def _cmd_beregn(args: argparse.Namespace) -> int:
    from core.engine import run_beregn

    return run_beregn(oplysninger_path=args.input)


def _cmd_fradragstjek(args: argparse.Namespace) -> int:
    from core.fradrag import run_fradragstjek

    return run_fradragstjek(oplysninger_path=args.input)


def _cmd_rapport(args: argparse.Namespace) -> int:
    from core.report import run_rapport

    return run_rapport(oplysninger_path=args.input, out=args.out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fradragsjagt",
        description="Gratis, lokal dansk fradrags- og skatteassistent.",
        epilog=DISCLAIMER,
    )
    p.add_argument("--version", action="version", version=f"fradragsjagt {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("setup", help="Opret lokal brugerprofil (kommune, pendling, ...).")
    sp.add_argument("--non-interactive", action="store_true", help="Brug defaults/flag i stedet for prompts.")
    sp.set_defaults(func=_cmd_setup)

    sp = sub.add_parser("parse", help="Parse årsopgørelse/forskudsopgørelse/R75 PDF'er til felter.")
    sp.add_argument("pdf", nargs="+", help="Sti(er) til PDF-fil(er) hentet fra TastSelv.")
    sp.add_argument("--out", default="skatteoplysninger.json", help="Output JSON-fil.")
    sp.set_defaults(func=_cmd_parse)

    sp = sub.add_parser("beregn", help="Beregn skat med 2026-satser.")
    sp.add_argument("--input", default="skatteoplysninger.json", help="Parsede skatteoplysninger (JSON).")
    sp.set_defaults(func=_cmd_beregn)

    sp = sub.add_parser("fradragstjek", help="Find sandsynlige oversete fradrag.")
    sp.add_argument("--input", default="skatteoplysninger.json", help="Parsede skatteoplysninger (JSON).")
    sp.set_defaults(func=_cmd_fradragstjek)

    sp = sub.add_parser("rapport", help="Saml alt til en samlet rapport.")
    sp.add_argument("--input", default="skatteoplysninger.json", help="Parsede skatteoplysninger (JSON).")
    sp.add_argument("--out", default="fradragsjagt-rapport.md", help="Output Markdown-fil.")
    sp.set_defaults(func=_cmd_rapport)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
