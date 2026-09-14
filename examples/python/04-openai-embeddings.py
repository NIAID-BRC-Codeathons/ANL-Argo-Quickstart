#!/usr/bin/env python3
"""Batch embeddings with the openai SDK. Max 16 strings per request.

Install:
    pip install openai

Run:
    ARGO_USER=ac.yourname python3 04-openai-embeddings.py

Requires a connection to the codeathon network.
"""
import os

from openai import OpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = OpenAI(api_key=ARGO_USER, base_url="https://apps.inside.anl.gov/argoapi/v1")

resp = client.embeddings.create(
    model="text-embedding-3-small",
    input=["first document", "second document"],
)

for item in resp.data:
    print(item.index, len(item.embedding))   # 0 1536 / 1 1536
