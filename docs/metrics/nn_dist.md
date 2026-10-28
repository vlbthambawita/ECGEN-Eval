# Nearest-Neighbour Distance (`nn_dist`)

**Key:** `nn_dist` · **Family:** privacy · **Better:** lower ↓ (score), higher (authenticity) ·
**Per-lead:** yes

`nn_dist` asks two related questions:

- **Score**: *how close is each real ECG to its nearest synthetic ECG?*
- **Authenticity** (in `extra`): *what share of synthetic ECGs are genuinely new, rather than
  near-copies of a real recording?*

Generators trained on patient data can memorise training examples, which is a privacy risk.

## Try it

Lines connect each synthetic point to its nearest real point. Red lines are closer than a
typical real point is to its own nearest real neighbour, which is suspiciously close.

<div class="mviz" data-viz="nndist">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- With **novel samples**, the score is about the same as the real → real baseline, and
  authenticity is around 0.5.
- As more samples are **copied**, the score falls *below* the baseline and authenticity drops
  towards 0. A lower score is not always better: far below the real-real baseline means
  memorisation, not quality.

## How it works

For each lead:

1. Describe every recording with the **7-feature descriptor** and divide each feature by its
   standard deviation in the real set.
2. **Score**: for each real recording, find the distance to its nearest synthetic recording,
   then average.
3. **Threshold**: for each real recording, find the distance to its nearest *other* real
   recording; take the median.
4. **Authenticity**: the fraction of synthetic recordings whose nearest real recording is
   farther than that threshold.

## The math

\[
\text{score} = \frac{1}{n}\sum_{i=1}^{n} \min_j \lVert x_i - y_j\rVert,
\qquad
\tau = \operatorname{median}_i \min_{i'\neq i} \lVert x_i - x_{i'}\rVert
\]

\[
\text{authenticity} = \frac{1}{m}\sum_{j=1}^{m} \mathbb 1\!\left[\min_i \lVert y_j - x_i\rVert > \tau\right]
\]

## Reading the score

- Compare the score with the **real → real** nearest-neighbour distance. Much smaller means
  near-duplicates; much larger means the synthetic data is far from the real data.
- For a good generator with novel samples, authenticity is around 0.5, because half of real
  points are themselves closer than the median. Values near 0 are a red flag.
- Compute it against the **training** set the generator saw: that is where memorisation
  would show.
- Feature-space distances are a quick screen, not a privacy guarantee. Membership-inference
  attacks and distance-to-closest-record tests on raw signals are stronger checks (see the
  literature review's [privacy papers](../literature/database.md#metrics/Privacy)).

## Use it with ECGEN-Eval

=== "CLI"

    ```bash
    ecgen-eval eval --real train.npy --synthetic synth.npy -m nn_dist --output report.html
    ```

=== "Python"

    ```python
    from ecgen_eval import load_ecg_npy, AVAILABLE_METRICS

    train = load_ecg_npy("train.npy", fs=500)   # the generator's training data
    synth = load_ecg_npy("synth.npy", fs=500)

    result = AVAILABLE_METRICS["nn_dist"]().compute(train.data, synth.data, lead_names=train.lead_names)
    print("NN distance:", result.score)
    print("authenticity:", result.extra["authenticity"])
    ```

Parameters are in the [Metric Reference](../user-guide/metric-reference.md#nn_dist).

## Learn more

- Meehan et al., *A Non-Parametric Test to Detect Data-Copying in Generative Models*,
  AISTATS 2020.
- Alaa et al., *How Faithful is your Synthetic Data?*, ICML 2022 (authenticity).
