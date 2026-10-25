# CardioFlow: Learning to Generate ECG from PPG with Rectified Flow
- **ID / Year / Venue:** P028 / 2025 / IEEE International Conference on Acoustics Speech and Signal Processing
- **Model & task:** FlowMatching (rectified flow, one/few-step, peak masks); PPG2ECG
- **Losses:** unknown (abstract only) (rectified flow objective implied)
- **Evaluation:** ECG quality vs diffusion baselines (specific metrics unknown); inference speed (tags: fidelity;efficiency)
- **Data:** WESAD; DaLiA; leads: 1; fs: unknown (abstract only); length: unknown (abstract only)
- **Notes:** Rectified-flow PPG-to-ECG translation; uses masks highlighting PPG/ECG peaks to emphasise ECG structures; claims quality comparable/better than diffusion with much faster inference.
- **Takeaway for ECGEN-Eval:** Report sampling cost (NFE / wall-clock) alongside quality metrics.
- *Extraction source: abstract-only*
