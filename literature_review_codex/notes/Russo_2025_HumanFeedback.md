# Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human Feedback

**Citation:** Maria Russo and Joana Rebelo and Nuno Bento and Hugo Gamboa. *Towards High-Fidelity ECG Generation: Evaluation via Quality Metrics and Human Feedback*. BIOSTEC 2025, 2025. DOI: 10.5220/0013400500003911. arXiv: not applicable; first public: 2024-12; peer-reviewed date: 2025-02-01.

**Source/version:** [paper.pdf](../papers/2024/Russo_2024_HumanFeedback/paper.pdf). [Landing page](https://www.scitepress.org/Papers/2025/134005/134005.pdf).


**Task and model:** Proceedings version of thesis project evaluates SSSD-ECG fidelity/diversity/utility and clinical feedback. Related December2024 MSc thesis is analyzed as precursor; eligible publication is BIOSTEC2025, DOI10.5220/0013400500003911.

**Data and split:** PTB-XL 12 lead. Thesis implementation uses100Hz/10s and official fold split. Questionnaire20 ECG images:10 synthetic,10 real; three reviewers (cardiologist, internist, final-year medical student), July; images test recognition, not diagnosis (thesis §§3–5).

**Evaluation metrics:** Improved precision/recall, density, coverage; synthetic training TSTR and related TRTS/TSTS classification. Human real/synthetic ECG recognition and quality tier; CNN ensemble sample-quality class compared to aggregate fidelity. Definitions inherited from metric papers.

**Training objectives:** SSSD-ECG conditional diffusion noise-prediction MSE inherited. Thesis searches S4 layers, label embedding, diffusion steps; not controlled loss comparison. Evaluator five CNNs, class-weighted multiclass CE (thesis pp.34–38).

**Reported evidence:** Thesis: eight of ten synthetic signals misclassified as real by two evaluators with available follow-up; third reviewer follow-up missing. Best hyperparameter evaluator calls96% real and precision .94/density3.85, yet recall .03/coverage .89: fidelity/coverage trade-off (pp.48–49).

**Clinical utility, experts and privacy:** Not an independent blinded cardiology panel; one student, two physicians,20 image-rendered traces and selected outputs. Evaluator uses custom quality data; independence from generator data unclear. No privacy attack.

**Reproducibility:** Public thesis full text deposited2024-12 and 2025 conference paper. Thesis PDF read; proceedings PDF identified but not downloaded. Report only thesis-specific figures as such.

**Critical assessment:** Exploratory support for separate sample realism, distribution fidelity and coverage. Small human sample and correlated custom data limit evaluator validation.
