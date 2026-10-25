import csv,json,re,hashlib,datetime,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'source_manifest.json').read_text())
extras=[
 dict(study_id='Li_2026_EvaluationThesis',title='A Comprehensive Evaluation Framework for Synthetic ECG: Assessing Fidelity, Utility, and Privacy',authors='Yixin Li',year='2026',arxiv='',doi='',first_public_date='2026-05-08',peer_reviewed_date='',status='MSc thesis; public repository deposit',venue='University of Waterloo MSc thesis',landing_url='https://uwspace.uwaterloo.ca/items/0fff9cd3-cb39-4e3a-b81d-2ade38b1dd22',abstract='Evaluation of conditional SSSD-ECG on PTB-XL using utility, fidelity and membership-inference attacks.',files=['papers/2026/Li_2026_EvaluationThesis/paper.pdf'],attempts=[dict(url='https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/2c35ab52-959e-48f6-81a9-6e772d18fbbc/content',http_status=200,valid=True,bytes=0)]),
 dict(study_id='Russo_2025_HumanFeedback',title='Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human Feedback',authors='Maria Russo and Joana Rebelo and Nuno Bento and Hugo Gamboa',year='2025',arxiv='',doi='10.5220/0013400500003911',first_public_date='2024-12',peer_reviewed_date='2025-02-01',status='Peer-reviewed conference paper; related thesis version analyzed',venue='BIOSTEC 2025',landing_url='https://www.scitepress.org/Papers/2025/134005/134005.pdf',abstract='SSSD-ECG refinement and evaluation with fidelity/diversity/utility metrics and clinician feedback.',files=['papers/2024/Russo_2024_HumanFeedback/paper.pdf'],attempts=[dict(url='https://www.scitepress.org/Papers/2025/134005/134005.pdf',http_status='not_downloaded',valid=False,bytes=0),dict(url='https://run.unl.pt/server/api/core/bitstreams/6f7314ad-ba0b-4e7d-9917-82ff54662db9/content',http_status=200,valid=True,bytes=0)],version_note='Proceedings full text not downloaded; analyzed linked 2024 thesis PDF. Thesis is not equivalent to the published four-author paper; results attributed to thesis where details differ.')
 ,dict(study_id='Zhou_2025_DiffECGClassification',title='DiffECG: Diffusion Model-Powered Label-Efficient and Personalized Arrhythmia Diagnosis',authors='Tianren Zhou and Zhenge Jia and Dongxiao Yu and Zhaoyan Shen',year='2025',arxiv='',doi='',first_public_date='2025',peer_reviewed_date='2025',status='Peer-reviewed conference paper; excluded classification-only',venue='IJCAI 2025',landing_url='https://www.ijcai.org/proceedings/2025/0890.pdf',abstract='Classification and representation learning; no synthetic ECG waveform generation evaluation.',files=['papers/2025/Zhou_2025_DiffECGClassification/paper.pdf'],attempts=[dict(url='https://www.ijcai.org/proceedings/2025/0890.pdf',http_status=200,valid=True,bytes=(R/'papers/2025/Zhou_2025_DiffECGClassification/paper.pdf').stat().st_size if (R/'papers/2025/Zhou_2025_DiffECGClassification/paper.pdf').exists() else 0)])
]
for x in extras:
 if not any(y['study_id']==x['study_id'] for y in manifest):manifest.append(x)
(R/'source_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
by={x['study_id']:x for x in manifest}
e={}
for f in ['evidence.json','evidence_additions.json','evidence_round3.json','evidence_round4.json','evidence_round5.json']:e.update(json.loads((R/f).read_text()))
include=set(e)
webcounts=[14,13,4,12,11,14,18,9,12,15,6,3,12,8,12]
webqueries=[
['ECG synthetic generation diffusion GAN evaluation loss 2024 2025 2026','electrocardiogram generation evaluation physiological loss benchmark','ECG generation flow matching autoregressive variational autoencoder 2024 2025 2026','synthetic ECG generation privacy memorization clinical evaluation'],
['site:arxiv.org ECG generation diffusion 2024 2025 2026 losses evaluation','site:arxiv.org electrocardiogram generation flow matching autoregressive','ECG generation 2024 GAN loss','ECG evaluation synthetic metrics 2026'],
['site:arxiv.org ECG diffusion generation'],['ECG generation 2024 2025 loss'],['ECG flow matching'],['ECG generation variational 2024 2025'],['electrocardiogram generation autoregressive waveform'],['synthetic ECG perceptual loss'],['DiffuSETS generation -site:github.com -site:researchgate.net'],['SSSD-ECG evaluation privacy'],
['Assessing the robustness ECG pdf Russo','Exploring latent diffusion models ECG arxiv','AI modeling photoplethysmography to electrocardiography PMC','DiffECG publication 2024 2025'],
['Exploring latent diffusion models for ECG generation on the minute scale pdf'],['Assessing the robustness of evaluation metrics filetype:pdf'],['synthetic electrocardiogram spectral loss OR contrastive loss'],
['DiffECG A Versatile 2024 DOI','ECG synthesis via diffusion-based state space augmented transformer publication date','Conditional Electrocardiogram Generation Using Hierarchical publication','ODE-Constrained Generative Modeling of Cardiac Dynamics TMLR']]
search=[]
def S(source,query,ret,screened,filters='',notes=''):
 search.append(dict(source=source,query=query,filters=filters,execution_date='2026-10-25',available_results=ret,screened=screened,notes=notes))
S('Europe PMC REST core search','(TITLE_ABS:ECG OR TITLE_ABS:electrocardiogram OR TITLE_ABS:electrocardiographic) AND (TITLE_ABS:synthetic OR TITLE_ABS:generation OR TITLE_ABS:generative OR TITLE_ABS:synthesis) AND FIRST_PDATE:[2023-10-25 TO 2026-10-25]',755,100,'FIRST_PDATE inclusive; relevance order; pageSize=100','Capped at100 of755; broad query.')
S('Europe PMC REST core search','(TITLE_ABS:ECG OR TITLE_ABS:electrocardiogram OR TITLE_ABS:electrocardiographic) AND (TITLE_ABS:synthetic OR TITLE_ABS:generative OR TITLE_ABS:synthesis) AND FIRST_PDATE:[2023-10-25 TO 2024-12-31]',103,100,'FIRST_PDATE inclusive; relevance order; pageSize=100','Date-stratified top-up capped at100.')
S('Europe PMC REST core search','(TITLE_ABS:ECG OR TITLE_ABS:electrocardiogram) AND (TITLE_ABS:synthetic OR TITLE_ABS:generative) AND (TITLE_ABS:evaluation OR TITLE_ABS:metric OR TITLE_ABS:loss OR TITLE_ABS:privacy OR TITLE_ABS:benchmark) AND FIRST_PDATE:[2023-10-25 TO 2026-10-25]',94,94,'FIRST_PDATE inclusive; all returned','Focused metrics/objectives query.')
S('arXiv API','(ti:ECG OR ti:electrocardiogram) AND (all:generation OR all:synthetic) AND submittedDate:[202310250000 TO 202610252359]',213,100,'Relevance order; max_results=100','Capped at100 of213; broad direct API.')
for i,(qset,n) in enumerate(zip(webqueries,webcounts),1):
 cards=len(re.findall(r'\(https?://[^)]+\)$',(R/f'papers/search_sources/web_batch{i:02d}.txt').read_text(),re.M))
 S('General web search (discovery/access)','\n---\n'.join(qset),cards,cards,'Queries issued together in one web-search call; result cards pooled in saved response','Individual per-query card counts were not retained. Screened combined result cards only; cards may duplicate across batches.')
for source,q,note in [
 ('OpenAlex works lookup','https://doi.org/10.1016/j.compbiomed.2025.109138','Metadata/location check for ECGEN; no alternative full text located.'),
 ('OpenAlex works lookup','https://doi.org/10.1016/j.compbiomed.2026.111824','Metadata/location check for Russo robustness; no alternative full text located.'),
 ('Europe PMC targeted metadata','EXT_ID:41392270','Bibliographic/full-text lookup for CardioPPG.'),
 ('Europe PMC targeted metadata','EXT_ID:40309320','Bibliographic/full-text lookup for Sang personalization.'),
 ('Crossref title metadata','DiffECG: A Versatile Probabilistic Diffusion Model for ECG Signals Synthesis','Metadata lookup; DOI checked against conference record.'),
 ('Web citation-led discovery','"DiffuSETS" "generation" -site:github.com -site:researchgate.net','Backward/reference-led discovery; no exhaustive forward citation graph.'),
 ('Web citation-led discovery','"SSSD-ECG" "evaluation" "privacy"','Backward/reference-led discovery.'),
 ('Reference list inspection','FlowECG, MultiBeat ECG, SE-Diff references','Backward search only; no complete citing network.')]:
 S(source,q,1,1,'Targeted metadata/reference follow-up',note)
with (R/'search_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=search[0].keys());w.writeheader();w.writerows(search)
inv=[]
for x in manifest:
 rels=x.get('files',[]) or ['']
 for rel in rels:
  path=R/rel if rel else None; attempts=x.get('attempts',[])
  status=('landing page/abstract only; full text unavailable' if path and path.name=='publisher.html' else 'downloaded; format verified by text extraction' if path and path.exists() else 'full text unavailable; no local file')
  inv.append(dict(study_id=x['study_id'],title=x['title'],authors=x.get('authors',''),year=x.get('year',''),venue=x.get('venue',''),publication_status=x.get('status',''),first_public_date=x.get('first_public_date',''),peer_reviewed_date=x.get('peer_reviewed_date',''),doi=x.get('doi',''),arxiv=x.get('arxiv',''),landing_url=x.get('landing_url',''),direct_url='; '.join(a.get('url','') for a in attempts if a.get('valid')),access_date='2026-10-25',version=x.get('version_note','published full text' if x.get('peer_reviewed_date') else 'arXiv/repository manuscript'),local_path=rel,download_status=status,bytes=path.stat().st_size if path and path.exists() else '',notes=x.get('version_note','')))
with (R/'paper_inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=inv[0].keys());w.writeheader();w.writerows(inv)
screen=[]
for x in manifest:
 sid=x['study_id']
 if sid in include: decision,reason,stage='include','Eligible learned ECG waveform generation with source-located full-text extraction','full text'
 elif sid=='Speziale_2026_Amyloidosis':decision,reason,stage='exclude','Protocol/planned evaluation only; no completed generated-waveform evaluation in analyzed full text','full text'
 elif sid=='Tang_2025_PCCGAN':decision,reason,stage='exclude','Feature-coefficient augmentation only; no evaluated reconstructed waveform generation in analyzed full text','full text'
 elif sid=='Zhou_2025_DiffECGClassification':decision,reason,stage='exclude','Classification/representation paper; no synthetic ECG waveform evaluation','full text'
 else:decision,stage,reason='await full text','title/abstract and access check','Potentially relevant waveform-generation study; full text unavailable or not obtained; metrics/losses/results not inferred.'
 screen.append(dict(study_id=sid,title=x['title'],doi=x.get('doi',''),arxiv=x.get('arxiv',''),first_public_date=x.get('first_public_date',''),peer_reviewed_date=x.get('peer_reviewed_date',''),stage=stage,decision=decision,reason=reason,source=x.get('source_key','candidate discovery'),fulltext_paths='; '.join(x.get('files',[]))))
with (R/'screening_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=screen[0].keys());w.writeheader();w.writerows(screen)
ext=[]
for sid,v in e.items():
 x=by[sid]; ext.append(dict(study_id=sid,title=x['title'],year=x.get('year'),venue=x.get('venue'),status=x.get('status'),first_public_date=x.get('first_public_date'),peer_reviewed_date=x.get('peer_reviewed_date'),task_model=v['task_model'],data_protocol=v['data_protocol'],metrics=v['metrics'],training_losses=v['losses'],ablation_results=v['evidence'],utility_expert_privacy=v['utility_expert_privacy'],reproducibility=v['reproducibility'],critical_notes=v['critique'],source_files='; '.join(x.get('files',[]))))
with (R/'extraction.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=ext[0].keys());w.writeheader();w.writerows(ext)
for sid,v in e.items():
 x=by[sid]; sources='; '.join(f'[{Path(q).name}](../{q})' for q in x.get('files',[])) or 'Full text unavailable; see unavailable_papers.md.'
 metadata=f"**Citation:** {x.get('authors','')}. *{x['title']}*. {x.get('venue','')}, {x.get('year','')}. DOI: {x.get('doi') or 'not identified'}. arXiv: {x.get('arxiv') or 'not applicable'}; first public: {x.get('first_public_date','not verified')}; peer-reviewed date: {x.get('peer_reviewed_date') or 'not verified'}.\n\n**Source/version:** {sources}. [Landing page]({x.get('landing_url','')}).\n"
 body='\n\n'.join(f"**{label}:** {v[key]}" for label,key in [('Task and model','task_model'),('Data and split','data_protocol'),('Evaluation metrics','metrics'),('Training objectives','losses'),('Reported evidence','evidence'),('Clinical utility, experts and privacy','utility_expert_privacy'),('Reproducibility','reproducibility'),('Critical assessment','critique')])
 (R/'notes'/f'{sid}.md').write_text(f"# {x['title']}\n\n{metadata}\n\n{body}\n")
metricrows=[
('Paired pointwise MAE/RMSE/MSE','Mean absolute/squared sample error over aligned target and output; lower. Requires true paired signal, stable phase, scale, lead and length. Appropriate for reconstruction/translation, not unconditional random samples.','PGLRF; PPGFlowECG; CLEPGAN; P2Es; PhysDiff; WearECG; CardioPPG; FlowECG'),
('DTW / paired DTW','Minimum accumulated local distance along a monotone temporal warping path; lower. Paired use requires defensible target identity; nearest-sample DTW for unpaired generation is a different statistic and rewards larger sample pools.','MultiBeat; FlowECG; P2Es; FEMVAE; thesis privacy DCR; PhysDiff'),
('Fréchet distance / FID / FRD','Gaussian 2-Wasserstein distance between feature means/covariances. Extractor, layer, normalization, sample count and training data are part of the metric. Raw-vector FD, ECG-feature FD and FID are not interchangeable.','DiffuSETS; MultiBeat; cNVAE; Cardoso; CLEPGAN; GRU-Diffusion; LA VQ-Editor; CardioPPG; WearECG'),
('Manifold precision/recall/coverage/density','kNN/manifold estimates of sample quality and support coverage; precision≈validity, recall≈coverage. Sensitive to k, feature model, reference sample and duplication. Report components and intervals.','DiffuSETS; CardioPPG; Russo thesis; Hu'),
('ECG morphology/physiology metrics','Detected HR/RR/HRV, PR/QRS/QT/QTc, ST deviation, P/QRS/T amplitudes/axes, beat counts, rhythm transitions. Define detector, sampling, failures, units, aggregation and condition strata.','DiffuSETS; Zanchi; PGLRF; thesis; PPGFlowECG; CardioPPG; CoFE; MultiODE'),
('Spectral/time-frequency metrics','PSD, Fourier/mel distance, wavelet energy, spectral similarity. Define window, normalization, frequency bins and scale. Global spectrum does not localize QRS/ST events.','MIDT; SE-Diff; CLEPGAN; P2Es; thesis; CardioPPG'),
('Classifier utility: TSTR/TRTR','Train on synthetic and test on held-out real, against real-train/real-test baseline with same model, class balance and patient split. Measures task utility, not general clinical validity or fidelity.','SSSDnle; DiffuSETS; MultiBeat; Hu; MIDT; thesis; GRU-Diffusion; GAN comparison'),
('Real/fake expert assessment','Blinded randomized balanced sample, expertise, repeated rating, agreement and confidence required. Chance-level detection is perceptual indistinguishability under that protocol, not safety or diagnostic equivalence.','SSSDnle; DiffuSETS; Zanchi2025; Zanchi2026; PPGFlowECG; WearECG; Russo thesis'),
('Privacy/MIA','Explicit threat-model attacks on membership, nearest-neighbor/memorization, linkage and sensitive attributes; report AUC and low-FPR TPR with matched member/nonmember cohorts. One heuristic is not a guarantee.','MIDT; Hu; thesis; SSSDnle discussion'),
('Efficiency','Measure sampling steps and wall-clock/energy/memory on named hardware, batch, output length and quality target. FLOPs/parameter count alone do not establish deployed latency.','FlowECG; CLEPGAN; P2Es; GRU-Diffusion')]
with (R/'metric_catalog.md').open('w') as f:
 f.write('# Metric catalog\n\nMetric definitions below summarize reviewed implementations. Study links open extraction notes. They are not pooled across incompatible protocols.\n\n| Metric family | Definition and required inputs | Limitations/implementation needs | Studies |\n|---|---|---|---|\n')
 for n,d,s in metricrows:
  links=', '.join(f'[{z}](notes/{z}.md)' for z in s.split('; '))
  f.write(f'| {n} | {d} | Use within-study; retain pairedness, extractor, split and sample-count details. | {links} |\n')
lossrows=[
('Diffusion denoising/noise MSE','Predict injected Gaussian noise or clean x0 at sampled timestep. Training objective, not quality metric.','DiffuSETS; SSSDnle; MultiODE; PGLRF; P2Es; MIDT; thesis; GRU-Diffusion; Neifar; SE-Diff; Qiu'),
('VAE ELBO/reconstruction + KL','Expected likelihood/reconstruction and KL posterior-to-prior; balance via beta/schedule. Specify decoder likelihood, reductions and annealing.','DiffuSETS; cNVAE; FEMVAE; CardioPPG; WearECG; Sang; CLEPGAN'),
('GAN adversarial objectives','Logistic/softplus or Wasserstein critic with gradient penalty; signs and regularizers differ. State exact generator/discriminator losses.','GAN comparison; Hu; Zanchi; Kong; CLEPGAN; MultiODE; Tiwari; Zhang; CoFE; Adib'),
('Spectral/multiresolution loss','L1/L2 amplitude or log-magnitude difference on FFT/STFT/mel/PSD. Specify windows, overlap, scale and aggregation.','MIDT; SE-Diff; CLEPGAN; P2Es; CardioPPG'),
('Physiology/ODE/Euler residual','Penalize derivatives/simulator residual, event timing or cross-lead consistency. Fitted simulator is a prior, not truth; confirm gradients reach generated state.','MultiODE; PGLRF; Qiu; P2Es; FEMVAE'),
('Contrastive/crossmodal alignment','InfoNCE/NT-Xent or cross-entropy for matched PPG-ECG, text-ECG or latent pairs. Report temperature, negatives and patient identity.','PPGFlowECG; CLEPGAN; CardioPPG; P2Es; ECGTwin'),
('Distribution/correlation complementarity','Mutual information, orthogonality, cross-lead relationships and temporal interference. Estimator and coefficient alter the target.','Oladunni; P2Es; MIDT'),
('Task/classification/semantic objectives','Label CE, diagnostic similarity or text-embedding alignment for conditional generation; keep train objective distinct from downstream evaluator.','Hu; UniECG; DiffuSETS; ZhangQualityGAN; Tiwari; Yang')]
with (R/'loss_catalog.md').open('w') as f:
 f.write('# Loss catalog\n\n| Loss family | Objective and purpose | Main limitations and examples |\n|---|---|---|\n')
 for n,d,s in lossrows:
  links=', '.join(f'[{z}](notes/{z}.md)' for z in s.split('; '))
  f.write(f'| {n} | {d} | {links} |\n')

