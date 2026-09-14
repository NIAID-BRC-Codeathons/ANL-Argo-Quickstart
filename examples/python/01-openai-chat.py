#!/usr/bin/env python3
"""Chat completion with the openai SDK. Drives any Argo model.

Install:
    pip install openai

Run:
    ARGO_USER=ac.yourname python3 01-openai-chat.py

Requires a connection to the codeathon network.
"""
import os

from openai import OpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = OpenAI(
    api_key=ARGO_USER,
    base_url="https://apps.inside.anl.gov/argoapi/v1",
)

resp = client.chat.completions.create(
    model="claudesonnet5",
    messages=[
        {"role": "system", "content": "You are a concise bioinformatics assistant."},
        {"role": "user", "content": "In one sentence, what is a pangenome?"},
    ],
    max_tokens=300,
)

print(resp.choices[0].message.content)
