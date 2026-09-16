#!/usr/bin/env bash
# Proves all three open-model endpoints are up. Run this first.
#
#   ./00-smoke-test.sh
#
# No credential required. Requires a connection to the Argonne-auth network.
set -euo pipefail
HOST="${MANGO_HOST:-mango.cels.anl.gov}"

for port_name in "8003 Llama" "8004 Qwen" "9998 Embedding"; do
  set -- $port_name
  port=$1; name=$2
  printf '%-10s ' "$name"
  if curl -sf --max-time 10 "http://$HOST:$port/health" >/dev/null; then
    echo "up   $(curl -s --max-time 10 "http://$HOST:$port/v1/models" \
      | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"][0]["id"])')"
  else
    echo "DOWN (http://$HOST:$port)"
  fi
done
