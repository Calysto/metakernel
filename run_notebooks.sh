#!/usr/bin/env bash
set -euo pipefail

EXAMPLES_DIR="$(dirname "$0")/examples"

# Start ipcluster
echo "Starting ipcluster..."
uv run ipcluster start --daemonize --n=5
echo "Waiting for ipcluster to be ready..."
sleep 10

SCRIPT_DIR="$(dirname "$0")"

run_notebook() {
    local notebook="$1"
    local kernel="$2"
    local with_pkg="$3"
    echo "Running: $notebook (kernel: $kernel)"
    uv run --with "$with_pkg" jupyter nbconvert \
        --to notebook \
        --execute \
        --inplace \
        --ExecutePreprocessor.kernel_name="$kernel" \
        --ExecutePreprocessor.timeout=120 \
        "$EXAMPLES_DIR/$notebook"
}

run_notebook "Jigsaw in IPython.ipynb"          "python3"          "jupyter"
run_notebook "Mandelbrot.ipynb"                  "calysto_scheme"   "calysto-scheme"
run_notebook "MetaKernel Echo Demo.ipynb"        "metakernel_echo"  "$SCRIPT_DIR/metakernel_echo"
run_notebook "MetaKernel Python Demo.ipynb"      "metakernel_python" "$SCRIPT_DIR/metakernel_python"
run_notebook "Processing Magic in IPython.ipynb" "python3"          "jupyter"
run_notebook "Tutor Magic in IPython.ipynb"      "python3"          "jupyter"

echo "Stopping ipcluster..."
uv run ipcluster stop

echo "Done."
