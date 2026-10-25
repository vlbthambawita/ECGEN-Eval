from pathlib import Path
R=Path(__file__).resolve().parents[1]
aliases={
'PGLRF':'Wang_2026_PGLRF','PPGFlowECG':'Fang_2025_PPGFlow','CLEP-GAN':'Li_2025_CLEPGAN','CLEPGAN':'Li_2025_CLEPGAN',
'P2Es':'Ji_2026_P2Es','PhysDiff':'Qiu_2026_PhysDiff','FEMVAE':'Nishikimi_2024_FEMVAE','MultiBeat':'Pohl_2025_MultiBeat',
'FlowECG':'Bondar_2025_FlowECG','MIDT':'Huang_2025_MIDT','SSSDnle':'Skorik_2024_SSSDnle','SSSD thesis':'Li_2026_EvaluationThesis',
'cNVAE':'Sviridov_2025_cNVAE','Cardoso':'Cardoso_2023_Bayesian','CardioPPG':'Fang_2025_CardioPPG',
'LA VQ-Editor':'Hu_2024_DigitalTwin','Hu':'Hu_2024_DigitalTwin','MultiODE':'Yehuda_2024_MultiODE',
'Zanchi2025':'Zanchi_2025_Brugada','Zanchi2026':'Zanchi_2026_Validation','WearECG':'Guan_2026_WearECG',
'thesis':'Li_2026_EvaluationThesis','Russo thesis':'Russo_2025_HumanFeedback','DiffuSETS':'Lai_2025_DiffuSETS',
'GAN comparison':'Adib_2025_GANComparison','SE-Diff':'Wang_2025_SEDiff','ECGTwin':'Lai_2025_ECGTwin',
'UniECG':'Jin_2025_UniECG','Neifar':'Neifar_2024_DiffECG','Oladunni':'Oladunni_2026_Complementarity',
'Tiwari':'Tiwari_2026_Minority','ZhangQualityGAN':'Zhang_2026_QualityGAN','Nunez':'Nunez_2024_Augmentation',
'Yang':'Yang_2024_CECGGAN','Adib':'Adib_2025_GANComparison','Sang':'Sang_2025_Personalization',
'CoFE':'Jang_2025_CoFE','GRU-Diffusion':'Wang_2025_SEDiff','Kong':'Kong_2024_fGAN','Qiu':'Qiu_2026_PhysDiff',
'Zanchi':'Zanchi_2026_Validation','Zhang':'Zhang_2026_QualityGAN','SSSDnle discussion':'Skorik_2024_SSSDnle','thesis privacy DCR':'Li_2026_EvaluationThesis'}
for fn in ['metric_catalog.md','loss_catalog.md']:
 p=R/fn;t=p.read_text()
 # Change note-link destinations only, retaining the short display labels.
 for alias,sid in aliases.items():
  t=t.replace(f'(notes/{alias}.md)',f'(notes/{sid}.md)')
 p.write_text(t)

