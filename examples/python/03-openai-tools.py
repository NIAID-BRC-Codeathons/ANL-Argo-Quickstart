#!/usr/bin/env python3
"""Tool / function calling. Non-streaming path only.

Install:
    pip install openai

Run:
    ARGO_USER=ac.yourname python3 03-openai-tools.py

Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

ARGO_USER = os.environ.get("ARGO_USER", "ac.jdoe")

client = OpenAI(api_key=ARGO_USER, base_url="https://apps.inside.anl.gov/argoapi/v1")

tools = [{
    "type": "function",
    "function": {
        "name": "lookup_genome",
        "description": "Look up a genome record in BV-BRC by its genome ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "genome_id": {
                    "type": "string",
                    "description": "BV-BRC genome identifier, e.g. 83332.12",
                },
            },
            "required": ["genome_id"],
        },
    },
}]

resp = client.chat.completions.create(
    model="claudesonnet5",
    messages=[{"role": "user", "content": "Look up genome 83332.12 for me."}],
    tools=tools,
    max_tokens=500,
)

call = resp.choices[0].message.tool_calls[0]
print(call.function.name)        # lookup_genome
print(call.function.arguments)   # {"genome_id": "83332.12"}
