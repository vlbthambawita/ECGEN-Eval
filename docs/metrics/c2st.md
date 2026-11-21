# Classifier Two-Sample Test

**Key:** `c2st` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

The classifier two-sample test asks: *can a classifier learn to tell real ECGs from synthetic
ones?* If its accuracy on held-out data stays at 50 %, the two sets are indistinguishable for
that classifier. The further above 50 %, the easier the synthetic data is to spot. 14 papers
in the [literature review](../literature/database.md#metrics/Fidelity) use a variant of it; the best known is the
*discriminative score* of TimeGAN.

## Try it

Each point is one recording described by two features. Hollow points were misclassified on
held-out data.

<div class="mviz" data-viz="c2st">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Indistinguishable**: accuracy is near 50 % and the score near 0.
- **Shifted**: the classes separate and the score approaches 0.5.
- **Too narrow, linear classifier** against **Too narrow, 1-NN classifier**: the synthetic
  data sits in the middle of the real data. A straight line cannot separate that, so the
  linear classifier reports "indistinguishable". The 1-NN classifier sees the difference.
  The score depends on the classifier you choose.

## How it works

1. Subsample both sets to the same size, so that chance level is exactly 50 %.
2. Per lead, describe each recording by features: the 11 signal features of [`fd`](fd.md)
   (`features="handcrafted"`, default) or the decimated waveform reduced by PCA
   (`features="signal"`).
3. Label real recordings 0 and synthetic recordings 1 and run stratified `n_splits`-fold
   cross-validation. Scaling and PCA are fitted inside each training fold, so nothing leaks
   from the test fold.
4. Score the out-of-fold predictions.

ECGEN-Eval also trains one classifier on the features of all leads together and reports it in
`extra["all_leads"]`. It is usually better at spotting synthetic data than any single lead.

## The math

\[
\texttt{c2st} = \max\big(0,\; \mathrm{accuracy} - 0.5\big)
\]

This equals TimeGAN's discriminative score \(|0.5 - \mathrm{accuracy}|\) whenever the
accuracy is at or above chance. Accuracy below 50 % on held-out data is an artefact (very
small sets, or the same recording present in both sets) and not evidence of a difference, so
it is clipped to 0. The raw accuracy is in `extra`.

## Reading the score

- 0 = the classifier is at chance; 0.5 = it separates the sets perfectly.
- **The score is only comparable between runs with the same `classifier` and `features`**
  ([P043](../literature/database.md#papers/P043)). A weak classifier makes every generator look good. Report both settings.
- Look at `extra["auc"]` as well: it uses the predicted probabilities and is more sensitive
  than accuracy when the classes overlap.
- `extra["all_leads"]["p_above_chance"]` is a one-sided binomial p-value for "accuracy is
  above 50 %".
- With the default settings, `extra["feature_importance"]` lists the mean absolute
  logistic-regression coefficient of each feature: which property gives the synthetic data
  away.
- A generator that copies its training data scores 0. This metric cannot detect
  memorisation; use [`nn_dist`](nn_dist.md).
- Published results span the whole range: [P116](../literature/database.md#papers/P116) reports an AUC of 0.68 for a diffusion
  model and 1.00 for TimeGAN on the same data.

| `classifier` | Model | Notes |
|---|---|---|
| `"logreg"` (default) | Logistic regression | Fast; only finds differences a linear boundary can separate |
| `"rf"` | Random forest, 100 trees | Finds non-linear differences; much slower |
| `"knn"` | 1-nearest neighbour | Non-linear, no training; weak in high dimensions |

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m c2st --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["c2st"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("score:", result.score, "accuracy:", result.extra["accuracy"], "AUC:", result.extra["auc"])
    ```

```python
# A stronger, slower test
metric = AVAILABLE_METRICS["c2st"](classifier="rf", features="handcrafted")
```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#c2st).

## Learn more

- Lopez-Paz & Oquab (2017). Revisiting classifier two-sample tests. *ICLR*.
  [arXiv:1610.06545](https://arxiv.org/abs/1610.06545)
- Yoon, Jarrett & van der Schaar (2019). Time-series generative adversarial networks.
  *NeurIPS* 32 (discriminative score).
- Related: [`ks_test`](ks_test.md) tests one feature at a time; [`mmd`](mmd.md) is a kernel
  two-sample test; [`pr_dist`](pr_dist.md) separates realism from coverage.
