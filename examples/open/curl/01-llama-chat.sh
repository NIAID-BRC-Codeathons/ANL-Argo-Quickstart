#!/bin/sh
# Chat with Llama 4 Scout over plain HTTP. No dependencies, no credential.
#
#   ./01-llama-chat.sh
#
# Requires a connection to the Argonne-auth network.
set -eu
HOST="${MANGO_HOST:-mango.cels.anl.gov}"

curl -sS "http://$HOST:8003/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic",
    "messages": [{"role": "user", "content": "In one sentence, what is a pangenome?"}],
    "max_tokens": 300
  }'
