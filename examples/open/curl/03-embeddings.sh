#!/bin/sh
# Embed one string with SFR-Embedding-Mistral.
#
#   ./03-embeddings.sh
#
# Requires a connection to the Argonne-auth network.
set -eu
HOST="${MANGO_HOST:-mango.cels.anl.gov}"

curl -sS "http://$HOST:9998/v1/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Salesforce/SFR-Embedding-Mistral",
    "input": "Escherichia coli is a Gram-negative bacterium."
  }'
