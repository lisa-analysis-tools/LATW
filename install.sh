#!/bin/bash

usage="$(basename "$0") [-h] -- program to install packages needed for LISA Analysis Tools Workshop

where:
    -h  show this help text

keyword argument options (given as key=value):
    env_name:  Name of generated conda environment. Default is 'lisa_env'.
    # run_tests: Either true or false. Whether to run tests after install. Default is true.
    
"

while getopts 'h' option; do
  case "$option" in
    h) echo "$usage"
       exit 3
       ;;
  esac
done

for ARGUMENT in "$@"
do
   KEY=$(echo $ARGUMENT | cut -f1 -d=)

   KEY_LENGTH=${#KEY}
   VALUE="${ARGUMENT:$KEY_LENGTH+1}"

   export "$KEY"="$VALUE"
done

if [ -z ${env_name+x} ]; then env_name="lisa_env"; fi
# if [ -z ${run_tests+x} ]; then run_tests="true"; fi

# if [[ "$run_tests" != "true" ]] && [[ "$run_tests" != "false" ]]; 
#     then echo "run_tests variable must be 'true' or 'false'.";
#     exit 2;
# fi

echo "Now installing into conda environment named $env_name."

echo "Installing LATW setup."; 

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "This system is macOS."

    machine=$(uname -m)
    if [[ "$machine" == "arm64" ]]; then
        echo "This is an M1 Mac."
        conda create -n "$env_name" -c conda-forge -y wget gsl hdf5 numpy pandas Cython scipy tqdm  openblas lapack liblapacke jupyter ipython h5py requests matplotlib python=3.12
    else
        echo "This is not an M1 Mac."
        conda create -n "$env_name" -c conda-forge -y clangxx_osx-64 clang_osx-64 wget gsl  openblas lapack liblapacke hdf5 numpy pandas Cython scipy tqdm jupyter ipython h5py requests matplotlib python=3.12
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "This system is Unix/Linux."
    conda create -n "$env_name" -c conda-forge -y gcc_linux-64 gxx_linux-64 wget gsl  openblas lapack liblapacke hdf5 numpy pandas Cython scipy tqdm jupyter ipython h5py requests matplotlib python=3.12
else
    echo "Unsupported operating system."
fi

# get conda base information
IN="$(conda info | grep -i 'base environment')"

tmp=$(echo $IN | tr " " "\n")
i=0
out=()
for tmp_i in $tmp
do
    out[i]=$tmp_i
    let "i = $i + 1"
done

conda_base="${out[3]}"
conda_init_sh="$conda_base/etc/profile.d/conda.sh"
echo "$conda_init_sh"
source $conda_init_sh

conda activate "$env_name"
echo "should be done"
conda_check="$(conda info | grep -i 'active environment')"
echo "conda env: $conda_check"
echo "Environment created. Installing additional packages before FEW install."

python_here=""$conda_base"/envs/"$env_name"/bin/python"
pip_here=""$conda_base"/envs/"$env_name"/bin/pip"

echo "python: $python_here" 
echo "pip: $pip_here"

"$pip_here" install corner eryn chainconsumer mpmath;

machine=$(uname -m)

# Pin numba<0.62 so pip resolves llvmlite<0.45, which ships prebuilt wheels.
# numba>=0.62 pulls llvmlite 0.48, which is source-only on macOS x86_64 / py3.12
# and fails to build ("llvmlite needs CMake tools to build") since the conda env
# has neither CMake nor a matching LLVM. Validated with numba 0.61.2 / llvmlite 0.44.0.
"$pip_here" install "numba<0.62"

"$python_here" -m pip install lisaanalysistools
"$python_here" -m pip install fastlisaresponse
"$python_here" -m pip install bbhx
"$python_here" -m pip install fastemriwaveforms
"$python_here" -m pip install gbgpu

conda activate "$env_name"
# if [[ "$run_tests" == "true" ]]; 
#  then echo "Running tests...";
#  "$python_here" -m unittest discover;
# fi
