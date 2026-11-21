"""
2-D embedding projections (PCA, t-SNE, UMAP) of real and synthetic ECG sets.

These plots are qualitative. Two choices make them less misleading:

* the projection is fitted **on the real data only** (PCA, UMAP) and the synthetic
  data is projected into it, so a synthetic set cannot shape the map it is judged on;
* the real data is drawn as a density, with synthetic points on top, so samples that
  fall off the real manifold stand out.

t-SNE has no out-of-sample transform, so it is always fitted jointly.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Union

import numpy as np
import plotly.graph_objects as go

from ecgen_eval.data.dataset import ECGDataset

METHODS = ("pca", "tsne", "umap")
FEATURE_SETS = ("handcrafted", "signal", "clinical")

_REAL_POINT = "rgba(31, 119, 180, 0.35)"
_SYNTH_POINTS = [
    "rgba(255, 127, 14, 0.75)",
    "rgba(44, 160, 44, 0.75)",
    "rgba(214, 39, 40, 0.75)",
    "rgba(148, 103, 189, 0.75)",
]

ArrayLike = Union[ECGDataset, np.ndarray, "pd.DataFrame"]  # noqa: F821


def _feature_matrix(obj, features: str) -> np.ndarray:
    """Turn a dataset / array / DataFrame into an (N, F) matrix."""
    if isinstance(obj, ECGDataset):
        obj = obj.data
    if hasattr(obj, "select_dtypes"):  # pandas DataFrame of clinical features
        skip = {"sample_idx", "beat_idx", "r_sample"}
        num = obj.select_dtypes(include=[np.number])
        return num[[c for c in num.columns if c not in skip]].to_numpy(dtype=np.float64)
    arr = np.asarray(obj)
    if arr.ndim == 2:  # precomputed features or embeddings
        return arr.astype(np.float64)
    if arr.ndim != 3:
        raise ValueError(f"Expected (N, L, T) signals or (N, F) features, got shape {arr.shape}")
    if features == "signal":
        stride = max(1, int(np.ceil(arr.shape[2] / 250)))
        return arr[:, :, ::stride].reshape(arr.shape[0], -1).astype(np.float64)
    if features == "handcrafted":
        from ecgen_eval.metrics._signal_features import extended_features

        return np.concatenate(
            [extended_features(arr[:, li, :]) for li in range(arr.shape[1])], axis=1
        )
    raise ValueError(
        f"features={features!r} needs a DataFrame (clinical) or is unknown. "
        f"Choose one of {FEATURE_SETS} or pass (N, F) arrays."
    )


def compute_embedding_2d(
    real: ArrayLike,
    synths: Union[Sequence[ArrayLike], Dict[str, ArrayLike]],
    method: str = "pca",
    features: str = "handcrafted",
    fit_on: str = "real",
    n_subsample: int = 1000,
    seed: int = 42,
    **method_kwargs,
) -> dict:
    """
    Project real and synthetic sets to 2-D.

    Parameters
    ----------
    real : ECGDataset, (N, L, T) array, (N, F) array, or clinical-feature DataFrame
    synths : list (or {label: ...} dict) of the same kind of object
    method : 'pca' | 'tsne' | 'umap' ('umap' needs ``pip install "ecgen-eval[umap]"``)
    features : 'handcrafted' (11 signal features per lead), 'signal' (decimated
        waveform, reduced to 50 principal components first) or 'clinical' (pass the
        ``summary_df`` DataFrames from ``FeatureExtractor``). Ignored for (N, F) arrays.
    fit_on : 'real' (default) or 'joint'. t-SNE is always joint.
    n_subsample : max points per set; every set is cut to the same count
    seed : random seed
    **method_kwargs : forwarded to the projector (e.g. ``perplexity=`` for t-SNE,
        ``n_neighbors=`` for UMAP)

    Returns
    -------
    dict with ``real`` (N, 2), ``synth`` {label: (N, 2)} and ``meta`` (method,
    features, fit_on, n_per_set, n_dropped, axis_labels, real_label).
    """
    method = method.lower()
    if method not in METHODS:
        raise ValueError(f"Unknown method {method!r}. Choose one of {METHODS}.")
    if fit_on not in ("real", "joint"):
        raise ValueError("fit_on must be 'real' or 'joint'.")

    if isinstance(synths, dict):
        labels, synth_objs = list(synths.keys()), list(synths.values())
    else:
        synth_objs = list(synths)
        labels = [getattr(s, "label", None) or f"Synthetic {i + 1}"
                  for i, s in enumerate(synth_objs)]
    real_label = getattr(real, "label", None) or "Real"
    seen: Dict[str, int] = {}
    for i, lab in enumerate(labels):  # two datasets may share a label; keep both
        seen[lab] = seen.get(lab, 0) + 1
        if seen[lab] > 1:
            labels[i] = f"{lab} ({seen[lab]})"

    mats = [_feature_matrix(o, features) for o in [real] + synth_objs]
    n_dropped = []
    for i, m in enumerate(mats):  # rows with NaN/inf cannot be projected
        ok = np.isfinite(m).all(axis=1)
        n_dropped.append(int((~ok).sum()))
        mats[i] = m[ok]
    if min(len(m) for m in mats) < 3:
        raise ValueError("Each set needs at least 3 complete rows for a 2-D embedding.")
    if len({m.shape[1] for m in mats}) != 1:
        raise ValueError("Real and synthetic feature matrices have different widths.")

    rng = np.random.default_rng(seed)
    n = min(min(len(m) for m in mats), n_subsample)
    index = []
    for i, m in enumerate(mats):
        idx = np.sort(rng.choice(len(m), size=n, replace=False)) if len(m) > n else np.arange(n)
        index.append(idx)
        mats[i] = m[idx]

    if method == "tsne":
        fit_on = "joint"
    X_real, X_all = mats[0], np.concatenate(mats)
    X_fit = X_real if fit_on == "real" else X_all

    # Standardise, then (for raw signals) compress, using the fit set only.
    mu, sd = X_fit.mean(axis=0), X_fit.std(axis=0) + 1e-12
    X_fit_s, X_all_s = (X_fit - mu) / sd, (X_all - mu) / sd
    if X_all_s.shape[1] > 50:
        from sklearn.decomposition import PCA

        pre = PCA(n_components=min(50, len(X_fit_s) - 1), random_state=seed).fit(X_fit_s)
        X_fit_s, X_all_s = pre.transform(X_fit_s), pre.transform(X_all_s)

    axis_labels = [f"{method.upper()} 1", f"{method.upper()} 2"]
    if method == "pca":
        from sklearn.decomposition import PCA

        proj = PCA(n_components=2, random_state=seed, **method_kwargs).fit(X_fit_s)
        Z = proj.transform(X_all_s)
        ev = 100.0 * proj.explained_variance_ratio_
        axis_labels = [f"PC1 ({ev[0]:.1f} % of {fit_on} variance)",
                       f"PC2 ({ev[1]:.1f} % of {fit_on} variance)"]
    elif method == "tsne":
        from sklearn.manifold import TSNE

        kwargs = dict(method_kwargs)
        max_perp = max(1.0, (len(X_all_s) - 1) / 3.0)
        kwargs["perplexity"] = float(min(kwargs.get("perplexity", 30.0), max_perp))
        kwargs.setdefault("init", "pca")
        Z = TSNE(n_components=2, random_state=seed, **kwargs).fit_transform(X_all_s)
    else:
        try:
            import umap
        except ImportError as exc:
            raise ImportError(
                "method='umap' needs umap-learn. Install it with "
                '`pip install "ecgen-eval[umap]"` or use method="pca".'
            ) from exc
        kwargs = dict(method_kwargs)
        kwargs["n_neighbors"] = int(min(kwargs.get("n_neighbors", 15), len(X_fit_s) - 1))
        reducer = umap.UMAP(n_components=2, random_state=seed, **kwargs).fit(X_fit_s)
        Z = reducer.transform(X_all_s) if fit_on == "real" else reducer.embedding_

    return {
        "real": Z[:n],
        "synth": {lab: Z[n * (i + 1): n * (i + 2)] for i, lab in enumerate(labels)},
        "meta": {
            "method": method,
            "features": features,
            "fit_on": fit_on,
            "n_per_set": int(n),
            "n_dropped": dict(zip([real_label] + labels, n_dropped)),
            "indices": dict(zip([real_label] + labels, [i.tolist() for i in index])),
            "axis_labels": axis_labels,
            "real_label": real_label,
        },
    }


def plot_embedding_2d(embedding: dict, title: Optional[str] = None) -> go.Figure:
    """
    Plot the output of :func:`compute_embedding_2d`.

    Real data: density contours plus faint points. Each synthetic set: points in its
    own colour. Hover shows the row index of the sample in its (NaN-filtered) set.
    """
    meta = embedding["meta"]
    real = np.asarray(embedding["real"])
    idx = meta.get("indices", {})
    fig = go.Figure()
    fig.add_trace(go.Histogram2dContour(
        x=real[:, 0], y=real[:, 1], name=f"{meta['real_label']} (density)",
        colorscale="Blues", showscale=False, ncontours=8, opacity=0.55,
        contours=dict(showlines=True), line=dict(width=1), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=real[:, 0], y=real[:, 1], mode="markers", name=meta["real_label"],
        marker=dict(size=4, color=_REAL_POINT),
        customdata=idx.get(meta["real_label"]),
        hovertemplate="<b>%{fullData.name}</b><br>sample %{customdata}<extra></extra>",
    ))
    for si, (label, pts) in enumerate(embedding["synth"].items()):
        pts = np.asarray(pts)
        fig.add_trace(go.Scatter(
            x=pts[:, 0], y=pts[:, 1], mode="markers", name=label,
            marker=dict(size=5, color=_SYNTH_POINTS[si % len(_SYNTH_POINTS)]),
            customdata=idx.get(label),
            hovertemplate="<b>%{fullData.name}</b><br>sample %{customdata}<extra></extra>",
        ))
    fit = "fitted on real data only" if meta["fit_on"] == "real" else "joint fit (real + synthetic)"
    fig.update_layout(
        title=title or (f"{meta['method'].upper()} projection of {meta['features']} features "
                        f"— {fit}, {meta['n_per_set']} points per set"),
        xaxis_title=meta["axis_labels"][0], yaxis_title=meta["axis_labels"][1],
        height=560, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="rgba(200,200,200,0.5)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.5)", zeroline=False)
    return fig
