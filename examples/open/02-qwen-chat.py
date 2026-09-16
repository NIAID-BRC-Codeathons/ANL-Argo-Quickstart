#!/usr/bin/env python3
"""Chat completion against Qwen 3.6, which reasons before it answers.

Install:
    pip install openai

Run:
    python3 02-qwen-chat.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:8004/v1")

resp = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[{"role": "user", "content": "In one sentence, what is a pangenome?"}],
    # Qwen spends tokens on internal reasoning before it emits an answer, and
    # that reasoning draws on this same budget. Too low and you get an empty
    # response, not a truncated one. 2000-4000 for simple questions, 8000+ for
    # hard ones. Same failure mode as gemini35flash on Argo.
    max_tokens=4000,
)

print(resp.choices[0].message.content)
