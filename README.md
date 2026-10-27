# Ibarat — Free Writing Studio

**Live:** https://clinic-demo.fastapicloud.dev/ibarat

Original clean-room build from the daily-app-gap-build series (2026-10-27).
Target studied from PUBLIC sources only: QuillBot — the paraphrasing
category's reference product, on a16z's first consumer-AI spending list
(Oct 2026), whose free tier caps paraphrasing at 125 words per pass,
paywalls most modes, and whose citation generator has been reported to
fabricate DOIs and authors.

## What Ibarat does differently

1. **Free, unlimited, no account, no card, no word cap.** All 7 modes
   free, any length.
2. **All 7 modes free** — Standard, Fluency, Formal, Simple, Creative,
   Shorten, Expand — as a documented rule-based rewriter (curated
   synonym/phrase tables, visible in `ibarat/engine.py`), plus an
   optional Gemini neural rewrite when a key is configured.
3. **Protected terms + change measurement.** List technical terms,
   drug names or author names and they are never swapped; every
   rewrite reports a word-set similarity score and changed-word count.
4. **Citation builder that never invents.** APA, MLA and Chicago
   author-date from fields you type. A DOI/URL appears ONLY if you
   supply it; otherwise the citation ends cleanly with a note.
5. **Extractive summarizer + real readability/style analysis.**
   TF-scored sentence selection (original order, no invented wording),
   Flesch Reading Ease + grade (formula shown), and deterministic
   style flags (repeated words, long sentences, passive candidates,
   fillers).
6. **Private by construction.** No account, no history stored, nothing
   sent anywhere except the optional Gemini call. No training on
   user text, ever.

## Deliberately NOT shipped

- No plagiarism score (without a reference corpus, no such score
  would be honest).
- No AI detector / humanizer — evasion tools are refused on purpose.
- No invented citations, DOIs or authors, ever.

## Honest scope

Rule-based rewrites change wording; they do not understand meaning —
read every output before using it. Paraphrasing someone else's work
without citing it is still plagiarism; this tool helps reword YOUR
writing and format YOUR citations.

## Verify

```bash
python3 tests/verify.py
```

32 checks: all 7 modes, protected terms, shorten phrase table,
similarity extremes, summarizer pick, Flesch hand-calc
("The cat sat on the mat." → 116.15), style flags, APA citation exact
string, no-DOI invents nothing, route smoke + no regressions on
/quwwat /ishtehar /dars /bayan /lablink (when run against the
clinic-demo app).

## Layout

- `ibarat/engine.py` — paraphrase / summarize / readability / analyze / cite
- `ibarat/gemini.py` — optional Gemini rewrite (key from env at call time only)
- `ibarat/pages.py` — single-page UI
- `ibarat/routes.py` — FastAPI router (`/ibarat`)
- `tests/verify.py` — verification suite
