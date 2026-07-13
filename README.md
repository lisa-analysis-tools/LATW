# LISA Analysis Tools Workshop (LATW) — development branch

This is the **`dev` branch** of LATW: the tutorial series for the
**development state** of the LISA Analysis Tools stack — the versions
installed by `LISAanalysistools/install.sh` (GPUBackendTools@spline,
Eryn@dev, LISAanalysistools@dev, BBHx@dev, GBGPU@dev,
FastEMRIWaveforms@gpu_backend, phentax).

If you want the workshop tutorials for the **pip-released** packages
(`pip install lisaanalysistools eryn gbgpu bbhx fastemriwaveforms ...`),
use the [`main` branch](https://github.com/lisa-analysis-tools/LATW/tree/main)
instead. That is the branch policy of this repo: `main` ↔ pip releases,
`dev` ↔ the install.sh development stack (see [CLAUDE.md](CLAUDE.md)).

## Installation (dev stack — no Colab, no pip releases)

The dev tutorials need the editable development installation:

```
git clone https://github.com/lisa-analysis-tools/lisa-analysis-tools.git LISAanalysistools
bash LISAanalysistools/install.sh
```

This clones the sibling repos (including this one) side by side, checks
out the development branches, and editable-installs everything. Then
`jupyter lab` in `LATW/tutorials/` and start with `00`.

## The tutorials

**Informational track** (`tutorials/`) — instructive, fully executed;
each section opens with a TL;DR and one minimal cell, with "Going deeper"
subsections for pipeline developers:

- `00` Setup & Atlas — installation, how to use the tutorials + docs, and
  a map of the whole ecosystem (what lives where and how to find it).
- `01` A global fit in four lines — run a small stock global fit, then
  pull every structured product out of it and see every knob.
- `02` Foundations — domains (TD/FD/STFT/WDM), sensitivity, the detector,
  and `AnalysisContainer` (from one SNR to the global fit's residuals).
- `03` Response & TDI — from a waveform to a LISA data stream.
- `04` Source waveforms — GB, MBHB, EMRI, SOBHB with the stock classes
  (exactly the way the global fit builds them).
- `05` Sampling with Eryn — from a toy MCMC to the global fit's engine.
- `06` Backends & the dev workflow — Python/C++/CUDA/JAX, install.sh,
  and how to develop for the stack.
- `07` Stock global fits in depth — data processors, settings, recipes,
  and writing your own Move-level module.
- `08` Stock global fit gallery — a deep demo of every stock fit.

**Exercise track** (`tutorials/further/`) — the workshop series proper
(Tasks + Questions; answers in `further/answers/`). Baseline: if you want
to do a real research project on LISA data analysis, you should generally
understand and be able to work through these tutorials.

- `X1` Sensitivity, SNR, inner products & likelihoods
- `X2` EMRIs + response/TDI (ends with a standalone EMRI MCMC)
- `X3` Fixed-dimensional MCMC with Eryn
- `X4` MBHBs & MCMC (with heterodyned/fast likelihoods)
- `X5` RJMCMC with Eryn
- `X6` Galactic binaries: MCMC & RJ (with the fast GB likelihood)
- `X7` Stellar-origin BHBs
- `X8` A mini global fit (build, swap parts, write your own module)

Contributor conventions (cell skeleton, answer markers, runtime/memory
budgets): [tutorials/STYLE.md](tutorials/STYLE.md). Execute everything via
`scripts/run_all.sh` (sequential, thread-pinned).

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), based on the LISA Consortium
code of conduct.

## Authors

* **Michael Katz**

## Contributors / Organizing Committee

* Nikos Karnesis
* Natalia Korsakova
* Argyro Sasli
* Albin Nilsson
* Rodrigo Tenorio
* Durgesh Rai
* Christian Chapman-Bird
