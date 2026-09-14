#!/usr/bin/env bash
# Chat via the Anthropic Messages endpoint.
#
#   export ARGO_USER=ac.yourname
#   ./03-messages-anthropic.sh
#
# Requires a connection to the codeathon network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS https://apps.inside.anl.gov/argoapi/v1/messages \
  -H "x-api-key: $ARGO_USER" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudeopus5",
    "max_tokens": 1024,
    "system": "You are a concise bioinformatics assistant.",
    "messages": [{"role": "user", "content": "What is a pangenome?"}]
  }'
