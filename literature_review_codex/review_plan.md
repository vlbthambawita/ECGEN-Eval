# Synthetic ECG evaluation and training losses: prospective review plan

Prepared before paper searches on 2026-10-25 (UTC). Review root: `literature_review_codex/`. This is a single-reviewer, structured scientific review, not an exhaustive systematic review. The prohibited sibling directory will not be accessed. Existing prompts and user changes will be preserved.

## Questions and eligibility

Examine (1) waveform, distribution, physiological/clinical, diversity, utility, privacy, and efficiency evaluation; (2) training objectives, their definitions, weights, and experimental support; (3) reproducibility and suitability for an ECG-generation benchmark; (4) methodological gaps.

Inclusive date window: **2023-10-25 through 2026-10-25**, based on the actual UTC search date. A first public report OR first peer-reviewed publication must fall in this window. A revision alone does not qualify. Record preprint and publication dates separately and merge versions. Earlier methods can be background only.

Include learned generation of ECG waveforms, conditional or unconditional, and waveform-generating augmentation studies. Exclude non-ECG, mechanistic-only simulation, image-only generation, and classification without waveform generation. Reconstruction, imputation, denoising, and lead translation are adjacent unless explicit generation evaluation warrants inclusion. Reviews support discovery only. Abstract-only candidates remain pending rather than being represented as full-text evidence.

## Search sources, queries, and limits

Use complementary accessible sources: direct Europe PMC/PubMed and arXiv interfaces/APIs where possible, scholarly/publisher/conference websites, and general web search for discovery and access. Attempt OpenAlex or Semantic Scholar if needed. Record actual access, including unavailable services; do not call web site-restricted searches native database searches. No requirement to use inaccessible Google Scholar, IEEE, or ACM native search.

Broad query families: `(ECG OR electrocardiogram OR electrocardiographic) AND (synthetic OR generation OR generative OR synthesis)`; model-specific variants with GAN/adversarial, VAE/variational autoencoder, diffusion/score-based, flow matching/normalizing flow, and autoregressive. Focused variants add `(evaluation OR validation OR fidelity OR morphology OR diversity OR utility OR privacy OR benchmark)` or `(loss OR objective OR spectral OR perceptual OR physiological OR contrastive)`. Adapt and log exact executed syntax, filters, date, available count, returned/screened count, and access failures.

For API searches, screen up to 100 returned records per query in relevance/date order and document truncation. For web searches, screen the returned result cards, not an imagined search-engine total. Search broad and model-specific families plus focused evaluation/loss queries. Follow references and citing/related records for key full-text studies. Stop after these planned families and targeted citation searches have been completed and two refinement searches add no new eligible full-text study; if access or practical constraints prevent saturation, explicitly report limited coverage and the actual stopping point.

## Screening and records

Keep a result-level search record to support deduplication and counts. Deduplicate DOI, arXiv ID, and normalized title/authors, manually checking preprint/journal pairs. Assign `FirstAuthor_Year_ShortTitle` IDs. Record title/abstract and full-text decisions and reasons in `screening_log.csv`; record exclusions, background, adjacent, and pending separately. Reconcile raw retrieved records, duplicates, unique screened studies, full-text assessed, included, excluded, and full-text unavailable. Do not imply independent reviewer agreement.

## Extraction and source preservation

Before any download, append `/literature_review_codex/papers/` to `.gitignore` without replacing user content; inspect tracked/staged originals. Save original PDFs, HTML, and supplementary material only under `papers/<year>/<study_id>/`. Verify PDF signatures/readability and identity; retain accessible HTML if PDFs fail. Record URLs, dates, version, status, file path, and identifiers in `paper_inventory.csv`. Record failures in `unavailable_papers.md`.

For each included study, create a note and extraction row covering metadata/task/model/conditioning; datasets, sample units, leads, frequency, duration, preprocessing, splits/patient separation/external validation; every observed evaluation metric, definition, pairing, units/direction, aggregation, feature extractor/reference; utility and expert protocols; total and component losses, equations/faithful paraphrases, weights and roles; ablations/statistics/runs/failures; code/data/weights and limitations. Each substantive claim must have a page/section/table/equation locator. Use `not reported`, `unclear`, `not applicable`, or `full text unavailable` explicitly. Do not infer missing coefficients or clinical evidence. Distinguish paper evidence from reviewer interpretation and code evidence.

## Synthesis and deliverables

Produce `literature_review.md`, `metric_catalog.md`, `loss_catalog.md`, `references.bib`, logs/inventory/extraction, notes, and unavailable-paper list. Compare protocols and evidence rather than ranking incompatible model scores. Critically examine paired errors for unpaired generation, feature-space validity, physiology versus distribution matching, diversity/memorization, and utility versus independent clinical validity. Recommend a feasible core suite with optional extensions and label reviewer proposals requiring validation.

## Completion checks

Reconcile counts and identifiers; verify included studies have full-text evidence, notes, extraction, bibliography, and valid local/source links; verify downloads and ignore behavior; list unresolved full text and source limitations; preserve user changes and make no commit. Report actual coverage and any unfinished extraction instead of asserting completeness.

## Amendments

- 2026-10-25: The broad Europe PMC search returned 755 hits but was capped at 100, and the arXiv search returned 213 but was capped at 100. Added an early-window Europe PMC query and a metric/loss/privacy-focused query to reduce recency and abstract-term coverage bias; these did not eliminate it.
- 2026-10-25: Added general web search batches and targeted citation/reference searches as supplementary discovery and access checks. Their result cards were not treated as an indexed database corpus; no full forward-citation graph was available.
- 2026-10-25: Expanded the adjacent scope narrowly to PPG-to-ECG and lead translation where the study explicitly evaluates learned ECG waveform generation, while retaining classification-only and feature-only augmentation exclusions.
- 2026-10-25: Publisher access constraints left 15 otherwise potentially eligible records pending; two publisher HTML records provided landing-page/abstract content only. Their outcomes are not inferred, and they are reported separately in the pending list.
- 2026-10-25: Search sources overlap across APIs, web cards, targeted lookups, and citations; therefore the candidate register is reconciled by study disposition but no artificial post-screening rejection total or strict PRISMA flow is claimed.
