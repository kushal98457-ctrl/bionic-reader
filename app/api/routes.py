"""
API routes.

    POST /convert        -> JSON in, JSON out (HTML fragment)  [text only]
    POST /convert/file    -> multipart upload (.txt/.pdf/.docx), returns HTML
    POST /convert/export  -> multipart upload OR text, returns a file
                              (txt / html / pdf) as an attachment

The routes are intentionally thin: extract -> engine.process_text -> render.
"""

import io
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.core.bionic_engine import process_text
from app.core.config import BionicConfig
from app.extractors import docx_extractor, pdf_extractor, text_extractor
from app.renderers import html_renderer, pdf_renderer, text_renderer

router = APIRouter()


class ConvertRequest(BaseModel):
    text: str
    strength: float = Field(default=0.40, gt=0.0, le=1.0)


class ConvertResponse(BaseModel):
    html: str


@router.post("/convert", response_model=ConvertResponse)
def convert_text(payload: ConvertRequest) -> ConvertResponse:
    """Convert raw pasted text into bionic HTML. Matches the spec's example API."""
    config = BionicConfig.from_ratio(payload.strength)
    nodes = process_text(payload.text, config)
    return ConvertResponse(html=html_renderer.render(nodes))


def _extract_upload(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    data = file.file.read()

    if filename.endswith(".pdf"):
        return pdf_extractor.extract_from_bytes(data)
    if filename.endswith(".docx"):
        return docx_extractor.extract_from_bytes(data)
    if filename.endswith(".txt") or filename.endswith(".md"):
        return text_extractor.extract_text(data.decode("utf-8", errors="replace"))

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported file type for '{file.filename}'. Use .txt, .pdf, or .docx.",
    )


@router.post("/convert/file", response_model=ConvertResponse)
def convert_file(
    file: UploadFile = File(...),
    strength: float = Form(default=0.40),
) -> ConvertResponse:
    """Convert an uploaded .txt/.pdf/.docx file into bionic HTML."""
    raw_text = _extract_upload(file)
    config = BionicConfig.from_ratio(strength)
    nodes = process_text(raw_text, config)
    return ConvertResponse(html=html_renderer.render(nodes))


@router.post("/convert/export")
def convert_export(
    format: str = Form(..., description="One of: txt, html, pdf"),
    strength: float = Form(default=0.40),
    text: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
):
    """
    Export bionic-formatted output as a downloadable file.
    Accepts either raw `text` OR an uploaded `file` (not both).
    """
    if format not in ("txt", "html", "pdf"):
        raise HTTPException(status_code=400, detail="format must be one of: txt, html, pdf")

    if file is not None:
        raw_text = _extract_upload(file)
    elif text is not None:
        raw_text = text
    else:
        raise HTTPException(status_code=400, detail="Provide either `text` or `file`.")

    config = BionicConfig.from_ratio(strength)
    nodes = process_text(raw_text, config)

    if format == "txt":
        content = text_renderer.render(nodes).encode("utf-8")
        media_type = "text/plain"
        filename = "bionic_output.txt"
    elif format == "html":
        content = html_renderer.render_full_page(nodes).encode("utf-8")
        media_type = "text/html"
        filename = "bionic_output.html"
    else:  # pdf
        content = pdf_renderer.render_to_bytes(nodes)
        media_type = "application/pdf"
        filename = "bionic_output.pdf"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
