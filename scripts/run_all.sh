#!/usr/bin/env bash
# Sequential notebook-execution harness (dev branch).
#
# Executes every informational notebook (tutorials/NN_*.ipynb) and every
# answer notebook (tutorials/further/answers/*-complete.ipynb) IN PLACE,
# strictly one kernel at a time, niced, with all threading pinned to 1 —
# a full pass must never make the laptop unresponsive.
#
# Per notebook it logs status, wall time, and peak RSS to the results log.
#
# Usage:
#   scripts/run_all.sh                 # the full default set
#   scripts/run_all.sh path/to/nb ...  # just the named notebooks
# Env:
#   NB_TIMEOUT      per-cell timeout in seconds (default 1800)
#   RUN_ALL_LOG     results log path (default ./run_all_results.log)
#   PYTHON_BIN      python with jupyter installed (default: python on PATH)

set -u
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
       VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMEOUT="${NB_TIMEOUT:-1800}"
LOG="${RUN_ALL_LOG:-$ROOT/run_all_results.log}"
PY="${PYTHON_BIN:-python}"

if [ "$#" -gt 0 ]; then
    NBS=("$@")
else
    NBS=()
    for nb in "$ROOT"/tutorials/[0-9][0-9]_*.ipynb \
              "$ROOT"/tutorials/further/answers/*-complete.ipynb; do
        [ -e "$nb" ] && NBS+=("$nb")
    done
fi

if [ "${#NBS[@]}" -eq 0 ]; then
    echo "run_all.sh: no notebooks found" >&2
    exit 1
fi

: > "$LOG"
fail=0
for nb in "${NBS[@]}"; do
    echo "=== $(date '+%H:%M:%S') $nb" | tee -a "$LOG"
    tfile="$(mktemp)"
    start=$(date +%s)
    if /usr/bin/time -l nice -n 10 "$PY" -m jupyter nbconvert \
            --to notebook --execute --inplace \
            --ExecutePreprocessor.timeout="$TIMEOUT" "$nb" 2> "$tfile"; then
        status=OK
    else
        status=FAIL
        fail=1
        # surface the tail of the error for the log
        tail -n 25 "$tfile" | tee -a "$LOG"
    fi
    end=$(date +%s)
    rss_bytes=$(awk '/maximum resident set size/{print $1}' "$tfile")
    rss_mb=$(( ${rss_bytes:-0} / 1048576 ))
    echo "$status  $((end - start))s  peakRSS=${rss_mb}MB  $nb" | tee -a "$LOG"
    rm -f "$tfile"
done

echo "---" | tee -a "$LOG"
[ "$fail" -eq 0 ] && echo "ALL OK" | tee -a "$LOG" || echo "FAILURES (see above)" | tee -a "$LOG"
exit $fail
