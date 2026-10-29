"""Build the literature-review database used by the documentation site.

Inputs (all in ``literature_review_claude/``):

- ``papers_index.csv``: one row per paper (bibliography, model, task, datasets, verbatim
  loss functions and evaluation metrics) from the first extraction pass.
- ``structured_extraction.jsonl``: second, structured pass (per-metric evaluation records
  with evaluation categories, data type/format, leads, sampling rate, segment length,
  conditioning, fairness / robustness / privacy analyses). Papers missing here fall back to
  keyword-matched metric families.
- ``notes/<basename>.md``: per-paper notes (the "Takeaway for ECGEN-Eval" line is used).

Output: a normalised SQLite database ``docs/literature/ecgen_literature.sqlite`` plus a flat
``papers.csv``. The "Paper Database" docs page opens the SQLite file in the browser with
sql.js.

Schema: ``papers``; ``authors`` + ``paper_authors``; ``evaluations`` (one row per metric a
paper uses) + ``evaluation_categories``; and a generic facet model (``facets`` -> ``terms``
-> ``paper_terms``) so new filter dimensions or values are added as rows, not tables. Views
``paper_facets``, ``evaluation_details`` and ``metric_usage`` simplify queries.

A second, independent part catalogues open-source ECG feature extractors (source data in
``feature_extractors/``: ``feature_vocab.csv`` + ``tools.jsonl``): tables ``extractors``,
``extractor_inputs``, ``extractor_input_kinds``, ``extractor_signal_types``,
``feature_vocab``, ``extractor_features`` and ``extractor_evidence``, with views
``extractor_feature_details``, ``feature_coverage`` and ``ecgen_feature_support``.

Only papers whose PDF has been downloaded are included by default; pass ``--all`` to also
include abstract-only entries.

Usage::

    python literature_review_claude/build_db.py          # downloaded papers only
    python literature_review_claude/build_db.py --all    # every indexed paper
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = HERE / "papers_index.csv"
STRUCTURED = HERE / "structured_extraction.jsonl"
NOTES = HERE / "notes"
OUT_DIR = ROOT / "docs" / "literature"
DB_PATH = OUT_DIR / "ecgen_literature.sqlite"
EXTRACTORS = HERE / "feature_extractors"

MODEL_CATEGORIES = {
    "01_GAN": "GAN",
    "02_VAE": "VAE",
    "03_Diffusion": "Diffusion",
    "04_Flow_Matching_and_Normalizing_Flows": "Flow matching / NF",
    "05_Autoregressive_Transformer_SSM_LLM": "Autoregressive / Transformer / LLM",
    "06_Hybrid_and_Other": "Hybrid / other",
    "07_Evaluation_Methods_and_Benchmarks": "Evaluation method / benchmark",
    "08_Surveys_and_Reviews": "Survey / review",
    "09_Background_Seminal": "Background (pre-Oct 2023)",
}

# Evaluation categories, in display order, with a one-line definition.
EVAL_CATEGORIES = {
    "Fidelity": "Realism / similarity of synthetic samples to real data",
    "Diversity": "Coverage and variety of the synthetic data (recall, mode collapse)",
    "Utility": "Usefulness for downstream tasks (TSTR, TRTS, augmentation)",
    "Privacy": "Memorisation, re-identification and membership-inference risk",
    "Fairness": "Behaviour across demographic subgroups; demographic attribute preservation",
    "Robustness": "Behaviour under noise, perturbation, domain shift; external validation",
    "Clinical validity": "Physiological plausibility: intervals, HR/HRV, fiducials, lead physics",
    "Human / expert": "Cardiologist ratings and visual Turing tests",
    "Conditional consistency": "Agreement between the generated ECG and the requested condition",
    "Efficiency": "Sampling cost: runtime, number of function evaluations, parameters",
}

# Canonical metric family -> (default evaluation category, ECGEN-Eval key(s) or "",
# keyword regex used only for papers without a structured extraction).
METRICS = {
    "RMSE": ("Fidelity", "mae (RMSE in extra)", r"\brmse\b|root mean squared? error"),
    "MAE": ("Fidelity", "mae", r"\bmae\b|mean absolute error"),
    "MSE": ("Fidelity", "", r"\bmse\b|mean squared? error"),
    "PRD / normalised PRD": ("Fidelity", "prd", r"\bn?prd\b|percent(age)? root.mean"),
    "Pearson / correlation": ("Fidelity", "", r"pearson|correlation coeff|\bpcc\b|cross-?correlation"),
    "DTW": ("Fidelity", "dtw", r"\bdtw\b|dynamic time warp"),
    "Curve Fréchet distance": ("Fidelity", "", r"(discrete|curve)[- ]?fr[eé]chet|\bfd\b"),
    "PSNR / SNR": ("Fidelity", "psnr", r"psnr|\bsnr\b|signal.to.noise"),
    "SSIM": ("Fidelity", "ssim", r"ssim|structural similarity"),
    "Euclidean distance": ("Fidelity", "", r"euclidean"),
    "Cosine similarity": ("Fidelity", "", r"cosine"),
    "Spectral / PSD similarity": (
        "Fidelity", "psd, spectral_entropy", r"\bpsd\b|spectral (similarity|distance)|power spectr"),
    "FID / embedding Fréchet": (
        "Fidelity", "fed, fd", r"\bfid\b|fr[eé]chet incep|\bfrd\b|\bfed\b|context-fid|rfid"),
    "Inception-score-like": ("Fidelity", "", r"inception score|resnet score"),
    "MMD": ("Fidelity", "mmd", r"\bmmd\b|maximum mean discrep"),
    "Wasserstein / EMD": ("Fidelity", "swd", r"wasserstein|\bemd\b|earth mover"),
    "KL / JS divergence": ("Fidelity", "", r"kullback|\bkl\b|jensen|\bjsd?\b"),
    "Precision / recall / density / coverage": (
        "Diversity", "pr_dist", r"precision.recall|\bdensity\b|coverage|α-precision|improved precision"),
    "Diversity / mode-collapse measure": ("Diversity", "", r"mode collapse|diversity|intra-class"),
    "Classifier two-sample test": (
        "Fidelity", "", r"discriminative score|two-sample|c2st|real.vs.?.?(fake|synthetic) classif|1-?nn"),
    "Statistical tests": (
        "Fidelity", "", r"\bks\b|kolmogorov|t-test|hotelling|wilcoxon|mann.whitney|permutation"),
    "t-SNE / UMAP / PCA plots": ("Fidelity", "", r"t-?sne|umap|pacmap|\bpca\b"),
    "Visual inspection (qualitative)": ("Fidelity", "", r"visual inspection|qualitative"),
    "R² (coefficient of determination)": ("Fidelity", "", r"\br2\b|r²|coefficient of determination"),
    "Heart rate / HRV": ("Clinical validity", "heart_rate, hrv", r"heart.rate|hrv|sdnn|rmssd|pnn50"),
    "Clinical intervals (PR/QRS/QT/ST)": (
        "Clinical validity", "features module (no metric yet)", r"\bqtc?\b|\bpr interval|qrs (duration|width)"),
    "Fiducial / R-peak timing": ("Clinical validity", "", r"r-?peak|fiducial|beat timing"),
    "Inter-lead consistency": ("Clinical validity", "", r"einthoven|inter-?lead|goldberger"),
    "Signal quality index": ("Clinical validity", "sqi", r"\bsqi\b|signal quality"),
    "Physiological validity rate": ("Clinical validity", "", r"validity|malformed|failure rate"),
    "Downstream classification": ("Utility", "", r"accuracy|\bf1\b|auroc|\bauc\b"),
    "TSTR / TRTS": ("Utility", "", r"tstr|trts|train(ed)? on synthetic"),
    "Augmentation gain": ("Utility", "", r"augment"),
    "Label / condition adherence": ("Conditional consistency", "", r"label faithful|adherence"),
    "Text–ECG alignment (CLIP)": ("Conditional consistency", "", r"\bclip\b"),
    "Expert / Turing test": ("Human / expert", "", r"cardiologist|expert|turing|physician"),
    "Expert diagnostic agreement": ("Human / expert", "", r"diagnostic agreement"),
    "Membership inference / re-identification": (
        "Privacy", "", r"membership|re-?identif|\bmia\b"),
    "Nearest-neighbour / DCR distance": (
        "Privacy", "nn_dist", r"\bdcr\b|closest record|authenticity|memori[sz]"),
    "Subgroup performance gap": ("Fairness", "", r"subgroup|fairness|\bbias\b"),
    "Demographic attribute preservation": ("Fairness", "", r"demographic|age and sex|sex and age"),
    "Noise / perturbation robustness": ("Robustness", "", r"perturbation|noise robust|robustness"),
    "Cross-dataset / external validation": ("Robustness", "", r"external validation|cross-dataset"),
    "Seed / run variability": ("Robustness", "", r"seeds|standard deviation over runs"),
    "Metric sensitivity analysis": ("Robustness", "", r"metric sensitivity|sensitivity analysis"),
    "Efficiency (NFE / runtime / params)": (
        "Efficiency", "", r"\bnfe\b|inference (time|speed)|sampling (steps|time)|runtime"),
}

LOSSES = {
    "Adversarial (GAN)": r"adversarial|minimax|\bgan\b|\bbce\b|binary cross",
    "WGAN / gradient penalty": r"wgan|wasserstein|gradient penalty",
    "Least-squares / hinge GAN": r"lsgan|least.squares|hinge",
    "L1 reconstruction": r"\bl1\b|mean absolute|absolute error",
    "L2 / MSE reconstruction": r"\bl2\b|\bmse\b|mean squared",
    "Diffusion noise prediction": (
        r"noise.prediction|ε|epsilon|ddpm|l_simple|denoising (score|loss|objective)"
        r"|predicted noise|score matching|v-prediction"),
    "Flow-matching velocity": r"flow matching|rectified|velocity",
    "KL / ELBO": r"\bkl\b|kullback|elbo|evidence lower",
    "Classification CE": r"cross.entropy|auxiliary classif|classification loss",
    "Spectral / frequency": r"spectral|frequency|fft|stft|mel|fourier|wavelet|dwt",
    "Physiology / physics": (
        r"\bode\b|physio|physics|einthoven|goldberger|lead constraint|simulator|morpholog"
        r"|r-peak|peak loss|qrs|pde"),
    "Contrastive / CLIP": r"contrastive|infonce|clip|nt-xent",
    "VQ / codebook": r"commitment|codebook|\bvq",
    "Cycle consistency": r"cycle",
    "Perceptual / feature matching": r"perceptual|feature.matching",
    "DTW loss": r"\bdtw\b",
    "Correlation loss": r"correlation loss|pearson",
    "Token cross-entropy": r"next.token|token|nll",
}

TASKS = {
    "Unconditional": r"uncond",
    "Class-conditional": r"class-cond|label|class cond|disease",
    "Text-conditional": r"text",
    "Lead reconstruction": r"lead",
    "PPG → ECG": r"ppg",
    "Other modality → ECG": r"modality|radar|bcg|scg|vibra|video|seismo|ballisto",
    "Imputation / completion": r"imput|completion|missing",
    "Super-resolution": r"super-resolution|super resolution",
    "Augmentation": r"augment|imbalanc",
    "Evaluation": r"evaluation",
    "Survey": r"survey|review",
}

DATASETS = {
    "PTB-XL": r"ptb-?xl",
    "MIT-BIH": r"mit-?bih",
    "MIMIC-IV-ECG": r"mimic-?iv",
    "MIMIC-II/III": r"mimic-?(ii|iii|2|3)\b",
    "PTB Diagnostic": r"\bptb\b(?!-?xl)",
    "Chapman / Shaoxing / Ningbo": r"chapman|shaoxing|ningbo",
    "CPSC": r"cpsc",
    "Georgia / PhysioNet 2020-21": r"georgia|physionet.{0,12}20(20|21)",
    "BIDMC": r"bidmc",
    "VitalDB": r"vitaldb",
    "CapnoBase": r"capno",
    "WESAD / PPG-DaLiA": r"wesad|dalia",
    "UK Biobank": r"biobank",
    "CinC 2017": r"cinc.{0,6}2017|physionet.{0,12}2017",
    "Private / in-house": r"private|in-house|hospital",
}

# Facets shown as filters: (name, label, multi-valued, paper-dict key), in display order.
FACETS = [
    ("category", "Model category", 0, "category"),
    ("year", "Year", 0, "year"),
    ("eval_category", "Evaluation category", 1, "eval_categories"),
    ("metric", "Evaluation metric", 1, "metric_families"),
    ("loss", "Loss function", 1, "loss_families"),
    ("task", "Task", 1, "task_tags"),
    ("conditioning", "Conditioning", 1, "conditioning"),
    ("data_type", "Data type", 1, "data_type"),
    ("data_format", "Data format", 1, "data_format"),
    ("leads", "Leads generated", 0, "leads_bin"),
    ("sampling_rate", "Sampling rate", 0, "fs_bin"),
    ("segment_length", "Segment length", 0, "length_bin"),
    ("dataset", "Dataset", 1, "dataset_tags"),
    ("data_access", "Data access", 0, "data_access"),
    ("code", "Code", 0, "code_flag"),
    ("venue_type", "Publication type", 0, "venue_type"),
    ("extraction_source", "Extraction source", 0, "source"),
]

UNKNOWN = re.compile(r"^(unknown|not reported|not applicable|n/?a|none)", re.I)


def families(text: str, table: dict) -> list[str]:
    t = (text or "").lower()
    out = []
    for name, spec in table.items():
        pattern = spec[-1] if isinstance(spec, tuple) else spec
        if re.search(pattern, t):
            out.append(name)
    return out


def clean(value: str) -> str:
    value = (value or "").strip()
    return "" if UNKNOWN.match(value) else value


def takeaway(basename: str) -> str:
    note = NOTES / f"{basename}.md"
    if not note.exists():
        return ""
    m = re.search(r"\*\*Takeaway for ECGEN-Eval:\*\*\s*(.+)", note.read_text())
    return m.group(1).strip() if m else ""


def number(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"\d+(\.\d+)?", str(value or ""))
    return float(m.group(0)) if m else None


def leads_bin(n: float | None) -> str:
    if n is None:
        return "Not reported"
    if n <= 1:
        return "1 lead"
    if n <= 3:
        return "2–3 leads"
    if n < 12:
        return "4–11 leads"
    return "12 leads" if n == 12 else "15+ leads"


def fs_bin(fs: float | None) -> str:
    if fs is None:
        return "Not reported"
    if fs <= 150:
        return "≤ 150 Hz"
    if fs <= 300:
        return "151–300 Hz"
    if fs <= 400:
        return "301–400 Hz"
    if fs <= 600:
        return "401–600 Hz"
    return "> 600 Hz"


def length_bin(s: float | None) -> str:
    if s is None:
        return "Not reported"
    if s <= 2:
        return "≤ 2 s (beats)"
    if s < 10:
        return "2–9 s"
    if s <= 12:
        return "10 s"
    if s <= 60:
        return "11–60 s"
    return "> 1 min"


def venue_type(venue: str) -> str:
    v = (venue or "").lower()
    if re.search(r"arxiv|rxiv|ssrn|preprint", v):
        return "Preprint"
    if re.search(r"thes|dissertation|repositor|hal\b|uwspace|tel\.", v):
        return "Thesis"
    if re.search(r"conference|proceedings|symposium|workshop|computing in cardiology|lecture notes"
                 r"|embc|icassp|biostec|ijcai|neurips|icml|iclr|miccai|bibm", v):
        return "Conference"
    return "Journal" if v else "Not reported"


def load_structured() -> dict[str, dict]:
    if not STRUCTURED.exists():
        return {}
    out = {}
    for line in STRUCTURED.read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            out[d["id"]] = d
    return out


# "Other: ..." families from the structured extraction that map onto a canonical family.
FAMILY_ALIASES = {
    "other: visual inspection": "Visual inspection (qualitative)",
    "other: r² score": "R² (coefficient of determination)",
    "other: r² (coefficient of determination)": "R² (coefficient of determination)",
}


def canonical_family(name: str) -> str:
    name = (name or "").strip()
    name = FAMILY_ALIASES.get(name.lower(), name)
    if name in METRICS:
        return name
    low = name.lower()
    for k in METRICS:
        if k.lower() == low:
            return k
    return name or "Other"


def build(include_all: bool) -> list[dict]:
    structured = load_structured()
    papers = []
    for r in csv.DictReader(INDEX.open(newline="")):
        if r["notes"].startswith("EXCLUDED"):  # dropped after full-text re-check
            continue
        downloaded = r["pdf_path"] != "not downloaded"
        if not downloaded and not include_all:
            continue
        basename = Path(r["pdf_path"]).stem if downloaded else ""
        s = structured.get(r["id"], {})

        evaluations = []
        for e in s.get("evaluations", []):
            fam = canonical_family(e.get("family", ""))
            cats = [c for c in e.get("categories", []) if c in EVAL_CATEGORIES]
            if not cats:
                cats = [METRICS[fam][0]] if fam in METRICS else ["Fidelity"]
            evaluations.append({"metric": e.get("metric", fam), "family": fam,
                                "categories": cats, "how": e.get("how", "")})
        if not s:  # fallback: keyword-matched families from the first-pass text
            for fam in families(r["eval_metrics"], METRICS):
                evaluations.append({"metric": fam, "family": fam,
                                    "categories": [METRICS[fam][0]], "how": ""})

        eval_cats = {c for e in evaluations for c in e["categories"]}
        for key, cat in (("fairness", "Fairness"), ("robustness", "Robustness"),
                         ("privacy", "Privacy")):
            if s.get(key):
                eval_cats.add(cat)

        n_leads = s.get("n_leads_generated") if s else number(clean(r["n_leads"]))
        fs = s.get("fs_hz") if s else number(clean(r["fs_hz"]))
        seg = s.get("segment_length_s") if s else number(clean(r["signal_length_s"]))
        code = r["code_available"] if r["code_available"].lower().startswith("http") else ""

        papers.append({
            "id": r["id"],
            "year": int(r["year"]) if r["year"].isdigit() else None,
            "title": r["title"],
            "authors": [a.strip() for a in r["authors"].split(";") if a.strip()],
            "venue": r["venue"],
            "url": r["doi_or_url"],
            "category": MODEL_CATEGORIES.get(r["category"], r["category"]),
            "background": r["category"].startswith("09"),
            "downloaded": downloaded,
            "model_family": r["model_family"],
            "task": r["task"],
            "task_tags": families(r["task"], TASKS),
            "datasets": r["datasets"],
            "dataset_tags": families(r["datasets"], DATASETS),
            "n_leads": clean(r["n_leads"]),
            "fs_hz": clean(r["fs_hz"]),
            "signal_length_s": clean(r["signal_length_s"]),
            "n_leads_generated": n_leads,
            "fs_hz_model": fs,
            "segment_length_model": seg,
            "leads_bin": leads_bin(n_leads),
            "fs_bin": fs_bin(fs),
            "length_bin": length_bin(seg),
            "data_type": [v for v in s.get("data_type", []) if v != "Not applicable"],
            "data_format": [v for v in s.get("data_format", []) if v != "Not applicable"],
            "conditioning": [v for v in s.get("conditioning", []) if v != "Not applicable"],
            "data_access": s.get("data_access") or "Not reported",
            "loss_functions": r["loss_functions"],
            "loss_families": families(r["loss_functions"], LOSSES),
            "eval_metrics": r["eval_metrics"],
            "evaluations": evaluations,
            "metric_families": sorted({e["family"] for e in evaluations}),
            "eval_categories": [c for c in EVAL_CATEGORIES if c in eval_cats],
            "fairness": s.get("fairness") or "",
            "robustness": s.get("robustness") or "",
            "privacy": s.get("privacy") or "",
            "embedding_extractor": clean(r["feature_extractor_for_embedding_metrics"]),
            "code": code,
            "code_flag": "Code available" if code else "No code link",
            "venue_type": venue_type(r["venue"]),
            "source": r["extraction_source"],
            "notes": r["notes"],
            "takeaway": takeaway(basename) if basename else "",
        })
    return papers


SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE papers (
    id                    TEXT PRIMARY KEY,   -- P001 ... (stable review ID)
    year                  INTEGER,
    title                 TEXT NOT NULL,
    venue                 TEXT,
    url                   TEXT,               -- DOI / arXiv / landing page
    model_family          TEXT,               -- free text as extracted
    task                  TEXT,
    datasets              TEXT,
    n_leads_generated     REAL,
    fs_hz                 REAL,               -- sampling rate used by the model
    segment_length_s      REAL,
    loss_functions        TEXT,               -- verbatim extracted losses
    eval_metrics          TEXT,               -- verbatim extracted metrics
    fairness              TEXT,               -- description of fairness analysis, if any
    robustness            TEXT,               -- description of robustness analysis, if any
    privacy               TEXT,               -- description of privacy analysis, if any
    embedding_extractor   TEXT,
    code_url              TEXT,
    extraction_source     TEXT,               -- full-text | abstract-only
    pdf_downloaded        INTEGER NOT NULL,
    background            INTEGER NOT NULL,   -- 1 for pre-Oct-2023 seminal works
    notes                 TEXT,
    takeaway              TEXT                -- takeaway for ECGEN-Eval
);

CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);

CREATE TABLE paper_authors (
    paper_id  TEXT    NOT NULL REFERENCES papers(id),
    author_id INTEGER NOT NULL REFERENCES authors(id),
    position  INTEGER NOT NULL,
    PRIMARY KEY (paper_id, author_id)
);

-- Facets are the filter dimensions; new dimensions are added as rows, not tables.
CREATE TABLE facets (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,
    label       TEXT NOT NULL,
    multi       INTEGER NOT NULL,           -- 1 if a paper can have several terms
    sort_order  INTEGER NOT NULL
);

-- Values of a facet. For metrics, parent_id is the default evaluation category and
-- ecgen_eval names the matching ECGEN-Eval metric key(s).
CREATE TABLE terms (
    id          INTEGER PRIMARY KEY,
    facet_id    INTEGER NOT NULL REFERENCES facets(id),
    name        TEXT NOT NULL,
    parent_id   INTEGER REFERENCES terms(id),
    ecgen_eval  TEXT,
    description TEXT,
    UNIQUE (facet_id, name)
);

CREATE TABLE paper_terms (
    paper_id TEXT    NOT NULL REFERENCES papers(id),
    term_id  INTEGER NOT NULL REFERENCES terms(id),
    PRIMARY KEY (paper_id, term_id)
);
CREATE INDEX idx_paper_terms_term ON paper_terms(term_id);

-- One row per metric / protocol a paper uses (or, for surveys, reviews).
CREATE TABLE evaluations (
    id          INTEGER PRIMARY KEY,
    paper_id    TEXT    NOT NULL REFERENCES papers(id),
    metric_name TEXT    NOT NULL,            -- as named in the paper
    family_id   INTEGER NOT NULL REFERENCES terms(id),   -- canonical metric family
    how         TEXT                         -- what was compared, on what features
);
CREATE INDEX idx_evaluations_paper ON evaluations(paper_id);

CREATE TABLE evaluation_categories (
    evaluation_id INTEGER NOT NULL REFERENCES evaluations(id),
    category_id   INTEGER NOT NULL REFERENCES terms(id),
    PRIMARY KEY (evaluation_id, category_id)
);

CREATE VIEW paper_facets AS
SELECT pt.paper_id, f.name AS facet, f.label AS facet_label, t.name AS term, t.ecgen_eval
FROM paper_terms pt
JOIN terms t  ON t.id = pt.term_id
JOIN facets f ON f.id = t.facet_id;

CREATE VIEW evaluation_details AS
SELECT e.id AS evaluation_id, e.paper_id, p.year, p.title, e.metric_name,
       fam.name AS family, cat.name AS category, fam.ecgen_eval, e.how
FROM evaluations e
JOIN papers p   ON p.id = e.paper_id
JOIN terms fam  ON fam.id = e.family_id
JOIN evaluation_categories ec ON ec.evaluation_id = e.id
JOIN terms cat  ON cat.id = ec.category_id;

-- ECG feature-extractor catalogue (independent of the papers tables).
CREATE TABLE extractors (
    id                  TEXT PRIMARY KEY,   -- X001 ...
    name                TEXT NOT NULL,
    category            TEXT NOT NULL,      -- delineation | dl_delineation | rpeak | hrv | sqi |
                                            -- ml_table | generic_ts | non_python |
                                            -- reference_measurements
    url                 TEXT,
    pypi                TEXT,
    install             TEXT,
    license             TEXT,
    license_class       TEXT,               -- permissive | copyleft | none | noncommercial |
                                            -- proprietary
    version             TEXT,
    release_date        TEXT,
    maintained          TEXT,               -- yes | stale | unknown
    language            TEXT,
    python_requires     TEXT,
    runtime_deps        TEXT,
    paper_citation      TEXT,
    paper_doi           TEXT,
    method              TEXT,
    n_features_reported INTEGER,            -- as stated by the tool / paper
    other_outputs       TEXT,               -- outputs without a feature_vocab id
    verified            TEXT,               -- source | docs | paper | readme
    notes               TEXT
);

-- What each extractor accepts and returns (one row per extractor).
CREATE TABLE extractor_inputs (
    extractor_id       TEXT PRIMARY KEY REFERENCES extractors(id),
    signal_types       TEXT,                -- e.g. "ECG; PPG"
    input_kinds        TEXT,                -- e.g. "raw_1d; wfdb_record"
    shape              TEXT,
    multilead          TEXT,                -- native | per-lead | single-lead
    fs_param           TEXT,                -- sampling-rate argument name
    fs_default         REAL,
    fs_supported       TEXT,
    fs_min_recommended REAL,
    fs_notes           TEXT,
    min_duration_s     REAL,
    duration_notes     TEXT,
    amplitude_units    TEXT,
    preprocessing      TEXT,
    batch              TEXT,
    output_format      TEXT,
    output_levels      TEXT                 -- e.g. "beat; record"
);

CREATE TABLE extractor_input_kinds (
    extractor_id TEXT NOT NULL REFERENCES extractors(id),
    kind         TEXT NOT NULL,             -- raw_1d | raw_multilead | wfdb_record | csv | edf |
                                            -- mat | rpeaks | rr_intervals | image
    PRIMARY KEY (extractor_id, kind)
);

CREATE TABLE extractor_signal_types (
    extractor_id TEXT NOT NULL REFERENCES extractors(id),
    signal_type  TEXT NOT NULL,             -- ECG | PPG | EDA | ...
    PRIMARY KEY (extractor_id, signal_type)
);

-- Canonical feature vocabulary; ecgen_eval_column links to ECGEN-Eval's summary_df.
CREATE TABLE feature_vocab (
    id                TEXT PRIMARY KEY,
    feature_group     TEXT NOT NULL,        -- fiducial | rate | interval | amplitude | ...
    name              TEXT NOT NULL,
    unit              TEXT,
    ecgen_eval_column TEXT,
    description       TEXT,
    sort_order        INTEGER NOT NULL
);

-- One row per (extractor, canonical feature, API): the native name(s) and where they come from.
CREATE TABLE extractor_features (
    id           INTEGER PRIMARY KEY,
    extractor_id TEXT NOT NULL REFERENCES extractors(id),
    feature_id   TEXT NOT NULL REFERENCES feature_vocab(id),
    native       TEXT,                      -- output key(s) / column name(s) in the tool
    api          TEXT,                      -- function or class that produces it
    level        TEXT,                      -- beat | lead | record | window | sample
    notes        TEXT
);
CREATE INDEX idx_extractor_features_feature ON extractor_features(feature_id);

CREATE TABLE extractor_evidence (
    extractor_id TEXT NOT NULL REFERENCES extractors(id),
    source       TEXT NOT NULL              -- URL or file that was read to verify the entry
);

CREATE VIEW extractor_feature_details AS
SELECT x.id AS extractor_id, x.name AS extractor, x.category, x.license, x.license_class,
       v.feature_group, v.id AS feature_id, v.name AS feature, v.unit, v.ecgen_eval_column,
       f.native, f.api, f.level, f.notes
FROM extractor_features f
JOIN extractors x    ON x.id = f.extractor_id
JOIN feature_vocab v ON v.id = f.feature_id;

CREATE VIEW feature_coverage AS
SELECT v.feature_group, v.id AS feature_id, v.name AS feature, v.ecgen_eval_column,
       COUNT(DISTINCT f.extractor_id) AS n_extractors,
       (SELECT group_concat(name, '; ') FROM (
            SELECT DISTINCT x.name FROM extractor_features f2
            JOIN extractors x ON x.id = f2.extractor_id
            WHERE f2.feature_id = v.id ORDER BY x.name)) AS extractors
FROM feature_vocab v
LEFT JOIN extractor_features f ON f.feature_id = v.id
GROUP BY v.id
ORDER BY v.sort_order;

-- For every ECGEN-Eval summary_df column: which extractors can provide it, and how.
CREATE VIEW ecgen_feature_support AS
SELECT v.ecgen_eval_column, v.name AS feature, x.name AS extractor, x.license_class,
       i.input_kinds, i.multilead, i.fs_supported, f.native, f.api
FROM feature_vocab v
JOIN extractor_features f ON f.feature_id = v.id
JOIN extractors x         ON x.id = f.extractor_id
JOIN extractor_inputs i   ON i.extractor_id = x.id
WHERE v.ecgen_eval_column IS NOT NULL
ORDER BY v.sort_order, x.name;

CREATE VIEW metric_usage AS
SELECT category, family AS metric, ecgen_eval, COUNT(DISTINCT paper_id) AS n_papers
FROM evaluation_details
GROUP BY category, family
ORDER BY category, n_papers DESC;
"""


def load_extractors() -> tuple[list[dict], list[dict]]:
    """Read the feature vocabulary and the extractor catalogue; check feature ids."""
    vocab_path, tools_path = EXTRACTORS / "feature_vocab.csv", EXTRACTORS / "tools.jsonl"
    if not (vocab_path.exists() and tools_path.exists()):
        return [], []
    vocab = list(csv.DictReader(vocab_path.open(newline="", encoding="utf-8-sig")))
    known = {v["id"] for v in vocab}
    tools = [json.loads(line) for line in tools_path.read_text().splitlines() if line.strip()]
    for t in tools:
        bad = sorted({f["feature"] for f in t.get("features", [])} - known)
        if bad:
            raise ValueError(f"{t['id']} {t['name']}: unknown feature ids {bad}")
    return vocab, tools


def joined(value) -> str:
    return "; ".join(map(str, value)) if isinstance(value, list) else (value or "")


def write_extractors(con: sqlite3.Connection, vocab: list[dict], tools: list[dict]) -> None:
    for i, v in enumerate(vocab):
        con.execute("INSERT INTO feature_vocab VALUES (?,?,?,?,?,?,?)",
                    (v["id"], v["group"], v["name"], v["unit"] or None,
                     v["ecgen_eval_column"] or None, v["description"] or None, i))
    for t in tools:
        inp, out = t.get("input", {}), t.get("output", {})
        con.execute(
            "INSERT INTO extractors VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (t["id"], t["name"], t["category"], t.get("url"), t.get("pypi"), t.get("install"),
             t.get("license"), t.get("license_class"), t.get("version"), t.get("release_date"),
             t.get("maintained"), t.get("language"), t.get("python_requires"),
             t.get("runtime_deps"), t.get("paper_citation"), t.get("paper_doi"),
             t.get("method"), t.get("n_features_reported"), joined(t.get("other_outputs")),
             t.get("verified"), t.get("notes")))
        con.execute(
            "INSERT INTO extractor_inputs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (t["id"], joined(inp.get("signal_types")), joined(inp.get("input_kinds")),
             inp.get("shape"), inp.get("multilead"), inp.get("fs_param"),
             number(inp.get("fs_default")) if inp.get("fs_default") is not None else None,
             inp.get("fs_supported"),
             number(inp.get("fs_min_recommended"))
             if inp.get("fs_min_recommended") is not None else None,
             inp.get("fs_notes"),
             number(inp.get("min_duration_s")) if inp.get("min_duration_s") is not None else None,
             inp.get("duration_notes"), inp.get("amplitude_units"), inp.get("preprocessing"),
             inp.get("batch"), out.get("format"), joined(out.get("levels"))))
        for k in dict.fromkeys(inp.get("input_kinds") or []):
            con.execute("INSERT INTO extractor_input_kinds VALUES (?,?)", (t["id"], k))
        for k in dict.fromkeys(inp.get("signal_types") or []):
            con.execute("INSERT INTO extractor_signal_types VALUES (?,?)", (t["id"], k))
        for f in t.get("features", []):
            con.execute(
                "INSERT INTO extractor_features (extractor_id, feature_id, native, api, level, "
                "notes) VALUES (?,?,?,?,?,?)",
                (t["id"], f["feature"], f.get("native"), f.get("api"), f.get("level"),
                 f.get("notes") or None))
        for src in t.get("evidence", []):
            con.execute("INSERT INTO extractor_evidence VALUES (?,?)", (t["id"], src))


def write_sqlite(papers: list[dict], meta: dict, path: Path) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO meta VALUES (?, ?)", meta.items())

    facet_ids = {}
    for i, (name, label, multi, _) in enumerate(FACETS):
        facet_ids[name] = con.execute(
            "INSERT INTO facets (name, label, multi, sort_order) VALUES (?,?,?,?)",
            (name, label, multi, i)).lastrowid

    term_ids: dict[tuple[str, str], int] = {}

    def term(facet: str, name: str, parent: int | None = None, ecgen: str = "",
             description: str = "") -> int:
        key = (facet, name)
        if key not in term_ids:
            term_ids[key] = con.execute(
                "INSERT INTO terms (facet_id, name, parent_id, ecgen_eval, description) "
                "VALUES (?,?,?,?,?)",
                (facet_ids[facet], name, parent, ecgen or None, description or None)).lastrowid
        return term_ids[key]

    # Register the controlled vocabularies so unused values are still queryable.
    for name, desc in EVAL_CATEGORIES.items():
        term("eval_category", name, description=desc)
    for name, (cat, ecgen, _) in METRICS.items():
        term("metric", name, term("eval_category", cat), ecgen)
    for vocab, facet in ((LOSSES, "loss"), (TASKS, "task"), (DATASETS, "dataset")):
        for name in vocab:
            term(facet, name)
    for name in MODEL_CATEGORIES.values():
        term("category", name)

    author_ids: dict[str, int] = {}
    for p in papers:
        con.execute(
            "INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (p["id"], p["year"], p["title"], p["venue"], p["url"], p["model_family"], p["task"],
             p["datasets"], p["n_leads_generated"], p["fs_hz_model"], p["segment_length_model"],
             p["loss_functions"], p["eval_metrics"], p["fairness"], p["robustness"],
             p["privacy"], p["embedding_extractor"], p["code"], p["source"],
             int(p["downloaded"]), int(p["background"]), p["notes"], p["takeaway"]))
        for pos, name in enumerate(p["authors"]):
            if name not in author_ids:
                author_ids[name] = con.execute(
                    "INSERT INTO authors (name) VALUES (?)", (name,)).lastrowid
            con.execute("INSERT OR IGNORE INTO paper_authors VALUES (?,?,?)",
                        (p["id"], author_ids[name], pos))
        for e in p["evaluations"]:
            fam = e["family"]
            parent = term("eval_category", METRICS[fam][0]) if fam in METRICS else None
            eid = con.execute(
                "INSERT INTO evaluations (paper_id, metric_name, family_id, how) VALUES (?,?,?,?)",
                (p["id"], e["metric"], term("metric", fam, parent), e["how"])).lastrowid
            for c in e["categories"]:
                con.execute("INSERT OR IGNORE INTO evaluation_categories VALUES (?,?)",
                            (eid, term("eval_category", c)))
        for facet, _, _, key in FACETS:
            vals = p[key] if isinstance(p[key], list) else [p[key]]
            for v in vals:
                if v not in (None, ""):
                    con.execute("INSERT OR IGNORE INTO paper_terms VALUES (?,?)",
                                (p["id"], term(facet, str(v))))
    write_extractors(con, *load_extractors())
    con.commit()
    con.execute("VACUUM")
    con.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true", help="include abstract-only papers too")
    args = ap.parse_args()

    papers = build(args.all)
    vocab, tools = load_extractors()
    meta = {
        "generated": date.today().isoformat(),
        "n_papers": str(len(papers)),
        "scope": "all indexed papers" if args.all else "papers with downloaded full text",
        "review_window": "2023-10-01 to 2026-10-25",
        "source": "literature_review_claude/papers_index.csv + structured_extraction.jsonl",
        "n_extractors": str(len(tools)),
        "n_feature_vocab": str(len(vocab)),
        "extractors_source": "literature_review_claude/feature_extractors/tools.jsonl",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_sqlite(papers, meta, DB_PATH)

    flat = ["id", "year", "title", "authors", "venue", "url", "category", "model_family", "task",
            "conditioning", "data_type", "data_format", "n_leads_generated", "fs_hz_model",
            "segment_length_model", "datasets", "data_access", "loss_functions", "loss_families",
            "eval_metrics", "metric_families", "eval_categories", "fairness", "robustness",
            "privacy", "embedding_extractor", "code", "venue_type", "source", "notes",
            "takeaway"]
    with (OUT_DIR / "papers.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(flat)
        for p in papers:
            w.writerow(["; ".join(map(str, p[k])) if isinstance(p[k], list) else p[k]
                        for k in flat])
    print(f"wrote {len(papers)} papers to {DB_PATH} and {OUT_DIR / 'papers.csv'}")
    if tools:
        write_extractor_csv(vocab, tools)
        print(f"wrote {len(tools)} feature extractors ({len(vocab)} vocabulary features)")


def write_extractor_csv(vocab: list[dict], tools: list[dict]) -> None:
    """Flat tool list and a feature x tool support matrix, for spreadsheets."""
    cols = ["id", "name", "category", "url", "install", "license", "license_class", "version",
            "release_date", "maintained", "language", "runtime_deps", "paper_doi", "method"]
    icols = ["signal_types", "input_kinds", "shape", "multilead", "fs_param", "fs_default",
             "fs_supported", "fs_min_recommended", "fs_notes", "min_duration_s",
             "amplitude_units", "preprocessing"]
    with (OUT_DIR / "feature_extractors.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols + icols + ["output_format", "n_vocab_features", "features"])
        for t in tools:
            inp = t.get("input", {})
            feats = sorted({x["feature"] for x in t.get("features", [])})
            w.writerow([joined(t.get(k)) for k in cols] + [joined(inp.get(k)) for k in icols]
                       + [t.get("output", {}).get("format", ""), len(feats), "; ".join(feats)])
    with (OUT_DIR / "feature_support_matrix.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["feature_group", "feature_id", "feature", "ecgen_eval_column"]
                   + [t["name"] for t in tools])
        have = [{x["feature"] for x in t.get("features", [])} for t in tools]
        for v in vocab:
            w.writerow([v["group"], v["id"], v["name"], v["ecgen_eval_column"]]
                       + ["x" if v["id"] in h else "" for h in have])


if __name__ == "__main__":
    main()
