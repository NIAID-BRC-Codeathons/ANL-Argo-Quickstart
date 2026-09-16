#!/usr/bin/env python3
"""Tool / function calling. Qwen only.

Sending tools to Llama on port 8003 fails with HTTP 400:
    "auto" tool choice requires --enable-auto-tool-choice and
    --tool-call-parser to be set
That is a server launch flag, not something you can fix from the client.

Install:
    pip install openai

Run:
    python3 04-qwen-tools.py

No credential required. Requires a connection to the Argonne-auth network.
"""
import os

from openai import OpenAI

HOST = os.environ.get("MANGO_HOST", "mango.cels.anl.gov")

client = OpenAI(api_key="EMPTY", base_url=f"http://{HOST}:8004/v1")

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
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[{"role": "user", "content": "Look up genome 83332.12 for me."}],
    tools=tools,
    tool_choice="auto",
    max_tokens=4000,
)

message = resp.choices[0].message

# Qwen may answer in prose instead of calling the tool, so check before indexing.
if message.tool_calls:
    call = message.tool_calls[0]
    print(call.function.name)        # lookup_genome
    print(call.function.arguments)   # {"genome_id": "83332.12"}
else:
    print("No tool call. Model said:", message.content)
