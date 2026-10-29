# QT interval & QTc

**Columns:** `qt_interval_ms`, `qtc_bazett_ms` · **Unit:** ms · **Measured on:** lead II (default)

**In one sentence:** the QT interval runs from the start of the main spike to the end of the T
wave, the full time the lower chambers need to activate **and recharge**; QTc is the same
time corrected for heart rate.

!!! example "Everyday picture"
    Think of the lower chambers as a camera flash that has to recharge before it can fire again.
    QT is "fire + recharge". The heart recharges faster when it beats faster, so a raw QT
    can't be compared between a slow and a fast heart. QTc converts every QT to what it would
    be at 60 bpm, which makes them comparable.

## Try it

Try the presets in order. **Same QT, faster heart** keeps the QT at 400 ms but raises the heart
rate: the QTc jumps, because at 100 bpm a 400 ms recharge is slow.

<div class="mviz" data-viz="clinical" data-focus="qt">Interactive demo loading… (needs JavaScript)</div>

What to notice:

- **QT alone depends on the heart rate.** That is why doctors, and ECGEN-Eval, also report QTc.
- **Bazett's correction:** QTc = QT ÷ √RR, with RR in seconds. At 60 bpm RR = 1 s, so QTc = QT.
- **Long QT** means the lower chambers recharge slowly. Doctors watch for this because a very
  long QTc raises the risk of dangerous heart rhythms, and some medicines lengthen it.

## What's typical

| QTc | Plain meaning |
|---|---|
| under 350 ms | short |
| about 350–450 ms | typical (the upper limit is a little higher for women, about 460 ms) |
| 450–500 ms | long-ish, worth a second look |
| over 500 ms | long |

## Why it matters for synthetic ECGs

The end of the T wave is gentle and easy to blur, and the T wave has to move with the heart rate.
A generator that copies one "average" T wave onto every beat produces QT values that don't
shrink at fast rates, which shows up as a QTc distribution that is too wide or shifted.

## How ECGEN-Eval measures it

1. `qt_interval_ms`: time from QRS onset (all leads, see [QRS duration](qrs-duration.md)) to
   the end of the T wave, median over beats.
2. The **end of the T wave** uses the *tangent method*: find the steepest part of the T wave's
   return to the baseline, extend it as a straight line, and take the point where the line
   meets the baseline. This is done on every lead (T peaks from NeuroKit2's delineator) and
   combined with the median across leads.
3. `qtc_bazett_ms` = `qt_interval_ms` ÷ √(`rr_mean_ms` / 1000).

Needs NeuroKit2 (`NaN` without it). Against GE 12SL, QT has r 0.85 but is about 17 ms
shorter on average; the tangent method is known to end the T wave earlier. QTc has r 0.63
([validation](index.md#validation)).

## Learn more

- [Heart rate & RR](heart-rate.md) · [T-wave amplitude](t-wave.md)
- Bazett (1920), *An analysis of the time-relations of electrocardiograms*, Heart 7, 353–370.
- Rautaharju et al. (2009), AHA/ACCF/HRS recommendations, Part IV: the ST segment, T and U
  waves, and the QT interval. [doi:10.1161/CIRCULATIONAHA.108.191096](https://doi.org/10.1161/CIRCULATIONAHA.108.191096)
