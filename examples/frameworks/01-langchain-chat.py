#!/usr/bin/env python3
"""LangChain ChatOpenAI pointed at Argo.

Install:
    pip install langchain-openai

Run:
    ARGO_USER=ac.yourname python3 01-langchain-chat.py

Requires a connection to the Argonne-auth network.
"""
import os

from langchain_openai import ChatOpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

llm = ChatOpenAI(
    model="claudesonnet5",
    base_url="https://apps.inside.anl.gov/argoapi/v1",
    api_key=ARGO_USER,          # your username, not a key
    # temperature=1 is the only value claudesonnet5 and the gpt5/gpt55/gpt56*
    # models accept, and every other Argo model accepts it too. Set it
    # explicitly: if you omit it, langchain-openai may send its own default.
    temperature=1,
    # Argo reads only max_tokens for Claude models, and recent langchain-openai
    # puts max_completion_tokens on the wire instead. Force the field Argo reads.
    # Older langchain-openai without extra_body: model_kwargs={"max_tokens": 1024}
    extra_body={"max_tokens": 1024},
)

print(llm.invoke("In one sentence, what is a pangenome?").content)
