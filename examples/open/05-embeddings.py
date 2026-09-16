#!/usr/bin/env python3
"""One embedding from SFR-Embedding-Mistral: 4096 dimensions.

Install:
    pip install openai

Run:
    python3 05-embeddings.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:9998/v1")

resp = client.embeddings.create(
    model="Salesforce/SFR-Embedding-Mistral",
    input="Escherichia coli is a Gram-negative bacterium.",
)

vector = resp.data[0].embedding
print(f"{len(vector)} dimensions")
print(vector[:5])
