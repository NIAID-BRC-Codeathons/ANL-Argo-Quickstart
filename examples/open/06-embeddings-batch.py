#!/usr/bin/env python3
"""Embed several texts in one request by passing a list.

Install:
    pip install openai

Run:
    python3 06-embeddings-batch.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:9998/v1")

texts = [
    "Escherichia coli is a Gram-negative bacterium.",
    "Influenza A virus contains a segmented RNA genome.",
    "Genome assembly reconstructs sequences from sequencing reads.",
]

resp = client.embeddings.create(
    model="Salesforce/SFR-Embedding-Mistral",
    input=texts,
)

# Results come back in request order, but each carries its own .index if you
# need to be certain after reordering or retrying.
for item in resp.data:
    print(f"text {item.index}: {len(item.embedding)} dimensions")
