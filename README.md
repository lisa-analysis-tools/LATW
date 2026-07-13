# LISA Analysis Tools Workshop (LATW)

This repo houses the tutorial codes for the LISA Analysis Tools Workshop. The tutorials are stored in the [tutorials](tutorials/) directory. In that same directory, you will find the answer keys. Introductory talk recordings can be found [here](https://www.youtube.com/playlist?list=PLdWF50RX1STO2DbfkqlBbhhaDdLTETAE7). PDF versions of the slides are in [intro_talks](intro_talks/). 

If you participate in a LAT workshop or work through the tutorials, please fill out this [survey](https://forms.gle/DFEBFRHSD1HRZ4HU9). We would really appreciate it!

The tutorials are numbered as follows:

0) Introductory tutorial for helpful Python concepts related to the successful usage of LISA Analysis Tools packages. This also gives the user a flavor of what the tutorials are like. 

1) Introduction to [LISA Analysis Tools](https://mikekatz04.github.io/LISAanalysistools) (`lisatools`). This includes setting up LISA sensitivity information, using data analysis classes, calculating inner products, SNRs, and Likelihoods. 

2) EMRIs and LISA Response: build EMRI waveforms wrapped in a time-domain LISA response function. This combines the use of [Fast EMRI Waveforms](https://bhptoolkit.org/FastEMRIWaveforms/html/index.html) (`few`) and [`fastlisaresponse`](https://mikekatz04.github.io/lisa-on-gpu).

3) MCMC with Eryn: use various **fixed-dimensional** MCMC techniques with the [Eryn](https://mikekatz04.github.io/Eryn) (`eryn`) sampler package.

4) MCMC and MBHBs: use lessons learned in Eryn to build up to a full MCMC with Massive Black Hole Binaries. [BBHx](https://mikekatz04.github.io/BBHx) (`bbhx`) is used to produce LISA TDI waveforms. We also use that package to perform the analysis with the "Heterodyning" technique. 

5) RJMCMC with Eryn: perform trans-dimensional or Reversible Jump MCMC with the [Eryn](https://mikekatz04.github.io/Eryn) (`eryn`) sampler package. 

6) Galactic Binaries: analyze Galactic binary waveforms and use them in MCMC and RJMCMC analyses. We will use [GBGPU](https://mikekatz04.github.io/GBGPU) to produce waveforms using the FastGB waveform construction method in the frequency domain. 

There is also a challenge problem on designing a mini global fit. 


# Installation

All tutorials can be run in Google Colab. There is a cell at the beginning of each tutorial that you can uncomment and run that will install necessary packages (for each tutorial) into the Colab environment. 

LATW leverages conda environments to install and use necessary packages. If you do not have [Anaconda](https://www.anaconda.com/download) or [miniconda](https://docs.anaconda.com/free/miniconda/index.html) installed, you must do this first and load your `base` conda environment. 

First, clone the repo and `cd` to the `LATW` directory.:
```
git clone https://github.com/mikekatz04/LATW.git
cd LATW/
```

Install all packages necessary for the tutorials by running:
```
bash install.sh
```
Running `bash install.sh -h` will also give you some basic install options. 

If you want more flexibility (you will need Python 3.12), you can install each package with `pip`: `numpy`, `scipy`, `matplotlib`, `pandas`, `eryn`, `corner`, `chainconsumer`, `lisaanalysistools`, `fastlisaresponse`, `gbgpu`, `bbhx`, `fastemriwaveforms`.

Once installation is completed, `cd` to the tutorial directory and run `jupyter lab`. Select your tutorial and begin!

# Last validated against

These tutorials were last validated on **2026-07-13** (Python 3.12) against the
following pip releases:

| Package | Version | | Package | Version |
|---|---|---|---|---|
| lisaanalysistools | 1.2.5 | | fastemriwaveforms | 2.0.0 |
| fastlisaresponse | 1.1.11 | | gbgpu | 1.2.4 |
| bbhx | 1.2.3 | | eryn | 1.2.6 |
| gpubackendtools | 0.1.1 | | corner | 2.3.0 |
| chainconsumer | 1.3.0 | | mpmath | 1.4.1 |
| numpy | 2.2.6 | | scipy | 1.18.0 |
| numba | 0.61.2 | | llvmlite | 0.44.0 |

Tutorials 0, 1, 3, 5, and 6 run clean end-to-end. Tutorial 2 was updated to the
Fast EMRI Waveforms **2.0** API (see below).

Install note: `install.sh` now pins `numba<0.62`. Unpinned, pip resolves numba
0.62 → llvmlite 0.48, which is source-only on macOS x86_64 / py3.12 and fails to
build ("llvmlite needs CMake tools to build") in the stock conda env.

## FEW 2.0 update (Tutorial 2)

Fast EMRI Waveforms 2.0 replaced the pre-2.0 waveform/trajectory classes. Tutorial 2
and `pnbeyondGR_example.py` now use the 2.0 API: custom trajectories subclass
`few.trajectory.ode.base.ODEBase` (implementing `evaluate_rhs`, with the integrator
applying the mass-ratio scaling), custom waveforms subclass
`SphericalHarmonicWaveformBase` + `SchwarzschildEccentric` with
`inspiral_module=EMRIInspiral` / `amplitude_module=AmpInterpSchwarzEcc`, `use_gpu=`
is replaced by `force_backend`, and mode selection uses `mode_selection=`.

## Known issue — LISA response on macOS x86_64

On macOS x86_64 with the versions above, two release/packaging defects currently
block the LISA-response sections of Tutorials 2 and 4 and the challenge problem:

1. **Vendored-runtime clash.** Each delocated wheel bundles its own
   `libstdc++`/`libgcc`/`libgfortran`; loading two together (e.g. `few` +
   `fastlisaresponse`, or `bbhx`) aborts with `SIGABRT`. It can be worked around
   by pointing every package's `.dylibs/{libstdc++.6,libgcc_s.1.1,libgfortran.5}.dylib`
   at a single shared copy.
2. **`lisatools` orbit pointer.** After (1), `lisatools` 1.2.5
   `detector.Orbits.ptr` returns `self.pycppdetector.ptr`, but the compiled
   `OrbitsWrapCPU` exposes no `ptr`, so the `bbhx` and `fastlisaresponse` response
   kernels raise `TypeError: an integer is required`. This has no in-notebook
   (release-compatible) workaround and needs a fix in the `lisaanalysistools` wheel.

# Code of Conduct

In [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), you will find the workshop code of conduct. It is heavily based on the LISA Consortium code of conduct. We strongly advise anyone who uses these tutorials in any way to follow this code of conduct. 

# Authors

* **Michael Katz**

# Contributors / Organizing Committee

* Nikos Karnesis
* Natalia Korsakova
* Argyro Sasli
* Albin Nilsson
* Rodrigo Tenorio
* Durgesh Rai
* Christian Chapman-Bird

