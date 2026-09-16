# RAGStack PMC Literature Search Cheatsheet

RAGStack is a retrieval-augmented generation (RAG) platform that lets you search
a corpus of scientific papers (from PubMed Central and other sources) and get
grounded answers with citations. It uses an OpenAI-compatible API -- you send a
question, it finds relevant passages, and optionally generates an answer backed
by those passages.

## What You Need

- **One** of the following (see Step 1):
  - A **BV-BRC account** (any existing account works), or
  - A **pre-registered API key** (ask an organizer for one)
- `curl` or Python with the `requests` library

No software to install, no server to run. Everything is already deployed.

## Your Two URLs

| | URL |
|---|---|
| **Browser UI** | https://www.bv-brc.org/ragstack/hackathon/ui/ |
| **API** | https://www.bv-brc.org/ragstack/hackathon/api |

The UI is good for exploring interactively. The API is what you use from scripts
and notebooks.

---

## Step 1: Authenticate

There are two ways to authenticate. Pick **one** -- never send both in the same
request (that's a 400 error).

### Option A: Use a pre-registered API key

Ask an organizer for an API key. This is the simplest option if you don't have a
BV-BRC account.

```bash
export BASE=https://www.bv-brc.org/ragstack/hackathon/api
export AUTH="X-API-Key: your-key-here"
```

### Option B: Use your BV-BRC account

If you have a BV-BRC account, you can use your BV-BRC token instead.

**From the command line** (if you have the BV-BRC CLI installed):

```bash
p3-login your-bvbrc-username
# enter your password when prompted -- writes token to ~/.patric_token

export BASE=https://www.bv-brc.org/ragstack/hackathon/api
export AUTH="Authorization: $(cat ~/.patric_token)"
```

**From the browser:** Go to https://www.bv-brc.org/ragstack/hackathon/ui/, click
Sign In, and enter your BV-BRC username and password. You can copy the token from
the Account page, then use it in your shell:

```bash
export BASE=https://www.bv-brc.org/ragstack/hackathon/api
export AUTH="Authorization: paste-your-token-here"
```

> **Note:** The BV-BRC token goes in the `Authorization` header with NO `Bearer`
> prefix. Just the raw token.

### Verify it works

```bash
curl -s $BASE/health
# {"status":"ok"}  -- this needs no credential

curl -s "$BASE/v1/stats/tenants?counts=false" -H "$AUTH" | python3 -m json.tool
# shows your tenant and role -- if this works, you're authenticated
```

---

## Step 2: See What's Available

### List collections you can search

```bash
curl -s $BASE/v1/collections -H "$AUTH" | python3 -m json.tool
```

This shows you which collections exist, which one is your default, and how many
chunks each has. The `default` field at the top level tells you what gets
searched when you don't specify a collection.

### Check who you are

```bash
curl -s "$BASE/v1/stats/tenants?counts=false" -H "$AUTH" | python3 -m json.tool
```

---

## Step 3: Search the Literature

There are two ways to search: **retrieve** (just find passages) and **query**
(find passages and generate an answer).

### Retrieve -- find relevant passages, no LLM answer

This is the fastest option. It finds the most relevant chunks of text from the
corpus and returns them ranked by relevance.

```bash
curl -s -X POST $BASE/v1/retrieve \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "mechanisms of antibiotic resistance in Klebsiella pneumoniae",
    "top_k": 5
  }' | python3 -m json.tool
```

Each result (called a "source") looks like this:

```json
{
  "doc_id": "5f94e8b5-...",
  "chunk_id": "f3020aa7-...",
  "score": 0.0164,
  "content": "...the actual text passage...",
  "metadata": {
    "title": "Paper Title Here",
    "authors": "Smith J, Jones A",
    "journal": "mBio",
    "doi": "10.1128/...",
    "pmcid": "PMC12345678",
    "section_title": "Results",
    "chunk_index": 3,
    "prev_chunk_id": "c6304b79-...",
    "next_chunk_id": "1656f49a-..."
  }
}
```

### Query -- get an LLM-generated answer with citations

This does the same retrieval, then feeds the passages to an LLM to generate a
grounded answer with `[n]` citation markers pointing to the sources.

```bash
curl -s -X POST $BASE/v1/query \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "how do efflux pumps confer multidrug resistance?",
    "top_k": 5
  }' | python3 -m json.tool
```

The response has three parts:

| Field | What it contains |
|---|---|
| `answer` | The LLM-generated answer with `[1]`, `[2]` etc. citation markers |
| `sources` | The ranked passages the answer was grounded on (same format as retrieve) |
| `rewritten_queries` | Any query expansions the system used internally |

> If the deployment has no LLM configured, `answer` will say
> `[LLM not configured]` but the sources are still real and useful.

---

## Search Options

Both `/v1/retrieve` and `/v1/query` accept these parameters:

| Parameter | Default | What it does |
|---|---|---|
| `query` | required | Your question or search terms |
| `top_k` | `5` | How many passages to return |
| `collection` | your default | Which collection to search (from Step 2) |
| `collections` | `null` | Search multiple collections at once (list of IDs, max 5) |
| `retrieval_mode` | `"hybrid"` | `"hybrid"` (keyword + semantic), `"vector"` (semantic only), `"bm25"` (keyword only) |
| `filters` | `{}` | Filter by metadata fields, e.g. `{"journal": "mBio"}` |
| `rerank` | `null` | `true`/`false` to force cross-encoder reranking on or off |
| `context_window` | `0` | Include surrounding chunks (1-3 = number of chunks each direction) |

### Examples

**Keyword-only search** (good for exact terms like gene names or accessions):

```bash
curl -s -X POST $BASE/v1/retrieve \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "blaKPC-2 Klebsiella",
    "retrieval_mode": "bm25",
    "top_k": 10
  }'
```

**Filter by journal:**

```bash
curl -s -X POST $BASE/v1/retrieve \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "CRISPR cas9 genome editing bacteria",
    "filters": {"journal": "Nature Biotechnology"},
    "top_k": 5
  }'
```

**Get surrounding context** (see the text before and after each hit):

```bash
curl -s -X POST $BASE/v1/retrieve \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "phage therapy clinical trials",
    "context_window": 2,
    "top_k": 5
  }'
```

Each source will include a `context` array with neighboring chunks:

```json
{
  "content": "...the matched passage...",
  "context": [
    {"chunk_id": "...", "position": -2, "content": "...two chunks before..."},
    {"chunk_id": "...", "position": -1, "content": "...one chunk before..."},
    {"chunk_id": "...", "position":  1, "content": "...one chunk after..."},
    {"chunk_id": "...", "position":  2, "content": "...two chunks after..."}
  ]
}
```

**Search across multiple collections:**

```bash
curl -s -X POST $BASE/v1/retrieve \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{
    "query": "antimicrobial resistance genes",
    "collections": ["open-access", "my-papers"],
    "top_k": 10
  }'
```

Each source will include a `collection` field telling you which collection it
came from.

---

## Reading More of a Document

Each passage has `prev_chunk_id` and `next_chunk_id` in its metadata. You can
fetch those chunks to read more of the paper:

```bash
curl -s "$BASE/v1/chunks?ids=c6304b79-...,1656f49a-..." -H "$AUTH" \
  | python3 -m json.tool
```

- Comma-separated, up to 200 IDs per request.
- Each returned chunk has its own `prev_chunk_id` / `next_chunk_id`, so you can
  keep walking through the entire document.
- At the start/end of a document, the neighbor ID will be absent or `null`.

---

## Creating Your Own Collection

The hackathon tenant starts empty. You can create your own private collection
and fill it with your own documents.

### Create it

```bash
curl -s -X POST $BASE/v1/collections \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"id": "my-papers", "label": "My papers"}' \
  | python3 -m json.tool
```

The collection is private to you until you share it. You can have up to 10
collections.

### Upload PDFs into it

```bash
curl -s -X POST $BASE/v1/ingest/upload \
  -H "$AUTH" \
  -F collection=my-papers \
  -F files=@paper1.pdf \
  -F files=@paper2.pdf \
  | python3 -m json.tool
```

This returns a `job_id`. Ingestion is asynchronous -- poll for status:

```bash
curl -s $BASE/v1/ingest/YOUR_JOB_ID -H "$AUTH" | python3 -m json.tool
```

Status goes: `accepted` -> `running` -> `completed` (or `failed`).

**Limits:**
- Up to 50 files per upload, 50 MB each, 500 MB total per request
- One ingest job at a time (a second upload while one is running returns 429)
- PDF, plain text, and Markdown are accepted

> **For non-PDF files**, you must declare the content type explicitly:
> ```bash
> curl -s -X POST $BASE/v1/ingest/upload -H "$AUTH" \
>   -F collection=my-papers \
>   -F "files=@notes.md;type=text/markdown" \
>   -F "files=@data.txt;type=text/plain"
> ```
> Without the `;type=...` suffix, `curl` sends `application/octet-stream` for
> `.md` files and the server rejects it.

### Share it with someone

```bash
# Share with a specific BV-BRC user
curl -s -X POST $BASE/v1/collections/my-papers/shares \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"grantee": "colleague_username", "permission": "read"}'

# Make it public (readable by everyone)
curl -s -X POST $BASE/v1/collections/my-papers/shares \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"grantee": "@public", "permission": "read"}'
```

### Delete a collection

```bash
curl -s -X DELETE $BASE/v1/collections/my-papers -H "$AUTH"
```

---

## Python Examples

### Retrieve passages

```python
import requests

BASE = "https://www.bv-brc.org/ragstack/hackathon/api"

# Option A: API key (ask an organizer for one)
headers = {
    "X-API-Key": "your-key-here",
    "Content-Type": "application/json",
}

# Option B: BV-BRC token
# with open("/path/to/.patric_token") as f:
#     token = f.read().strip()
# headers = {
#     "Authorization": token,
#     "Content-Type": "application/json",
# }

response = requests.post(f"{BASE}/v1/retrieve", headers=headers, json={
    "query": "mechanisms of antibiotic resistance",
    "top_k": 5,
})

data = response.json()
for source in data["sources"]:
    meta = source["metadata"]
    print(f"[{source['score']:.4f}] {meta.get('title', 'No title')}")
    print(f"  Journal: {meta.get('journal', '?')}  DOI: {meta.get('doi', '?')}")
    print(f"  {source['content'][:200]}...")
    print()
```

### Get an LLM-generated answer

```python
response = requests.post(f"{BASE}/v1/query", headers=headers, json={
    "query": "how do bacteria develop resistance to carbapenems?",
    "top_k": 5,
})

data = response.json()
print("Answer:")
print(data["answer"])
print()
print("Sources:")
for i, source in enumerate(data["sources"], 1):
    meta = source["metadata"]
    print(f"  [{i}] {meta.get('title', '?')} ({meta.get('journal', '?')})")
```

### Upload a PDF and wait for ingestion

```python
import time

# Use whichever auth header you set up above (without Content-Type for multipart)
auth_header = {"X-API-Key": "your-key-here"}  # or {"Authorization": token}

# Upload
with open("my_paper.pdf", "rb") as f:
    response = requests.post(
        f"{BASE}/v1/ingest/upload",
        headers=auth_header,
        data={"collection": "my-papers"},
        files={"files": ("my_paper.pdf", f, "application/pdf")},
    )

job_id = response.json()["job_id"]
print(f"Job submitted: {job_id}")

# Poll until done
while True:
    status = requests.get(
        f"{BASE}/v1/ingest/{job_id}",
        headers=auth_header,
    ).json()
    print(f"Status: {status['status']}")
    if status["status"] in ("completed", "failed"):
        break
    time.sleep(5)
```

---

## Troubleshooting

**401 error?**
Your credential is missing or invalid. If using an API key, double-check the key
with an organizer. If using a BV-BRC token, it may be expired -- run `p3-login`
again or re-sign-in through the UI. Remember: the `Authorization` header takes
the raw token with no `Bearer` prefix, and you must never send both
`Authorization` and `X-API-Key` in the same request.

**404 on a collection you know exists?**
You don't have read access. Ask the owner to share it with you, or check
`GET /v1/collections` to see what you can actually access.

**403 "no collection accepts your uploads"?**
You omitted the `collection` parameter and don't own any collections. Either
name one you own (`-F collection=my-papers`) or create one first.

**429 on upload?**
You already have an ingest job running. Only one at a time. Poll the existing
job until it finishes, then retry.

**Empty or no answer from /v1/query?**
The deployment may not have an LLM configured. The sources are still real -- use
`/v1/retrieve` instead and read the passages directly.

**"no loader for .xml" on ingest?**
XML files are accepted at the upload gate but have no parser yet. Convert to
plain text or PDF.

**How do I report a problem?**
Every error response includes a `Reference:` ID (also in the `X-Request-Id`
response header). Include that ID when reporting -- it lets the operators find
your request in the logs.

---

## Quick Reference

```bash
# Health check (no auth needed)
curl -s $BASE/health

# List your collections
curl -s $BASE/v1/collections -H "$AUTH"

# Search (retrieve only, no LLM)
curl -s -X POST $BASE/v1/retrieve -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"query": "your question here", "top_k": 5}'

# Search with LLM answer
curl -s -X POST $BASE/v1/query -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"query": "your question here", "top_k": 5}'

# Fetch specific chunks by ID
curl -s "$BASE/v1/chunks?ids=CHUNK_ID_1,CHUNK_ID_2" -H "$AUTH"

# Create a collection
curl -s -X POST $BASE/v1/collections -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"id": "my-collection", "label": "My Collection"}'

# Upload PDFs
curl -s -X POST $BASE/v1/ingest/upload -H "$AUTH" \
  -F collection=my-collection -F files=@paper.pdf

# Check ingest status
curl -s $BASE/v1/ingest/JOB_ID -H "$AUTH"

# Share a collection
curl -s -X POST $BASE/v1/collections/my-collection/shares \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"grantee": "username", "permission": "read"}'

# Delete a collection
curl -s -X DELETE $BASE/v1/collections/my-collection -H "$AUTH"

# Who am I?
curl -s "$BASE/v1/stats/tenants?counts=false" -H "$AUTH"
```
