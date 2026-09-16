#!/bin/sh
# Chat with Qwen 3.6 over plain HTTP.
#
#   ./02-qwen-chat.sh
#
# max_tokens must be generous: Qwen reasons internally before answering and
# that reasoning draws on the same budget. Too low returns an empty message.
#
# Requires a connection to the Argonne-auth network.
set -eu
HOST="${MANGO_HOST:-mango.cels.anl.gov}"

curl -sS "http://$HOST:8004/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.6-35B-A3B",
    "messages": [{"role": "user", "content": "In one sentence, what is a pangenome?"}],
    "max_tokens": 4000
  }'
