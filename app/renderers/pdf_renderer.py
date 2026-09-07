"""
PDF Renderer

Uses fpdf2 to lay out the bionic text with the emphasized portion of each
word in bold and the remainder in regular weight, wrapping naturally like
normal text.

Real-world text (books, PDFs pulled off the web, Word docs) is full of
"smart" typography that plain core PDF fonts (Helvetica/Times) can't
render at all: curly quotes ' ' " ", em/en dashes, ellipses, and
ligatures like "fi"/"fl". fpdf2's built-in core fonts only support
Latin-1, so that content used to raise FPDFUnicodeEncodingException and
fail the whole export. To fix this we embed a real Unicode TTF font
(DejaVu Sans, bundled in ./fonts/) that covers all of that plus accented
characters, instead of restricting input to what a 1985-era font handles.
"""

from pathlib import Path
from typing import List

from app.core.bionic_engine import BionicNode, BionicWord, PlainText

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_REGULAR = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"


def _configure_font(pdf) -> str:
    """Register the bundled Unicode font if available; fall back to a core
    font (with best-effort character substitution) if the font files are
    missing for some reason, so the app degrades rather than crashes."""
    if FONT_REGULAR.exists() and FONT_BOLD.exists():
        pdf.add_font("DejaVu", style="", fname=str(FONT_REGULAR))
        pdf.add_font("DejaVu", style="B", fname=str(FONT_BOLD))
        return "DejaVu"
    return "Helvetica"


def render_to_bytes(nodes: List[BionicNode], title: str = "Bionic Reader Output") -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    font_name = _configure_font(pdf)
    using_fallback = font_name == "Helvetica"
    pdf.set_font(font_name, size=13)

    def safe(text: str) -> str:
        # Only needed for the Helvetica fallback path, which can't render
        # non-Latin-1 characters at all — replace them rather than crash.
        if not using_fallback:
            return text
        return text.encode("latin-1", errors="replace").decode("latin-1")

    # fpdf2's write() lets us mix bold/regular segments on the same line
    # with automatic wrapping, which is exactly what bionic text needs.
    for node in nodes:
        if isinstance(node, BionicWord):
            if node.emphasized:
                pdf.set_font(font_name, style="B", size=13)
                pdf.write(8, safe(node.emphasized))
            if node.remaining:
                pdf.set_font(font_name, style="", size=13)
                pdf.write(8, safe(node.remaining))
        elif isinstance(node, PlainText):
            pdf.set_font(font_name, style="", size=13)
            text = safe(node.text)
            if "\n" in text:
                # Render each line break as an actual newline in the PDF
                segments = text.split("\n")
                for i, seg in enumerate(segments):
                    if seg:
                        pdf.write(8, seg)
                    if i < len(segments) - 1:
                        pdf.ln(8)
            else:
                pdf.write(8, text)

    return bytes(pdf.output())


def render_to_file(nodes: List[BionicNode], path: str, title: str = "Bionic Reader Output") -> None:
    data = render_to_bytes(nodes, title=title)
    with open(path, "wb") as f:
        f.write(data)
