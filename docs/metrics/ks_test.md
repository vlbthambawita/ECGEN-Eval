# Kolmogorov–Smirnov Test

**Key:** `ks_test` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** yes

The two-sample Kolmogorov–Smirnov (KS) test asks: *could these two sets of numbers have been
drawn from the same distribution?* It compares the two cumulative distributions and reports
the largest gap between them, \(D\). 19 papers in the
[literature review](../literature/database.md#metrics/Fidelity) use statistical tests on real against synthetic
data, and the KS test is the most common one.

## Try it

Each curve shows, for every value on the x-axis, the share of recordings at or below it. The
red line marks the largest vertical gap, which is \(D\).

<div class="mviz" data-viz="ksTest">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Shifted mean** moves one curve sideways; **Too uniform** makes it steeper. Both open a
  gap, so the KS test reacts to changes in location and in spread.
- **Small shift, 50 recordings** against **Same shift, 1000 recordings**: \(D\) stays about
  the same, but the p-value collapses from "not significant" to "< 0.001". The difference
  between the two sets did not change; only the amount of data did.

That is why the score of this metric is \(D\) and not the p-value.

## How it works

1. Per lead, describe every recording by 7 numbers: mean, standard deviation, RMS, maximum
   absolute amplitude, energy, zero-crossing rate and lag-1 autocorrelation.
2. For each of the 7 features, compute \(D\) between the real and the synthetic values.
3. The lead score is the mean \(D\) over the 7 features; the overall score is the mean over
   leads.
4. p-values go to `extra`, raw and adjusted for multiple testing (Holm by default) over all
   features × leads.

## The math

With empirical distribution functions \(F_r\) and \(F_s\):

\[
D = \sup_x \big| F_r(x) - F_s(x) \big|
\]

The p-value comes from SciPy when it is installed, and otherwise from the asymptotic
Kolmogorov distribution with \(n_e = n_r n_s / (n_r + n_s)\):

\[
p \approx 2 \sum_{j=1}^{\infty} (-1)^{j-1} e^{-2 j^2 \lambda^2},
\qquad \lambda = \Big(\sqrt{n_e} + 0.12 + \tfrac{0.11}{\sqrt{n_e}}\Big) D
\]

## Reading the score

- \(D\) ranges from 0 (identical distributions) to 1 (no overlap). It is an effect size and
  does not depend on the units of the feature.
- `extra["per_feature_D"]` shows which feature differs most. A high \(D\) for `std`, `rms`
  and `energy` together means an amplitude problem; a high \(D\) for `zero_crossing_rate`
  points to noise or frequency content.
- `extra["frac_rejected"]` is the share of the feature × lead tests rejected at `alpha` after
  correction. With thousands of recordings almost every test is rejected, even for
  negligible differences. Do not use it to compare runs of different size.
- [P020](../literature/database.md#papers/P020) tested a per-feature KS similarity under perturbations and found it stable
  under amplitude changes of the synthetic data.

### KS on clinical features

Several papers run the test on physiological quantities instead of signal statistics: heart
rate and SDNN ([P074](../literature/database.md#papers/P074)), intervals and amplitudes ([P080](../literature/database.md#papers/P080)). ECGEN-Eval does this in
the report: with `--feature-plots`, the Clinical Feature Summary table gets a **KS D** and an
adjusted **p** column for every feature. In Python:

```python
from ecgen_eval.features import extract_features, compare_feature_distributions

_, real_feat = extract_features(real)
_, synth_feat = extract_features(synth)
print(compare_feature_distributions(real_feat, synth_feat))
#           feature  n_real  n_synth  ks_D  ks_p  ks_p_adjusted  mwu_p  cohens_d
```

`ecgen-eval features ... --stats-output stats.csv` writes the same table. See
[Clinical Features](../user-guide/features.md#statistical-comparison).

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy -m ks_test --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["ks_test"]().compute(real.data, synth.data, lead_names=real.lead_names)
    print("mean D:", result.score, result.extra["per_feature_D"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#ks_test).

## Learn more

- Massey (1951). The Kolmogorov-Smirnov test for goodness of fit. *J. Am. Stat. Assoc.*
  46(253), 68–78.
  [doi:10.1080/01621459.1951.10500769](https://doi.org/10.1080/01621459.1951.10500769)
- Related: [`mmd`](mmd.md) and [`swd`](swd.md) compare the same 7 features jointly instead of
  one at a time; [`c2st`](c2st.md) asks a classifier.
- How papers use it: [Paper Database](../literature/database.md#metrics/Fidelity), family *Statistical tests*.
