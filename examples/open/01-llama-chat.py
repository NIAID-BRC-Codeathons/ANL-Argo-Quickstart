#!/usr/bin/env python3
"""Chat completion against Llama 4 Scout.

Install:
    pip install openai

Run:
    python3 01-llama-chat.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

# The server requires the api_key field but never checks it. "EMPTY" is the
# convention; your Argo username does not belong here and would do nothing.
client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:8003/v1")

resp = client.chat.completions.create(
    model="RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic",
    messages=[
        {"role": "system", "content": "You are a concise bioinformatics assistant."},
        {"role": "user", "content": "In one sentence, what is a pangenome?"},
    ],
    max_tokens=300,
)

print(resp.choices[0].message.content)
