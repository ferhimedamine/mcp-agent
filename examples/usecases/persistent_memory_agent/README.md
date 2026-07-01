# Persistent Memory Agent

Demonstrates cross-session memory using [Dakera](https://dakera.ai) MCP — a self-hosted vector memory server. Directly addresses the feature request in [#12](https://github.com/lastmile-ai/mcp-agent/issues/12).

## The three memory tiers

| Tier | Storage | Survives restart? | Tool |
|------|---------|-------------------|------|
| Short-term | mcp-agent `Context` | No | Built-in |
| Session | Dakera per-session | Yes (in Dakera) | `dakera_session_start` / `dakera_store` |
| Long-term | Dakera semantic index | Yes | `dakera_recall` |

## Prerequisites

```bash
# 1. Start Dakera (local Docker — no external API needed)
docker run -d -p 3300:3300 \
    -e DAKERA_API_KEY=demo \
    ghcr.io/dakera-ai/dakera:latest

# 2. Verify the MCP server starts
npx @dakera-ai/dakera-mcp --help

# 3. Set env vars
export DAKERA_API_URL=http://localhost:3300
export DAKERA_API_KEY=demo
export ANTHROPIC_API_KEY=your-key
```

## Run

```bash
cd examples/usecases/persistent_memory_agent

# First run: researches and stores findings
python main.py

# Second run: agent recalls prior findings from Dakera before continuing
python main.py
```

## MCP tools available

Key Dakera tools exposed via MCP:

| Tool | Purpose |
|------|---------|
| `dakera_store` | Persist a memory entry |
| `dakera_recall` | Semantic recall (decay-weighted) |
| `dakera_search` | Hybrid BM25 + vector search |
| `dakera_batch_recall` | Recall across multiple queries at once |
| `dakera_session_start` | Begin a named session |
| `dakera_session_end` | Close a session |
| `dakera_session_memories` | Retrieve all memories in a session |
| `dakera_extract_entities` | NER → knowledge graph |
| `dakera_knowledge_graph` | Query entity relationships |
| `dakera_forget` | Delete specific memories |
| `dakera_consolidate` | Deduplicate related memories |
| `dakera_memory_get` | Fetch a specific memory by ID |
| `dakera_memory_update` | Update an existing memory |
| `dakera_memory_feedback` | Signal memory quality for adaptive ranking |

## Config

See `mcp_agent.config.yaml`. The Dakera MCP server runs via `uvx dakera-mcp` (npm: `@dakera-ai/dakera-mcp`).
