#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(dirname "$0")/.."
EXAMPLES_DIR="$REPO_DIR/examples"

# Start ipcluster
echo "Starting ipcluster..."
uv run --with ipyparallel ipcluster start --daemonize --n=5
echo "Waiting for ipcluster to be ready..."
uv run --with ipyparallel python - <<'EOF'
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
    local with_pkg="$3"
    echo "Running: $notebook (kernel: $kernel)"
    uv run --with nbconvert --with "$with_pkg" jupyter nbconvert \
        --to notebook \
        --execute \
        --inplace \
        --ExecutePreprocessor.kernel_name="$kernel" \
        --ExecutePreprocessor.timeout=120 \
        "$EXAMPLES_DIR/$notebook"
}

run_notebook "Jigsaw in IPython.ipynb"          "python3"          "jupyter"
run_notebook "Mandelbrot.ipynb"                  "calysto_scheme"   "calysto-scheme"
uv run --with nbconvert jupyter nbconvert --to notebook --inplace \
    --ClearOutputPreprocessor.enabled=True \
    "$EXAMPLES_DIR/Mandelbrot.ipynb"
run_notebook "MetaKernel Echo Demo.ipynb"        "metakernel_echo"  "$REPO_DIR/metakernel_echo"
run_notebook "MetaKernel Python Demo.ipynb"      "metakernel_python" "$REPO_DIR/metakernel_python"
run_notebook "Processing Magic in IPython.ipynb" "python3"          "jupyter"
run_notebook "Tutor Magic in IPython.ipynb"      "python3"          "jupyter"

echo "Stopping ipcluster..."
uv run --with ipyparallel ipcluster stop

echo "Done."
