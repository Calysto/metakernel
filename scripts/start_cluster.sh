#!/usr/bin/env bash
# Start ipcluster with N engines and wait until they are ready.
# Usage: start_cluster.sh <n>
set -euo pipefail

N="${1:-3}"

echo "Starting ipcluster with $N engines..."
poetry run ipcluster start -n="$N" &

poetry run python - "$N" <<'EOF'
import ipyparallel as ipp, time, sys
n = int(sys.argv[1])
for _ in range(60):
    try:
        c = ipp.Client()
        if len(c) >= n:
            print(f"Cluster ready with {len(c)} engines")
            sys.exit(0)
    except Exception:
        pass
    time.sleep(2)
print("ERROR: cluster not ready after 120s", file=sys.stderr)
sys.exit(1)
EOF
