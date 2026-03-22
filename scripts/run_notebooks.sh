#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(dirname "$0")/.."
EXAMPLES_DIR="$REPO_DIR/examples"

poetry sync --with test-all
poetry run pip install -q --no-deps -e ./metakernel_python/
poetry run pip install -q --no-deps -e ./metakernel_echo/

bash "$(dirname "$0")/start_cluster.sh" 5

run_notebook() {
    local notebook="$1"
    local kernel="$2"
    echo "Running: $notebook (kernel: $kernel)"
    poetry run jupyter nbconvert \
        --to notebook \
        --execute \
        --inplace \
        --ExecutePreprocessor.kernel_name="$kernel" \
        --ExecutePreprocessor.timeout=120 \
        "$EXAMPLES_DIR/$notebook"
}

run_notebook "Jigsaw in IPython.ipynb"          "python3"
run_notebook "Mandelbrot.ipynb"                  "calysto_scheme"
poetry run jupyter nbconvert --to notebook --inplace \
    --ClearOutputPreprocessor.enabled=True \
    "$EXAMPLES_DIR/Mandelbrot.ipynb"
run_notebook "MetaKernel Echo Demo.ipynb"        "metakernel_echo"
run_notebook "MetaKernel Python Demo.ipynb"      "metakernel_python"
run_notebook "Processing Magic in IPython.ipynb" "python3"
run_notebook "Tutor Magic in IPython.ipynb"      "python3"

echo "Stopping ipcluster..."
poetry run ipcluster stop

echo "Done."
