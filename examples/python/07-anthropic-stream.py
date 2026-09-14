#!/usr/bin/env python3
"""Streaming with the anthropic SDK, plus the final message metadata.

Install:
    pip install anthropic

Run:
    ARGO_USER=ac.yourname python3 07-anthropic-stream.py

Requires a connection to the codeathon network.
"""
import os

from anthropic import Anthropic

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = Anthropic(
    api_key=ARGO_USER,
    base_url="https://apps.inside.anl.gov/argoapi",
)

with client.messages.stream(
    model="claudeopus5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Count to five."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    final = stream.get_final_message()   # call inside the context manager

print()
print(f"[{final.stop_reason}] {final.usage.output_tokens} output tokens")
