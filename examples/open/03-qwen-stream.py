#!/usr/bin/env python3
"""Streaming chat against Qwen 3.6. Llama (port 8003) streams the same way.

Install:
    pip install openai

Run:
    python3 03-qwen-stream.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:8004/v1")

stream = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[{"role": "user", "content": "Explain metagenomic binning in two sentences."}],
    max_tokens=4000,   # see 02-qwen-chat.py: reasoning shares this budget
    stream=True,
)

for chunk in stream:
    # Defensive guard. This server sent a choices entry on every chunk when
    # tested, but the delta is empty on the first and last ones, and vLLM emits
    # a choices-less usage chunk if you pass stream_options={"include_usage":
    # True}. Checking both costs nothing.
    if chunk.choices:
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
print()
