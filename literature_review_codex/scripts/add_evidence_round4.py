import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
D={}
def A(i,t,d,m,l,e,u,r,c): D[i]=dict(task_model=t,data_protocol=d,metrics=m,losses=l,evidence=e,utility_expert_privacy=u,reproducibility=r,critique=c)
A('Ji_2026_P2Es',
'Conditional diffusion translates PPG to 12-lead ECG. A domain-adjacent waveform synthesis study included because it reports generated waveform evaluation (pp.5–8).',
'MIMIC II/III/IV after overlap removal; 125 Hz, 2-s windows, subject-wise z-score, patient-level 80/20 split; final merged set count not stated in inspected methods. Ablations and bidirectional III↔IV cross-dataset assessment (pp.7,11–12).',
'Paired-reference MSE, multilead DTW, variance of waveform error, KL between selected feature distributions, marginal Wasserstein, and limb-lead electrical-axis cosine similarity (Table 1 p.8). This is translation fidelity. MACs/latency/model size separate; no expert or privacy assessment.',
'Contrastive PPG-to-affinity-group cross entropy Eq.6 (temperature unspecified). Total Eq.18 = lambda1 interlead relation error + lambda2 Fourier-domain L2 + lambda3 axis L2 + lambda4 alignment penalty; coefficients 1,.5,.2,.3. Alignment Eq.17 sums R-peak position, amplitude-range, and heart-rate-count discrepancy. Bespoke frequency-blur/QRS-adaptive corruption is process design, not a separately identified additive training loss (pp.5–7).',
'MIMIC IV full model Table2 MSE .0902, DTW .0583, error variance .4647, KL .4920, MW 8.0902, axis cosine .9542. Ablations remove affinity, frequency processing, multiscale reverse architecture; full best. 50 DDIM steps, reported 81% faster than 1000-step DDPM (pp.7–12).',
'No clear TSTR with independent classifier trained only on generated ECG. Patient-level split and cross-dataset reverse-direction degradation MIMICIII→IV MSE .1056 vs within .0914 (p.12). No clinician/privacy protocol.',
'Substantial implementation and split detail, 57M+ parameters; code/checkpoint availability not verified. Exact final sample count and some loss scale details unavailable.',
'Paired errors measure translation with paired targets and aligned windows. Multiple baselines share protocol, but clinical-grade claims exceed the outcomes; authors note single-lead ECG cannot substitute for diagnostic 12-lead ECG.')
A('Fang_2025_CardioPPG',
'CardioPPG translates PPG to ECG with STFT low/high bands, quantized VQ-VAE tokens and PPG-conditioned bidirectional transformers that iteratively reveal masked tokens (npj Digital Medicine 2025; Methods “Conditional generative model with TimeVQVAE”).',
'Paired 10-s ECG/PPG windows standardized to 256Hz, amplitudes [-1,1], no explicit lag correction. Source 8,942,348 paired segments over 3 sources; PulseDB-MIMIC subset split 70/10/20 by subject for downstream tasks; external ring AF train44/test40 subjects. Generation metric cohort/count details appear supplemental and were unavailable.',
'MAE/MSE ↓ paired waveforms, PSNR/SSIM ↑, FID ↓ with ROCKET features, FD ↓ raw first/second moments, MDD marginal density, ACD autocorrelation difference, SD/KD skew/kurtosis differences. 95% bootstrap CIs, 1000 resamples; STFT window n32 vs16/64/128. No expert or privacy attack in main article (“Quality assessment…”).',
'VQ stage STFT32, separate LF/HF encoders/codebooks; summed squared dictionary and beta commitment terms plus LF/HF reconstruction L2; beta unspecified. Frozen quantizer/decoder in stage2. Two masked-token cross entropies: LF tokens conditional on masked LF and PPG; HF conditional on LF, masked HF and PPG; iterative masked inference with cosine schedule. Contrastive pretraining bidirectional CE tau=.05 (Methods).',
'Text states CardioPPG beats RDDM/WGAN/RecQRS on most metrics; examples FID .001 vs .008 and ACD .367 vs31.046. 1000-bootstrap CIs in supplement. No explicit isolated loss ablation in extracted methods.',
'Primary emphasis is CVD screening with subject-level cohorts and external smart-ring PPG AF test. This supports utility for that task, not independently diagnostic waveform validity. No generated ECG clinician blinding/privacy reported. Code URL github.com/Yukui-1999/CardioPPG.',
'Published full text and code URL available. Detailed CIs and generation cohort are supplemental; supplement not locally available and was not used.',
'PPG-to-ECG lag is not corrected; paired MAE can penalize phase offsets and cannot be compared with unconditional generation. Feature/distribution scores depend on ROCKET and preprocessing.')
A('Sang_2025_Personalization',
'Conditional VAE generates subject-specific 12-lead ECG from anatomy/demographics/electrode positions; explicitly generates samples and evaluates morphology against in-silico simulation (Methods §2.5; Results §§3.1–3.2).',
'UK Biobank 37,508 participants; 10-s,500Hz,12 leads; 21,083 paired ECG/MRI cases for anatomy experiments. Each VAE 80/20 train/test, batch64,80 epochs; split unit called dataset and subject-disjointness unclear. Median beats used in most analyses. Separate incident-CVD cohort 33,713 subjects.',
'Morphological trends by lead under heart translation/rotation compared qualitatively with mechanistic simulation; only partial lead-wise agreement and some directional disagreements (§§3.1–3.2). Incident risk C-index .63; +sex/age .65 (§3.3), separate risk model, not generation fidelity. No scalar FID, expert, privacy or TSTR.',
'Conditional ELBO Eq.14: negative expected log-likelihood represented by waveform MSE plus beta KL(q(z|x,y)||N(0,I)); beta example 1e-4. Anatomy condition concatenated into encoder and decoder; random latent samples generate signal (Methods §2.5).',
'Anatomical rotation/translation trends compared against Mincholé simulation; agreement varies by lead and some trends are opposite (Results §§3.1–3.2). C-index is not a generative quality score. No multi-run uncertainty.',
'No held-out generation metric or independent clinicians; no TSTR or MIA. 1,834 electrode-position subset; generative model split protocol underspecified.',
'Peer-reviewed Frontiers Digital Health full text and architecture available. ELBO and MRI subset count reported; beta setting example only.',
'Comparison tests anatomy-conditioned trends rather than population distributions. Incomplete and opposite lead trends qualify physiological-consistency claims.')
A('Li_2026_EvaluationThesis',
'University of Waterloo MSc thesis evaluates conditional SSSD-ECG on PTB-XL using multi-domain fidelity, TSTR/TRTR utility, forecasting, and seven membership attacks (repository first deposit 2026-05-08; thesis §§3–4).',
'PTB-XL 21,837 records/18,885 patients,12 leads,10s, downsampled 100Hz/1000 samples, per-lead dataset z-score. Official folds1–8 train,9 validation,10 test, multi-hot five superclass labels; diffusion uses 8 independent leads and derives 4 (pp.42–48).',
'Utility: ResNet AUROC/F1,1000 bootstrap CIs; lead-aware one-step LSTM RMSE/Pearson. Fidelity: 12-lead ACF MAE, Welch Hann PSD log-MAE, lead-specific FastDTW 20-random-candidate minimum with real-real ratio, db4 level4 normalized wavelet energy MAE, NeuroKit2 LeadII HR/RR/SDNN/RMSSD/QRS count/R amplitude MAPE (pp.49–53). Privacy: seven black/grey-box attacks in Euclidean, DTW, wavelet domains; AUC, TPR@1/10%FPR, DCR/NNDR ratios, global and single-label subgroup (pp.54–58).',
'200-step conditional DDPM, linear beta 1e-4 to .02; noise-prediction MSE; eight channels,36 bidirectional S4 residual layers, class embedding; Adam 2e-4,2000 epochs,H100 (pp.46–48).',
'TSTR AUC .828 [.818,.839] vs TRTR .886 [.878,.895]; TSTR F1 .607/.685. ACF MAE .0065, PSD log-MAE .269, LeadI DTW RS/RR ratio1.003. Global MIA AUC .500–.539; DTW .539±.009 over five seeds. Per-class Euclidean-feature HYP AUC .607 on only56 nonmembers (pp.61,63,70,87–90). HRV discrepancies despite strong aggregate ACF/DTW (pp.86,96).',
'No clinicians. Global MIA is low, but subgroup HYP attack .607 has a small evaluation group. TSTR remains below real-trained performance, HYP weakest. Forecasting Pearson .918 vs .923; RMSE .1058 vs .1025 (p.63).',
'Explicit implementation, splits, seeds and attack detail; thesis not peer reviewed. Validate with independent implementation and shadow attacks.',
'Useful comparison of aggregate similarity with precise HRV and attacks. Single split/checkpoint and PTB-XL constrain generalization; low attack AUC does not establish formal privacy, fairness or attribute protection.')
A('Russo_2025_HumanFeedback',
'Proceedings version of thesis project evaluates SSSD-ECG fidelity/diversity/utility and clinical feedback. Related December2024 MSc thesis is analyzed as precursor; eligible publication is BIOSTEC2025, DOI10.5220/0013400500003911.',
'PTB-XL 12 lead. Thesis implementation uses100Hz/10s and official fold split. Questionnaire20 ECG images:10 synthetic,10 real; three reviewers (cardiologist, internist, final-year medical student), July; images test recognition, not diagnosis (thesis §§3–5).',
'Improved precision/recall, density, coverage; synthetic training TSTR and related TRTS/TSTS classification. Human real/synthetic ECG recognition and quality tier; CNN ensemble sample-quality class compared to aggregate fidelity. Definitions inherited from metric papers.',
'SSSD-ECG conditional diffusion noise-prediction MSE inherited. Thesis searches S4 layers, label embedding, diffusion steps; not controlled loss comparison. Evaluator five CNNs, class-weighted multiclass CE (thesis pp.34–38).',
'Thesis: eight of ten synthetic signals misclassified as real by two evaluators with available follow-up; third reviewer follow-up missing. Best hyperparameter evaluator calls96% real and precision .94/density3.85, yet recall .03/coverage .89: fidelity/coverage trade-off (pp.48–49).',
'Not an independent blinded cardiology panel; one student, two physicians,20 image-rendered traces and selected outputs. Evaluator uses custom quality data; independence from generator data unclear. No privacy attack.',
'Public thesis full text deposited2024-12 and 2025 conference paper. Thesis PDF read; proceedings PDF identified but not downloaded. Report only thesis-specific figures as such.',
'Exploratory support for separate sample realism, distribution fidelity and coverage. Small human sample and correlated custom data limit evaluator validation.')
(root/'evidence_round4.json').write_text(json.dumps(D,indent=2,ensure_ascii=False)+'\n')

