# Are AI-generated electrocardiograms clinically accurate? Benchmarking accuracy of AI-generated ECGs: a multiplatform performance study of public LLMs
- **ID / Year / Venue:** P019 / 2026 / European Heart Journal - Digital Health
- **Model & task:** EvalOnly (public text-to-image/LLM platforms: Bard, Bing Image Creator, DALL-E); evaluation (text-cond ECG image generation by general-purpose AI)
- **Losses:** not applicable
- **Evaluation:** Blinded expert rhythm diagnosis by 3 physicians incl. cardiologist with adjudication; accuracy = agreement with prompted rhythm; proportion uninterpretable
- **Data:** 113 AI-generated ECG images (10 rhythms x 3 platforms x 4, after exclusions); leads: not reported (rhythm strips, images); fs: not applicable (images); length: not reported
- **Takeaway for ECGEN-Eval:** Label-consistency (does generated ECG match prompted class?) via expert or classifier, plus retrieval/memorisation check, is essential for conditional generators.
- *Extraction source: full-text*
