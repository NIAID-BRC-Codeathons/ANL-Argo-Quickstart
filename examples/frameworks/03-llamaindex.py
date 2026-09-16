#!/usr/bin/env python3
"""LlamaIndex OpenAILike + OpenAIEmbedding against Argo.

Install:
    pip install llama-index llama-index-llms-openai-like llama-index-embeddings-openai

Run:
    ARGO_USER=ac.yourname python3 03-llamaindex.py

Requires a connection to the Argonne-auth network.
"""
import os

from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai import OpenAIEmbedding

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

llm = OpenAILike(
    model="claudesonnet5",
    api_base="https://apps.inside.anl.gov/argoapi/v1",
    api_key=ARGO_USER,
    is_chat_model=True,      # required, or LlamaIndex uses the completions API
    context_window=200000,
    # OpenAILike defaults to temperature=0.1, which claudesonnet5 rejects with
    # "`temperature` is deprecated for this model." 1 is accepted everywhere.
    temperature=1.0,
    max_tokens=1024,   # must reach Argo as max_tokens, not max_completion_tokens;
                       # if you get a 500 "Streaming is required", see the quickstart
)

embed_model = OpenAIEmbedding(
    model_name="text-embedding-3-small",
    api_base="https://apps.inside.anl.gov/argoapi/v1",
    api_key=ARGO_USER,
)

print(llm.complete("In one sentence, what is a pangenome?"))
