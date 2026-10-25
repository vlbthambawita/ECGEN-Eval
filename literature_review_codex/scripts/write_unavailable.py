import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]; M=json.loads((R/'source_manifest.json').read_text())
E={}
for fn in ['evidence.json','evidence_additions.json','evidence_round3.json','evidence_round4.json','evidence_round5.json']:E.update(json.loads((R/fn).read_text()))
lines=['# Papers awaiting full-text review','',
'The following records passed title/abstract relevance screening, but no complete readable article was available in this review workspace. They are not counted among the 35 full-text evidence records and no unreported result, metric or loss is inferred. Access was limited to public lawful copies; no paywall or authentication was bypassed. A landing page, abstract, or response code other than a readable PDF/XML/HTML is not full text.','']
for x in M:
 sid=x['study_id']
 if sid in E or sid in ['Speziale_2026_Amyloidosis','Tang_2025_PCCGAN']:continue
 attempts=x.get('attempts',[])
 lines += [f'## {sid}: {x.get("title","")}', '',
 f'**Citation:** {x.get("authors","")}. {x.get("venue","")}, {x.get("year","")}. DOI: {x.get("doi") or "not identified"}. First public date: {x.get("first_public_date","not verified")}; peer-reviewed date: {x.get("peer_reviewed_date") or "not verified"}.',
 f'**Relevance:** Potential learned ECG waveform generation or direct synthetic-ECG evaluation; full-text verification is still needed for final inclusion.',
 f'**Publisher/landing page:** {x.get("landing_url","not located")}. Alternative full text: {"arXiv " + x["arxiv"] if x.get("arxiv") else "No lawful alternate full-text copy located in the sources searched."}',
 '**Attempt and outcome:** '+('; '.join(f'{a.get("url","")}: {a.get("error") or ("HTTP "+str(a.get("http_status"))+", readable="+str(a.get("valid")))}' for a in attempts) if attempts else 'Search result/landing page only; no separate full-text download was completed.'),
 '**Current evidence:** '+('Abstract/metadata only. '+(x.get('abstract','')[:650] if x.get('abstract') else 'No abstract saved in the local candidate record.') if any(Path(R/f).suffix in ['.html','.xml'] for f in x.get('files',[])) else 'Title/abstract-level relevance; full-text metrics/losses not asserted.'),
 f'**Expected local destination:** papers/{x.get("year","")}/{sid}/paper.pdf and/or fulltext.xml.','']
lines += ['## Assistance priority','',
'The most consequential unresolved full texts are Russo et al. on robustness of synthetic ECG evaluation metrics, Kranz et al. on minute-scale latent diffusion, Dissanayake et al. on continuous multi-step generation, Hegde et al. on utility, and Zhang et al. on MorphDiff. Zhou et al. and Xiao & Xia are available as publisher landing-page abstracts, but the full article is not locally readable. A library-accessible copy or author manuscript would allow these records to be screened and extracted.']
(R/'unavailable_papers.md').write_text('\n'.join(lines)+'\n')

