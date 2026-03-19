# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

ECGEN-Eval provides evaluation metrics for generated ECGs (Electrocardiograms). It is part of a broader ECG generation research suite that includes ECGEN-FM, ECGEN-VAE, ECGEN_pulse2pulse_plus, and Pulse2Pulse.

## Repository Status

This repository is in early initialization. No source code, build system, or test infrastructure exists yet. When implementing, follow the conventions established in the sibling projects under `/work/vajira/DL2026/`.

## Expected Setup (to be established)

When adding code, the project will likely use:
- Python with `pyproject.toml` or `requirements.txt` for dependency management
- `pytest` for testing
- Evaluation metrics comparing generated vs. real ECG signals
