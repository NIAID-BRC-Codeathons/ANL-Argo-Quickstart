#!/usr/bin/env bash
# GPT-5.x call. Argo accepts max_tokens or max_completion_tokens for OpenAI models.
#
#   export ARGO_USER=ac.yourname
#   ./05-gpt5x.sh
#
# Requires a connection to the codeathon network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer $ARGO_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt56sol",
    "messages": [{"role": "user", "content": "What is a pangenome?"}],
    "max_completion_tokens": 300
  }'
