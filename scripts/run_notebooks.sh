#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(dirname "$0")/.."
EXAMPLES_DIR="$REPO_DIR/examples"

echo "Starting ipcluster..."
# Install calysto_scheme kernel and start ipcluster in the same env.
# Run in background (no --daemonize) so the process stays alive for engines.
poetry run bash -c "
    python -m calysto_scheme install --user &&
    ipcluster start --n=5
" &
echo "Waiting for ipcluster to be ready..."
poetry run python - <<'EOF'
import ipyparallel as ipp, time, sys
for _ in range(60):
    try:
        c = ipp.Client()
        if len(c) >= 5:
            print(f"Cluster ready with {len(c)} engines")
            sys.exit(0)
    except Exception:
        pass
    time.sleep(2)
print("ERROR: cluster not ready after 120s", file=sys.stderr)
sys.exit(1)
EOF

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
