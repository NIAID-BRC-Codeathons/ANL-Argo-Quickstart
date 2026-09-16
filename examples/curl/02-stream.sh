#!/usr/bin/env bash
# Streaming chat completion. -N disables curl output buffering.
#
#   export ARGO_USER=ac.yourname
#   ./02-stream.sh
#
# Requires a connection to the Argonne-auth network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS -N https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer $ARGO_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudesonnet5",
    "messages": [{"role": "user", "content": "Count to five."}],
    "max_tokens": 100,
    "stream": true
  }'
