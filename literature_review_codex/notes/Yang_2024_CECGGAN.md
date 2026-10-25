# Data imbalance in cardiac health diagnostics using CECG-GAN

**Citation:** Yang Y and Lan T and Wang Y and Li F and Liu L and Huang X and Gao F and Jiang S and Zhang Z and Chen X. *Data imbalance in cardiac health diagnostics using CECG-GAN*. Scientific reports, 2024. DOI: 10.1038/s41598-024-65619-8. arXiv: not applicable; first public: 2024-06-26; peer-reviewed date: 2024-06-26.

**Source/version:** [fulltext.xml](../papers/2024/Yang_2024_CECGGAN/fulltext.xml). [Landing page](https://doi.org/10.1038/s41598-024-65619-8).


**Task and model:** TransformerconditionalGAN with encoder/decoder latentmapping for minoritybeataugmentation (Methods).

**Data and split:** MIT-BIH47subjects,300point R-centeredbeats;db5nine-levelwaveletdenoising;N/A/V/L/R. CSPC2020additional10patients,~24h each. ResNettrainrate.8;independentpatienttest and generator/classifier split boundaries unclear (Methods,Tables3,9–11).

**Evaluation metrics:** PRD,curveFD,RMSE,MAE;classificationprecision,recall,F1;denoisingSNR is preprocessingassessment,not generativefidelity. FD formula underdefined. Sample-selection accepts generateddata when classifierperformance improves (Table4,selectionsection).

**Training objectives:** Encoder/decoderreconstruction,latentgeneratoralignment,and conditionaladversarialtraining described as stages;complete equations and coefficients not reported in methods. No directlossablation (Table4).

**Reported evidence:** MIT-BIH averageF1 94.102→98.7255%;minorityA1950→68024examples;CSPCresults also improve (Tables9–11). No independenttest restriction on classifier-driven sampleselection stated;potentialselectionleakage.

**Clinical utility, experts and privacy:** Augmentation experiments,not TSTR. No blindedexpert or privacyattack. Synthesizing from3–4people per grouplimits diversity (Discussion).

**Reproducibility:** Normalization/pairing and exactobjective incomplete. Reported externaldataset is retrainingevaluation,not verifiedzero-shotvalidation.

**Critical assessment:** Reviewer: benefits cannot be attributed to a specific loss;validate selection onvalidationdata only and keep realtest untouched.
