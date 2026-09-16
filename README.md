# Using AI Models with Argo
### 2026 NIAID AI Codeathon — participant quick start

Argo is Argonne National Laboratory's LLM gateway. It gives you one consistent
API in front of frontier models from **OpenAI, Anthropic, and Google**, plus text
embedding models. For this codeathon, your organizers have arranged Argo access
for every participant.

Two things make Argo different from calling OpenAI or Anthropic directly:

1. **There are no API keys.** Your Argonne collaborator username *is* your credential.
2. **Model names are Argo-specific short strings** — `claudeopus5`, not `claude-opus-5`.

Everything else behaves like the vendor APIs you already know.

## What's in this repo

Every code block below is also a runnable file under [`examples/`](examples/), so you
can clone the repo and run rather than copy out of a web page. Each block links to its
file.

```
examples/
├── 00-smoke-test.sh        network + auth check — run this first
├── curl/                   zero-dependency HTTP, one script per endpoint
├── python/                 the openai and anthropic SDKs
├── frameworks/             LangChain and LlamaIndex
└── agents/                 Claude Code, Continue.dev, aider
```

[`examples/README.md`](examples/README.md) has the per-file index.

**Two-minute start:**

```bash
git clone https://github.com/NIAID-BRC-Codeathons/ANL-Argo-Quickstart
cd ANL-Argo-Quickstart
export ARGO_USER=ac.yourname          # your Argonne collaborator username
./examples/00-smoke-test.sh           # JSON list of models = you're good
```

Every script reads `ARGO_USER` from the environment and fails with a clear message if
it is unset, so you set your username once per shell instead of editing files.

> **Before you send real data**, read [§2 What you may send](#2-what-you-may-send).
> There are limits on what may go through this gateway.

A standalone styled version of this guide is in `argo-quickstart.html` — open it
locally, or publish it with GitHub Pages if you want a link to hand out.

## Contents

| | | | |
|---|---|---|---|
| [1 Before your first call](#1-before-your-first-call) | [2 What you may send](#2-what-you-may-send) | [3 Authentication](#3-authentication) | [4 Endpoints](#4-endpoints) |
| [5 Choosing a model](#5-choosing-a-model) | [6 Parameter rules](#6-per-model-parameter-rules--read-this-before-you-debug) | [7 curl](#7-curl--the-zero-dependency-path) | [8 Python SDKs](#8-python-the-openai-and-anthropic-sdks) |
| [9 LangChain & LlamaIndex](#9-langchain-and-llamaindex) | [10 Coding assistants](#10-ai-coding-assistants) | [11 Troubleshooting](#11-troubleshooting) | [12 Usage etiquette](#12-usage-etiquette) |
| [13 Getting help](#13-getting-help) | | | |

---

## 1. Before your first call

**Connect to the `Argonne-auth` wireless network.**

Log in with your collaborator username — `ac.jdoe` — and the domain password you set
up when your account was created. Argonne staff connect to `Argonne-auth` with their
normal credentials.

This is important and easy to forget. Argo lives at `apps.inside.anl.gov`, which is
only reachable from inside Argonne's network. `Argonne-auth` is your path in. Off that
network — on hotel wifi, a phone hotspot, or a cloud VM — **every call will hang and
time out**. A connection timeout almost always means "wrong network," not "broken
code."

> **Your domain password gets you onto the network and nothing else.** It is not part
> of any Argo call — the API authenticates on your username alone. If an example or a
> tool ever seems to want a password, it is misconfigured. Never put your domain
> password in a script, a config file, or an environment variable.

**Know your username.** It looks like `ac.jdoe`. You need the bare username:

- ✅ `ac.jdoe`
- ❌ `ac.jdoe@anl.gov` — no email addresses
- ❌ `"ac.jdoe"` — no surrounding quotes or other special characters

Argo validates this on every call (the lookup is cached for 24 hours, so long
runs don't pay a database round-trip each time). Calls are logged against your
username for usage accounting.

**Smoke test.** Run this first. It proves network *and* auth in one shot:

```bash
curl -sS https://apps.inside.anl.gov/argoapi/v1/models \
  -H "Authorization: Bearer ac.jdoe"
```

▶ **Run it:** [`examples/00-smoke-test.sh`](examples/00-smoke-test.sh)

A JSON list of model names means you're good. Anything else — see
[Troubleshooting](#11-troubleshooting).

---

## 2. What you may send

Argo is a gateway. Your prompt is not processed on a machine in an Argonne server
room — it goes to a commercial model running in cloud infrastructure Argonne
controls. Argonne's position on what that means:

- **Argo is approved for CUI.**
- **Processing stays in US-based data centers.** This holds across every model family
  Argo fronts: the OpenAI models run in Argonne's Microsoft tenancy under the same
  controls that govern its M365 environment, and the Anthropic and Google models run
  in an equivalent US-based enclave.

**Be deliberate anyway.** An approval covers the platform. It does not cover the
decision to put a particular dataset into a prompt, and that decision is yours. If
data is not yours to publish — unpublished collaborator results, clinical or
personally identifying records, embargoed or otherwise restricted material — clear it
with the data owner before it goes into a prompt. Argonne asks users to keep
personally identifying information out of prompts in particular. The blunt reason to
care: if something does end up somewhere it shouldn't, "the platform was approved"
will not be much comfort to you, and the codeathon organizers would rather nobody ends
up pointing at Argonne over a judgment call made at this event.

This applies to files as much as to what you type. A coding assistant transmits the
contents of the files it reasons about, so the rule covers your working directory, not
just the chat box.

**Guardrails belong to the model vendor, not to Argonne.** Your calls are subject to
whatever content filters are in place on the target model, and those vary by model
family. A scientifically routine prompt can be refused or flagged — the Argo
maintainers documented a plain code-generation prompt being rejected as a suspected
policy violation. When that happens it is the provider's filter, not a problem with
your account: rephrase, or try another model family.

**What Argonne records.** Argonne does not store the content of prompts or responses,
and does not use them to train or improve the models. What it does record is usage
metadata — your username, the time, the model, and the *length* of each prompt and
response. Your usage is therefore logged against your `ac.` username and is
attributable to you.

If you are unsure whether something is safe to send, ask the codeathon organizers
before you send it, not after.

---

## 3. Authentication

Wherever a client library asks for an API key, **put your username there instead**.

| Client expects | You supply |
|---|---|
| `api_key` / `OPENAI_API_KEY` | `ac.jdoe` |
| `Authorization:` header | `Bearer ac.jdoe` |
| `x-api-key` (Anthropic-style) | `ac.jdoe` |
| `user` field in request body (legacy endpoints) | `ac.jdoe` |

That's the whole auth model — but understand what it does and doesn't protect.

**Your username is an identifier, not a secret.** There is no key to rotate and
nothing to leak, because there is nothing secret in the first place. Usernames appear
in email addresses, commit logs, and papers. Anyone who can reach the gateway and
knows your username can make calls as you.

What follows from that:

- **The network is the access control.** Argo is protected by being reachable only
  from inside Argonne, not by your credential. The thing actually worth protecting is
  your domain password, because that is what puts you on `Argonne-auth`.
- **Attribution is a claim, not a proof.** Usage is recorded against whatever username
  was sent. Use your own, and only your own.
- **A terminal screenshot contains your credential.** Harmless among participants on
  the same network; worth a thought before posting one publicly.

None of this requires anything of you beyond normal account hygiene. It does mean
"there's no API key" should read as *simpler*, not as *safer*.

---

## 4. Endpoints

Base URL: **`https://apps.inside.anl.gov/argoapi`**

| What you want | Endpoint |
|---|---|
| OpenAI-compatible base URL | `https://apps.inside.anl.gov/argoapi/v1` |
| Chat completions (OpenAI-style) | `.../argoapi/v1/chat/completions` |
| Messages (Anthropic-style) | `.../argoapi/v1/messages` |
| Embeddings (OpenAI-style) | `.../argoapi/v1/embeddings` |
| List available models | `.../argoapi/v1/models` |
| Interactive API explorer (Swagger UI) | `.../argoapi/docs` |
| Chat — Argo legacy format | `.../argoapi/api/v1/resource/chat/` |
| Streaming chat — Argo legacy format | `.../argoapi/api/v1/resource/streamchat/` |
| Embeddings — Argo legacy format | `.../argoapi/api/v1/resource/embed/` |

> **Use `apps.inside.anl.gov`, not `apps-dev.inside.anl.gov`.** The `-dev` host is an
> unstable R&D environment that changes without notice. Older examples and blog posts
> floating around still reference it; drop the `-dev`.

The **Swagger UI at `/argoapi/docs`** is worth five minutes early on. You can fire
test calls from the browser and see exactly what the gateway accepts.

The `/v1` endpoints are the ones to build on. The legacy `/api/v1/resource/*`
endpoints still work but use a non-standard request and response shape (a bare
`{"response": "..."}` object), so no off-the-shelf client speaks them.

---

## 5. Choosing a model

Argo uses its own short model IDs. Query `/v1/models` for the live list — the table
below is a curated starting point, current as of the Argo documentation dated
**August 3, 2026**.

### Good defaults for a codeathon

| Use case | Model ID | Context / max output |
|---|---|---|
| Best overall, agentic coding | `claudeopus5` | 1M / 128k |
| Strong general work, cheaper | `claudesonnet5` | — |
| Long-context general work | `claudesonnet46` | 1M / 64k |
| Fast and inexpensive | `claudehaiku45` | 200k / 64k |
| OpenAI frontier | `gpt56sol` | 1.05M / 128k |
| OpenAI balanced (mini tier) | `gpt56terra` | 1.05M / 128k |
| OpenAI high-volume (nano tier) | `gpt56luna` | 1.05M / 128k |
| Google, long context | `gemini35flash` | 1.05M / 64k |
| Google, cheapest | `gemini31flashlite` | 1.05M / 64k |
| Embeddings, general | `v3small` (`text-embedding-3-small`) | 8,191 in / 1,536 dim |
| Embeddings, highest quality | `v3large` (`text-embedding-3-large`) | 8,191 in / 3,072 dim |

### Also available

**Anthropic:** `claudeopus48`, `claudeopus47`, `claudeopus46`, `claudeopus45`, `claudeopus41`, `claudesonnet45`

**OpenAI:** `gpt55`, `gpt54`, `gpt54mini`, `gpt54nano`, `gpt52`, `gpt51`, `gpt5`, `gpt5mini`, `gpt5nano`, `gpt41`, `gpt41mini`, `gpt41nano`, `gpto1`, `gpto3`, `gpto3mini`, `gpto4mini`, `gpt4o`

**Google:** `gemini25pro`, `gemini25flash` *(both slated for deprecation — don't start new work on them)*

**Embeddings:** `ada002` (`text-embedding-ada-002`)

**Deprecated — do not use:** `gpt35`, `gpt35large`, `gpt4`, `gpt4large`, `gpt4turbo`, `gpt4olatest`, `gpto1preview`, `gpto1mini`, `claudeopus4`, `claudesonnet4`, `claudesonnet37`, `claudesonnet35v2`, `claudehaiku35`

> Embedding models accept **either** the Argo short name (`v3small`) or the official
> OpenAI name (`text-embedding-3-small`). Prefer the official name with LangChain and
> LlamaIndex — those libraries sometimes validate embedding model names client-side and
> will reject `v3small` before the request ever leaves your machine.

---

## 6. Per-model parameter rules — read this before you debug

This is the single biggest source of lost time with Argo. Each vendor family accepts
a different set of sampling and length parameters, and the gateway passes your call
through to the vendor, so vendor-side rules apply.

| Model family | Rules |
|---|---|
| `claudesonnet5` | **Rejects `temperature` at any value other than `1`, and rejects `top_p` entirely**, with a 400: `` `temperature` is deprecated for this model. `` It is the only Claude model on Argo that does this. `top_k` is accepted. Send `temperature=1` or nothing at all. |
| `claudeopus5`, `claudeopus48`, `claudeopus47` | Accept `temperature` and `top_p` without complaint, but **the values have no effect** — they are stripped before the vendor call. Steer behavior through prompting. `max_tokens` is required. Extended thinking uses the `output_config` parameter, which Argo passes through. |
| `claudesonnet46`, `claudesonnet45`, `claudehaiku45`, `claudeopus46`, `claudeopus45`, `claudeopus41` | Accept `temperature`, `top_p`, both, or neither. Sending both is not an error — Argo drops `top_p` — but pick one and you'll get what you asked for. If you omit them, Argo defaults to `max_tokens=21000`, `temperature=0.7`, `top_p=0.9`. |
| **All Anthropic models** | Require non-empty **user** content. A system prompt alone, or a whitespace-only user message, errors out — Argo substitutes `"[continue]"` to avoid this. |
| **All Anthropic models**, on `/v1/chat/completions` | **You must send `max_tokens` explicitly, and keep it at 21,000 or below for non-streaming calls.** Argo reads only `max_tokens` here — `max_completion_tokens` is silently ignored. Omit the limit, or set it above ~21,000, and the call fails with a 500. Stream instead when you need more. |
| `gpt5`, `gpt55`, `gpt56sol`, `gpt56terra`, `gpt56luna` | `temperature` must be exactly **1**, or omitted. Any other value is a 400: `Unsupported value: 'temperature' does not support 0.2 with this model.` `top_p` and `max_completion_tokens` are fine. `gpt41`, `gpt4o`, `gpt51`, `gpt52` and `gpt54` are *not* affected — they take any temperature. |
| **All GPT-5.x** (`gpt5`…`gpt56*`) | On Argo's `/v1/chat/completions`, **either** `max_tokens` or `max_completion_tokens` works, and omitting both is fine — Argo normalizes. (OpenAI's own API rejects `max_tokens` for these models; Argo does not.) |
| **o-series** (`gpto1`, `gpto3`, `gpto3mini`, `gpto4mini`) | No `temperature`, `top_p`, or `max_tokens`. Use `max_completion_tokens`. |
| **Gemini** | Argo maps `max_tokens` → `max_output_tokens` and `stop` → `stop_sequences` for you. Any `temperature` is accepted. |
| `gemini35flash` | **Give it a generous `max_tokens` (2,048+) or omit it.** It spends its output budget on internal reasoning first, so a small limit leaves nothing for the answer and the call dies with a 500: `'NoneType' object has no attribute 'parts'`. `gemini31flashlite` and `gemini25flash` are fine at small limits. |

*Every rule in this table was measured against the Argo gateway on 2026-09-14 by
sending the parameter in question to each model and recording the response. Where it
contradicts the Argo API notes, trust the table — the notes predate the newest models.*

> **If you see `500 — Streaming is required for operations that may take longer than
> 10 minutes`**, this is the cause. It is Anthropic-only: GPT and Gemini models are
> unaffected and are happy with no token limit at all. Verified against Opus 5,
> Opus 4.5, Sonnet 5, Sonnet 4.6, and Haiku 4.5.

**Feature availability:**

- **Tool / function calling** — fully working on the non-streaming chat path for OpenAI, Google, and Anthropic models. Disabled on the legacy `/streamchat/` endpoint, which returns an informational error. Gemini tool calling is the least battle-tested; report breakage.
- **Image input** — supported on the OpenAI-compatible and Anthropic Messages endpoints for multimodal OpenAI, Google, and Anthropic models. **Attach files directly or base64-encode them; don't pass public web URLs.**
- **Streaming** — available across models on the streaming paths.

---

## 7. curl — the zero-dependency path

Good for smoke tests, shell scripts, and proving a problem isn't your Python env.

### Chat completion (OpenAI-compatible)

```bash
curl -sS https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer ac.jdoe" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudesonnet5",
    "messages": [
      {"role": "system", "content": "You are a concise bioinformatics assistant."},
      {"role": "user", "content": "In one sentence, what is a pangenome?"}
    ],
    "max_tokens": 300
  }'
```

▶ **Run it:** [`examples/curl/01-chat.sh`](examples/curl/01-chat.sh)

### Streaming

```bash
curl -sS -N https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer ac.jdoe" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudesonnet5",
    "messages": [{"role": "user", "content": "Count to five."}],
    "max_tokens": 100,
    "stream": true
  }'
```

▶ **Run it:** [`examples/curl/02-stream.sh`](examples/curl/02-stream.sh)

`-N` disables curl's output buffering so you see tokens as they arrive.

### Anthropic Messages format

```bash
curl -sS https://apps.inside.anl.gov/argoapi/v1/messages \
  -H "x-api-key: ac.jdoe" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claudeopus5",
    "max_tokens": 1024,
    "system": "You are a concise bioinformatics assistant.",
    "messages": [{"role": "user", "content": "What is a pangenome?"}]
  }'
```

▶ **Run it:** [`examples/curl/03-messages-anthropic.sh`](examples/curl/03-messages-anthropic.sh)

### Embeddings

```bash
curl -sS https://apps.inside.anl.gov/argoapi/v1/embeddings \
  -H "Authorization: Bearer ac.jdoe" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": ["first document", "second document"]
  }'
```

▶ **Run it:** [`examples/curl/04-embeddings.sh`](examples/curl/04-embeddings.sh)

`input` takes a single string or a list. The response is standard OpenAI shape:
`data[i].embedding` holds each vector, with `usage.prompt_tokens` and
`usage.total_tokens` alongside.

### A GPT-5.x call, showing the parameter difference

```bash
curl -sS https://apps.inside.anl.gov/argoapi/v1/chat/completions \
  -H "Authorization: Bearer ac.jdoe" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt56sol",
    "messages": [{"role": "user", "content": "What is a pangenome?"}],
    "max_completion_tokens": 300
  }'
```

▶ **Run it:** [`examples/curl/05-gpt5x.sh`](examples/curl/05-gpt5x.sh)

Argo accepts `max_tokens` here too, despite OpenAI's own API rejecting it for GPT-5.x — the gateway normalizes. `max_completion_tokens` is the portable choice.

---

## 8. Python: the openai and anthropic SDKs

The two official vendor SDKs both work against Argo unmodified — you are only
overriding the base URL and passing your username where a key would go.

Which to reach for:

- **`openai`** talks to Argo's OpenAI-compatible endpoint and can drive **every** model Argo offers — OpenAI, Anthropic, and Google alike. This is the one to use unless you need something Anthropic-specific.
- **`anthropic`** talks to Argo's Anthropic Messages endpoint and only drives `claude*` models, but gives you the native Anthropic request shape — including `output_config` for extended thinking on Opus 4.7+.

```bash
pip install openai anthropic
```

▶ **Install:** [`examples/python/requirements.txt`](examples/python/requirements.txt)

### OpenAI SDK — chat

```python
from openai import OpenAI

client = OpenAI(
    api_key="ac.jdoe",      # your username, not a key
    base_url="https://apps.inside.anl.gov/argoapi/v1",
)

resp = client.chat.completions.create(
    model="claudesonnet5",
    messages=[
        {"role": "system", "content": "You are a concise bioinformatics assistant."},
        {"role": "user", "content": "In one sentence, what is a pangenome?"},
    ],
    max_tokens=300,
)

print(resp.choices[0].message.content)
```

▶ **Run it:** [`examples/python/01-openai-chat.py`](examples/python/01-openai-chat.py)

Swapping `model="gemini35flash"` or `model="gpt56sol"` is the only change needed to
move between vendors — mind the parameter rules in §6 when you do.

### OpenAI SDK — streaming

Guard against chunks with an empty `choices` list — the final usage chunk has none,
and indexing it blindly is the most common way a streaming loop dies one token from
the end.

```python
from openai import OpenAI

client = OpenAI(
    api_key="ac.jdoe",      # your username, not a key
    base_url="https://apps.inside.anl.gov/argoapi/v1",
)

stream = client.chat.completions.create(
    model="claudesonnet5",
    messages=[{"role": "user", "content": "Count to five."}],
    max_tokens=100,
    stream=True,
)

parts = []
for chunk in stream:
    if not chunk.choices:          # final usage-only chunk carries no choices
        continue
    delta = chunk.choices[0].delta.content
    if delta:
        parts.append(delta)
        print(delta, end="", flush=True)

print()                            # close the line once the stream ends
full_text = "".join(parts)
print(f"[{len(full_text)} characters]")
```

▶ **Run it:** [`examples/python/02-openai-stream.py`](examples/python/02-openai-stream.py)

### OpenAI SDK — tool calling

Use the non-streaming path; tool calling is disabled on the streaming endpoint.

```python
from openai import OpenAI

client = OpenAI(api_key="ac.jdoe", base_url="https://apps.inside.anl.gov/argoapi/v1")

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
```

▶ **Run it:** [`examples/python/03-openai-tools.py`](examples/python/03-openai-tools.py)

Argo translates this standard OpenAI tool schema into each vendor's native format,
so the same code works against Anthropic and Google models.

### OpenAI SDK — embeddings

```python
from openai import OpenAI

client = OpenAI(api_key="ac.jdoe", base_url="https://apps.inside.anl.gov/argoapi/v1")

resp = client.embeddings.create(
    model="text-embedding-3-small",
    input=["first document", "second document"],
)

for item in resp.data:
    print(item.index, len(item.embedding))   # 0 1536 / 1 1536
```

▶ **Run it:** [`examples/python/04-openai-embeddings.py`](examples/python/04-openai-embeddings.py)

Batches are capped at **16 strings per request**. Chunk longer lists yourself.

### OpenAI SDK — a GPT-5.x call

```python
from openai import OpenAI

client = OpenAI(api_key="ac.jdoe", base_url="https://apps.inside.anl.gov/argoapi/v1")

resp = client.chat.completions.create(
    model="gpt56sol",
    messages=[{"role": "user", "content": "What is a pangenome?"}],
    max_completion_tokens=300,   # portable; Argo also accepts max_tokens here
)

print(resp.choices[0].message.content)
```

▶ **Run it:** [`examples/python/05-openai-gpt5x.py`](examples/python/05-openai-gpt5x.py)

### Anthropic SDK — messages

Note the base URL here has **no `/v1`**. The Anthropic client appends its own path.

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="ac.jdoe",      # your username, not a key
    base_url="https://apps.inside.anl.gov/argoapi",
)

msg = client.messages.create(
    model="claudeopus5",
    max_tokens=1024,
    system="You are a concise bioinformatics assistant.",
    messages=[{"role": "user", "content": "What is a pangenome?"}],
)

# claudeopus5 has extended thinking on by default, so content[0] is a
# ThinkingBlock, not text. Join every text block instead of indexing.
print("".join(b.text for b in msg.content if b.type == "text"))
```

▶ **Run it:** [`examples/python/06-anthropic-messages.py`](examples/python/06-anthropic-messages.py)

**`claudeopus5` returns a `thinking` block before its `text` block** — extended
thinking is on by default for that model on Argo. Indexing `msg.content[0].text`
raises `AttributeError: 'ThinkingBlock' object has no attribute 'text'`. Filter by
block type, as above. Every other Claude model on Argo returns text alone, but the
filter is correct for all of them, so write it that way from the start.

`max_tokens` is required by the Anthropic API and by Argo. `temperature` and `top_p`
are silently discarded by Opus 4.7+, and `claudesonnet5` rejects both outright unless
`temperature` is exactly `1` — see §6.

### Anthropic SDK — streaming

`text_stream` yields text deltas only. Call `get_final_message()` inside the
context manager if you also need the stop reason, token usage, or tool calls.

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="ac.jdoe",      # your username, not a key
    base_url="https://apps.inside.anl.gov/argoapi",
)

with client.messages.stream(
    model="claudeopus5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Count to five."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    final = stream.get_final_message()   # call inside the context manager

print()
print(f"[{final.stop_reason}] {final.usage.output_tokens} output tokens")
```

▶ **Run it:** [`examples/python/07-anthropic-stream.py`](examples/python/07-anthropic-stream.py)

Streaming is also how you get past the **21,000 output token ceiling** on Anthropic
models — above that, non-streaming calls truncate.

---

## 9. LangChain and LlamaIndex

Both work against Argo's OpenAI-compatible endpoint. You are configuring the
*OpenAI* integration and pointing it at Argo — even when the model behind it is
Claude or Gemini.

### Setup

```bash
pip install langchain langchain-openai
# or
pip install llama-index llama-index-llms-openai-like llama-index-embeddings-openai
```

```bash
export OPENAI_API_KEY=ac.jdoe
export OPENAI_BASE_URL=https://apps.inside.anl.gov/argoapi/v1
```

▶ **Source it:** [`examples/frameworks/env.sh`](examples/frameworks/env.sh)

Setting the environment variables keeps credentials out of your source and means
most examples from the LangChain docs work unmodified.

### LangChain — chat

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="claudesonnet5",
    base_url="https://apps.inside.anl.gov/argoapi/v1",
    api_key="ac.jdoe",          # your username, not a key
    temperature=1,              # the one value every Argo model accepts
    # Argo reads only max_tokens for Claude models, and recent langchain-openai
    # puts max_completion_tokens on the wire instead. Force the field Argo reads.
    extra_body={"max_tokens": 1024},
)

print(llm.invoke("In one sentence, what is a pangenome?").content)
```

▶ **Run it:** [`examples/frameworks/01-langchain-chat.py`](examples/frameworks/01-langchain-chat.py)

### LangChain — embeddings and a minimal RAG index

```python
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",   # official name — see note in §5
    base_url="https://apps.inside.anl.gov/argoapi/v1",
    api_key="ac.jdoe",
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
```

▶ **Run it:** [`examples/frameworks/02-langchain-embeddings.py`](examples/frameworks/02-langchain-embeddings.py)

Batch embedding requests are capped at **16 strings per call**. LangChain chunks
automatically, but if you are calling the endpoint yourself, split your batches.

### LlamaIndex

```python
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai import OpenAIEmbedding

llm = OpenAILike(
    model="claudesonnet5",
    api_base="https://apps.inside.anl.gov/argoapi/v1",
    api_key="ac.jdoe",
    is_chat_model=True,      # required, or LlamaIndex uses the completions API
    context_window=200000,
    max_tokens=1024,
)

embed_model = OpenAIEmbedding(
    model_name="text-embedding-3-small",
    api_base="https://apps.inside.anl.gov/argoapi/v1",
    api_key="ac.jdoe",
)

print(llm.complete("In one sentence, what is a pangenome?"))
```

▶ **Run it:** [`examples/frameworks/03-llamaindex.py`](examples/frameworks/03-llamaindex.py)

Use `OpenAILike`, not `OpenAI`. The stock `OpenAI` class checks model names against
a hardcoded list of OpenAI models and will reject `claudesonnet5`.

### Framework caveats

These trip people up because the framework sends parameters you didn't write:

- **Default temperature.** Frameworks send a temperature you didn't write: `ChatOpenAI` has historically defaulted to `0.7`, and LlamaIndex's `OpenAILike` defaults to `0.1`. Both are rejected by `claudesonnet5` and by `gpt5`/`gpt55`/`gpt56*`. **Set `temperature=1` explicitly** — it is accepted by every model on Argo, and writing it out stops the framework from substituting its own default. Deleting the argument is *not* equivalent.
- **`max_tokens` vs `max_completion_tokens`.** Recent `langchain-openai` sends `max_completion_tokens` on the wire even when you write `max_tokens=...`. Argo ignores that field for Claude models, so the call arrives with no limit and fails. Force the field Argo reads with `extra_body={"max_tokens": 1024}` (older versions: `model_kwargs={"max_tokens": 1024}`). GPT and Gemini models need no workaround.
- **`top_p` on `claudesonnet5` is a hard error**, not a silently-dropped parameter. Other Claude models accept both `temperature` and `top_p` and quietly drop `top_p`; `claudesonnet5` returns a 400.
- **Embeddings are sent as token arrays.** `OpenAIEmbeddings` tokenizes your text client-side and posts token-ID arrays, which Argo rejects with `422 — Input should be a valid string`. Pass `check_embedding_ctx_length=False` to send plain strings. That also turns off LangChain's automatic chunking of over-long inputs, so split documents yourself (a text splitter) and keep each chunk under the model's 8,191-token limit. LlamaIndex's `OpenAIEmbedding` sends strings already and needs no flag.
- **tiktoken warnings.** Token-counting helpers don't recognize Argo model IDs and may warn or fall back to a default encoding. Harmless; silence it with `tiktoken_model_name="gpt-4o"` if it's noisy.
- **Structured output and tool calling** go through the standard OpenAI tool-calling schema. Argo translates to each vendor's native format. Anthropic and OpenAI models are solid here; Gemini is the least tested.

---

## 10. AI coding assistants

Any tool that speaks the OpenAI or Anthropic wire format can be pointed at Argo.
The pattern is always the same: **override the base URL, and use your username
where the tool asks for an API key.**

> Argonne maintains a dedicated **"Vibe Coding with Argo"** guide with per-tool
> configuration and maintained config templates. Ask the codeathon organizers for
> access. Treat that guide as authoritative if it disagrees with the settings below.

**Two things to know before you point an agent at Argo.**

*The variable is named like a secret, but holds your username.* Several tools read
`ANTHROPIC_AUTH_TOKEN` or `OPENAI_API_KEY`; against Argo you put `ac.jdoe` there. Two
consequences: the value lands in your shell history and any rc file you add it to, and
the name invites you to later paste a *real* vendor API key into the same variable.
Keep these exports in a per-project file you source (as in `examples/agents/`), not in
`~/.bashrc`, and don't commit them.

*Coding agents run commands and edit files.* Claude Code, Aider, and Continue act on
your machine with your permissions, and they act on text they read from the repository
— so a file in a checkout you didn't write can influence what the agent does. Point
them at your codeathon workspace, not at a personal or privileged checkout, and read
what they propose before approving it.

### Claude Code

Point it at Argo's Anthropic Messages endpoint:

```bash
export ANTHROPIC_BASE_URL=https://apps.inside.anl.gov/argoapi
export ANTHROPIC_AUTH_TOKEN=ac.jdoe
export ANTHROPIC_MODEL=claudeopus5
export ANTHROPIC_SMALL_FAST_MODEL=claudehaiku45
claude
```

▶ **Source it:** [`examples/agents/claude-code.sh`](examples/agents/claude-code.sh)

`ANTHROPIC_SMALL_FAST_MODEL` handles background tasks; pointing it at Haiku keeps
those cheap. Note the base URL here has **no `/v1`** — the Anthropic client appends
its own path.

### Continue.dev (VS Code / JetBrains)

In `~/.continue/config.yaml`:

```yaml
models:
  - name: Claude Opus 5 (Argo)
    provider: openai
    model: claudeopus5
    apiBase: https://apps.inside.anl.gov/argoapi/v1
    apiKey: ac.jdoe
    roles: [chat, edit, apply]

  - name: Claude Haiku 4.5 (Argo)
    provider: openai
    model: claudehaiku45
    apiBase: https://apps.inside.anl.gov/argoapi/v1
    apiKey: ac.jdoe
    roles: [autocomplete]
```

▶ **Copy it:** [`examples/agents/continue-config.yaml`](examples/agents/continue-config.yaml)

Argonne maintains an up-to-date Continue template in the Vibe Coding guide — grab
that rather than hand-rolling if you can.

### Kilo Code, Cline, Roo Code

In the extension's provider settings:

- **API Provider:** `OpenAI Compatible`
- **Base URL:** `https://apps.inside.anl.gov/argoapi/v1`
- **API Key:** `ac.jdoe`
- **Model ID:** `claudeopus5` (type it manually — the model list may not autopopulate)

### aider

```bash
export OPENAI_API_BASE=https://apps.inside.anl.gov/argoapi/v1
export OPENAI_API_KEY=ac.jdoe
aider --model openai/claudesonnet5
```

▶ **Source it:** [`examples/agents/aider.sh`](examples/agents/aider.sh)

### argo-proxy

Several Argo examples reference **`argo-proxy`**, a local process that exposes an
OpenAI-compatible endpoint in front of Argo. It predates Argo's native
OpenAI-compatible support and is still handy for tools that are fussy about
endpoint behavior. It is not required — native `/v1` support covers most cases.
Ask the organizers if a tool only works through it.

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Connection hangs, then times out | Not on the Argonne network | Join `Argonne-auth`. Verify with the `/v1/models` smoke test in §1. |
| Username validation error | Malformed username | Bare username only: `ac.jdoe`. No `@anl.gov`, no quotes, no special characters. |
| Error listing valid model names | Bad `model` value | Use an Argo ID from §5 or `GET /v1/models`. Vendor names like `claude-opus-5` are not accepted. |
| Error mentioning `max_tokens` | o-series model | Use `max_completion_tokens`. GPT-5.x on Argo accepts either. |
| `400` — `` `temperature` is deprecated for this model. `` | `claudesonnet5` with any `temperature` but `1` | Set `temperature=1`, or drop the parameter. A framework may be injecting its own default — set it explicitly rather than deleting it. |
| `400` — `` `top_p` is deprecated for this model. `` | `claudesonnet5` with `top_p` | `claudesonnet5` takes no `top_p` at all. Remove it; `top_k` works if you need it. |
| `400` — `Unsupported value: 'temperature' does not support …` | `gpt5`, `gpt55`, or a `gpt56*` model | `temperature` must be exactly `1`, or omitted. |
| `500` — `'NoneType' object has no attribute 'parts'` | `gemini35flash` with a small `max_tokens` | Raise `max_tokens` to 2,048+ or omit it. Reasoning consumed the whole budget, leaving no answer. |
| Empty or errored Anthropic response | No user content | Anthropic models need a non-empty user message; a system prompt alone won't do. |
| `500` &ldquo;Streaming is required for operations that may take longer than 10 minutes&rdquo; | No `max_tokens` reached an Anthropic model — omitted, above ~21,000, or sent as `max_completion_tokens`, which Argo ignores | Pass `max_tokens` ≤ 21,000 explicitly. From LangChain use `extra_body={"max_tokens": 1024}`. Stream if you need more output. |
| `AttributeError: 'ThinkingBlock' object has no attribute 'text'` | `claudeopus5` returned a thinking block first | Don't index `content[0]`. Use `"".join(b.text for b in msg.content if b.type == "text")`. |
| `ModuleNotFoundError: No module named 'llama_index.llms.openai_like'` | `llama-index` is a meta-package; adapters ship separately | `pip install llama-index-llms-openai-like`. Same pattern for other LlamaIndex integrations. |
| `422` — `Input should be a valid string` on `/v1/embeddings` | LangChain sent pre-tokenized token-ID arrays | Set `check_embedding_ctx_length=False` on `OpenAIEmbeddings`, and chunk long documents yourself. |
| `400` — prompt *flagged as potentially violating our usage policy* | The target vendor's content filter, not Argo | Rephrase, or try another model family. See §2. |
| Tool calling fails on a streaming call | Documented limitation | Use the non-streaming chat path for tool calling. |
| Sampling parameters seem ignored on Opus 4.7/4.8/5 | Working as designed | Those models accept the parameters and then strip them. Steer with prompting. |

When something looks like a gateway bug rather than your code, capture the full
request and the full error text before reporting it — that's what makes it fixable.

---

## 12. Usage etiquette

Every call costs real money against Argonne's account, and usage is attributed to
your username.

- **Prototype on cheap models.** `claudehaiku45`, `gpt56luna`, and `gemini31flashlite` are fast and inexpensive. Move to `claudeopus5` or `gpt56sol` once the logic works.
- **Cap your output.** Always set `max_tokens` / `max_completion_tokens`.
- **Watch your loops.** An agent loop with a bug can burn a surprising amount in minutes. Add an iteration ceiling before you walk away from it.
- **Coordinate bulk runs.** Argo asks that large or long-running automated jobs be flagged in advance. If your project involves embedding or summarizing a large corpus, tell the codeathon organizers before you launch it — they will clear it with the Argo team if needed.

---

## 13. Getting help

| | |
|---|---|
| Codeathon organizers | First stop for access, accounts, and network issues |
| Interactive API explorer | <https://apps.inside.anl.gov/argoapi/docs> |
| Live model list | `GET https://apps.inside.anl.gov/argoapi/v1/models` |

---

*Model lists and parameter rules are drawn from the Argo API Documentation dated
August 3, 2026. Argo adds models frequently — `GET /v1/models` is always the
current source of truth.*
