import json,csv,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1]
M=json.loads((R/'source_manifest.json').read_text()); by={x['study_id']:x for x in M}
E={}
for f in ['evidence.json','evidence_additions.json','evidence_round3.json','evidence_round4.json','evidence_round5.json']:E.update(json.loads((R/f).read_text()))
# Bibliography; only citation facts in local metadata/source files.
def bibkey(s):
 x=by[s]; return re.sub(r'[^A-Za-z0-9]','',x.get('authors','').split(' and ')[0].split()[-1])+str(x.get('year',''))+re.sub(r'[^A-Za-z0-9]','',s.split('_')[-1])
with (R/'references.bib').open('w') as f:
 for sid in sorted(E,key=lambda z:(int(str(by[z].get('year','0'))[:4]),z)):
  x=by[sid]; key=bibkey(sid); title=x['title'].replace('{','').replace('}','')
  authors=x.get('authors','').replace(' and ',' and ')
  typ='misc' if not x.get('peer_reviewed_date') else 'article'
  f.write(f'@{typ}{{{key},\n  title = {{{title}}},\n  author = {{{authors}}},\n  year = {{{x.get("year","")}}},\n')
  if x.get('venue'):f.write(f'  journal = {{{x["venue"]}}},\n')
  if x.get('doi'):f.write(f'  doi = {{{x["doi"]}}},\n')
  if x.get('arxiv'):f.write(f'  eprint = {{{x["arxiv"]}}},\n  archivePrefix = {{arXiv}},\n')
  if x.get('landing_url'):f.write(f'  url = {{{x["landing_url"]}}},\n')
  f.write('}\n\n')
rows=[]
for sid,v in E.items():
 x=by[sid]
 typ='paired translation/reconstruction' if any(q in v['task_model'].lower() for q in ['ppg-to','ppg to','translation','reconstruct','reconstruction','lead-translation','counterfactual']) else 'population / conditional ECG synthesis'
 axes=[]
 text=(v['metrics']+' '+v['utility_expert_privacy']).lower()
 for q,label in [('fid','distribution'),('frechet','distribution'),('precision','coverage'),('recall','coverage'),('hr','physiology'),('qrs','physiology'),('tstr','TSTR'),('synthetic-only','TSTR'),('cardiologist','expert'),('physician','expert'),('privacy','privacy'),('membership','privacy'),('latency','efficiency'),('flops','efficiency')]:
  if q in text and label not in axes:axes.append(label)
 rows.append((sid,typ,', '.join(axes) or 'waveform / task-specific',v['task_model']))
review=[]
review += ['# Evaluation of learned synthetic ECG generation: literature review','',
'**Search window:** 25 October 2023–25 October 2026 (inclusive; search date 25 October 2026). This is a single-reviewer structured review, not an exhaustive systematic review. The prohibited sibling folder was not accessed.',
'',
'## Questions and scope',
'',
'The review asks how learned ECG waveform generators are evaluated for signal fidelity, physiological/clinical validity, diversity/coverage, downstream utility, privacy and computational cost; which training objectives are used and experimentally tested; and which evaluation choices support a practical benchmark. It includes learned GAN, VAE, diffusion, flow, autoregressive and related waveform synthesis, including conditional and waveform augmentation. Mechanistic-only simulation, ECG-image-only work, classification without waveform generation and protocol-only studies are excluded. Reconstruction, imputation, counterfactual editing and lead/PPG translation appear in a clearly identified adjacent task group when a generated waveform is actually scored.',
'',
'## Search and screening',
'',
'Europe PMC REST was queried directly with two broad title/abstract generation searches (one full-window, one early-window stratification) and a focused metric/loss/privacy query; the three returned 100, 100 and 94 rows (294 query rows total). The first two each exceeded the 100-row page limit (hit counts755 and103). The focused query returned all94. Deduplicating the Europe PMC rows by DOI/PMID/title yielded235 records. The direct arXiv API broad search returned the top100 of213 by relevance. Four arXiv titles matched the Europe PMC title set; the combined scholarly-source pool is therefore331 deduplicated records from394 raw API rows. These are query-specific results, not a census of either database.',
'',
'Fifteen general web-search batches returned163 result cards across query batches (142 unique card URLs), screened as supplementary discovery and access evidence. These are not native searches of IEEE Xplore, ACM, Google Scholar or Semantic Scholar. OpenAlex and Crossref were used for targeted metadata/location lookups. Publisher websites and paper reference lists supported access and backward citation discovery; no complete forward-citation graph was run. Native Google Scholar/IEEE/ACM/Semantic Scholar access was not available in this session. Exact queries, caps, results and batch-card counts are in [search_log.csv](search_log.csv); saved response bodies are under papers/search_sources/.',
'',
'After title/abstract screening and citation-led discovery, 53 candidate study records were retained for detailed eligibility/access checking. Thirty-five met the window and scope and have source-located full-text evidence. Three accessible full texts were excluded: one evaluation protocol without completed evaluation, one feature-only augmentation without waveform synthesis, and one classification-only study. Fifteen potentially relevant records await full text or a complete full-text extraction; their titles and access outcomes are listed in [unavailable_papers.md](unavailable_papers.md). Preprint and journal versions were merged by study where identified; differences and analyzed local versions are in each note and [paper_inventory.csv](paper_inventory.csv). Counts are single-reviewer decisions; no independent duplicate screening occurred.',
'',
'The prospective plan was adjusted after execution: a relevance-ranked Europe PMC query was capped at100/755, so the early-year and focused query were added to reduce (not eliminate) recency and abstract-terminology bias. General web search was kept as a discovery stream, not represented as database searching. OpenAlex/Crossref were used for metadata checks rather than broad searches because accessible endpoints did not provide a second systematic index. These limits preclude a completeness claim.',
'',
'## Included study characteristics',
'',
'The 35 included records span conditional/unconditional GANs, VAEs, score/diffusion models, rectified flow, autoregressive token generation, and hybrid objectives. The pool combines population synthesis and conditional ECG generation with adjacent paired translation/reconstruction studies. Dataset conventions vary widely: MIT-BIH beat snippets, PTB-XL 10-second multilead recordings, MIMIC-IV 12-lead records, Brugada patient traces, simulated heartbeats, and paired PPG–ECG windows. Some studies document patient-level splits; several use shuffled samples or leave split units unclear. The table is a map of task and reported evaluation dimensions, not a quality ranking.',
'',
'| Study note | Task group | Evaluation dimensions reported | Model family |','|---|---|---|---|']
for sid,typ,axes,model in sorted(rows,key=lambda z:z[0]):
 review.append(f'| [{sid}](notes/{sid}.md) | {typ} | {axes} | {model[:165].replace("|","/")} |')
review+=['','The full extraction, including definitions, units, sample units, split details, losses and limitations, is in [extraction.csv](extraction.csv) and the individual notes. There are no defensible cross-paper score rankings because signal scale, leads, duration, feature extractor, sample count, pairing, reference cohort and test split differ.',
'',
'## Evaluation findings',
'',
'**Paired error and unpaired generation answer different questions.** MAE/RMSE/MSE are interpretable when a generated waveform is conditioned on a paired input and target, the time axis is aligned, and normalization is fixed. They are not a pointwise fidelity metric for an independently drawn sample with no ground-truth counterpart. PPG→ECG papers can use paired errors, but physiological pulse transit and sensor lag can shift events; report alignment handling and HR/QRS errors beside paired error. Unpaired random pairing makes RMSE mostly a phase-mismatch statistic.',
'',
'**Distribution scores are implementation-defined.** “Fréchet distance” may mean a Gaussian fit to raw vectors, a ResNet ECG embedding (FRD), an ECG-specific Net1D embedding, ROCKET features or another representation. “FID” is not comparable across extractors or pre-processing. Report feature network, training population, layer, signal transforms, sample count, covariance regularization, and real–real reference. Precision/recall/coverage add quality and support information, but their neighborhood k and reference manifold must be stated. A low distance can coexist with mode collapse.',
'',
'**Physiological summaries expose failures hidden by averages.** HR/mean RR alone misses beat-to-beat variation, waveform morphology and event timing. Reviewed studies measure HRV, QRS/PR/QT/QTc, ST deviation, P/T amplitudes, electrical axis and multilead relationships, but definitions, fiducial detectors and failure handling are often absent. In the Waterloo thesis, ACF/DTW are close to real-real reference while SDNN/RMSSD still diverge; small peak localization errors can be amplified in interval variability. Zanchi’s p>0.05 feature tests do not establish equivalence, especially with 21 real people and 1,122 generated windows.',
'',
'**Utility must be tested on held-out people and against a real-data baseline.** TSTR compared with TRTR on the same held-out real patients is stronger evidence than training-set classification accuracy or a classifier tested on synthetic data alone. Report patient-level split, class balance, augmentation ratio and classifier tuning symmetrically. Utility can improve while fake traces remain easy to spot (SSSD-nle), and diagnosis performance on synthetic samples does not by itself prove clinical validity. Test multiple clinically distinct tasks and rare classes.',
'',
'**Expert tests and privacy attacks need explicit protocols.** Real/fake detection should specify blinded randomization, expertise, class prevalence, repeated exposure, confidence and agreement. Near-chance results from five cardiologists or seven specialists are informative but limited to a selected task and set. Privacy requires a stated attacker and membership, linkage, attribute or memorization outcomes; one feature-distance heuristic or untested privacy motivation is insufficient. The thesis’s seven attacks show mostly near-chance global membership discrimination but a higher, small-sample subgroup result, so conclusions should remain scoped to those attacks.',
'',
'**Metric names are not definitions.** The extraction catches examples such as Zanchi’s “MAE” meaning maximum absolute error; MIDT’s NNAA and MIR are custom; “FD” alternates raw and learned features; Euclidean distance, DTW and Fréchet summaries may use different pairing and aggregation. Training loss, validation score and post-hoc metric must be reported separately. A loss’s intended physiological role is not evidence of benefit unless ablated while architecture, data and sampling remain fixed.',
'',
'## Training objectives and evidence',
'',
'Noise-prediction MSE is the most common diffusion objective. Its prevalence does not show that it produces physiologically valid signals: conditioning, architecture, data quality and sampling can dominate. Most VAE papers use a reconstruction likelihood plus KL regularization; KL schedules and likelihood assumptions are often missing. GAN studies range from logistic adversarial training to WGAN-GP, sometimes with paired reconstruction or frequency terms.',
'',
'Spectral and multiresolution losses aim to preserve frequency structure, but their evidence is mixed. Kong et al. report a 31-seed validation reduction in heart-rate extraction error after adding a spectral term, with a residual training-schedule confound and no diagnostic-waveform assessment. MIDT reports improved interlead correlations alongside underdefined loss weights and inconsistent privacy metrics. These are promising task-specific signals, not proof that spectral terms universally improve generation.',
'',
'Physiological/ODE regularizers provide more direct hypotheses. MultiODE compares intra- and interlead terms and reports condition-specific downstream changes; PGLRF reports ablations for simulator guidance and paired morphology; both remain dependent on fitted priors, splits and limited external validation. SE-Diff’s printed objective may not pass gradient through frozen representations as described, illustrating why equations and code should both be checked. Contrastive alignment and classifier-guided objectives can improve conditioning or downstream class balance while encouraging collapse toward the evaluator’s representation. Validate each term against independent physiologic outcomes and diversity.',
'',
'## Practical evaluation suite for new ECG generators',
'',
'1. **Lock the data protocol first:** state dataset release, records and people, labels, sampling, duration, leads, filtering/scaling, overlap, patient-level train/validation/test splits, generator and metric-extractor training data, and external cohort. Keep a final real test set unused for model selection.',
'2. **Report unconditional distribution quality and coverage:** ECG-trained frozen feature FID/Fréchet score plus kNN precision/recall/coverage; publish extractor, code, sample count and real–real baseline. Add per-diagnosis/age/sex strata and uncertainty across independent model seeds.',
'3. **Report physiological summaries by condition:** HR/RR and HRV, QRS/PR/QT/QTc, ST/P/T morphology, beat count and multilead consistency with detector name, units, failure rate and calibration. For paired tasks add MAE/RMSE and alignment protocol; for unpaired generation do not invent samplewise pairing.',
'4. **Measure utility and failure cases:** TSTR versus TRTR on patient-held-out data, with balanced and realistic prevalence, several tasks and rare-class results. Include precision/recall and calibration, not only accuracy. Separate classifier-driven sample selection from independent testing.',
'5. **Use human review for claims that need clinical judgment:** blinded real/fake and separate diagnostic tasks, balanced case sampling, multiple cardiologists, repeated ratings, confidence, inter-rater agreement and adjudication. Treat the panel as one evidence stream.',
'6. **Audit release risk:** nearest-neighbor/memorization checks plus black-box membership/linkage and sensitive-attribute attacks at realistic low false-positive rates; include subgroup sizes. Do not claim differential privacy unless a mechanism and accountant support it.',
'7. **Measure cost at a stated quality point:** wall-clock sampling time, steps, hardware, batch, memory and model size; compare quality–latency curves rather than steps alone.',
'',
'This suite is a reviewer recommendation synthesized from the evidence, not a validated benchmark standard. Validate feature extractors and physiological detectors across datasets and demographic groups before using thresholds.',
'',
'## Limitations',
'',
'This single-reviewer search is limited by 100-row API caps, general web-card discovery, unavailable native bibliographic indexes, incomplete forward citation chasing, and inaccessible publisher full text. Fifteen potentially relevant records remain pending full-text review. Some included full texts are preprints or theses; many do not report multiple seeds, patient splits, metric implementations or loss coefficients. Supplementary files were not systematically obtained. The resulting review is useful for method selection and protocol design but should not be called exhaustive or guideline-compliant.',
'',
'## Deliverables and audit','',
'The record counts reconcile as follows: 294 Europe PMC query rows +100 arXiv rows=394 raw API rows; 235 unique Europe PMC records +100 arXiv records−4 cross-source title matches=331 unique scholarly records. Supplementary web discovery:163 cards across queries,142 unique URLs. The curated candidate register contains53 records:35 included,3 full-text exclusions and15 awaiting full text. It combines indexed-search records with targeted and citation-led discovery, so it is not a strict subset of the 331-record API pool. We do not infer a post-screening exclusion count from overlapping discovery streams. Search-result discovery and candidate selection were judgmental and completed by one reviewer.',
'',
f'Created {len(E)} study notes and extraction rows. The source inventory contains {sum(1 for q in (R/"papers").rglob("*") if q.is_file())} local source files, including multiple version/format files; it is not a unique-paper count. Original source folders are ignored by the repository rule. No files were staged or committed.',
'',
'Key linked files: [search log](search_log.csv), [screening log](screening_log.csv), [paper inventory](paper_inventory.csv), [extraction table](extraction.csv), [metric catalog](metric_catalog.md), [loss catalog](loss_catalog.md), [references](references.bib), [unavailable papers](unavailable_papers.md).']
(R/'literature_review.md').write_text('\n'.join(review)+'\n')

