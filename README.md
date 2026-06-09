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

### Example

```bash
BASE=https://your-app.up.railway.app

# Add two 1536-dim vectors
curl -X POST $BASE/vectors -H 'Content-Type: application/json' \
  -d '{"vectors": [[0.1, ...], [0.2, ...]], "ids": [1001, 1002]}'

# Search
curl -X POST $BASE/search -H 'Content-Type: application/json' \
  -d '{"query": [0.1, ...], "k": 5}'
```

## Notes

- **Dimension is fixed at creation.** Changing `INDEX_DIM` after vectors are added requires a `/reset` (or a fresh volume).
- **Persistence** depends on a volume mounted at `/data`. Without one, the index is lost on redeploy.
- TurboVec wheels target `x86-64-v3` (Haswell 2013+), which Railway's infrastructure supports.
- Re-adding an existing ID returns `409`. Deleting an unknown ID is treated as a no-op by the binding (no error).

## License

The wrapper in this directory is provided as-is. TurboVec itself is MIT licensed by [Ryan Codrai](https://github.com/RyanCodrai/turbovec).
