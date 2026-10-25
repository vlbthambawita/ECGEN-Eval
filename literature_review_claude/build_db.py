"""Build the literature-review database used by the documentation site.

Reads ``papers_index.csv`` (one row per paper, produced by the review) plus the
per-paper notes in ``notes/`` and writes a normalised SQLite database to
``docs/literature/ecgen_literature.sqlite`` (and a flat CSV copy). The "Paper Database"
docs page opens the SQLite file in the browser with sql.js and filters it there.

Schema: ``papers``, ``authors`` + ``paper_authors``, and a generic facet model
(``facets`` -> ``terms`` -> ``paper_terms``) so new filter dimensions or values are added as
rows rather than new tables. Views ``paper_facets`` and ``metric_usage`` simplify queries.

Only papers whose PDF has been downloaded (``pdf_path`` is not "not downloaded")
are included by default, because their entries were extracted from the full text.
Pass ``--all`` to also include abstract-only entries.

Usage::

    python literature_review_claude/build_db.py          # downloaded papers only
    python literature_review_claude/build_db.py --all    # every indexed paper
"""

from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = HERE / "papers_index.csv"
NOTES = HERE / "notes"
OUT_DIR = ROOT / "docs" / "literature"
DB_PATH = OUT_DIR / "ecgen_literature.sqlite"

CATEGORIES = {
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

# metric family -> (metric type, ECGEN-Eval key or "", regex over the extracted metric text)
METRICS = {
    "RMSE": ("fidelity", "mae (extra)", r"\brmse\b|root mean squared? error"),
    "MAE": ("fidelity", "mae", r"\bmae\b|mean absolute error"),
    "MSE": ("fidelity", "", r"\bmse\b|mean squared? error"),
    "PRD": ("fidelity", "prd", r"\bprd\b|percent(age)? root.mean"),
    "Pearson / correlation": ("fidelity", "", r"pearson|correlation coeff|\bpcc\b|cross-?correlation"),
    "DTW": ("fidelity", "dtw", r"\bdtw\b|dynamic time warp"),
    "Curve Fréchet distance": (
        "fidelity", "", r"(discrete|curve)[- ]?fr[eé]chet|fr[eé]chet distance \(fd\)|\bfd\b"),
    "PSNR / SNR": ("fidelity", "psnr", r"psnr|\bsnr\b|signal.to.noise"),
    "SSIM": ("fidelity", "ssim", r"ssim|structural similarity"),
    "Euclidean distance": ("fidelity", "", r"euclidean"),
    "Cosine similarity": ("fidelity", "", r"cosine"),
    "Spectral / PSD similarity": (
        "fidelity", "psd", r"\bpsd\b|spectral (similarity|distance|entropy)|power spectr|spectrum"),
    "FID / embedding Fréchet": (
        "distribution", "fed",
        r"\bfid\b|fr[eé]chet incep|fr[eé]chet (ecg|resnet)|\bfrd\b|\bfed\b|context-fid|rfid"),
    "MMD": ("distribution", "mmd", r"\bmmd\b|maximum mean discrep"),
    "Wasserstein / EMD": ("distribution", "swd", r"wasserstein|\bemd\b|earth mover"),
    "KL / JS divergence": ("distribution", "", r"kullback|\bkl\b|jensen|\bjsd?\b"),
    "Precision / recall / coverage": (
        "distribution", "pr_dist",
        r"precision.recall \(|\bdensity\b|coverage|α-precision|alpha-precision|beta-recall|improved precision|manifold|k-nn precision"),
    "Classifier two-sample test": (
        "distribution", "",
        r"discriminative score|two-sample|2-sample|c2st|real.vs.?.?(fake|synthetic) classif|1-?nn|nearest.neighbou?r adversarial|nnaa"),
    "Statistical tests": (
        "distribution", "", r"\bks\b|kolmogorov|t-test|hotelling|wilcoxon|mann.whitney|permutation|delong"),
    "t-SNE / UMAP / PCA plots": ("visual", "", r"t-?sne|umap|pacmap|\bpca\b"),
    "Heart rate / HRV": ("clinical", "heart_rate, hrv", r"heart.rate|\bhr\b|\brr\b|hrv|sdnn|rmssd|pnn50"),
    "Clinical intervals (PR/QRS/QT)": (
        "clinical", "features module", r"\bqtc?\b|\bpr interval|\bpr\b|qrs (duration|width)|\bst\b"),
    "Fiducial / R-peak timing": (
        "clinical", "", r"r-?peak|fiducial|peak (timing|detection)|beat timing"),
    "Inter-lead consistency": ("clinical", "", r"einthoven|inter-?lead|lead correlation|goldberger"),
    "Signal quality index": ("clinical", "sqi", r"\bsqi\b|signal quality|kurtosis"),
    "Downstream classification": (
        "utility", "", r"accuracy|\bf1\b|auroc|\bauc\b|sensitivity|specificity|g-mean"),
    "TSTR / TRTS": ("utility", "", r"tstr|trts|train(ed)? on synthetic|train synthetic|trstr|trsts"),
    "Label / condition adherence": (
        "conditional", "", r"label faithful|controllab|conditioned vs generated|\bclip\b|rclip|alignment score|adherence"),
    "Expert / Turing test": (
        "expert", "", r"cardiologist|expert|turing|clinician|physician|visual (inspection|assessment)"),
    "Privacy / memorisation": (
        "privacy", "nn_dist",
        r"membership|privacy|re-?identif|memori[sz]|\bdcr\b|authenticity|\bmir\b|\bmia\b"),
    "Efficiency (NFE / runtime)": (
        "efficiency", "",
        r"\bnfe\b|inference (time|speed|steps)|sampling (steps|time|speed)|runtime|latency|function evaluations|parameters"),
}

LOSSES = {
    "Adversarial (GAN)": r"adversarial|minimax|\bgan\b|\bbce\b|binary cross",
    "WGAN / gradient penalty": r"wgan|wasserstein|gradient penalty",
    "Least-squares / hinge GAN": r"lsgan|least.squares|hinge",
    "L1 reconstruction": r"\bl1\b|mean absolute|absolute error",
    "L2 / MSE reconstruction": r"\bl2\b|\bmse\b|mean squared",
    "Diffusion noise prediction": (
        r"noise.prediction|ε|epsilon|ddpm|l_simple|denoising (score|loss|objective)|predicted noise|score matching|v-prediction"),
    "Flow-matching velocity": r"flow matching|rectified|velocity",
    "KL / ELBO": r"\bkl\b|kullback|elbo|evidence lower",
    "Classification CE": r"cross.entropy|auxiliary classif|classification loss",
    "Spectral / frequency": r"spectral|frequency|fft|stft|mel|fourier|wavelet|dwt",
    "Physiology / physics": (
        r"\bode\b|physio|physics|einthoven|goldberger|lead constraint|simulator|morpholog|r-peak|peak loss|qrs|pde"),
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

TAGS = ["fidelity", "distribution", "clinical", "utility", "expert", "privacy", "efficiency"]

UNKNOWN = re.compile(r"^(unknown|not reported|n/?a|none)", re.I)


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


def build(include_all: bool) -> list[dict]:
    rows = list(csv.DictReader(INDEX.open(newline="")))
    papers = []
    for r in rows:
        downloaded = r["pdf_path"] != "not downloaded"
        if not downloaded and not include_all:
            continue
        basename = Path(r["pdf_path"]).stem if downloaded else ""
        metrics_text = r["eval_metrics"]
        metric_fams = families(metrics_text, METRICS)
        tags = [t for t in TAGS if t in r["eval_category_tags"].lower()]
        if "utility-tstr" in r["eval_category_tags"].lower() and "utility" not in tags:
            tags.append("utility")
        authors = [a.strip() for a in r["authors"].split(";") if a.strip()]
        papers.append({
            "id": r["id"],
            "year": int(r["year"]) if r["year"].isdigit() else None,
            "title": r["title"],
            "authors": authors,
            "venue": r["venue"],
            "url": r["doi_or_url"],
            "category": CATEGORIES.get(r["category"], r["category"]),
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
            "loss_functions": r["loss_functions"],
            "loss_families": families(r["loss_functions"], LOSSES),
            "eval_metrics": metrics_text,
            "metric_families": metric_fams,
            "metric_types": sorted({METRICS[f][0] for f in metric_fams} | set(tags)),
            "embedding_extractor": clean(r["feature_extractor_for_embedding_metrics"]),
            "code": r["code_available"] if r["code_available"].lower().startswith("http") else "",
            "source": r["extraction_source"],
            "notes": r["notes"],
            "takeaway": takeaway(basename) if basename else "",
        })
    return papers


SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE papers (
    id                  TEXT PRIMARY KEY,   -- P001 ... (stable review ID)
    year                INTEGER,
    title               TEXT NOT NULL,
    venue               TEXT,
    url                 TEXT,               -- DOI / arXiv / landing page
    model_family        TEXT,               -- free text as extracted
    task                TEXT,
    datasets            TEXT,
    n_leads             TEXT,
    fs_hz               TEXT,
    signal_length_s     TEXT,
    loss_functions      TEXT,               -- verbatim extracted losses
    eval_metrics        TEXT,               -- verbatim extracted metrics
    embedding_extractor TEXT,
    code_url            TEXT,
    extraction_source   TEXT,               -- full-text | abstract-only
    pdf_downloaded      INTEGER NOT NULL,   -- 1 if the PDF is in the review folder
    background          INTEGER NOT NULL,   -- 1 for pre-Oct-2023 seminal works
    notes               TEXT,
    takeaway            TEXT                -- takeaway for ECGEN-Eval
);

CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);

CREATE TABLE paper_authors (
    paper_id  TEXT    NOT NULL REFERENCES papers(id),
    author_id INTEGER NOT NULL REFERENCES authors(id),
    position  INTEGER NOT NULL,
    PRIMARY KEY (paper_id, author_id)
);

-- Facets are the filter dimensions (category, metric, loss, ...). New dimensions are added as
-- rows here, not as new tables.
CREATE TABLE facets (
    id          INTEGER PRIMARY KEY,
    name        TEXT UNIQUE NOT NULL,       -- machine name, e.g. 'metric'
    label       TEXT NOT NULL,              -- display name, e.g. 'Metric'
    multi       INTEGER NOT NULL,           -- 1 if a paper can have several terms
    sort_order  INTEGER NOT NULL
);

-- Terms are the values within a facet. parent_id links e.g. a metric to its metric type.
CREATE TABLE terms (
    id          INTEGER PRIMARY KEY,
    facet_id    INTEGER NOT NULL REFERENCES facets(id),
    name        TEXT NOT NULL,
    parent_id   INTEGER REFERENCES terms(id),
    ecgen_eval  TEXT,                       -- matching ECGEN-Eval metric key(s), if any
    UNIQUE (facet_id, name)
);

CREATE TABLE paper_terms (
    paper_id TEXT    NOT NULL REFERENCES papers(id),
    term_id  INTEGER NOT NULL REFERENCES terms(id),
    PRIMARY KEY (paper_id, term_id)
);

CREATE INDEX idx_paper_terms_term ON paper_terms(term_id);

-- Convenience view: one row per (paper, facet, term).
CREATE VIEW paper_facets AS
SELECT pt.paper_id, f.name AS facet, f.label AS facet_label, t.name AS term, t.ecgen_eval
FROM paper_terms pt
JOIN terms t  ON t.id = pt.term_id
JOIN facets f ON f.id = t.facet_id;

-- Convenience view: metrics with their type and ECGEN-Eval coverage, and usage counts.
CREATE VIEW metric_usage AS
SELECT m.name AS metric, mt.name AS metric_type, m.ecgen_eval, COUNT(pt.paper_id) AS n_papers
FROM terms m
JOIN facets f ON f.id = m.facet_id AND f.name = 'metric'
LEFT JOIN terms mt ON mt.id = m.parent_id
LEFT JOIN paper_terms pt ON pt.term_id = m.id
GROUP BY m.id ORDER BY n_papers DESC;
"""

# name, label, multi, paper-dict key
FACETS = [
    ("category", "Category", 0, "category"),
    ("year", "Year", 0, "year"),
    ("metric_type", "Metric type", 1, "metric_types"),
    ("metric", "Metric", 1, "metric_families"),
    ("loss", "Loss function", 1, "loss_families"),
    ("task", "Task", 1, "task_tags"),
    ("dataset", "Dataset", 1, "dataset_tags"),
    ("extraction_source", "Extraction source", 0, "source"),
]


def write_sqlite(papers: list[dict], meta: dict, path: Path) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO meta VALUES (?, ?)", meta.items())

    facet_ids = {}
    for i, (name, label, multi, _) in enumerate(FACETS):
        cur = con.execute("INSERT INTO facets (name, label, multi, sort_order) VALUES (?,?,?,?)",
                          (name, label, multi, i))
        facet_ids[name] = cur.lastrowid

    term_ids: dict[tuple[str, str], int] = {}

    def term(facet: str, name: str, parent: int | None = None, ecgen: str = "") -> int:
        key = (facet, name)
        if key not in term_ids:
            cur = con.execute(
                "INSERT INTO terms (facet_id, name, parent_id, ecgen_eval) VALUES (?,?,?,?)",
                (facet_ids[facet], name, parent, ecgen or None))
            term_ids[key] = cur.lastrowid
        return term_ids[key]

    # Register the full vocabularies so unused terms are still queryable.
    types = sorted({v[0] for v in METRICS.values()} | set(TAGS))
    for t in types:
        term("metric_type", t)
    for name, (mtype, ecgen, _) in METRICS.items():
        term("metric", name, term("metric_type", mtype), ecgen)
    for name in LOSSES:
        term("loss", name)
    for name in TASKS:
        term("task", name)
    for name in DATASETS:
        term("dataset", name)
    for name in CATEGORIES.values():
        term("category", name)

    author_ids: dict[str, int] = {}
    for p in papers:
        con.execute(
            "INSERT INTO papers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (p["id"], p["year"], p["title"], p["venue"], p["url"], p["model_family"], p["task"],
             p["datasets"], p["n_leads"], p["fs_hz"], p["signal_length_s"], p["loss_functions"],
             p["eval_metrics"], p["embedding_extractor"], p["code"], p["source"],
             int(p["downloaded"]), int(p["background"]), p["notes"], p["takeaway"]))
        for pos, name in enumerate(p["authors"]):
            if name not in author_ids:
                author_ids[name] = con.execute(
                    "INSERT INTO authors (name) VALUES (?)", (name,)).lastrowid
            con.execute("INSERT OR IGNORE INTO paper_authors VALUES (?,?,?)",
                        (p["id"], author_ids[name], pos))
        for facet, _, _, key in FACETS:
            vals = p[key] if isinstance(p[key], list) else [p[key]]
            for v in vals:
                if v not in (None, ""):
                    con.execute("INSERT OR IGNORE INTO paper_terms VALUES (?,?)",
                                (p["id"], term(facet, str(v))))
    con.commit()
    con.execute("VACUUM")
    con.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true", help="include abstract-only papers too")
    args = ap.parse_args()

    papers = build(args.all)
    meta = {
        "generated": date.today().isoformat(),
        "n_papers": str(len(papers)),
        "scope": "all indexed papers" if args.all else "papers with downloaded full text",
        "review_window": "2023-10-01 to 2026-10-25",
        "source": "literature_review_claude/papers_index.csv",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_sqlite(papers, meta, DB_PATH)

    flat =["id", "year", "title", "authors", "venue", "url", "category", "model_family", "task",
            "datasets", "n_leads", "fs_hz", "signal_length_s", "loss_functions", "loss_families",
            "eval_metrics", "metric_families", "metric_types", "embedding_extractor", "code",
            "source", "notes", "takeaway"]
    with (OUT_DIR / "papers.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(flat)
        for p in papers:
            w.writerow(["; ".join(p[k]) if isinstance(p[k], list) else p[k] for k in flat])
    print(f"wrote {len(papers)} papers to {DB_PATH} and {OUT_DIR / 'papers.csv'}")


if __name__ == "__main__":
    main()
