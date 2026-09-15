#!/usr/bin/env bash
# Chat completion via the OpenAI-compatible endpoint.
#
#   export ARGO_USER=ac.yourname
#   ./01-chat.sh
#
# Requires a connection to the Argonne-auth network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer $ARGO_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudesonnet5",
    "messages": [
      {"role": "system", "content": "You are a concise bioinformatics assistant."},
      {"role": "user", "content": "In one sentence, what is a pangenome?"}
    ],
    "max_tokens": 300
  }'
