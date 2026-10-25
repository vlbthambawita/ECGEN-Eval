# Fréchet ECG Distance (FED)

FED is the ECG counterpart of the Fréchet Inception Distance (FID) for images and the
Fréchet Audio Distance (FAD) for audio. Instead of handcrafted features (as in
[`fd`](metric-reference.md#fd)), it embeds every recording with a **pre-trained ECG foundation
model** and compares the Gaussian statistics of the real and synthetic embeddings:

\[
\mathrm{FED} = \lVert \mu_r - \mu_s \rVert^2 + \operatorname{Tr}\!\left(\Sigma_r + \Sigma_s - 2(\Sigma_r\Sigma_s)^{1/2}\right)
\]

Lower is better; 0 means identical embedding statistics.

[![FED pipeline: real and synthetic ECGs are embedded by a foundation model, Gaussians are fitted and compared with the Fréchet distance](../assets/diagrams/fed-light.svg#only-light){ .ecgen-diagram }](../assets/diagrams/fed-light.svg "Open full size")
[![FED pipeline: real and synthetic ECGs are embedded by a foundation model, Gaussians are fitted and compared with the Fréchet distance](../assets/diagrams/fed-dark.svg#only-dark){ .ecgen-diagram }](../assets/diagrams/fed-dark.svg "Open full size")

## Installation

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

## Weights and caching

Weights are downloaded from the Hugging Face Hub **on the first `compute()` call** — not at
import or construction time — and cached locally. To control where they go:

```bash
export HF_HOME=/data/hf-cache
```

If a model repository is gated, log in first with `huggingface-cli login`.

## Usage

=== "CLI"

    ```bash
    ecgen-eval eval \
      --real real.npy --synthetic synth.npy \
      -m fed --backbone ecgfounder --fed-device cuda --fed-batch-size 64 \
      --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval.metrics import FEDMetric

    fed = FEDMetric(backbone="hubert_ecg", device="cuda", batch_size=64)
    result = fed.compute(real.data, synth.data)
    print(result.score, result.extra["backbone"])
    ```

Compare all three backbones:

```python
for bb in ["ecgfounder", "hubert_ecg", "ecgfm"]:
    r = FEDMetric(backbone=bb, device="cuda").compute(real.data, synth.data)
    print(f"{bb:>11}: {r.score:.3f}")
```

## Interpreting FED

- FED values are **only comparable within the same backbone** — embedding dimensionality and
  scale differ between models.
- Fréchet distances are biased upward for small sample sizes. Use the same number of
  recordings (`n_subsample`) for every model you compare, ideally ≥ a few hundred.
- Compute a **real-vs-real** FED (two disjoint halves of the real set) as a reference floor.
- FED has no per-lead breakdown: embeddings describe the whole recording.

## Using the encoders directly

The encoder adapters can be used on their own, e.g. for t-SNE/UMAP visualisations of
embeddings:

```python
from ecgen_eval.metrics.encoders import get_encoder

enc = get_encoder("ecgfounder", device="cuda", batch_size=32)
emb = enc.encode(real.data)   # (N, D)
```

To add a new backbone, see [Adding a FED Backbone](../development/adding-backbones.md).
