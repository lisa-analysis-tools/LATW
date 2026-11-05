# Running the tutorials on Windows

The compiled packages (`lisaanalysistools`, `gbgpu`, `fastlisaresponse`, `bbhx`) have no Windows
wheels and `install.sh` has no Windows branch, so on Windows they are built from their git tags with MSVC.
This recipe was verified on Windows 11 in PowerShell, CPU only, with the versions in the README's
"Last validated against" table (on 2026-11-04). It has not yet been rerun end to end on a clean machine.

## 1. Prerequisites
- **Visual Studio 2022 Build Tools**, C++ workload (MSVC v143 + Windows 11 SDK):
  `winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"`
- **[Miniforge](https://github.com/conda-forge/miniforge)** (conda-forge, `mamba`). The commands below assume it is in `%USERPROFILE%\miniforge3`.
- **git**.

## 2. Conda environment
In PowerShell:
```powershell
& "$env:USERPROFILE\miniforge3\Library\bin\mamba.exe" create -y -n latw --override-channels -c conda-forge `
  "python=3.12" "numpy=2.2" "numba<0.62" "scipy=1.18" "h5py<3.15" "pandas<3" matplotlib "astropy=7.2" `
  "mpmath=1.4.1" "corner=2.3.0" jupyterlab ipykernel "fastemriwaveforms=2.0.0" "multispline=0.8.5" lisaconstants `
  "libblas=*=*openblas" "libcblas=*=*openblas" "liblapack=*=*openblas" "liblapacke=*=*openblas" "blas-devel=*=*openblas" `
  pkg-config gsl cmake ninja "pybind11=3.0.4" scikit-build-core cython setuptools_scm `
  jsonschema nvidia-ml-py platformdirs pydantic pyyaml requests rich tqdm wrapt statsmodels seaborn pillow
& "$env:USERPROFILE\miniforge3\envs\latw\python.exe" -m pip install "eryn==1.2.6" "chainconsumer==1.3.0" "gpubackendtools==0.1.1"
```
**Why OpenBLAS:** left alone, the solver can pick the MKL BLAS without `intel-openmp`, and then the first
matrix product kills Python (and Jupyter kernels) with exit code `0xC06D007F`. `blas-devel` provides the
LAPACKE headers, import library and `openblas.pc` that the bbhx build needs.
(The tested env was built from these packages in a few steps; this single `create` line was checked
with `--dry-run` only: it solves to numpy 2.2.6, OpenBLAS 0.3.34 and no MKL.)

## 3. Build shell (repeat in every new PowerShell window)
If scripts are blocked (the default on Windows 11 Home), start with `powershell -ExecutionPolicy Bypass`.
```powershell
$vs = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -property installationPath
Import-Module "$vs\Common7\Tools\Microsoft.VisualStudio.DevShell.dll"
Enter-VsDevShell -VsInstallPath $vs -SkipAutomaticLocation -DevCmdArguments "-arch=x64 -host_arch=x64"
& "$env:USERPROFILE\miniforge3\shell\condabin\conda-hook.ps1"; conda activate latw
$env:CMAKE_GENERATOR = "Ninja"; $env:CC = "cl"; $env:CXX = "cl"
$env:CMAKE_PREFIX_PATH = "$env:CONDA_PREFIX\Library"
$env:PKG_CONFIG_PATH = "$env:CONDA_PREFIX\Library\lib\pkgconfig"
$GBT = "$env:CONDA_PREFIX\Lib\site-packages\gpubackendtools\cutils"
$B = "C:\lisa"   # keep this short (MAX_PATH)
$common = "--no-build-isolation", "--no-deps", "-w", "$B\wheels", "-C", "cmake.build-type=Release"
```

## 4. Sources and patches
```powershell
mkdir $B; cd $B
git clone -c core.autocrlf=false -b v1.2.5  https://github.com/mikekatz04/LISAanalysistools.git lisatools
git clone -c core.autocrlf=false -b v1.2.4  https://github.com/mikekatz04/GBGPU.git gbgpu
git clone -c core.autocrlf=false -b v1.1.11 https://github.com/mikekatz04/lisa-on-gpu.git flr
git clone -c core.autocrlf=false -b v1.2.3  https://github.com/mikekatz04/BBHx.git bbhx
```
Until upstream releases include them, apply these PRs (their diffs are against the default branches;
they apply to the tags, and the compiled changes were verified there):
- **lisatools** [#90](https://github.com/lisa-analysis-tools/lisa-analysis-tools/pull/90): expose
  `OrbitsWrap.ptr`. Without it the fastlisaresponse and bbhx response kernels raise
  `TypeError: an integer is required` (all platforms; item 2 of the README's macOS known issue).
- **bbhx** [#32](https://github.com/lisa-analysis-tools/BBHx/pull/32): replace a variable-length array
  in `Likelihood.cu` with `std::vector`; MSVC rejects VLAs (`C2131`).
- **bbhx** [#33](https://github.com/lisa-analysis-tools/BBHx/pull/33): read the arrays of pointers as
  `int64_t*` instead of `long*`. `long` is 32-bit on Windows, so pointers get silently truncated.
```powershell
cd $B\lisatools; curl.exe -L https://github.com/lisa-analysis-tools/lisa-analysis-tools/pull/90.diff -o pr.diff; git apply pr.diff
cd $B\bbhx   # -3 is needed: the two diffs touch neighbouring lines
foreach ($n in 32, 33) { curl.exe -L "https://github.com/lisa-analysis-tools/BBHx/pull/$n.diff" -o pr.diff; git apply -3 pr.diff }
```
**fastlisaresponse v1.1.11** (no upstream PR: `master` has rewritten this file): its
`src/fastlisaresponse/cutils/CMakeLists.txt` locates lisatools with a `'/'`-only string split, and
copies `global.hpp`, which lisatools 1.2 no longer ships. Apply from `$B\flr`:
```powershell
$p = @'
--- a/src/fastlisaresponse/cutils/CMakeLists.txt
+++ b/src/fastlisaresponse/cutils/CMakeLists.txt
@@ -96,5 +96,4 @@ execute_process(
   COMMAND "${PYTHON_EXECUTABLE}" -c "if True:
-    import lisatools
-    _tmp = lisatools.__file__
-    print(_tmp.split('/__init__.py')[0])"
+    import lisatools, pathlib
+    print(pathlib.Path(lisatools.__file__).parent.as_posix())"
   OUTPUT_VARIABLE LISATOOLS_DIR
@@ -137,2 +136,7 @@ set(FILES_TO_COPY
 foreach(FILE_TO_COPY IN LISTS FILES_TO_COPY)
+  if(NOT EXISTS "${FILE_TO_COPY}")
+    # global.hpp was removed in lisatools 1.2; nothing here includes it
+    message(STATUS "Skipping copy, not found: ${FILE_TO_COPY}")
+    continue()
+  endif()
   get_filename_component(NEW_FILE "${FILE_TO_COPY}" NAME)
@@ -167,3 +171,3 @@ if(FASTLISA_WITH_CPU)
   target_sources(fastlisaresponse_cpu_responselisa PUBLIC FILE_SET HEADERS FILES
-                                         global.hpp Detector.hpp cuda_complex.hpp LISAResponse.hh)
+                                         Detector.hpp cuda_complex.hpp LISAResponse.hh)
 endif()
@@ -179,3 +183,3 @@ if(FASTLISA_WITH_GPU)
   target_sources(fastlisaresponse_gpu_responselisa PUBLIC FILE_SET HEADERS FILES
-                                         global.hpp Detector.hpp cuda_complex.hpp LISAResponse.hh
+                                         Detector.hpp cuda_complex.hpp LISAResponse.hh
                                          )
'@
[IO.File]::WriteAllText("$PWD\flr.patch", $p.Replace("`r`n", "`n") + "`n")   # LF, no BOM
git apply flr.patch
```

## 5. Build, in this order
Each package is built into a wheel and installed into the env. fastlisaresponse must be built after the
patched lisatools is installed. If you change `CXXFLAGS`, delete that package's build dir first:
CMake caches the flags.
```powershell
$env:CXXFLAGS = "/D_USE_MATH_DEFINES /EHsc /bigobj"
cd $B\lisatools; $env:SETUPTOOLS_SCM_PRETEND_VERSION_FOR_LISAANALYSISTOOLS = "1.2.5+win"
python -m pip wheel . @common -C build-dir=$B\b\lisatools -C cmake.define.LISATOOLS_WITH_GPU=OFF
python -m pip install --no-deps --force-reinstall (Get-Item $B\wheels\lisaanalysistools-*.whl).FullName

cd $B\gbgpu
python -m pip wheel . @common -C build-dir=$B\b\gbgpu -C cmake.define.GBGPU_WITH_GPU=OFF
python -m pip install --no-deps (Get-Item $B\wheels\gbgpu-*.whl).FullName

cd $B\flr; $env:SETUPTOOLS_SCM_PRETEND_VERSION_FOR_FASTLISARESPONSE = "1.1.11+win"
$env:CXXFLAGS = "/D_USE_MATH_DEFINES /EHsc /bigobj /I$GBT"
python -m pip wheel . @common -C build-dir=$B\b\flr -C cmake.define.FASTLISA_WITH_GPU=OFF
python -m pip install --no-deps (Get-Item $B\wheels\fastlisaresponse-*.whl).FullName

# bbhx looks for lapacke/lapack/blas .pc files; conda-forge only ships openblas.pc, so add shims
mkdir $B\pkgconfig
foreach ($n in "lapacke", "lapack", "blas") {
  "Name: $n`nDescription: $n from OpenBLAS (shim)`nVersion: 3.11.0`nRequires: openblas" | Set-Content "$B\pkgconfig\$n.pc" }
$env:PKG_CONFIG_PATH = "$B\pkgconfig;$env:PKG_CONFIG_PATH"
cd $B\bbhx; $env:SETUPTOOLS_SCM_PRETEND_VERSION_FOR_BBHX = "1.2.3+win"
$env:CXXFLAGS = "/D_USE_MATH_DEFINES /EHsc /bigobj /I$GBT /DHAVE_LAPACK_CONFIG_H /DLAPACK_COMPLEX_CPP /DCUDA_DEVICE= /permissive-"
python -m pip wheel . @common -C build-dir=$B\b\bbhx -C cmake.define.BBHX_WITH_GPU=OFF `
  -C cmake.define.BBHX_LAPACKE_DETECT_WITH=PKGCONFIG -C cmake.define.BBHX_LAPACKE_FETCH=OFF -C cmake.define.BBHX_LAPACKE_EXTRA_LIBS=
python -m pip install --no-deps (Get-Item $B\wheels\bbhx-*.whl).FullName
python -m pip check
```
What the flags are for: `/I$GBT` adds the `gbt_global.h` include dir that the CMake files miss;
`/DHAVE_LAPACK_CONFIG_H /DLAPACK_COMPLEX_CPP` make `lapack.h` use `std::complex` under MSVC C++;
`/DCUDA_DEVICE=` works around an include-guard clash between bbhx `global.h` and `gbt_global.h`;
`/permissive-` fixes an overload lookup error in `cuda_complex.hpp`. The bbhx configure step downloads
three source files from lisatools `main`, so it needs network.

## 6. Kernel and notebooks
```powershell
python -m ipykernel install --user --name latw --display-name "Python 3.12 (latw)"
cd <your LATW clone>\tutorials; python -m jupyter lab
```
Pick the `latw` kernel, and start Jupyter from `tutorials/` (Tutorial 2 imports the local
`pnbeyondGR_example.py`). Verified so far: all eight `*-complete` notebooks executed (Tutorial 0 as is,
the others with reduced sampler step counts); full-length runs have not been done on Windows. The
challenge notebook also needs an eryn 1.2.6 `TransformContainer` fix in cell 17 (pending, separate PR).

## 7. Troubleshooting
- **Kernel dies, exit code `0xC06D007F` / `-1066598273`:** the env is on MKL BLAS. `mamba install -n latw`
  the four `lib*=*=*openblas` specs plus the numpy/numba/scipy/h5py pins from step 2 (or, as a stopgap,
  set `MKL_THREADING_LAYER=SEQUENTIAL`). Both were verified.
- **Path-too-long errors:** keep `$B` and the build dirs short. Verified with LongPaths disabled and build
  dirs of about 40 characters; enabling LongPaths was not tested.
- **Line endings:** clone with `core.autocrlf=false` as above (also needed for the `git apply` in step 4
  to leave LF files). Builds from CRLF checkouts were not tested.
- **First Tutorial 2 run:** FEW 2.0 downloads its data files on first use (network needed; they go to
  `%LOCALAPPDATA%\few`). The reduced Tutorial 2 run took about 7 minutes on CPU.
- **Memory:** verified on a 16 GB laptop with reduced walker/step counts. Tutorial 6 and the challenge
  allocate multi-million-bin arrays per likelihood call; close other programs for full runs.
- **`ModuleNotFoundError` for `lisatools.sensitivity` etc.:** an unrelated PyPI package is also called
  `lisatools`; never `pip install lisatools` (the right one is `lisaanalysistools`).
- Harmless noise: `'vswhere.exe' is not recognized`, `-march=native` not supported, and
  `Error while loading conda entry point: conda-libmamba-solver` (look for "Successfully built").
