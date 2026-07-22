"""Regel-register-pakke: auto-discovering regler for oversete fradrag."""

from __future__ import annotations

from .registry import REGLER, find_oversete_fradrag, fradragsregel

__all__ = ["REGLER", "find_oversete_fradrag", "fradragsregel"]
