"""
HTML Renderer

Turns the engine's structured BionicNode list into HTML, escaping user
content properly so arbitrary input text can't break out of the markup.
"""

import html as html_lib
from typing import List

from app.core.bionic_engine import BionicNode, BionicWord, PlainText


def render(nodes: List[BionicNode]) -> str:
    parts = []
    for node in nodes:
        if isinstance(node, BionicWord):
            emphasized = html_lib.escape(node.emphasized)
            remaining = html_lib.escape(node.remaining)
            if emphasized:
                parts.append(f"<strong>{emphasized}</strong>{remaining}")
            else:
                parts.append(remaining)
        elif isinstance(node, PlainText):
            # Preserve newlines as <br> for readability in HTML output
            escaped = html_lib.escape(node.text)
            escaped = escaped.replace("\n", "<br>\n")
            parts.append(escaped)
    return "".join(parts)


def render_full_page(nodes: List[BionicNode], title: str = "Bionic Reader Output") -> str:
    """Wrap the rendered fragment in a minimal standalone HTML document."""
    body = render(nodes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html_lib.escape(title)}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 700px; margin: 40px auto;
          line-height: 1.7; font-size: 18px; color: #222; padding: 0 20px; }}
  strong {{ font-weight: 700; color: #000; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
