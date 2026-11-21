"""
Classifier two-sample test (C2ST) / discriminative score for ECG evaluation.

Reference
---------
Lopez-Paz, D., & Oquab, M. (2017).
Revisiting classifier two-sample tests.
*International Conference on Learning Representations (ICLR)*.
https://arxiv.org/abs/1610.06545

Yoon, J., Jarrett, D., & van der Schaar, M. (2019).
Time-series generative adversarial networks.
*Advances in Neural Information Processing Systems (NeurIPS)*, 32.

Implementation notes
--------------------
A classifier is trained to tell real recordings (label 0) from synthetic ones
(label 1). If it cannot do better than chance, the two sets are indistinguishable
*for that classifier and those features*.

Per lead:

1. Balance the classes by subsampling both sets to the same size.
2. Describe each recording by features (``features='handcrafted'``: the 11 signal
   features of ``fd``; ``'signal'``: the decimated waveform reduced by PCA).
3. Get out-of-fold predictions with stratified k-fold cross-validation. Scaling and
   PCA are fitted inside each training fold.
4. Discriminative score = max(0, accuracy − 0.5)   (0 = indistinguishable, 0.5 =
   fully separable). This equals TimeGAN's |0.5 − accuracy| whenever the accuracy is
   at or above chance. Below-chance accuracy is an artefact of small samples or of
   recordings that appear in both sets, not evidence of a difference, so it is
   clipped to 0; the raw accuracy stays in ``extra``.

Accuracy, ROC AUC and a one-sided binomial p-value (accuracy above chance) are in
``extra``, together with one classifier trained on all leads at once.

A copy of the real data scores 0, so this metric cannot detect memorisation; use
``nn_dist`` for that.
"""

from __future__ import annotations

import math
import warnings
from typing import List, Optional

import numpy as np

from ecgen_eval.metrics._matching import subsample
from ecgen_eval.metrics._signal_features import EXTENDED_FEATURE_NAMES, extended_features
from ecgen_eval.metrics.base import BaseMetric, MetricResult

_REFERENCE = (
    "Lopez-Paz, D., & Oquab, M. (2017). Revisiting classifier two-sample tests. "
    "International Conference on Learning Representations (ICLR). "
    "https://arxiv.org/abs/1610.06545"
)

_DESCRIPTION = (
    "Classifier Two-Sample Test: discriminative score (accuracy − 0.5) of a cross-validated "
    "real-vs-synthetic classifier, per lead. Lower is better (0 = indistinguishable)."
)

CLASSIFIERS = ("logreg", "rf", "knn")
FEATURES = ("handcrafted", "signal")


class C2STMetric(BaseMetric):
    """
    Discriminative score of a real-vs-synthetic classifier, per lead.

    Parameters
    ----------
    classifier : {'logreg', 'rf', 'knn'}
        Logistic regression (default), random forest (100 trees) or 1-nearest
        neighbour.
    features : {'handcrafted', 'signal'}
        'handcrafted' (default): 11 signal features per lead. 'signal': waveform
        decimated to at most 250 points, then PCA to at most 32 components.
    n_splits : int
        Cross-validation folds. Default: 5.
    n_subsample : int
        Max recordings per class. Default: 1000.
    seed : int
        Random seed. Default: 42.
    """

    name = "c2st"
    description = _DESCRIPTION
    reference = _REFERENCE
    higher_is_better = False

    def __init__(
        self,
        classifier: str = "logreg",
        features: str = "handcrafted",
        n_splits: int = 5,
        n_subsample: int = 1000,
        seed: int = 42,
    ):
        if classifier not in CLASSIFIERS:
            raise ValueError(f"Unknown classifier {classifier!r}. Choose one of {CLASSIFIERS}.")
        if features not in FEATURES:
            raise ValueError(f"Unknown features {features!r}. Choose one of {FEATURES}.")
        self.classifier = classifier
        self.features = features
        self.n_splits = n_splits
        self.n_subsample = n_subsample
        self.seed = seed

    # ------------------------------------------------------------------ #
    # BaseMetric interface                                                 #
    # ------------------------------------------------------------------ #

    def compute(
        self,
        real: np.ndarray,
        synth: np.ndarray,
        lead_names: Optional[List[str]] = None,
    ) -> MetricResult:
        self._check_inputs(real, synth)
        n_leads = real.shape[1]
        if lead_names is None:
            lead_names = [f"L{i+1}" for i in range(n_leads)]

        rng = np.random.default_rng(self.seed)
        n = min(real.shape[0], synth.shape[0], self.n_subsample)
        r = subsample(real, n, rng)
        s = subsample(synth, n, rng)
        y = np.concatenate([np.zeros(n, dtype=int), np.ones(n, dtype=int)])

        nan = float("nan")
        per_lead = {ln: nan for ln in lead_names}
        acc = dict(per_lead)
        auc = dict(per_lead)
        extra = {
            "classifier": self.classifier,
            "features": self.features,
            "n_per_class": int(n),
        }

        if n < 4:
            warnings.warn(
                f"c2st needs at least 4 recordings per class, got {n}; returning NaN.",
                RuntimeWarning,
            )
            return self._result(nan, per_lead, extra)

        n_splits = max(2, min(self.n_splits, n))
        extra["n_splits"] = n_splits
        folds: dict = {}
        blocks = []
        importance = np.zeros(len(EXTENDED_FEATURE_NAMES))

        for li, lname in enumerate(lead_names):
            X = np.concatenate([self._featurize(r[:, li, :]), self._featurize(s[:, li, :])])
            blocks.append(X)
            res = self._cross_validate(X, y, n_splits)
            per_lead[lname] = max(0.0, res["accuracy"] - 0.5)
            acc[lname] = res["accuracy"]
            auc[lname] = res["auc"]
            folds[lname] = res["fold_accuracy"]
            if self.classifier == "logreg" and self.features == "handcrafted":
                importance += self._coefficients(X, y)

        all_res = self._cross_validate(np.concatenate(blocks, axis=1), y, n_splits)
        extra.update({
            "per_lead_accuracy": acc,
            "per_lead_auc": auc,
            "per_lead_fold_accuracy": folds,
            "accuracy": float(np.mean(list(acc.values()))),
            "auc": float(np.mean(list(auc.values()))),
            "all_leads": {
                "accuracy": all_res["accuracy"],
                "auc": all_res["auc"],
                "score": max(0.0, all_res["accuracy"] - 0.5),
                "p_above_chance": all_res["p_above_chance"],
            },
        })
        if self.classifier == "logreg" and self.features == "handcrafted":
            extra["feature_importance"] = {
                name: float(v / n_leads) for name, v in zip(EXTENDED_FEATURE_NAMES, importance)
            }
        if 2 * n <= 2000:
            extra["one_nn_loo_accuracy"] = self._one_nn_loo(np.concatenate(blocks, axis=1), y)

        return self._result(float(np.mean(list(per_lead.values()))), per_lead, extra)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _result(self, score: float, per_lead: dict, extra: dict) -> MetricResult:
        return MetricResult(
            metric_name=self.name,
            score=score,
            higher_is_better=self.higher_is_better,
            per_lead_scores=per_lead,
            description=self.description,
            reference=self.reference,
            extra=extra,
        )

    def _featurize(self, signals: np.ndarray) -> np.ndarray:
        if self.features == "handcrafted":
            return extended_features(signals)
        stride = max(1, int(np.ceil(signals.shape[1] / 250)))
        return np.asarray(signals[:, ::stride], dtype=np.float64)

    def _pipeline(self, n_train: int, n_features: int):
        from sklearn.decomposition import PCA
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        steps = [StandardScaler()]
        if self.features == "signal":
            steps.append(PCA(n_components=min(32, n_features, n_train - 1),
                             random_state=self.seed))
        if self.classifier == "logreg":
            steps.append(LogisticRegression(max_iter=1000))
        elif self.classifier == "rf":
            steps.append(RandomForestClassifier(n_estimators=100, random_state=self.seed))
        else:
            steps.append(KNeighborsClassifier(n_neighbors=1))
        return make_pipeline(*steps)

    def _cross_validate(self, X: np.ndarray, y: np.ndarray, n_splits: int) -> dict:
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import StratifiedKFold

        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        prob = np.empty(len(y))
        fold_acc = []
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=self.seed)
        for train, test in cv.split(X, y):
            model = self._pipeline(len(train), X.shape[1]).fit(X[train], y[train])
            prob[test] = model.predict_proba(X[test])[:, 1]
            fold_acc.append(float(np.mean((prob[test] > 0.5) == y[test])))
        correct = int(np.sum((prob > 0.5) == y))
        return {
            "accuracy": correct / len(y),
            "auc": float(roc_auc_score(y, prob)),
            "fold_accuracy": fold_acc,
            "p_above_chance": _binomial_p_above_half(correct, len(y)),
        }

    def _coefficients(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """|coefficient| per standardised feature of a logistic regression on all data."""
        model = self._pipeline(len(y), X.shape[1]).fit(np.nan_to_num(X), y)
        return np.abs(model[-1].coef_[0])

    @staticmethod
    def _one_nn_loo(X: np.ndarray, y: np.ndarray) -> float:
        """Leave-one-out 1-NN accuracy on standardised features (0.5 is ideal)."""
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
        sq = np.einsum("ij,ij->i", X, X)
        d = sq[:, None] + sq[None, :] - 2.0 * (X @ X.T)
        np.fill_diagonal(d, np.inf)
        return float(np.mean(y[np.argmin(d, axis=1)] == y))


def _binomial_p_above_half(k: int, n: int) -> float:
    """One-sided p-value P(X ≥ k) for X ~ Binomial(n, 0.5), normal approximation."""
    if n == 0:
        return float("nan")
    z = (k - 0.5 - n / 2.0) / math.sqrt(n / 4.0)
    return float(0.5 * math.erfc(z / math.sqrt(2.0)))
