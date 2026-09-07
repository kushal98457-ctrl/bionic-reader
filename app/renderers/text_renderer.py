"""
Plain-text / terminal renderer.

Since a bare .txt file or a terminal can't render bold, emphasis is
conveyed with UPPERCASE on the emphasized portion — a common convention
for terminal "bionic-style" readers.
"""

from typing import List

from app.core.bionic_engine import BionicNode, BionicWord, PlainText


def render(nodes: List[BionicNode]) -> str:
    parts = []
    for node in nodes:
        if isinstance(node, BionicWord):
            parts.append(node.emphasized.upper() + node.remaining)
        elif isinstance(node, PlainText):
            parts.append(node.text)
    return "".join(parts)
