# PowerMem Memory Integration Guide

## Overview

[PowerMem](https://www.powermem.ai/) is an agent memory component that summarizes conversations with an LLM and performs semantic retrieval against a vector store.

PowerMem itself is open source. Your actual operating cost depends on the LLM and database you choose:

- `SQLite + a low-cost or self-hosted model` can be very inexpensive
- `Cloud LLMs or managed databases` will cost according to the services you use

Useful links:

- **GitHub**: https://github.com/oceanbase/powermem
- **Website**: https://www.powermem.ai/
- **Examples**: https://github.com/oceanbase/powermem/tree/main/examples

## Key Features

- local memory summarization through an LLM
- user profile extraction through `UserMemory`
- relevance-based retrieval using vector search
- asynchronous memory operations
- private deployment support
- support for multiple storage backends, including `postgres` and `sqlite`

## Installation

PowerMem is already included in this project dependency set. If you need to install it manually:

```bash
pip install powermem
```

## Configuration

### Basic configuration

Configure PowerMem in `config.yaml`:

```yaml
selected_module:
  Memory: powermem

Memory:
  powermem:
    type: powermem
    # Enable user profile extraction
    enable_user_profile: true

    # ========== LLM ==========
    llm:
      provider: openai
      config:
        api_key: YOUR_LLM_API_KEY
        model: gpt-4o-mini
        openai_base_url: https://api.openai.com/v1
        # Optional: raise for “reasoning” models (e.g. Qwen3.x) so fact-extraction JSON is not truncated
        # max_tokens: 8192

    # ========== Embeddings ==========
    embedder:
      provider: openai
      config:
        api_key: YOUR_EMBEDDING_API_KEY
        model: text-embedding-3-small
        openai_base_url: https://api.openai.com/v1
        # embedding_dims: 1536

    # ========== Vector Store ==========
    vector_store:
      provider: sqlite
      config: {}
```

### Configuration reference

#### LLM settings

| Parameter | Description | Example values |
|------|------|--------|
| `llm.provider` | LLM provider type | `openai` |
| `llm.config.api_key` | API key | your provider key |
| `llm.config.model` | Model name | provider-specific |
| `llm.config.openai_base_url` | Optional OpenAI-compatible endpoint | provider-specific |
| `llm.config.max_tokens` | Optional completion limit passed to PowerMem’s LLM client | `8192` (see note below) |
| `llm_max_tokens` | Optional **top-level** field (flat / manager `config_json` alongside `llm_api_key`, `llm_model`, …). Merged into `llm.config.max_tokens` only when nested `llm.config` does not already set `max_tokens`. | `8192` |

PowerMem defaults to a relatively small `max_tokens` for internal calls (fact extraction, etc.). Models that spend many tokens on **reasoning** or thinking (for example Qwen3.5) can return an **empty** visible completion within that budget, which surfaces as JSON parse errors in logs. Increase `max_tokens` (via either key above) when you use such models.

#### Embedding settings

| Parameter | Description | Example values |
|------|------|--------|
| `embedder.provider` | Embedding provider type | `openai` |
| `embedder.config.api_key` | API key | your provider key |
| `embedder.config.model` | Embedding model name | provider-specific |
| `embedder.config.openai_base_url` | Optional OpenAI-compatible endpoint | provider-specific |

#### Vector store settings

| Parameter | Description | Example values |
|------|------|--------|
| `vector_store.provider` | Storage backend | `sqlite`, `postgres` |
| `vector_store.config` | Database configuration | backend-specific |

## Memory Modes

PowerMem supports two common modes:

| Mode | Config | Behavior | Storage requirement |
|------|------|------|----------|
| **Standard memory** | `enable_user_profile: false` | conversation memory storage and retrieval | any supported backend |
| **User profile mode** | `enable_user_profile: true` | memory plus structured user profile extraction | use a backend supported by your installed PowerMem version |

Check the PowerMem release notes for the exact backend support matrix of your installed version.

## Recommended Provider Patterns

### Option 1: OpenAI

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: gpt-4o-mini
        openai_base_url: https://api.openai.com/v1
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-3-small
        openai_base_url: https://api.openai.com/v1
    vector_store:
      provider: sqlite
      config: {}
```

### Option 2: Self-hosted OpenAI-compatible endpoint

If you run a local or private OpenAI-compatible model endpoint, point both the LLM and embedding configuration to that service:

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: local-token
        model: your-local-chat-model
        openai_base_url: http://127.0.0.1:8000/v1
    embedder:
      provider: openai
      config:
        api_key: local-token
        model: your-local-embedding-model
        openai_base_url: http://127.0.0.1:8000/v1
    vector_store:
      provider: sqlite
      config: {}
```

### Option 3: PostgreSQL backend

If you want a database-backed deployment rather than local SQLite:

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: gpt-4o-mini
        openai_base_url: https://api.openai.com/v1
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-3-small
        openai_base_url: https://api.openai.com/v1
    vector_store:
      provider: postgres
      config:
        host: 127.0.0.1
        port: 5432
        user: postgres
        password: your_password
        db_name: powermem
        collection_name: memories
        embedding_model_dims: 1536
```

## Device-Level Memory Isolation

PowerMem automatically uses the device ID (`device_id`) as `user_id` for memory isolation. That means:

- each device has its own memory space
- memories do not leak across devices
- multiple sessions on the same device can share memory context

## User Profiles with `UserMemory`

PowerMem can extract structured user profile information from conversations through `UserMemory`.

### Enable user profile extraction

Set `enable_user_profile: true`:

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: gpt-4o-mini
        openai_base_url: https://api.openai.com/v1
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-3-small
        openai_base_url: https://api.openai.com/v1
    vector_store:
      provider: sqlite
      config: {}
```

### User profile capabilities

| Capability | Description |
|------|------|
| **Information extraction** | Pulls out facts such as name, age, work, and interests |
| **Continuous updates** | Refines the user profile over time |
| **Profile-aware retrieval** | Combines user profile context with memory search |
| **Forgetting behavior** | Reduces the weight of stale or low-value information |

### How it works

When user profile mode is enabled, memory lookups can return:

1. **User profile context** such as stable preferences or identity clues
2. **Relevant memories** related to the current conversation

## Comparison with Other Memory Options

| Feature | PowerMem | mem0ai | mem_local_short |
|------|----------|--------|-----------------|
| Operating model | local summarization | cloud API | local summarization |
| Storage | local or database-backed | cloud | local YAML |
| Cost | depends on LLM and DB | limited free tier | effectively free |
| Semantic retrieval | ✅ vector search | ✅ vector search | ❌ full return |
| User profiles | ✅ `UserMemory` | ❌ | ❌ |
| Forgetting behavior | ✅ supported | ❌ | ❌ |
| Private deployment | ✅ supported | ❌ cloud-only | ✅ supported |

## Troubleshooting

### 1. API key errors

If you see `API key is required`, check:

- `llm.config.api_key` is set correctly
- `embedder.config.api_key` is set correctly
- the keys are still valid

### 2. Model not found

If the selected model cannot be resolved, verify:

- `llm.config.model` is correct
- `embedder.config.model` is correct
- your provider account has access to those models

### 3. Connection timeout

If requests time out:

- verify outbound network access
- verify the base URL if you are using a proxy or self-hosted endpoint
- confirm the target service is reachable

### 4. Empty LLM output / JSON parse errors (e.g. `Expecting value: line 1 column 1`)

If logs mention JSON decode failures during PowerMem fact extraction, the model may have **used the whole token budget** on reasoning and returned no JSON body. Set a higher limit using **`llm_max_tokens`** (flat manager JSON) or **`llm.config.max_tokens`** (nested `llm` block in YAML), for example `8192`, subject to your provider’s limits.

## Verification

You can verify that PowerMem imports correctly inside your virtual environment:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Test AsyncMemory import
python -c "from powermem import AsyncMemory; print('PowerMem import succeeded')"

# Test UserMemory import
python -c "from powermem import UserMemory; print('UserMemory import succeeded')"
```

## Additional Resources

- [PowerMem documentation](https://www.powermem.ai/)
- [PowerMem GitHub repository](https://github.com/oceanbase/powermem)
- [PowerMem examples](https://github.com/oceanbase/powermem/tree/main/examples)
