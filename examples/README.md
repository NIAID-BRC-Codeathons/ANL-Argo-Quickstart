# Argo examples

Runnable companions to the [main guide](../README.md). Every file here is extracted
from that document, so the two cannot drift apart.

## Before anything else

```bash
export ARGO_USER=ac.yourname      # your Argonne collaborator username
./00-smoke-test.sh
```

A JSON list of model names means network and auth are both working. A hang that
ends in a timeout means you are not on `Argonne-auth` — fix that before debugging
anything else.

Every script reads `ARGO_USER` from the environment and fails with a clear message
if it is unset, so you set your username once per shell rather than editing files.

## Layout

| Path | What it shows |
|---|---|
| [`00-smoke-test.sh`](00-smoke-test.sh) | Network + auth check. Run first. |
| [`curl/01-chat.sh`](curl/01-chat.sh) | Chat completion, OpenAI-compatible endpoint |
| [`curl/02-stream.sh`](curl/02-stream.sh) | Streaming chat |
| [`curl/03-messages-anthropic.sh`](curl/03-messages-anthropic.sh) | Chat via the Anthropic Messages endpoint |
| [`curl/04-embeddings.sh`](curl/04-embeddings.sh) | Text embeddings |
| [`curl/05-gpt5x.sh`](curl/05-gpt5x.sh) | GPT-5.x, showing `max_completion_tokens` |
| [`python/01-openai-chat.py`](python/01-openai-chat.py) | Chat with the `openai` SDK — drives any Argo model |
| [`python/02-openai-stream.py`](python/02-openai-stream.py) | Streaming, guarding the usage-only final chunk |
| [`python/03-openai-tools.py`](python/03-openai-tools.py) | Tool / function calling |
| [`python/04-openai-embeddings.py`](python/04-openai-embeddings.py) | Batch embeddings |
| [`python/05-openai-gpt5x.py`](python/05-openai-gpt5x.py) | GPT-5.x parameter difference |
| [`python/06-anthropic-messages.py`](python/06-anthropic-messages.py) | Messages with the `anthropic` SDK |
| [`python/07-anthropic-stream.py`](python/07-anthropic-stream.py) | Streaming plus final-message metadata |
| [`frameworks/env.sh`](frameworks/env.sh) | `source` to configure LangChain / LlamaIndex |
| [`frameworks/01-langchain-chat.py`](frameworks/01-langchain-chat.py) | `ChatOpenAI` against Argo |
| [`frameworks/02-langchain-embeddings.py`](frameworks/02-langchain-embeddings.py) | Embeddings + a minimal in-memory vector index |
| [`frameworks/03-llamaindex.py`](frameworks/03-llamaindex.py) | `OpenAILike` + `OpenAIEmbedding` |
| [`agents/claude-code.sh`](agents/claude-code.sh) | `source` to point Claude Code at Argo |
| [`agents/continue-config.yaml`](agents/continue-config.yaml) | Continue.dev model config |
| [`agents/aider.sh`](agents/aider.sh) | `source` to point aider at Argo |

`.sh` files under `curl/` are executable. Files under `agents/` and
`frameworks/env.sh` set environment variables — **source** them, don't run them.

## Install

```bash
pip install -r python/requirements.txt        # openai, anthropic
pip install -r frameworks/requirements.txt    # langchain, llama-index
```

## Two things that will bite you

**Model IDs are Argo's own.** `claudeopus5`, not `claude-opus-5`. Check
`GET /argoapi/v1/models` for the live list.

**Parameter rules differ by vendor family, and the differences bite at runtime.**
Anthropic models on the OpenAI-compatible endpoint need an explicit `max_tokens`
(≤ 21,000) or the call 500s; `claudesonnet5` rejects any `temperature` but `1` and any
`top_p`; `gpt5`/`gpt55`/`gpt56*` also require `temperature=1`. Opus 4.7+ accepts
sampling parameters and then ignores them. [Section 6 of the guide](../README.md#6-per-model-parameter-rules--read-this-before-you-debug)
has the measured table — read it before you debug a rejected call.

## Not covered here

Multimodal image input is supported on the OpenAI-compatible and Anthropic Messages
endpoints, but Argonne distributes its own template scripts for it. Ask the
organizers rather than adapting these files.
