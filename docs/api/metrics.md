# Metrics

## Registry

`AVAILABLE_METRICS` maps each metric key (as used by `ecgen-eval eval -m KEY`) to its class.

```python
from ecgen_eval.metrics import AVAILABLE_METRICS
metric = AVAILABLE_METRICS["mmd"]()
```

## Base classes

::: ecgen_eval.metrics.base.MetricResult

::: ecgen_eval.metrics.base.BaseMetric

## Fréchet utilities

::: ecgen_eval.metrics._frechet_utils
    options:
      show_root_heading: false
      filters: []

## Pairing helpers

Shared by `mse`, `rmse`, `euclidean`, `pearson`, `cosine` and `curve_frechet`. See
[Matching protocol](../user-guide/metric-reference.md#matching-protocol).

::: ecgen_eval.metrics._matching
    options:
      show_root_heading: false
      filters: []

::: ecgen_eval.metrics._pairwise.PairwiseSignalMetric

## Divergence, feature and test utilities

::: ecgen_eval.metrics._divergence
    options:
      show_root_heading: false
      filters: []

::: ecgen_eval.metrics._signal_features
    options:
      show_root_heading: false
      filters: []

::: ecgen_eval.metrics._stats
    options:
      show_root_heading: false
      filters: []

::: ecgen_eval.metrics.curve_frechet.discrete_frechet

## Metric classes

::: ecgen_eval.metrics.mmd.MMDMetric

::: ecgen_eval.metrics.fd.FDMetric

::: ecgen_eval.metrics.fed.FEDMetric

::: ecgen_eval.metrics.swd.SWDMetric

::: ecgen_eval.metrics.pr_dist.PRDistMetric

::: ecgen_eval.metrics.js_div.AmplitudeJSMetric

::: ecgen_eval.metrics.ks_test.KSTestMetric

::: ecgen_eval.metrics.c2st.C2STMetric

::: ecgen_eval.metrics.dtw.DTWMetric

::: ecgen_eval.metrics.prd.PRDMetric

::: ecgen_eval.metrics.mae.MAEMetric

::: ecgen_eval.metrics.psnr.PSNRMetric

::: ecgen_eval.metrics.ssim.SSIMMetric

::: ecgen_eval.metrics.mse.MSEMetric

::: ecgen_eval.metrics.mse.RMSEMetric

::: ecgen_eval.metrics.euclidean.EuclideanMetric

::: ecgen_eval.metrics.pearson.PearsonMetric

::: ecgen_eval.metrics.cosine.CosineMetric

::: ecgen_eval.metrics.curve_frechet.CurveFrechetMetric

::: ecgen_eval.metrics.sqi.SQIMetric

::: ecgen_eval.metrics.psd.PSDMetric

::: ecgen_eval.metrics.spectral_entropy.SpectralEntropyMetric

::: ecgen_eval.metrics.hrv.HRVMetric

::: ecgen_eval.metrics.heart_rate.HeartRateMetric

::: ecgen_eval.metrics.nn_dist.NNDistMetric

