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

## Metric classes

::: ecgen_eval.metrics.mmd.MMDMetric

::: ecgen_eval.metrics.fd.FDMetric

::: ecgen_eval.metrics.fed.FEDMetric

::: ecgen_eval.metrics.swd.SWDMetric

::: ecgen_eval.metrics.pr_dist.PRDistMetric

::: ecgen_eval.metrics.dtw.DTWMetric

::: ecgen_eval.metrics.prd.PRDMetric

::: ecgen_eval.metrics.mae.MAEMetric

::: ecgen_eval.metrics.psnr.PSNRMetric

::: ecgen_eval.metrics.ssim.SSIMMetric

::: ecgen_eval.metrics.sqi.SQIMetric

::: ecgen_eval.metrics.psd.PSDMetric

::: ecgen_eval.metrics.spectral_entropy.SpectralEntropyMetric

::: ecgen_eval.metrics.hrv.HRVMetric

::: ecgen_eval.metrics.heart_rate.HeartRateMetric

::: ecgen_eval.metrics.nn_dist.NNDistMetric

