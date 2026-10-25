# Literature Review Plan — Evaluation Methods and Loss Functions for Synthetic ECG Generation

- **Date started:** 2026-10-25
- **Prompt:** `updated_prompt.txt` (derived from `input_prompt.txt`)
- **Time window (core set):** 2023-10-01 → 2026-10-25. Pre-window seminal works go in `papers/09_Background_Seminal/`.

## Research questions

- **RQ1** Which evaluation metrics are used for synthetic ECGs, and how often? Categories:
  signal-level fidelity, distribution-level, clinical/physiological, downstream utility (TSTR/TRTS,
  augmentation), privacy/memorisation, human/expert evaluation.
- **RQ2** Which loss functions / training objectives are used, per model family?
- **RQ3** Which datasets, sampling rates, lead configurations and signal lengths are used?
- **RQ4** Is there an emerging standard (FID-like metrics on foundation-model embeddings, TSTR), and
  what pitfalls are reported?
- **RQ5** Which metrics are not yet in ECGEN-Eval (`mmd, dtw, prd, psd, fd, fed, psnr, ssim, swd, mae,
  hrv, pr_dist, sqi, nn_dist, heart_rate, spectral_entropy`)?

## Sources

| Source | Access | Use |
|---|---|---|
| arXiv API (`export.arxiv.org/api/query`) | open | primary preprint search + PDF download |
| OpenAlex API | open | cross-publisher search, OA PDF locations, DOIs |
| Europe PMC REST API | open | PubMed/PMC biomedical search + PMC OA PDFs |
| Semantic Scholar Graph API | open (rate-limited) | snowballing (references/citations), `openAccessPdf` |
| Web search | open | OpenReview, MDPI, Frontiers, IEEE landing pages, gap filling |

## Search queries (initial; all logged in `search_log.md`)

1. `"synthetic ECG"` AND (GAN OR diffusion OR "flow matching" OR VAE)
2. `"ECG generation"` diffusion
3. `"ECG synthesis"` generative adversarial network
4. `12-lead ECG` generation diffusion / score-based
5. text-to-ECG / report-to-ECG / text-conditioned ECG generation
6. PPG-to-ECG translation generative
7. ECG lead reconstruction / missing lead generative
8. "flow matching" ECG / electrocardiogram
9. evaluation of synthetic ECG / synthetic ECG quality metric
10. Fréchet ECG distance / FID electrocardiogram
11. synthetic physiological signals evaluation fidelity privacy utility
12. "train on synthetic test on real" ECG
13. ECG foundation model generation
14. ECG generative model / electrocardiogram generative model (broad catch-all)

## Inclusion / exclusion

**Include** (published or first posted 2023-10-01 or later):
- ECG signal generation with ML generative models (GAN, VAE, diffusion/score, flow matching/NF,
  AR/transformer, SSM, LLM/text-conditioned, hybrid), incl. conditional tasks (class, text, other
  leads, PPG→ECG, imputation, super-resolution, generative denoising);
- papers proposing/benchmarking evaluation methods for synthetic ECG or synthetic physiological time
  series;
- surveys/reviews on ECG generation (separate category).

**Exclude:** classification-only papers using augmentation without describing synthetic-data
evaluation; ECG *image* generation without signal evaluation; non-ECG signals (unless a general
evaluation method used by ECG papers → "related").

## Process

1. **Search** each source with each query (scripted; JSON raw results kept in `_work/` scratch,
   summarised in `search_log.md` with date and hit counts).
2. **Deduplicate** by arXiv ID / DOI / normalised title → candidate list.
3. **Screen** title + abstract → `screening.csv` (`id, title, year, source, decision, reason`).
4. **Snowball** from the 10–15 most relevant included papers (Semantic Scholar refs + citations).
5. **Download** legally OA PDFs only (arXiv, PMC OA, OpenAlex/Unpaywall OA locations, OpenReview,
   MDPI/Frontiers/Nature OA). Validate `%PDF` magic bytes; delete invalid files. Name:
   `<Year>_<FirstAuthorLastName>_<ShortTitle>.pdf`, placed in one category folder.
   Failures → `to_download.md`.
6. **Extract** losses/metrics/datasets from full text (PDF→text) or abstract (flagged) →
   `papers_index.csv` + `notes/<basename>.md`.
7. **Synthesise** → `01_literature_review_report.md`.

## Extraction schema (`papers_index.csv`)

`id, year, title, authors, venue, doi_or_url, pdf_path, model_family, task, datasets, n_leads,
fs_hz, signal_length_s, loss_functions, eval_metrics, eval_category_tags,
feature_extractor_for_embedding_metrics, code_available, extraction_source, notes`

## Folder layout

```
literature_review_claude/
  00_review_plan.md  search_log.md  screening.csv  papers_index.csv  to_download.md
  01_literature_review_report.md
  papers/{01_GAN,02_VAE,03_Diffusion,04_Flow_Matching_and_Normalizing_Flows,
          05_Autoregressive_Transformer_SSM_LLM,06_Hybrid_and_Other,
          07_Evaluation_Methods_and_Benchmarks,08_Surveys_and_Reviews,09_Background_Seminal}/
  notes/
```

`papers/` and all PDFs/archives are git-ignored (`.gitignore` updated 2026-10-25).

## Stopping criterion

Target ≈40–80 included core papers. Stop when the last round of queries + snowballing yields
<10% new includes (saturation).

## Working rules

No fabricated papers/DOIs/metrics; uncertain details marked "unverified". Progress files written
incrementally. API calls rate-limited with a descriptive User-Agent. No paywall circumvention.

## Plan changes

- **2026-10-25** — Semantic Scholar API returned HTTP 429 (no API key); snowballing done with OpenAlex
  `referenced_works` and `cites:` filters instead.
- **2026-10-25** — Raw API responses and helper scripts were kept in the session scratch directory rather
  than a `_work/` folder in the repo (keeps the repo clean).
- **2026-10-25** — The included set (167 in-window + 12 background) is larger than the 40–80 target, because
  the field grew quickly in 2024–2026. All included papers are indexed; full-text extraction covers every
  downloaded PDF, and abstract-only extraction is flagged in `papers_index.csv` (`extraction_source`).
- **2026-10-25** — Deterministic (non-generative) lead-reconstruction / PPG-to-ECG regressors and pure ECG
  denoising papers were excluded unless they used a generative model (GAN/VAE/diffusion/flow).
