## Template Titles

**Railway Title:** `TurboVec [Updated June '26]`
**Railway Description:** `TurboVec [June '26] (Compressed Vector Search & Embedding API) Self Host`
**Spreadsheet Title:** `TurboVec (Open-Source Compressed Vector Search & Embedding Retrieval API)`
**GitHub Description:** `TurboVec - open-source compressed vector search engine served as a REST API. Deploy on Railway with one click.`

---

![TurboVec open source vector search engine](https://res.cloudinary.com/dh2nt6hgh/image/upload/v1777637291/turbovec_banner_placeholder.webp "Hosting TurboVec open source vector search on Railway")

# Deploy and Host self hosted TurboVec (Open-Source Compressed Vector Search Engine) on Railway

TurboVec is a high-performance, open-source vector search engine written in Rust that compresses embeddings using Google Research's TurboQuant algorithm. It shrinks a 31 GB corpus of 10 million float32 documents to roughly 4 GB while searching faster than FAISS. This template wraps the TurboVec library in a REST API so you can self host it as a vector database for retrieval, RAG, and semantic search.

## About Hosting TurboVec open-source software on Railway (self hosted TurboVec template)

Self hosting TurboVec means your embeddings, indexes, and search traffic stay entirely on infrastructure you control, with no data leaving your VPC and no per-query fees. Because TurboVec ships as an embedded library rather than a server, this template adds a lightweight FastAPI HTTP layer exposing add, search, and delete endpoints. With Railway, the container build, networking, public domain, healthchecks, and a persistent volume for the index are handled automatically on each deploy.

## Why Deploy TurboVec, the Pinecone alternative on Railway (Railway Free Trial)

Instead of paying usage-based fees to hosted vector databases like Pinecone or Weaviate Cloud, you can run your own compressed vector API with full control over your embeddings and storage. On Railway, the TurboVec self hosting cost stays transparent because you only pay for what you use, and the software is always free. Plus, Railway gives every new user a $5 free trial when signing up with GitHub, making it easy to test your vector search API.

### Railway vs Other Hosting Providers and VPS for TurboVec self hosting

| Provider          | What You Get with Railway                                     | What You Get with the Other Provider                              |
| ----------------- | ------------------------------------------------------------ | ----------------------------------------------------------------- |
| **DigitalOcean**  | One-click deploy with a persistent volume and public domain  | A VPS where you handle Docker, Python builds, and networking      |
| **AWS**           | Transparent pricing, no EC2, EBS, or IAM complexity to manage | Powerful compute but VPC, security groups, and scaling to configure |
| **Hetzner**       | Fully managed app with auto networking and healthchecks       | Great pricing but manual Docker, reverse proxy, and TLS setup     |

## Common Use Cases for hosted TurboVec

Here are common use cases for the open-source compressed vector search engine:

* Powering Retrieval-Augmented Generation (RAG) pipelines by storing document embeddings and serving nearest-neighbour lookups to an LLM at query time.
* Building semantic search over large text, code, or product catalogs where storing full float32 vectors would be too expensive in memory.
* Running multi-tenant retrieval with filtered (allowlist) search to restrict results to a single customer, workspace, or candidate set.
* Replacing a managed vector database with a private, in-VPC embedding API for compliance-sensitive deployments.

![TurboVec vector search API dashboard](https://res.cloudinary.com/dh2nt6hgh/image/upload/v1777637290/turbovec_dashboard_placeholder.webp "TurboVec open source compressed vector search API")

## Dependencies for TurboVec Docker hosted on Railway

When hosting TurboVec on Railway, you need a persistent volume mounted at `/data` so the compressed index survives restarts and redeploys. No external database, cache, or managed service is required; TurboVec operates in memory with file-based persistence.

### Deployment Dependencies for Managed TurboVec Service (OSS Vector Search)

A managed TurboVec service on Railway requires only the application container and a single persistent volume for the `.tvim` index file. There is no PostgreSQL, Redis, or message-queue dependency, keeping the footprint and cost low.

### Implementation Details for TurboVec (Using TurboVec official Python package)

This template installs the official `turbovec` PyPI package (prebuilt wheels, no Rust toolchain needed) and serves it through a FastAPI app on the Railway-injected `PORT` with a healthcheck at `/health`. Key environment variables include `INDEX_DIM` (embedding dimensionality, default 1536), `INDEX_BIT_WIDTH` (2 or 4), `DATA_DIR=/data`, and an optional `API_KEY` that, when set, is enforced on every request via an `X-API-Key` header. The index uses stable external uint64 IDs that survive deletions.

## How does TurboVec compare against other vector search platforms

### TurboVec vs Pinecone (Pinecone Alternative)
* **Data Ownership:** With TurboVec your vectors live on your own Railway volume, while Pinecone stores everything on its managed cloud with per-query and per-pod billing.
* **Compression:** TurboVec's TurboQuant quantization gives up to 16x smaller indexes out of the box, lowering the memory and storage you pay for.

### TurboVec vs FAISS (FAISS Alternative)
* **Served by Default:** This template exposes TurboVec as a ready REST API, while FAISS is a raw library you must wrap and operate yourself.
* **Online Ingestion:** TurboVec ingests vectors with no training phase or tuning, unlike many FAISS index types.

### TurboVec vs Qdrant (Qdrant Alternative)
* **Footprint:** TurboVec needs only a container and a volume, while Qdrant runs as a heavier standalone service with its own storage.
* **Compression:** TurboVec's 2-bit and 4-bit quantization is built in, reducing index size without a separate quantization config.

### TurboVec vs Weaviate (Weaviate Alternative)
* **Simplicity:** TurboVec focuses purely on fast compressed vector search, while Weaviate bundles a schema layer, modules, and GraphQL.

## How to use TurboVec (the OSS vector search engine)?

TurboVec stores and searches embedding vectors; it does not generate them, so you create data by embedding your content with an embedding model first. Set `INDEX_DIM` to match that model (e.g. 1536 for OpenAI `text-embedding-3-small`), then `POST` the vectors with your own IDs to `/vectors`. To query, embed the search text with the same model and call `/search`, optionally with an `allowlist` of candidate IDs. Search returns IDs and scores, which you join back to documents in your own database.

## How to self host TurboVec on other VPS Services (TurboVec self hosting guide)

### Clone the Repository
Download **TurboVec** from [GitHub](https://github.com/RyanCodrai/turbovec).

### Install Dependencies
Ensure your VPS has **Docker** or **Python 3.9+** installed. Install with `pip install turbovec` along with `fastapi`, `uvicorn`, and `numpy` for the API layer.

### Configure Environment Variables
Set up the API configuration such as:
* `INDEX_DIM`
* `INDEX_BIT_WIDTH`
* `DATA_DIR`
* `API_KEY`
for your embeddings and storage path.

### Start the TurboVec Application
Run `uvicorn app.main:app --host 0.0.0.0 --port 8080` to start the API and expose it through your firewall or reverse proxy.

## Official Pricing of TurboVec (TurboVec pricing)
TurboVec is **open source** and completely free to self host under the MIT license. There are no per-query charges, per-vector fees, or premium tiers; you only pay for the infrastructure running it.

## TurboVec cloud vs self hosted comparison (Pricing, features, costs, and more)
TurboVec is a self-hosted-only library with no managed cloud offering. Self hosting gives you full control, private data, and no per-query caps, with Railway providing the simplest path via a managed build and a persistent volume.

### Monthly cost of self hosting TurboVec on Railway
The TurboVec self hosting cost on Railway is typically $5-$10/month, covering the application container and persistent storage for the compressed index with no per-query or per-vector fees.

### System Requirements for Hosting TurboVec on a VPS
TurboVec requires at least 1 vCPU and 512MB RAM (more for large indexes), an x86-64-v3 (Haswell 2013+) or ARM NEON CPU, and storage sized to your corpus, with Docker installed.

## Frequently Asked Questions (FAQs)

### What is TurboVec self hosted?
TurboVec self hosted means running your own compressed vector search API (on Railway, a VPS, or Docker) instead of a managed vector database like Pinecone, giving you data ownership, privacy, and no per-query fees.

### How much does TurboVec self hosting cost on Railway?
The TurboVec self hosting cost on Railway is typically $5-$10/month, covering the container and a persistent volume with no per-query or per-vector charges.

### Is TurboVec free to use?
Yes, TurboVec is open source and free to self host under the MIT license. You only pay for the infrastructure (like Railway or a VPS) that runs it.

### What quantization does TurboVec support?
TurboVec uses Google Research's TurboQuant algorithm with 2-bit and 4-bit quantization, achieving up to 16x compression versus float32 while keeping search fast.

### Where can I download TurboVec?
You can get TurboVec from the official [TurboVec GitHub](https://github.com/RyanCodrai/turbovec) repository or `pip install turbovec`, or deploy it as an API on Railway with one click using our template.

### What are some alternatives to TurboVec?
Popular alternatives include Pinecone, FAISS, Qdrant, Weaviate, and Milvus, though TurboVec stands out for its TurboQuant compression and tiny footprint.
