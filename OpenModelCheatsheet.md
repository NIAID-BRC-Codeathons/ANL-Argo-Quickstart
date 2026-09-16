# LLM API Cheatsheet

Three models are available on `mango.cels.anl.gov` through an OpenAI-compatible API. You talk to them the same way you would talk to the OpenAI API -- just point at a different URL.

## What's Available

| Model | What it does | URL |
|---|---|---|
| **Llama 4 Scout** | General chat | `http://mango.cels.anl.gov:8003/v1` |
| **Qwen 3.6** | Chat with built-in reasoning and tool use | `http://mango.cels.anl.gov:8004/v1` |
| **SFR-Embedding-Mistral** | Turn text into numerical vectors (embeddings) | `http://mango.cels.anl.gov:9998/v1` |

## Prerequisites

Install the OpenAI Python package:

```bash
pip install openai
```

No API key is needed. Use `"EMPTY"` as the key (the server requires the field but doesn't check it).

---

## Quick Start

### Ask Llama a question

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:8003/v1",
    api_key="EMPTY",
)

response = client.chat.completions.create(
    model="RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic",
    messages=[
        {"role": "system", "content": "You are a helpful scientific assistant."},
        {"role": "user", "content": "What is genome assembly?"},
    ],
    max_tokens=1000,
)

print(response.choices[0].message.content)
```

### Ask Qwen a question

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:8004/v1",
    api_key="EMPTY",
)

response = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[
        {"role": "user", "content": "What is genome assembly?"},
    ],
    max_tokens=4000,
)

print(response.choices[0].message.content)
```

> **Important:** Qwen is a "thinking" model. It reasons internally before
> answering, and that reasoning counts against your `max_tokens` budget. If you
> set `max_tokens` too low (e.g. 200), the model may use all the tokens on
> thinking and return an empty answer. **Use at least 2000-4000 for simple
> questions and 8000+ for complex ones.**

### Generate an embedding

An embedding converts text into a list of numbers (a vector) that captures its
meaning. These vectors are useful for similarity search, clustering, and
classification.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:9998/v1",
    api_key="EMPTY",
)

response = client.embeddings.create(
    model="Salesforce/SFR-Embedding-Mistral",
    input="Escherichia coli is a Gram-negative bacterium.",
)

vector = response.data[0].embedding
print(f"Vector has {len(vector)} dimensions")  # 4096
print(vector[:5])  # first 5 numbers
```

---

## Streaming Responses

By default the API waits until the full answer is generated, then returns it all
at once. Streaming gives you the answer token-by-token as it's generated, which
feels faster for interactive use.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:8004/v1",
    api_key="EMPTY",
)

stream = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[
        {"role": "user", "content": "Explain metagenomic binning."},
    ],
    max_tokens=4000,
    stream=True,
)

for chunk in stream:
    if chunk.choices:
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
```

Both Llama and Qwen support streaming. The embedding model does not (embeddings
are returned all at once).

---

## Tool Calling (Qwen only)

Tool calling lets the model decide when to call a function you define. Instead of
answering directly, the model returns a structured request saying "call this
function with these arguments." Your code executes the function and feeds the
result back.

This only works with Qwen (port 8004). Llama does not support tool calling.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:8004/v1",
    api_key="EMPTY",
)

# Define a tool the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_genome",
            "description": "Retrieve information about a genome by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genome_id": {
                        "type": "string",
                        "description": "The genome ID, e.g. 83332.12",
                    }
                },
                "required": ["genome_id"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="Qwen/Qwen3.6-35B-A3B",
    messages=[
        {"role": "user", "content": "Look up genome 83332.12"},
    ],
    tools=tools,
    tool_choice="auto",
    max_tokens=4000,
)

message = response.choices[0].message

if message.tool_calls:
    for call in message.tool_calls:
        print(f"Function: {call.function.name}")
        print(f"Arguments: {call.function.arguments}")
else:
    print(message.content)
```

---

## Batch Embeddings

You can embed multiple texts in a single request by passing a list instead of a
string.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://mango.cels.anl.gov:9998/v1",
    api_key="EMPTY",
)

texts = [
    "Escherichia coli is a Gram-negative bacterium.",
    "Influenza A virus contains a segmented RNA genome.",
    "Genome assembly reconstructs sequences from reads.",
]

response = client.embeddings.create(
    model="Salesforce/SFR-Embedding-Mistral",
    input=texts,
)

for i, item in enumerate(response.data):
    print(f"Text {i}: {len(item.embedding)} dimensions")
```

---

## Using curl Instead of Python

All the same endpoints work from the command line with `curl`. This is useful for
quick testing.

### Chat (Llama)

```bash
curl http://mango.cels.anl.gov:8003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic",
    "messages": [
      {"role": "user", "content": "What is genome assembly?"}
    ],
    "max_tokens": 1000
  }'
```

### Chat (Qwen)

```bash
curl http://mango.cels.anl.gov:8004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3.6-35B-A3B",
    "messages": [
      {"role": "user", "content": "What is genome assembly?"}
    ],
    "max_tokens": 4000
  }'
```

### Embedding

```bash
curl http://mango.cels.anl.gov:9998/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Salesforce/SFR-Embedding-Mistral",
    "input": "Escherichia coli is a Gram-negative bacterium."
  }'
```

---

## Common Parameters

| Parameter | What it does | Default |
|---|---|---|
| `model` | Which model to use (must match exactly) | required |
| `messages` | The conversation so far (list of role/content pairs) | required |
| `max_tokens` | Maximum number of tokens in the response | model default |
| `temperature` | Randomness (0 = deterministic, 1 = creative) | 1.0 |
| `stream` | Return tokens one at a time instead of all at once | `false` |

### Message roles

| Role | Purpose |
|---|---|
| `system` | Sets the model's behavior ("You are a helpful assistant...") |
| `user` | Your question or instruction |
| `assistant` | The model's previous reply (for multi-turn conversations) |
| `tool` | A tool/function result being fed back to the model |

---

## Model Details

### Llama 4 Scout

- **Full model name:** `RedHatAI/Llama-4-Scout-17B-16E-Instruct-FP8-dynamic`
- **Context window:** 60,000 tokens
- **Best for:** General question answering, text generation, summarization
- **Does not support:** Tool calling

### Qwen 3.6

- **Full model name:** `Qwen/Qwen3.6-35B-A3B`
- **Context window:** 131,072 tokens
- **Best for:** Complex reasoning, tool/function calling, code generation
- **Supports:** Tool calling, built-in chain-of-thought reasoning
- **Concurrency limit:** 4 simultaneous requests

### SFR-Embedding-Mistral

- **Full model name:** `Salesforce/SFR-Embedding-Mistral`
- **Max input length:** 4,096 tokens
- **Output dimensions:** 4,096
- **Best for:** Semantic search, text similarity, clustering

---

## Troubleshooting

**Empty or `null` response from Qwen?**
Increase `max_tokens`. Qwen thinks before answering, and that thinking uses
tokens. With a low budget the model runs out of tokens during its internal
reasoning and has nothing left for the actual answer.

**"Model not found" error?**
The model name must match exactly, including the `/`. Copy it from the table
above. You can also check what's loaded:

```bash
curl -s http://mango.cels.anl.gov:8003/v1/models | python3 -m json.tool
curl -s http://mango.cels.anl.gov:8004/v1/models | python3 -m json.tool
curl -s http://mango.cels.anl.gov:9998/v1/models | python3 -m json.tool
```

**Is the server running?**

```bash
curl -sf http://mango.cels.anl.gov:8003/health && echo "Llama OK"
curl -sf http://mango.cels.anl.gov:8004/health && echo "Qwen OK"
curl -sf http://mango.cels.anl.gov:9998/health && echo "Embedding OK"
```

**"tool choice requires --enable-auto-tool-choice" error?**
You're sending tool definitions to Llama (port 8003). Tool calling only works
with Qwen (port 8004).
