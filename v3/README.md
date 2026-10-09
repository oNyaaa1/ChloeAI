# ChloeAI local-first upgrade scaffold

This is a **starter integration**, not a patch to the original ChloeAI repository. It implements the foundation from the design note: a local model, a persistent knowledge store, semantic retrieval, source metadata, and approval-gated actions. Web crawling, automatic model training, and unrestricted system access are intentionally not included.

## Architecture

- **Ollama** serves the local chat model and embedding model.
- **MySQL** stores conversation turns, memory text, source URLs/titles, hashes, pending actions, and research-job records.
- **Qdrant** stores embedding vectors for semantic retrieval; MySQL remains the source of truth for memory text and provenance.
- **FastAPI** exposes chat, memory, search, and approval endpoints.
- **Approval gate** queues workspace file writes and does not execute them until an explicit approve call. Paths are constrained to `WORKSPACE_DIR`.

## 1. Prerequisites

Install Docker Desktop (or Docker Engine), Python 3.11+, and [Ollama](https://ollama.com/).

Pull local models:

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

You can change `OLLAMA_CHAT_MODEL` in `.env` to another model that fits your hardware. `nomic-embed-text` is expected to produce 768-dimensional embeddings in this starter.

## 2. Start data services

Copy `.env.example` to `.env` and change the example passwords before using this beyond a throwaway local test.

```bash
docker compose up -d
```

The service ports bind to `127.0.0.1` only. Wait for MySQL to become healthy.

## 3. Install and run the API

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the interactive API docs.

## 4. Try it

Save a memory with source provenance:

```bash
curl -X POST http://127.0.0.1:8000/memory \
  -H 'Content-Type: application/json' \
  -d '{"text":"The project uses a local Ollama model.","source_title":"Project notes","source_url":"https://example.com/notes"}'
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What do my project notes say about the model?"}'
```

Queue a file write; this **does not write the file yet**:

```bash
curl -X POST http://127.0.0.1:8000/actions/write-file \
  -H 'Content-Type: application/json' \
  -d '{"path":"notes/hello.txt","content":"Hello from ChloeAI"}'
```

Use the returned `id` to approve or reject:

```bash
curl -X POST http://127.0.0.1:8000/actions/ACTION_ID/decision \
  -H 'Content-Type: application/json' -d '{"approve":true}'
```

The write is constrained to `WORKSPACE_DIR` (defaults to `./workspace`). Treat the approval endpoint as a local trusted interface: this scaffold does not yet include user authentication, so **do not expose it to your LAN or the public internet**.

## Endpoints

- `GET /health` — process health and configured model
- `POST /chat` — conversation with semantic memory retrieval
- `POST /memory` — store text and optional source metadata
- `GET /memory/search?q=...` — retrieve relevant memories
- `POST /actions/write-file` — queue a workspace file write for approval
- `POST /actions/{id}/decision` — approve/reject a pending write

## Important implementation notes

1. **Database schema:** tables are created on startup for this prototype. Add Alembic migrations before production use.
2. **Vector consistency:** the starter writes MySQL first, then Qdrant. For production, use an outbox/retry worker so a Qdrant outage cannot leave a memory permanently unindexed.
3. **Source tracking:** memory rows keep source URL/title and content hash. For web research, add canonical URL, fetch timestamp, publisher, license, and a captured excerpt before ingesting results.
4. **Learning:** stored memories improve retrieval, not the model weights. Fine-tuning should be a separate, reviewed pipeline with curated examples and evaluations.
5. **Background research:** use a durable queue with bounded jobs, rate limits, cancellation, and source verification—not an unbounded `while brain_alive` loop.
6. **Security:** before adding shell execution, browser automation, or arbitrary file edits, implement authentication, per-tool permissions, audit logs, timeouts, and sandboxing. Never let model output directly become a shell command.
7. **Embedding dimension:** the collection is fixed at 768 dimensions for `nomic-embed-text`. If you select a different embedding model, update the dimension and recreate/reindex the collection intentionally.

## Next integration step

Re-upload the original `ChloeAI.zip` (or provide a working repository tree). Then this scaffold can be adapted to the existing entry point, config, UI, and conventions instead of replacing them with a parallel architecture.
