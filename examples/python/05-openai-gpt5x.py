#!/usr/bin/env python3
"""GPT-5.x call: max_completion_tokens instead of max_tokens.

Install:
    pip install openai

Run:
    ARGO_USER=ac.yourname python3 05-openai-gpt5x.py

Requires a connection to the codeathon network.
"""
import os

from openai import OpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = OpenAI(api_key=ARGO_USER, base_url="https://apps.inside.anl.gov/argoapi/v1")

resp = client.chat.completions.create(
    model="gpt56sol",
    messages=[{"role": "user", "content": "What is a pangenome?"}],
    max_completion_tokens=300,   # portable; Argo also accepts max_tokens here
)

print(resp.choices[0].message.content)
