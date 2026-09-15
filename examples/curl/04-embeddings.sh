#!/usr/bin/env bash
# Text embeddings. Max 16 strings per request.
#
#   export ARGO_USER=ac.yourname
#   ./04-embeddings.sh
#
# Requires a connection to the Argonne-auth network.
set -euo pipefail
: "${ARGO_USER:?Set ARGO_USER to your Argonne collaborator username, e.g. ac.jdoe}"

curl -sS https://apps.inside.anl.gov/argoapi/v1/embeddings \
  -H "Authorization: Bearer $ARGO_USER" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": ["first document", "second document"]
  }'
