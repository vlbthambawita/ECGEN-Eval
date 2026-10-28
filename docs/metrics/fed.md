# Fréchet ECG Distance (FED)

**Key:** `fed` · **Family:** distribution · **Better:** lower ↓ · **Per-lead:** no ·
**Extras:** `pip install "ecgen-eval[fed]"` ([installation](#installation))

FED asks: *if a model that has seen millions of real ECGs describes each recording as a
vector, do the real and synthetic sets look like the same population?* It is the ECG
counterpart of the Fréchet Inception Distance (FID) used for images.

## Try it

Each dot is one ECG, placed by two of the foundation model's embedding dimensions (real
embeddings have hundreds of dimensions; the demo shows two). FED fits a Gaussian to each cloud,
drawn here as an ellipse, and measures how far apart the two Gaussians are.

<div class="mviz" data-viz="frechet" data-variant="fed">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **Shifted mean** raises only the *mean term*: the synthetic ECGs are systematically different,
  for example in heart rate or amplitude.
- **Too little variety** raises the *covariance term*. A generator that produces near-identical
  ECGs (mode collapse) is penalised even when its average ECG is perfect.
- **Wrong correlation** keeps both clouds centred and equally wide, but the relationship
  between features is wrong. FED still sees it.
- **Only 30 samples**: identical distributions no longer score 0. Fréchet distances are
  biased upward for small samples, so the *real vs real* card is the floor you should compare
  against.

## How it works

[![FED pipeline: real and synthetic ECGs are embedded by a foundation model, Gaussians are fitted and compared with the Fréchet distance](../assets/diagrams/fed-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/fed-light.svg "Open full size")
[![FED pipeline: real and synthetic ECGs are embedded by a foundation model, Gaussians are fitted and compared with the Fréchet distance](../assets/diagrams/fed-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/fed-dark.svg "Open full size")

1. **Embed.** Every recording, shape `(leads, time)`, is passed through a pre-trained ECG
   foundation model (ECGFounder, HuBERT-ECG or ECG-FM), giving one vector of length *D*.
2. **Fit Gaussians.** Compute the mean vector *μ* and the covariance matrix *Σ* of the real
   embeddings, and the same for the synthetic embeddings.
3. **Compare.** Compute the Fréchet (2-Wasserstein) distance between the two Gaussians.

## The math

\[
\mathrm{FED} = \underbrace{\lVert \mu_r - \mu_s \rVert_2^2}_{\text{mean term}}
+ \underbrace{\operatorname{Tr}\!\left(\Sigma_r + \Sigma_s - 2\,(\Sigma_r\Sigma_s)^{1/2}\right)}_{\text{covariance term}}
\]

This is the squared 2-Wasserstein distance between \(\mathcal N(\mu_r,\Sigma_r)\) and
\(\mathcal N(\mu_s,\Sigma_s)\): the minimum average squared distance needed to move one
Gaussian onto the other. ECGEN-Eval adds \(\varepsilon = 10^{-6}\) to the covariance
diagonals before taking the matrix square root, for numerical stability.

## Reading the score

- **0** means identical embedding means and covariances. There is no upper bound.
- Values are **only comparable within one backbone**: each model has its own embedding size
  and scale.
- Use the **same number of recordings** for every model you compare (ideally several hundred
  or more). Fewer samples inflate the score.
- Report a **real-vs-real** FED (two disjoint halves of the real data) as the reference floor.
- FED only sees what the backbone encodes. Embeddings are trained for diagnosis, so FED is
  sensitive to clinically relevant morphology and may ignore some artefacts.
- FED summarises whole recordings: there are no per-lead scores.

## Installation

FED needs PyTorch and the Hugging Face libraries, which are optional extras:

```bash
pip install "ecgen-eval[fed]"   # torch, transformers, huggingface_hub
```

## Backbones

| `backbone` | Model | Architecture | Pre-training data | Hugging Face repo |
|---|---|---|---|---|
| `ecgfounder` *(default)* | ECGFounder | RegNet CNN | 10.7 M ECGs, 150 labels | `PKUDigitalHealth/ECGFounder` |
| `hubert_ecg` | HuBERT-ECG (base) | Transformer (HuBERT) | 9.1 M ECGs | `Edoardo-BS/hubert-ecg-base` |
| `ecgfm` | ECG-FM | wav2vec 2.0-style CNN + Transformer | 1.5 M ECGs (MIMIC-IV-ECG) | `bowang-lab/ECG-FM` |

How each adapter turns an `(N, L, T)` array into `(N, D)` embeddings:

- **ECGFounder** expects 12 leads; inputs with fewer leads are padded by repeating the last lead.
- **HuBERT-ECG** encodes each lead independently, mean-pools the last hidden state over time,
  then averages the per-lead embeddings.
- **ECG-FM** expects 12-lead input at 500 Hz and mean-pools the context-encoder output over time.

!!! tip "Match the backbone's expectations"
    Foundation models are trained on specific sampling rates and lead layouts (typically
    12-lead, 500 Hz). Resample and order leads accordingly for meaningful embeddings.

To add a new backbone, see [Adding a FED Backbone](../development/adding-backbones.md).

## Weights and caching

Weights are downloaded from the Hugging Face Hub **on the first `compute()` call**, not at
import or construction time, and cached locally. To control where they go:

```bash
export HF_HOME=/data/hf-cache
```

If a model repository is gated, log in first with `huggingface-cli login`.

## Use it with ECGEN-Eval

FED is not run by default, because it downloads model weights on first use. Request it with
`-m fed`:

=== "CLI"

    ```bash
    ecgen-eval eval --real real.npy --synthetic synth.npy \
      -m fed --backbone ecgfounder --fed-device cuda --fed-batch-size 64 \
      --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy
    from ecgen_eval.metrics import FEDMetric

    real = load_ecg_npy("real.npy", fs=500)
    synth = load_ecg_npy("synth.npy", fs=500)

    fed = FEDMetric(backbone="ecgfounder", device="cuda", batch_size=64)
    result = fed.compute(real.data, synth.data)
    print(result.score, result.extra["backbone"])
    ```

Compare all three backbones:

```python
for bb in ["ecgfounder", "hubert_ecg", "ecgfm"]:
    r = FEDMetric(backbone=bb, device="cuda").compute(real.data, synth.data)
    print(f"{bb:>11}: {r.score:.3f}")
```

All parameters (`backbone`, `device`, `batch_size`, `n_subsample`, `eps`) are in the
[Metric Reference](../user-guide/metric-reference.md#fed).

## Using the encoders directly

The encoder adapters can be used on their own, for example for t-SNE or UMAP plots of the
embeddings:

```python
from ecgen_eval.metrics.encoders import get_encoder

enc = get_encoder("ecgfounder", device="cuda", batch_size=32)
emb = enc.encode(real.data)   # (N, D)
```

## Learn more

- Heusel et al., *GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash
  Equilibrium*, NeurIPS 2017. This paper introduced FID.
- [Fréchet Distance (FD)](fd.md): the same formula on handcrafted features.
- The literature review's [Paper Database](../literature/database.md#metrics/Fidelity) lists
  the papers that report FID-style embedding distances for ECG.
