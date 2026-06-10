# TurboVec API - Railway Template

[TurboVec](https://github.com/RyanCodrai/turbovec) is a high-performance embedded vector search engine (Rust core + Python bindings) that compresses embeddings with Google Research's TurboQuant algorithm - up to 16x smaller than float32 while searching faster than FAISS.

TurboVec ships as a **library**, not a server. This template wraps it in a thin FastAPI HTTP service so you can self-host it as a vector-search API on Railway, with a persistent volume so your index survives restarts.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/turbovec)

## Features

- REST API over TurboVec's `IdMapIndex` (stable external uint64 IDs)
- `add` / `search` / `delete` / `save` / `reset` endpoints
- Filtered (allowlist) search for hybrid retrieval
- Persistent index on a mounted Railway volume (`/data/index.tvim`)
- Optional API-key auth via the `X-API-Key` header
- Prebuilt wheels - no Rust toolchain, fast cold builds

## How to use

1. Click **Deploy on Railway**.
2. Set the environment variables (see below). At minimum, set `INDEX_DIM` to match your embedding model (e.g. `1536` for OpenAI `text-embedding-3-small`).
3. Add a volume mounted at `/data` for persistence.
4. Once deployed, call the API at your Railway public domain.

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `INDEX_DIM` | `1536` | Vector dimensionality (must match your embeddings) |
| `INDEX_BIT_WIDTH` | `4` | Quantization bit width: `2` or `4` |
| `DATA_DIR` | `/data` | Directory for the persisted index (mount a volume here) |
| `AUTO_SAVE` | `true` | Persist to disk after every mutation |
| `API_KEY` | _(unset)_ | If set, all requests must send `X-API-Key: <value>` |
| `PORT` | `8080` | Injected by Railway |

## API

| Method | Path | Body | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | - | Healthcheck |
| `GET` | `/` | - | Index info (dim, bit width, count) |
| `POST` | `/vectors` | `{"vectors": [[...]], "ids": [1,2]}` | Add vectors with IDs |
| `POST` | `/search` | `{"query": [...], "k": 10, "allowlist": [..]}` | Nearest-neighbour search |
| `DELETE` | `/vectors/{id}` | - | Remove a vector by ID |
| `POST` | `/save` | - | Force-persist the index |
| `POST` | `/reset` | - | Drop all vectors |

## Authentication

If `API_KEY` is set (recommended for any public deployment), every request except `GET /health` must include the key in an `X-API-Key` header. Requests without it, or with the wrong value, get `401 Unauthorized`. Leave `API_KEY` unset to run the API open (no auth).

```bash
# Authenticated request
curl -H "X-API-Key: $API_KEY" $BASE/
```

### Example

```bash
BASE=https://your-app.up.railway.app
KEY=your-api-key   # the value you set for API_KEY

# Add two 1536-dim vectors
curl -X POST $BASE/vectors -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
  -d '{"vectors": [[0.1, ...], [0.2, ...]], "ids": [1001, 1002]}'

# Search
curl -X POST $BASE/search -H "X-API-Key: $KEY" -H 'Content-Type: application/json' \
  -d '{"query": [0.1, ...], "k": 5}'
```

## Creating and querying data

TurboVec stores and searches **raw float vectors (embeddings) plus a uint64 ID** — it does not generate embeddings itself, and it does not store your original text. You create the data by:

1. **Embedding** your content (text, images, code) with an embedding model of your choice.
2. **Ingesting** the resulting vectors via `POST /vectors`, each paired with an ID you control (typically your database primary key).
3. **Querying** by embedding the query with the *same* model and calling `POST /search`.
4. **Joining** the returned IDs back to the original content in your own store.

```
text/images ──► embedding model ──► vector ──► POST /vectors
query text  ──► embedding model ──► vector ──► POST /search ──► IDs ──► your DB
```

> The embedding model's output dimension must equal `INDEX_DIM`. Common values: `1536` (OpenAI `text-embedding-3-small` / `ada-002`), `3072` (`text-embedding-3-large`), `384`–`768` (most `sentence-transformers` models). Set `INDEX_DIM` before adding any vectors.

### End-to-end example (OpenAI embeddings)

```python
import openai, requests

BASE = "https://your-app.up.railway.app"
HEADERS = {"X-API-Key": "your-api-key"}   # omit if API_KEY is unset
client = openai.OpenAI()  # OPENAI_API_KEY in env

docs = {
    101: "Railway is a deployment platform for apps and databases.",
    102: "TurboVec compresses embedding vectors for fast search.",
    103: "Cats are small domesticated carnivorous mammals.",
}

# 1. CREATE DATA: embed each doc, push vector + id
ids, texts = list(docs.keys()), list(docs.values())
embs = [d.embedding for d in client.embeddings.create(
    model="text-embedding-3-small", input=texts).data]
requests.post(f"{BASE}/vectors", headers=HEADERS, json={"vectors": embs, "ids": ids})

# 2. SEARCH: embed the query, get back matching ids
q = client.embeddings.create(
    model="text-embedding-3-small",
    input="how do I host my app?").data[0].embedding
hits = requests.post(f"{BASE}/search", headers=HEADERS, json={"query": q, "k": 2}).json()

# 3. JOIN ids back to your own text
for h in hits["results"]:
    print(round(h["score"], 3), docs[h["id"]])   # doc 101 ranks first
```

A local embedding model works too — anything that produces a fixed-length float vector. For example, with `sentence-transformers` set `INDEX_DIM=384` and embed via `SentenceTransformer("all-MiniLM-L6-v2").encode(texts).tolist()` before posting.

## Notes

- **Dimension is fixed at creation.** Changing `INDEX_DIM` after vectors are added requires a `/reset` (or a fresh volume).
- **Persistence** depends on a volume mounted at `/data`. Without one, the index is lost on redeploy.
- TurboVec wheels target `x86-64-v3` (Haswell 2013+), which Railway's infrastructure supports.
- Re-adding an existing ID returns `409`. Deleting an unknown ID is treated as a no-op by the binding (no error).

## License

The wrapper in this directory is provided as-is. TurboVec itself is MIT licensed by [Ryan Codrai](https://github.com/RyanCodrai/turbovec).
