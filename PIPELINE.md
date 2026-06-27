# CFA Tutor — Content Pipeline

How the study text, practice questions, and flashcards are generated from the
CFA curriculum PDFs, and how to regenerate them cleanly.

## Why output looked broken

The practice/flashcard text used to read as broken English for two reasons:

1. **Extraction artifacts.** The PDFs encode line-break hyphens as a hidden
   `U+FFFE` character *inside* words (`with￾drawal`, `port￾folio`) and contain
   zero-width spaces. The old extractor (PyPDF2) also split letters from words
   (`R ates`, `T ime`). All of this flowed straight into the content.
2. **Fragment harvesting.** The question generator lifted raw sentence
   fragments and cut them at a fixed character count — mid-word and
   mid-sentence — so options and flashcard backs were truncated and ungrammatical.

## What changed

- `extract_pdfs.py` now uses **pypdfium2** and cleans each page: removes
  `U+FFFE`/zero-width characters, rejoins hyphenated words, and repairs
  letter-split words. This removes the artifacts at the source (0 spaced-letter
  artifacts vs ~300/volume before).
- `generate_questions.py` now builds **complete, polished sentences**: it
  repairs residual artifacts, trims only at sentence boundaries (never
  mid-word), capitalizes, ensures terminal punctuation, and drops any candidate
  that still looks broken or contains leaked math/formula fragments.
- All scripts use **paths relative to the repo** (no hardcoded machine paths),
  so the pipeline runs anywhere.

## Regenerating everything (after uploading all 10 PDFs)

Place the 10 volume PDFs beside the scripts (or in a `./pdfs/` subfolder), then:

```bash
pip install pypdfium2
python3 extract_pdfs.py      # PDFs   -> cfa_content.json  (clean raw text)
python3 clean_content.py     # text   -> structured HTML per module
python3 fix_titles.py        # apply canonical module titles
python3 generate_questions.py# HTML   -> questions.js (practice + flashcards)
python3 finalize.py          # drop raw text, minify cfa_content.json
```

`extract_pdfs.py` auto-detects which volume PDFs are present and skips the rest,
so partial runs are safe. The app (`index.html`) loads `cfa_content.json`,
`questions.js`, and `videos.js` directly — no build step.

## Note on the current commit

`questions.js` in this commit was regenerated from the existing 10-volume
`cfa_content.json` with the improved generator, so practice/flashcards already
read as clean English. The underlying `cfa_content.json` HTML is still from the
older extraction; re-running the full pipeline above (with all 10 PDFs) will
also clean the study-text and is the recommended long-term step.
