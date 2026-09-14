#!/usr/bin/env python3
"""Messages call with the anthropic SDK. Note the base URL has no /v1.

Install:
    pip install anthropic

Run:
    ARGO_USER=ac.yourname python3 06-anthropic-messages.py

Requires a connection to the codeathon network.
"""
import os

from anthropic import Anthropic

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = Anthropic(
    api_key=ARGO_USER,
    base_url="https://apps.inside.anl.gov/argoapi",
)

msg = client.messages.create(
    model="claudeopus5",
    max_tokens=1024,
    system="You are a concise bioinformatics assistant.",
    messages=[{"role": "user", "content": "What is a pangenome?"}],
)

# claudeopus5 has extended thinking on by default, so content[0] is a
# ThinkingBlock, not text. Join every text block instead of indexing.
print("".join(b.text for b in msg.content if b.type == "text"))
