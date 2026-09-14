#!/usr/bin/env python3
"""LangChain embeddings plus a minimal in-memory vector index.

Install:
    pip install langchain-openai

Run:
    ARGO_USER=ac.yourname python3 02-langchain-embeddings.py

Requires a connection to the codeathon network.
"""
import os

from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",   # official name — see note in §4
    base_url="https://apps.inside.anl.gov/argoapi/v1",
    api_key=ARGO_USER,
    # langchain-openai pre-tokenizes text and sends token-ID arrays, which Argo
    # rejects with a 422. This flag makes it send plain strings instead.
    check_embedding_ctx_length=False,
)

docs = [
    "Klebsiella pneumoniae is a Gram-negative bacterium.",
    "BV-BRC provides genomic data and analysis tools for bacterial pathogens.",
]

# InMemoryVectorStore ships with langchain-core: no extra dependency and no
# sunset warning. For an index bigger than a demo, swap in FAISS
# (pip install langchain-community faiss-cpu) — same from_texts/similarity_search API.
store = InMemoryVectorStore.from_texts(docs, embeddings)
print(store.similarity_search("What is BV-BRC?", k=1)[0].page_content)
