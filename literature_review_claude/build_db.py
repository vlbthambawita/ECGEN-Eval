"""Build the literature-review database used by the documentation site.

Reads ``papers_index.csv`` (one row per paper, produced by the review) plus the
per-paper notes in ``notes/`` and writes a normalised JSON database to
``docs/literature/papers.json`` (and a CSV copy) that the "Paper Database" docs page
loads and filters in the browser.

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
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX = HERE / "papers_index.csv"
NOTES = HERE / "notes"
OUT_DIR = ROOT / "docs" / "literature"

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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true", help="include abstract-only papers too")
    args = ap.parse_args()

    papers = build(args.all)
    meta = {
        "generated": date.today().isoformat(),
        "n_papers": len(papers),
        "scope": "all indexed papers" if args.all else "papers with downloaded full text",
        "metric_families": {k: {"type": v[0], "ecgen_eval": v[1]} for k, v in METRICS.items()},
        "loss_families": list(LOSSES),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "papers.json").write_text(
        json.dumps({"meta": meta, "papers": papers}, ensure_ascii=False, indent=1) + "\n")

    flat = ["id", "year", "title", "authors", "venue", "url", "category", "model_family", "task",
            "datasets", "n_leads", "fs_hz", "signal_length_s", "loss_functions", "loss_families",
            "eval_metrics", "metric_families", "metric_types", "embedding_extractor", "code",
            "source", "notes", "takeaway"]
    with (OUT_DIR / "papers.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(flat)
        for p in papers:
            w.writerow(["; ".join(p[k]) if isinstance(p[k], list) else p[k] for k in flat])
    print(f"wrote {len(papers)} papers to {OUT_DIR / 'papers.json'}")


if __name__ == "__main__":
    main()
