# Bionic Reader

Bolds the leading portion of each word so your eyes can skim the rest by
momentum — a "bionic reading" aid, built end-to-end per the staged plan:
core algorithm → text processing → web UI → file support → export.

## Architecture

```
INPUT (text / pdf / docx)
    -> Text Extractor      (app/extractors/)
    -> Tokenizer            (app/core/tokenizer.py)
    -> Rules                (app/core/rules.py)      # how many chars to bold
    -> Bionic Engine        (app/core/bionic_engine.py)  # renderer-agnostic
    -> Renderer             (app/renderers/)          # html / text / pdf
    -> OUTPUT
```

The engine never emits HTML directly — it produces `BionicWord(original,
emphasized, remaining)` objects. Renderers decide how that becomes
`<strong>` tags, uppercase terminal text, or bold PDF runs. This is what
lets new output formats get added without touching the algorithm.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/** — paste text or drop in a `.txt` / `.pdf`
/ `.docx` file, adjust the strength slider, hit Convert, and export as
TXT / HTML / PDF.

## Run the tests

```bash
pytest
```

## API

**POST /convert** — JSON in, JSON out (matches the original spec example)

```json
// request
{ "text": "Artificial intelligence helps students.", "strength": 0.4 }

// response
{ "html": "<strong>Art</strong>ificial <strong>int</strong>elligence helps students." }
```

**POST /convert/file** — multipart form: `file` (.txt/.pdf/.docx), `strength`
→ same `{ "html": ... }` response.

**POST /convert/export** — multipart form: `format` (txt/html/pdf),
`strength`, and either `text` or `file` → returns the converted file as a
download.

## Configuring the algorithm

`app/core/config.py` defines `BionicConfig`:

| Field | Purpose |
|---|---|
| `ratio` | fraction of each word's letters to bold (0.30 / 0.40 / 0.50 / 0.60 presets = LOW/MEDIUM/HIGH/MAX) |
| `min_word_length` | words shorter than this skip the ratio formula |
| `short_word_bold_chars` | chars to bold on short words (e.g. "a", "is") |
| `max_bold_chars` | ceiling so long words don't get half-bolded |
| `skip_numbers` / `skip_urls` | leave numbers/URLs untouched |

## Project layout

```
bionic-reader/
├── app/
│   ├── core/            # tokenizer, rules, config, the engine itself
│   ├── extractors/       # text / pdf / docx -> raw text
│   ├── renderers/        # bionic nodes -> html / text / pdf
│   ├── api/routes.py     # FastAPI endpoints
│   └── main.py           # app entrypoint, serves frontend/
├── frontend/             # vanilla HTML/CSS/JS UI (no build step)
├── tests/
└── requirements.txt
```

## Roadmap ideas (not built yet)

- Preserve DOCX styling (headings, bold-in-source) through to output
- EPUB / webpage input
- Per-paragraph reading-speed stats
- Browser extension for reading any webpage bionically
