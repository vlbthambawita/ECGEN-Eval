# P-wave duration

**Column:** `p_wave_duration_ms` · **Unit:** ms · **Measured on:** lead II (default)

**In one sentence:** the P wave is the small bump before the main spike, made by the two upper
chambers (the **atria**) activating; its duration is how long that takes.

!!! example "Everyday picture"
    The P wave is the "starter" of each beat: the upper chambers give a small squeeze to top up
    the lower chambers before the main pump stroke. A longer P wave means the electrical wave
    takes longer to cross the upper chambers, for example because they are stretched.

## Try it

Change the width and height of the P wave. Try **No P wave** too: without it there is nothing
to measure.

<div class="mviz" data-viz="clinical" data-focus="p">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **The P wave is small**, usually well under a quarter of the R spike, so it is the first thing
  to disappear in noise.
- **No P wave** means the beat did not start from the heart's normal pacemaker. In real ECGs
  this happens in some rhythm problems such as atrial fibrillation.

## What's typical

| P-wave duration | Plain meaning |
|---|---|
| up to about 120 ms (3 small boxes) | typical |
| longer than 120 ms | the upper chambers take longer to activate, often because they are enlarged |

## Why it matters for synthetic ECGs

The P wave is easy for a generator to get wrong because it is small: it may be missing, smeared
into the baseline, or merged into the QRS. A synthetic set that mostly lacks P waves does not
represent normal (sinus) rhythm, even if every other part looks right.

## How ECGEN-Eval measures it

`p_wave_duration_ms` is the time from P-wave start to P-wave end, median over beats.
NeuroKit2's peak-prominence delineator finds the P wave on every lead. Its start and end are
then moved in to where the wave reaches 15 % of its height, and the leads are combined with
the median.

Needs NeuroKit2 (`NaN` without it). The P wave is small and its edges are gentle, so this is
the least precise feature: against GE 12SL the typical error is 12 ms (r 0.41), and even two
commercial programs only reach r 0.48 ([validation](index.md#validation)).

## Learn more

- [PR interval](pr-interval.md): the P wave plus the pause that follows.
- Kligfield et al. (2007), AHA/ACC/HRS *Recommendations for the standardization and interpretation of the
  electrocardiogram*, Part I. [doi:10.1161/CIRCULATIONAHA.106.180200](https://doi.org/10.1161/CIRCULATIONAHA.106.180200)
