# Search Log

All searches run on **2026-10-25**. Date filter: published/first posted ≥ 2023-10-01.
Raw API responses were kept in the session scratch directory (not committed).

## 1. Database searches

| Source | Query ID | Query string | Total hits reported | Records retrieved (in window) |
|---|---|---|---|---|
| arXiv | Q1 | `all:"synthetic ECG" AND (all:GAN OR all:diffusion OR all:"flow matching" OR all:VAE OR all:generative)` | 25 | 14 |
| arXiv | Q2 | `(all:ECG OR all:electrocardiogram) AND all:generation AND all:diffusion` | 39 | 29 |
| arXiv | Q3 | `(all:ECG OR all:electrocardiogram) AND all:synthesis AND (all:adversarial OR all:GAN)` | 13 | 3 |
| arXiv | Q4 | `all:"12-lead" AND (all:ECG OR all:electrocardiogram) AND (all:generation OR all:generative OR all:diffusion)` | 84 | 51 |
| arXiv | Q5 | `(all:ECG OR all:electrocardiogram) AND all:text AND (all:generation OR all:generative) AND (all:diffusion OR all:conditioned OR all:report)` | 28 | 23 |
| arXiv | Q6 | `(all:PPG OR all:photoplethysmogram) AND (all:ECG OR all:electrocardiogram) AND (all:translation OR all:generation OR all:reconstruction)` | 73 | 49 |
| arXiv | Q7 | `(all:ECG OR all:electrocardiogram) AND all:lead AND all:reconstruction AND (all:generative OR all:diffusion OR all:GAN)` | 38 | 29 |
| arXiv | Q8 | `(all:ECG OR all:electrocardiogram) AND (all:"flow matching" OR all:"normalizing flow")` | 7 | 7 |
| arXiv | Q9 | `(all:ECG OR all:electrocardiogram) AND all:synthetic AND (all:evaluation OR all:metric OR all:fidelity OR all:quality)` | 69 | 43 |
| arXiv | Q10 | `(all:ECG OR all:electrocardiogram) AND (all:Frechet OR all:FID)` | 4 | 3 |
| arXiv | Q11 | `(all:physiological OR all:biosignal) AND all:synthetic AND all:evaluation AND (all:fidelity OR all:privacy OR all:utility)` | 27 | 22 |
| arXiv | Q12 | `(all:ECG OR all:electrocardiogram) AND (all:TSTR OR all:"train on synthetic")` | 2 | 0 |
| arXiv | Q13 | `(all:ECG OR all:electrocardiogram) AND all:"foundation model" AND (all:generation OR all:generative)` | 46 | 46 |
| arXiv | Q14 | `(ti:ECG OR ti:electrocardiogram) AND (ti:generative OR ti:generation OR ti:synthesis OR ti:synthetic OR ti:diffusion OR ti:GAN)` | 89 | 51 |
| arXiv | Q15 | `(all:ECG OR all:electrocardiogram) AND (all:VAE OR all:"variational autoencoder") AND (all:generation OR all:synthetic)` | 19 | 14 |
| OpenAlex | Q1 | `synthetic ECG generation GAN diffusion VAE` | 331 | 200 |
| OpenAlex | Q2 | `ECG generation diffusion model` | 3907 | 200 |
| OpenAlex | Q3 | `ECG synthesis generative adversarial network` | 1719 | 200 |
| OpenAlex | Q4 | `12-lead ECG generation diffusion` | 2850 | 200 |
| OpenAlex | Q5 | `text-to-ECG generation` | 10789 | 200 |
| OpenAlex | Q6 | `PPG to ECG translation generative` | 668 | 200 |
| OpenAlex | Q7 | `ECG lead reconstruction generative model` | 2175 | 200 |
| OpenAlex | Q8 | `flow matching electrocardiogram` | 3800 | 200 |
| OpenAlex | Q9 | `evaluation synthetic electrocardiogram quality metrics` | 3452 | 200 |
| OpenAlex | Q10 | `Frechet distance ECG generative` | 57 | 57 |
| OpenAlex | Q11 | `synthetic physiological signals evaluation fidelity privacy` | 2633 | 200 |
| OpenAlex | Q12 | `train on synthetic test on real ECG` | 6636 | 200 |
| OpenAlex | Q13 | `ECG foundation model generation` | 14926 | 200 |
| OpenAlex | Q14 | `electrocardiogram generative model synthetic` | 2240 | 200 |
| OpenAlex | Q15 | `variational autoencoder ECG generation` | 2499 | 200 |
| EuropePMC | Q1 | `(("synthetic ECG" OR "synthetic electrocardiogram") AND (GAN OR diffusion OR "flow matching" OR VAE OR generative)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 75 | 75 |
| EuropePMC | Q2 | `((ECG OR electrocardiogram) AND generation AND "diffusion model") AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 110 | 110 |
| EuropePMC | Q3 | `((ECG OR electrocardiogram) AND synthesis AND "generative adversarial") AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 296 | 296 |
| EuropePMC | Q5 | `((ECG OR electrocardiogram) AND text AND generation AND (diffusion OR "language model")) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 973 | 300 |
| EuropePMC | Q6 | `((PPG OR photoplethysmogram) AND (ECG OR electrocardiogram) AND (translation OR reconstruction) AND (GAN OR diffusion OR generative)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 340 | 300 |
| EuropePMC | Q7 | `((ECG OR electrocardiogram) AND "lead reconstruction" AND (generative OR GAN OR diffusion)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 14 | 14 |
| EuropePMC | Q9 | `(("synthetic ECG" OR "synthetic electrocardiogram") AND (evaluation OR metric OR fidelity)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 112 | 112 |
| EuropePMC | Q11 | `("synthetic" AND ("physiological signal" OR biosignal) AND evaluation AND (fidelity OR privacy OR utility)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 470 | 300 |
| EuropePMC | Q15 | `((ECG OR electrocardiogram) AND "variational autoencoder" AND (generation OR synthetic)) AND FIRST_PDATE:[2023-10-01 TO 2026-12-31]` | 176 | 176 |

Notes:
- arXiv: `export.arxiv.org/api/query`, sorted by submission date, paged until records fell before 2023-10-01.
- OpenAlex: full-text relevance `search=` with `from_publication_date:2023-10-01`, first 200 results per query (large hit counts reflect OpenAlex's loose relevance matching; top-ranked results were used).
- Europe PMC: `FIRST_PDATE:[2023-10-01 TO 2026-12-31]`, up to 300 records per query.
- Semantic Scholar Graph API returned HTTP 429 (rate limit) without a key, so OpenAlex was used for snowballing instead.

## 2. Deduplication and keyword pre-filter

- 2,957 unique records after deduplication on normalised title (DOI/arXiv-ID merged).
- Keyword pre-filter (title+abstract must contain an ECG term AND a generative-model term, and date ≥ 2023-10-01): **505 kept**, 2,452 excluded (reasons in `screening.csv`, stage `keyword-prefilter`).

## 3. Title/abstract screening

- 505 screened manually → **153 included**, 352 excluded (reasons in `screening.csv`).

## 4. Snowballing (OpenAlex references + citing works)

Seeds (17): DiffuSETS, SSSD-ECG-nle, TransDiffECG, Text-to-ECG (2025), FlowECG, Assessing robustness of evaluation metrics, Towards High-Fidelity ECG Generation (human feedback), Advancing ECG synthesis key metrics, Synthetic ECG scoping review, Comprehensive framework for synthetic ECG validation, DiffECG, ECG-DPM, SSSD-ECG transformer (Sensors 2023), DS4U-Net, Bayesian ECG reconstruction DDGM, Generating Realistic Multi-Beat ECG, Latent diffusion minute scale.

- 87 new ECG+generative records found → 11 new in-window includes, 12 pre-window seminal works kept as background, 64 excluded.

## 5. Web search gap-filling

| Query | New includes |
|---|---|
| BioDiffusion diffusion model biomedical signal synthesis ECG 2024 | BioDiffusion (Bioengineering 2024) |
| "Fréchet" ECG distance evaluation synthetic electrocardiogram | none new (Adib et al. 2025 already found) |
| benchmark ECG generation generative models evaluation metrics 2025 2026 | none new (MIDT-ECG, DiffuSETS already found) |
| text-conditioned 12-lead ECG generation MIMIC-IV-ECG diffusion | none new (SE-Diff, DiffuSETS already found) |
| flow matching ECG generation 2025 2026 | none new (FlowECG, PG-LRF, CardioFlow already found) |
| synthetic ECG privacy memorization membership inference | ECG Digital Twin Generation (IJCAI 2024); Waterloo MSc thesis on fidelity/utility/privacy framework |
| ECG diffusion model OpenReview ICLR NeurIPS 2025 | none new |
| LLM generates ECG signal tokens autoregressive | none new (ECG-Byte is ECG→text; excluded) |

## 6. Saturation

The last round (snowballing + 8 web queries) added 14 in-window papers vs. 153 from the main searches (≈8% < 10% threshold) → stopping criterion met.
