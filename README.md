<div align="center">

# Bionic Reader

**Read faster by letting your eyes finish the word for you.**

Bionic Reader bolds the leading fragment of each word — your brain fills in
the rest from memory, the way it already does with familiar words. The
result is a document your eyes can skim by momentum instead of reading
letter by letter.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-19%20passing-brightgreen)](#running-the-tests)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](#license)

</div>

---

## See it in action

<table>
<tr>
<th align="left" width="50%">Unbionified</th>
<th align="left" width="50%">Bionified</th>
</tr>
<tr>
<td valign="top">

You're currently reading the typical, unbionified text. So, your experience is sort of like driving a sedan—not that there's anything wrong with it. It's reliable and it's worked forever, but it's slow.

</td>
<td valign="top">

**You'**re **curr**ently **rea**ding **th**e **typ**ical, **unbio**nified **te**xt. **So**, **yo**ur **expe**rience **i**s **so**rt **o**f **li**ke **dri**ving **a** **se**dan—**no**t **th**at **the**re's **anyt**hing **wr**ong **wi**th **i**t. **It'**s **reli**able **an**d **it**'s **wor**ked **for**ever, **bu**t **it**'s **sl**ow.

</td>
</tr>
</table>

*(This is real output from the app's default settings — not a mockup.)*

Notice the first word after every period — **You'**re, **So**, **It'**s — gets
slightly stronger emphasis than a mid-sentence word of the same length. That's
intentional: attention naturally drifts right after a full stop or a new
sentence, so that word gets a bit more of an anchor. See
[Sentence-position weighting](#sentence-position-weighting) below.

---

## Features

- 📄 **Multiple input formats** — paste text directly, or upload `.txt`, `.pdf`, or `.docx`
- 🎚️ **Adjustable strength** — LOW / MEDIUM / HIGH / MAX presets, or a custom slider
- 🧠 **Sentence-position weighting** — the first word of each sentence/paragraph gets extra emphasis, where attention typically lapses first
- 📤 **Export anywhere** — download as `.txt`, `.html`, or a real `.pdf` with embedded Unicode fonts (handles smart quotes, em-dashes, accented characters — no crashes on real-world text)
- 📋 **Copy to clipboard** — preserves bold formatting when pasted into Word/Docs
- 🔗 **URL & number aware** — links and numbers are never mangled by the algorithm
- 🏗️ **Renderer-agnostic core** — the algorithm produces structured data, not HTML; adding a new output format never touches the emphasis logic
- ✅ **19 unit tests** covering the tokenizer, rules, engine, and extractors

---

## Quick start

```bash
git clone https://github.com/kushal98457-ctrl/bionic-reader.git
cd bionic-reader

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser. Paste text or drop a file,
adjust the strength slider, hit **Convert**, then export or copy the result.

---

## How it works

```
INPUT (text / pdf / docx)
    │
    ▼
Text Extractor        app/extractors/          plain text out, regardless of input format
    │
    ▼
Tokenizer              app/core/tokenizer.py    splits into words / punctuation / numbers / URLs,
    │                                           losslessly (rejoining tokens reproduces the input exactly)
    ▼
Rules                  app/core/rules.py        decides how many characters of each word to bold
    │
    ▼
Bionic Engine          app/core/bionic_engine.py   produces BionicWord(original, emphasized, remaining)
    │                                              — knows nothing about HTML, PDF, or any output format
    ▼
Renderer               app/renderers/           turns structured words into HTML / plain text / PDF
    │
    ▼
OUTPUT
```

The engine is deliberately **renderer-agnostic**: it never emits `<strong>`
tags or PDF draw calls directly. That separation is what let PDF export get
added, and Unicode-font support get fixed, without touching the emphasis
algorithm at all.

### Sentence-position weighting

Most bionic reading tools apply one flat rule to every word. This one adds a
second signal: the first word of a sentence or paragraph gets a boosted
emphasis ratio (configurable via `sentence_start_boost` in
`app/core/config.py`), since that's typically where a reader's attention has
just reset.

---

## Configuring the algorithm

All tuning lives in `app/core/config.py` as `BionicConfig`:

| Field | Purpose |
|---|---|
| `ratio` | fraction of each word's letters to bold — `0.30 / 0.40 / 0.50 / 0.60` map to the LOW / MEDIUM / HIGH / MAX presets |
| `min_word_length` | words shorter than this skip the ratio formula entirely |
| `short_word_bold_chars` | characters to bold on short words (e.g. "a", "is") |
| `max_bold_chars` | ceiling so long words don't get half the word bolded |
| `skip_numbers` / `skip_urls` | leave numbers and URLs untouched |
| `sentence_start_boost` | extra ratio applied to the first word of each sentence/paragraph |
| `sentence_start_max_bold_chars` | separate, higher cap for sentence-starting words |

---

## API reference

### `POST /convert`
JSON in, JSON out.

```json
// request
{ "text": "Artificial intelligence helps students.", "strength": 0.4 }

// response
{ "html": "<strong>Art</strong>ificial <strong>int</strong>elligence helps students." }
```

### `POST /convert/file`
Multipart form: `file` (`.txt` / `.pdf` / `.docx`), `strength` → same `{ "html": ... }` response.

### `POST /convert/export`
Multipart form: `format` (`txt` / `html` / `pdf`), `strength`, and either
`text` or `file` → returns the converted file as a download.

---

## Running the tests

```bash
pytest
```

19 tests cover the tokenizer (lossless reconstruction, punctuation
splitting, contractions, hyphenation, URLs, numbers), the bionic rules
(short/long word caps, sentence-start boost, preset ratios), and the
extractors (PDF, DOCX, plain text).

---

## Project layout

```
bionic-reader/
├── app/
│   ├── core/                  # tokenizer, rules, config, the engine itself
│   │   ├── tokenizer.py
│   │   ├── rules.py
│   │   ├── bionic_engine.py
│   │   └── config.py
│   ├── extractors/            # text / pdf / docx → raw text
│   ├── renderers/             # bionic nodes → html / text / pdf
│   │   └── fonts/             # bundled Unicode font for PDF export
│   ├── api/routes.py          # FastAPI endpoints
│   └── main.py                # app entrypoint, serves frontend/
├── frontend/                  # vanilla HTML/CSS/JS UI, no build step
├── tests/
├── requirements.txt
└── README.md
```

---

## Roadmap

- [ ] Preserve DOCX styling (headings, source bold) through to output
- [ ] EPUB and webpage URL input
- [ ] Per-paragraph reading-speed estimate
- [ ] Browser extension for reading any webpage bionically
- [ ] Adjustable font size / line spacing in the reading view

---

## License

MIT — free to use, modify, and share.

<div align="center">

Built as a personal project exploring reading-aid design and clean
algorithm/renderer separation.

</div>
