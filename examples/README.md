# Argo examples

Runnable companions to the [main guide](../README.md). Every file here is extracted
from that document, so the two cannot drift apart.

Everything outside [`open/`](open/) talks to Argo. `open/` talks to the self-hosted
open-weight models on `mango.cels.anl.gov`, which are a different service with
different rules — see [Open models](#open-models--not-argo) below.

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
pip install -r open/requirements.txt          # openai (open models, see below)
```

## Open models — not Argo

[`open/`](open/) targets the three open-weight models served on
`mango.cels.anl.gov`: Llama 4 Scout (chat, port 8003), Qwen 3.6 (reasoning and tool
calling, port 8004), and SFR-Embedding-Mistral (embeddings, port 9998).
[`OpenModelCheatsheet.md`](../OpenModelCheatsheet.md) is the prose version.

These are not Argo, and none of the Argo conventions carry over:

- **No credential.** The servers require the `api_key` field and never check it;
  `"EMPTY"` is the convention. Your Argo username does not belong here.
- **Full Hugging Face model names**, not Argo short IDs —
  `RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic`, not `llama4scout`.
- **`MANGO_HOST`**, not `ARGO_USER`, is the environment variable the scripts read,
  and it defaults to `mango.cels.anl.gov`.

Same network, though: you still need to be on `Argonne-auth`.

```bash
./open/00-smoke-test.sh
```

| Path | What it shows |
|---|---|
| [`open/00-smoke-test.sh`](open/00-smoke-test.sh) | All three servers, health and served model ID. Run first. |
| [`open/01-llama-chat.py`](open/01-llama-chat.py) | Chat with Llama 4 Scout |
| [`open/02-qwen-chat.py`](open/02-qwen-chat.py) | Chat with Qwen 3.6, with a realistic `max_tokens` |
| [`open/03-qwen-stream.py`](open/03-qwen-stream.py) | Streaming |
| [`open/04-qwen-tools.py`](open/04-qwen-tools.py) | Tool / function calling — Qwen only |
| [`open/05-embeddings.py`](open/05-embeddings.py) | One embedding, 4,096 dimensions |
| [`open/06-embeddings-batch.py`](open/06-embeddings-batch.py) | Batch embeddings |
| [`open/curl/01-llama-chat.sh`](open/curl/01-llama-chat.sh) | Chat, raw HTTP |
| [`open/curl/02-qwen-chat.sh`](open/curl/02-qwen-chat.sh) | Chat, raw HTTP |
| [`open/curl/03-embeddings.sh`](open/curl/03-embeddings.sh) | Embeddings, raw HTTP |

Two gotchas, both measured:

**Qwen's reasoning spends your `max_tokens`.** Ask for 200 and you get
`content=''` with `finish_reason='length'` — an empty response, not a truncated one.
Budget 2,000–4,000 for simple questions, 8,000+ for hard ones.

**Only Qwen does tool calling.** Sending `tools` to Llama on 8003 fails with an HTTP
400 asking for `--enable-auto-tool-choice` and `--tool-call-parser`, which are server
launch flags, not client settings.

## Two things that will bite you (on Argo)

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
