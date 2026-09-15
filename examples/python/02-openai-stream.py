#!/usr/bin/env python3
"""Streaming chat with the openai SDK, guarding the usage-only final chunk.

Install:
    pip install openai

Run:
    ARGO_USER=ac.yourname python3 02-openai-stream.py

Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = OpenAI(
    api_key=ARGO_USER,
    base_url="https://apps.inside.anl.gov/argoapi/v1",
)

stream = client.chat.completions.create(
    model="claudesonnet5",
    messages=[{"role": "user", "content": "Count to five."}],
    max_tokens=100,
    stream=True,
)

parts = []
for chunk in stream:
    if not chunk.choices:          # final usage-only chunk carries no choices
        continue
    delta = chunk.choices[0].delta.content
    if delta:
        parts.append(delta)
        print(delta, end="", flush=True)

print()                            # close the line once the stream ends
full_text = "".join(parts)
print(f"[{len(full_text)} characters]")
