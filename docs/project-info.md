# Context Learning Trajectory Generator - Project Info

## Project Overview

A Python framework that automatically generates agent trajectory training data from open-source projects. The core insight: teaching small LLMs (4B-30B) **how to learn from context** (read code, extract APIs, generate scripts, self-verify) is far more efficient than baking factual knowledge into weights.

The system uses a dual-agent conversation pipeline where one AI simulates a user and another acts as a coder with tool access to explore real project source code. All interactions are captured as structured trajectory data for fine-tuning.

## Repository

- **Location**: `/Users/jason/Projects/msj-context-learning/`
- **Language**: Python 3.11+
- **Package Manager**: uv
- **Entry Point**: `uv run python -m generator`

## Architecture

### 5-Stage Pipeline

```
Stage 1: Analyzer       → AI analyzes project (README + source), generates requirement list
Stage 2: User Agent     → AI simulates inexperienced user, initiates conversation
Stage 3: Coder Agent    → AI explores project with tools, generates single-page script (core trajectory)
Stage 4: Reviewer Agent → AI reads source code to verify script correctness (PASS/FAIL)
Stage 4.5: Fixer Agent  → If FAIL, AI fixes script based on review feedback (up to 2 rounds)
Stage 5: User Verify    → User agent checks if final script satisfies original requirement
```

### Multi-Model Architecture

Different AI models play different roles via OpenRouter API:

| Role | Default Model | Purpose |
|------|---------------|---------|
| Analyzer | `google/gemini-3-flash-preview` | Fast project analysis + requirement generation |
| User | `z-ai/glm-5-turbo` | Cheap user simulation |
| Coder | `anthropic/claude-sonnet-4.5` | Strong code generation + tool calling |
| Reviewer | `openai/gpt-5.2-codex` | Strong code review |

Available model pool (all via OpenRouter):
```
minimax/minimax-m2.5, z-ai/glm-5, moonshotai/kimi-k2.5, qwen/qwen3.5-397b-a17b,
openai/gpt-5.4, anthropic/claude-sonnet-4.6, z-ai/glm-5-turbo, z-ai/glm-4.7,
google/gemini-3-flash-preview, openai/gpt-5.2-codex, anthropic/claude-sonnet-4.5,
google/gemini-3.1-pro-preview
```

### Tool System

The Coder and Reviewer agents have access to 5 tools for project exploration:

| Tool | Description |
|------|-------------|
| `file_tree` | View project directory structure (max depth 3) |
| `file_list` | List files in a directory (recursive optional) |
| `file_read` | Read file contents with line numbers |
| `grep` | Regex search across project files |
| `bash` | Execute shell commands in project directory |

All tools are sandboxed to the project root directory with path escape prevention.

### Data Capture

Trajectory data is captured at the agent call layer (not via external proxy). Every API call, tool use, and message is recorded with:
- Conversation turns (role, content, tool_calls, tool_results)
- Timestamps and durations
- Model used per stage
- Token usage (input/output)
- Stage identifier and project context

### Output Formats

- **JSONL**: One file per project+requirement pair in `output/trajectories/`
- **ShareGPT**: Training-ready format with system/human/gpt/tool roles in `output/sharegpt/`

## Directory Structure

```
msj-context-learning/
├── generator/                    # Main Python package
│   ├── __main__.py               # Entry point
│   ├── cli.py                    # CLI (run, batch, export, list-projects)
│   ├── config.py                 # Models, API keys, paths, constants
│   ├── pipeline.py               # Pipeline orchestrator (single, project, batch)
│   ├── batch_state.py            # Batch state persistence for resume
│   ├── models/                   # Pydantic data models
│   │   ├── project.py            # AnchorProject, ProjectAnalysis
│   │   ├── requirement.py        # Requirement, RequirementSet, Difficulty
│   │   ├── conversation.py       # Message, ToolCallRecord, ConversationHistory
│   │   ├── trajectory.py         # TrajectoryRecord, StageRecord
│   │   └── review.py             # ReviewVerdict, UserVerification
│   ├── llm/
│   │   ├── client.py             # AsyncOpenRouterClient (httpx, tool-calling loop)
│   │   └── prompts.py            # Prompt templates for all stages
│   ├── tools/
│   │   ├── definitions.py        # Tool JSON schemas (OpenAI format)
│   │   ├── registry.py           # ToolRegistry
│   │   └── executor.py           # ToolExecutor (sandboxed execution)
│   ├── stages/
│   │   ├── analyzer.py           # Stage 1: project analysis
│   │   ├── user_agent.py         # Stage 2+5: user simulation + verification
│   │   ├── coder_agent.py        # Stage 3+4.5: code generation + fixing
│   │   └── reviewer_agent.py     # Stage 4: code review
│   ├── project_access/
│   │   ├── cloner.py             # git clone --depth 1
│   │   └── workspace.py          # Workspace management
│   └── capture/
│       ├── recorder.py           # TrajectoryRecorder
│       └── exporter.py           # JSONL + ShareGPT export
├── data/                         # 3000 anchor projects
│   ├── cli_tools.json            # 1000 CLI tools
│   ├── python_packages.json      # 1000 Python packages
│   └── js_ts_packages.json       # 1000 JS/TS packages
├── workspace/                    # Cloned repos (gitignored)
├── output/
│   ├── trajectories/             # Raw trajectory JSONL files (2,020 files, 1.1 GB)
│   ├── sharegpt/                 # ShareGPT format exports
│   ├── batch_state.json          # Python packages batch checkpoint
│   ├── batch_cli_glm5.json       # CLI batch (GLM-5 run) checkpoint
│   ├── batch_cli_kimi.json       # CLI batch (Kimi run) checkpoint
│   └── batch_cli_remaining.json  # CLI batch (merged final) checkpoint
├── docs/                         # Documentation
├── pyproject.toml                # uv project config
├── .env                          # OPENROUTER_API_KEY
└── .gitignore
```

## CLI Usage

```bash
# Single project
uv run python -m generator run --project httpx --type python_package -v

# Single project, all requirements
uv run python -m generator run --project httpx --type python_package -n 5 -c 5

# Batch: 200 projects, 5 reqs each, parallel
uv run python -m generator batch \
  --type python_package \
  --count 200 \
  --reqs-per-project 5 \
  --project-concurrency 3 \
  --req-concurrency 5

# Batch with multi-coder: split 5 reqs across 2 coder models (2 for glm-5, 3 for kimi-k2.5)
uv run python -m generator batch \
  --type cli_tool \
  --count 200 \
  --reqs-per-project 5 \
  --multi-coder '["z-ai/glm-5", "moonshotai/kimi-k2.5"]' \
  --coder-split 2,3 \
  --project-concurrency 3 \
  --req-concurrency 5

# Resume interrupted batch
uv run python -m generator batch --resume output/batch_state.json

# Resume with multi-coder
uv run python -m generator batch \
  --resume output/batch_cli_remaining.json \
  --multi-coder '["z-ai/glm-5", "moonshotai/kimi-k2.5"]' \
  --coder-split 2,3

# Export trajectories to ShareGPT
uv run python -m generator export --input output/trajectories/ --format sharegpt -o output/sharegpt/dataset.json

# List available projects
uv run python -m generator list-projects --type python_package --show-all
```

## Batch Processing - Robust Operation

The `batch` command supports:

- **Resume**: Reads `batch_state.json`, skips completed/failed projects, continues from pending
- **Error isolation**: One project failure doesn't stop the batch
- **Graceful shutdown**: Ctrl+C finishes current projects, saves state, exits cleanly
- **Dual-layer parallelism**: Project-level (`--project-concurrency`) + requirement-level (`--req-concurrency`)
- **Periodic checkpoint**: State saved to disk after every project completes
- **Multi-coder**: `--multi-coder` + `--coder-split` distributes requirements across multiple coder models per project
- **Three-level timeouts**: Tool loop (600s), per-requirement (900s), per-project (3600s) to prevent hangs

## Development Timeline

### Phase 1: Foundation
- Created project scaffolding: `pyproject.toml`, `.env`, `.gitignore`
- Implemented Pydantic data models (5 model files)
- Implemented `config.py` with model pool and role assignments

### Phase 2: Core Engine
- Built `AsyncOpenRouterClient` with httpx (direct OpenRouter API, not openai SDK)
- Implemented tool-calling loop: LLM calls tools → execute locally → append results → repeat
- Built 5-tool system with path sandboxing (file_tree, file_list, file_read, grep, bash)

### Phase 3: Trajectory Capture
- Built `TrajectoryRecorder` hooking into every API call and tool execution
- Built JSONL + ShareGPT exporter with quality filtering

### Phase 4: Pipeline Stages
- Implemented all 4 stages: Analyzer, User Agent, Coder Agent, Reviewer Agent
- Added Fixer stage (Stage 4.5): review → fix → re-review loop (max 2 rounds)

### Phase 5: Integration + CLI
- Built pipeline orchestrator wiring all stages
- Built CLI with `run`, `export`, `list-projects` commands

### Phase 6: Validation
- Single project test: `httpx` — full pipeline PASS
- Single project test: `click` — full pipeline PASS
- Parallel test: `requests` with 5 requirements × 5 concurrent — 5/5 PASS

### Phase 7: Batch Processing
- Added `BatchState` with checkpoint persistence
- Added `run_batch()` with project-level concurrency + signal handling
- Added `batch` CLI subcommand with resume support
- Validation: 3 projects (django, flask, fastapi) × 2 reqs — 6/6 PASS

### Phase 8: Production Batch Run (completed)
- 200 Python packages × 5 requirements each
- Multiple resume cycles to handle transient failures:
  - Run 1: 165/200 completed, 35 failed (GitHub rate limits + OpenRouter 402 errors)
  - Resume 1: 195/200 completed, 5 failed (4 wrong repo addresses + 1 API error)
  - Fix 4 repo addresses (beautifulsoup4, pulumi, passlib, openpyxl) + Resume 2: 199/200
  - Resume 3: 200/200 completed, 0 failed
- Final result: 200/200 projects, 960 trajectories, 837 PASS / 123 FAIL

### Phase 9: Python Dataset Export
- Exported 974 trajectory files (960 from batch + 14 from earlier validation runs) to ShareGPT format
- `dataset_pass.json`: 850 PASS conversations for fine-tuning
- `dataset_all.json`: 974 all conversations including failures

### Phase 10: Deadlock Fix + Multi-Coder Support
- **Root cause**: Batch process hung at 52/100 projects (CPU 100%, no network) due to missing timeouts at multiple levels
- **Three-level timeout fix**:
  - `tool_calling_loop()`: 600s overall timeout via `asyncio.wait_for()` wrapper in `client.py`
  - Per-requirement: 900s timeout in `run_project()._run_one()`
  - Per-project: 3600s timeout in `run_batch()._run_project()`
- **Multi-coder support**: New `--multi-coder` and `--coder-split` CLI args
  - `_assign_coders()` method distributes coder models across requirements per project
  - Supports explicit split (e.g., `[2,3]`) or round-robin
  - `run_single()` accepts `coder_model` override, threaded through `run_project()` and `run_batch()`

### Phase 11: CLI Tools Batch Run (completed)
- 200 CLI tool projects × 5 requirements each
- Multiple model runs:
  - GLM-5 batch: 98/100 projects, 124 trajectories (107P/17F), 40.3M tokens — low requirement completion rate (25.3%) due to API errors
  - Kimi-K2.5 batch: 150/200 projects (unintended overlap with GLM-5 range), 646 trajectories (543P/103F), 181.3M tokens
  - Multi-coder batch (final 48 projects): glm-5 (2 reqs) + kimi-k2.5 (3 reqs) per project, 231 trajectories (171P/60F)
- Batch got stuck at 52/100 due to deadlock (fixed in Phase 10), timeout protection prevented further hangs
- Final result: 200/200 CLI projects completed, 1,044 CLI trajectories on disk (854P/190F)

### Phase 12: Combined Dataset Export
- Exported all 2,020 trajectory files (Python + CLI) to ShareGPT format
- `dataset_pass.json`: 1,706 PASS conversations
- `dataset_all.json`: 2,020 all conversations

## Production Results — Combined

### Grand Total (All Batches)

| Metric | Value |
|--------|-------|
| Total trajectory files | 2,020 |
| Unique projects | 390 (200 Python + 197 CLI — some CLI projects overlap across runs) |
| PASS / FAIL | 1,706 / 314 |
| Overall PASS rate | 84.5% |
| Total tokens consumed | 738.6M |
| Raw trajectory size | 1,105 MB |

### Per-Batch Breakdown

| Batch | Projects | Trajectories | PASS/FAIL | Pass Rate | Tokens |
|-------|----------|-------------|-----------|-----------|--------|
| Python Packages | 200/200 | 976 | 837/123* | 87.2% | 416.2M |
| CLI Tools | 200/200 | 1,044 | 854/190 | 81.8% | 319.3M |
| **Combined** | **400** | **2,020** | **1,706/314** | **84.5%** | **738.6M** |

*Python count includes 16 pre-production validation trajectories on disk.

### Python Packages — Trajectory Duration Stats

| Metric | Value |
|--------|-------|
| Min | 35s |
| Median | 120s |
| Mean | 178s |
| P90 | 409s |
| P99 | 631s |
| Max | 808s |

### CLI Tools — Trajectory Duration Stats

| Metric | Value |
|--------|-------|
| Min | 44s |
| Median | 192s |
| Mean | 264s |
| P90 | 545s |
| Max | 2,678s |

### Python Packages — Category Breakdown (top categories)

| Category | Trajectories | PASS/FAIL | Tokens | Pass Rate |
|----------|-------------|-----------|--------|-----------|
| ml | 90 | 64/26 | 71.6M | 71.1% |
| database | 50 | 47/3 | 15.8M | 94.0% |
| dl | 48 | 44/4 | 20.9M | 91.7% |
| api | 45 | 40/5 | 16.4M | 88.9% |
| web-framework | 43 | 39/4 | 13.3M | 90.7% |
| visualization | 40 | 39/1 | 11.7M | 97.5% |
| devops | 37 | 31/6 | 27.5M | 83.8% |
| nlp | 32 | 29/3 | 15.9M | 90.6% |
| scientific | 25 | 25/0 | 6.7M | 100% |
| serialization | 20 | 20/0 | 5.7M | 100% |

### CLI Tools — Category Breakdown (top categories)

| Category | Trajectories | PASS/FAIL | Tokens | Pass Rate |
|----------|-------------|-----------|--------|-----------|
| file-management | 98 | 78/20 | 32.9M | 80% |
| network | 90 | 81/9 | 27.0M | 90% |
| container | 83 | 65/18 | 29.0M | 78% |
| database | 83 | 67/16 | 29.8M | 81% |
| cloud | 81 | 64/17 | 27.6M | 79% |
| package-manager | 75 | 61/14 | 18.8M | 81% |
| security | 67 | 52/15 | 24.6M | 78% |
| build-tool | 66 | 53/13 | 16.9M | 80% |
| shell | 66 | 53/13 | 19.1M | 80% |
| devops | 60 | 50/10 | 28.9M | 83% |
| editor | 33 | 28/5 | 12.1M | 85% |
| search | 32 | 28/4 | 6.9M | 88% |

### Most Expensive Projects (by token usage)

**Python:**

| Project | Trajectories | PASS/FAIL | Tokens | Pass Rate |
|---------|-------------|-----------|--------|-----------|
| great-expectations | 5 | 2/3 | 8.0M | 40% |
| autogen | 5 | 2/3 | 7.3M | 40% |
| outlines | 5 | 1/4 | 7.2M | 20% |
| llama-index | 5 | 2/3 | 6.9M | 40% |
| dagster | 5 | 5/0 | 6.4M | 100% |

**CLI:**

| Project | Trajectories | PASS/FAIL | Tokens | Pass Rate |
|---------|-------------|-----------|--------|-----------|
| docker | 12 | 7/5 | 6.6M | 58% |
| ansible | 10 | 8/2 | 6.2M | 80% |
| borgbackup | 7 | 4/3 | 5.3M | 57% |
| wget | 13 | 10/3 | 5.3M | 77% |
| yazi | 4 | 0/4 | 5.2M | 0% |

### Hardest Projects (lowest pass rate)

**Python:**

| Project | PASS/FAIL | Tokens | Pass Rate |
|---------|-----------|--------|-----------|
| outlines | 1/4 | 7.2M | 20% |
| safety | 1/4 | 6.2M | 20% |
| reflex | 1/4 | 5.8M | 20% |
| opencv-python | 1/4 | 1.1M | 20% |

**CLI:**

| Project | PASS/FAIL | Tokens | Pass Rate |
|---------|-----------|--------|-----------|
| gcloud | 0/5 | 0.8M | 0% (repo 404) |
| yazi | 0/4 | 5.2M | 0% |
| procs | 0/4 | 4.4M | 0% |
| k6 | 1/4 | 1.5M | 20% |
| nushell | 1/4 | 2.6M | 20% |

### Exported Datasets (Combined)

| File | Conversations | Turns | Tool Turns | Size |
|------|--------------|-------|------------|------|
| `dataset_pass.json` | 1,706 | 133,991 | 54,971 | 216 MB |
| `dataset_all.json` | 2,020 | 187,341 | 78,314 | 301 MB |
| Raw trajectories (JSONL) | 2,020 files | — | — | 1,105 MB |

### Dataset Length Distribution (PASS-only, estimated tokens)

| Metric | Value |
|--------|-------|
| Min | ~4.6k tokens |
| P10 | ~12.4k |
| P25 | ~17.0k |
| **Median** | **~23.3k** |
| Mean | ~29.8k |
| P75 | ~34.2k |
| P90 | ~58.3k |
| P95 | ~74.3k |
| P99 | ~104.7k |
| Max | ~229.6k |

**Token length buckets:**

| Bucket | Count | Percentage |
|--------|-------|------------|
| 4k-8k | 20 | 1.2% |
| 8k-16k | 357 | 20.9% |
| **16k-32k** | **852** | **49.9%** |
| 32k-64k | 342 | 20.0% |
| 64k-128k | 129 | 7.6% |
| 128k+ | 6 | 0.4% |

**Context window fit:**

| Window | Fits |
|--------|------|
| 8k | 1.3% |
| 16k | 23.2% |
| 32k | 73.2% |
| 64k | 92.4% |
| 128k | 99.7% |

**By message role (avg chars):** system 769, human 3,214, gpt 388 (short + frequent due to tool calling), tool 2,674

## Validation Results (Pre-Production)

### Single Project Tests

| Project | Quality | API Calls | Tokens | Duration |
|---------|---------|-----------|--------|----------|
| httpx | PASS | 24 | 151K | 81s |
| click | PASS | 27 | 242K | 101s |

### Parallel Test (requests × 5 requirements)

| Requirement | Quality | Tokens | Duration |
|-------------|---------|--------|----------|
| GET + JSON parse | PASS | 46K | 54s |
| POST + JSON body | PASS | 45K | 63s |
| Timeout handling | PASS | 80K | 100s |
| Session + cookies | PASS | 267K | 108s |
| Stream download | PASS | 84K | 74s |

### Batch Test (3 projects × 2 requirements)

| Project | Trajectories | PASS | Tokens |
|---------|-------------|------|--------|
| django | 2 | 2 | 533K |
| flask | 2 | 2 | 351K |
| fastapi | 2 | 2 | 302K |

## Key Design Decisions

1. **httpx over openai SDK**: Full control over request/response serialization for trajectory capture
2. **Read+bash tools, not read-only**: Open tool permissions including shell execution for richer trajectories
3. **Single-page script constraint**: Keeps generation and verification tractable, avoids multi-file complexity
4. **Review → Fix loop**: Reviewer FAIL triggers coder fix attempt (up to 2 rounds), improving overall PASS rate
5. **Built-in capture over proxy**: Agent-layer recording captures structured trajectory data directly, no external dependency
6. **JSONL per-trajectory**: Simple, portable, no database needed. Each file is self-contained.
7. **Different models per role**: Cheap models for user simulation, strong models for coding/review — cost efficiency
8. **Multi-coder distribution**: Split requirements across multiple coder models per project to reduce per-model API pressure and add diversity to training data
9. **Three-level timeout hierarchy**: Tool loop (600s) → requirement (900s) → project (3600s) prevents cascading hangs from any single stuck operation

## Lessons Learned from Production Batches

### Failure Patterns
- **GitHub rate limiting**: Concurrent `git clone` from 3+ projects triggers GitHub rate limits. Resolved naturally on resume with staggered starts.
- **OpenRouter 402 errors**: Burst API usage triggers rate/credit limits. Transient — resolved on resume.
- **Wrong repo addresses**: 4 out of 200 repos had stale/incorrect GitHub paths (beautifulsoup4, pulumi, passlib, openpyxl). Required manual verification via `git ls-remote`. CLI batch had 1 permanent failure (gcloud — repo 404).
- **Complex ML frameworks**: Projects like outlines, autogen, great-expectations had the lowest pass rates (20-40%), likely due to complex APIs and heavy framework abstractions that make single-script generation harder.
- **Deadlock/hang**: CLI batch hung at 52/100 projects — CPU 100%, no network activity. Root cause: missing timeouts at tool-calling loop, requirement, and project levels. A stuck API call or infinite tool loop could block indefinitely. Fixed with three-level `asyncio.wait_for()` timeouts.
- **GLM-5 API instability**: GLM-5 as coder had only 25.3% requirement completion rate (124 trajectories from 98 projects) vs Kimi-K2.5's 91.9%, primarily due to frequent API errors returning responses without `choices` key.

### What Worked Well
- **Resume-from-checkpoint**: Essential for long batches. Multiple crash/resume cycles completed all 400 projects across both batches.
- **Failed → Pending retry**: Moving failed projects back to pending on resume was critical for handling transient errors.
- **Dual-layer parallelism**: 3 projects × 5 requirements kept throughput high while avoiding excessive rate limiting.
- **Multi-coder distribution**: Splitting 5 requirements per project across 2 coder models (glm-5:2 + kimi-k2.5:3) reduced per-model API pressure and provided model diversity in the dataset.
- **Timeout protection**: After adding three-level timeouts, exactly 1 requirement timed out at 900s (properly caught) vs previous indefinite hangs.
- **Scientific/utility packages**: Categories like `scientific` (100% pass) and `serialization` (100% pass) were reliably easy — well-documented, clear APIs.
- **Network/search CLI tools**: Categories like `network` (90% pass) and `search` (88% pass) performed well — clear input/output patterns.
- **Review → Fix loop**: Many trajectories recovered from initial FAIL via the fix cycle, contributing to the overall pass rates.

### Cost Observations
- Python packages: average 2.1M tokens/project (~$0.50-2.00 depending on model pricing)
- CLI tools: average 1.6M tokens/project (cheaper on average — CLI tools tend to have simpler APIs)
- Hardest projects consumed 3-4x the average (great-expectations at 8.0M, docker at 6.6M tokens)
- Tool calls (especially `file_read` and `grep`) account for bulk of token usage — long source files get included in context
- Total across all batches: 738.6M tokens

## Related Components

- **Proxy Hook** (`/Users/jason/Projects/msj-claudecode/anthropic-proxy-hook/`): Bun/TS proxy that intercepts Claude Code → OpenRouter traffic, logs to SQLite. Can be used alongside this generator for raw conversation capture.
- **Agent SDK Docs** (`docs/claude-agent-sdk-python-ref.md`, `docs/claude-agent-sdk-typescript-references.md`): Offline API references for Claude Agent SDK.
- **Anchor Project Data** (`data/`): 3000 curated projects across CLI tools (1000), Python packages (1000), JS/TS packages (1000) with name, repo, category metadata.

## Data Quality & Coverage

### Anchor Project Fixes
4 repos in `data/python_packages.json` had incorrect GitHub addresses, discovered during batch run:

| Package | Old (wrong) Repo | New (correct) Repo |
|---------|------------------|--------------------|
| beautifulsoup4 | `waylan/beautifulsoup` | `wention/BeautifulSoup4` |
| pulumi | `pulumi/pulumi-python` | `pulumi/pulumi` |
| passlib | `glic3rern/passlib` | `ThirVondukr/passlib` |
| openpyxl | `theorchard/openpyxl` | `fluidware/openpyxl` |

1 CLI tool project permanently failed: `gcloud` (google-cloud-sdk) — GitHub repo not found (404).

### Dataset Composition
- 2,020 trajectory files covering 390 unique projects (200 Python packages + ~197 CLI tools) across 65+ categories
- Each trajectory is a complete multi-turn conversation: user request → coder exploration → code generation → review → (optional fix) → user verification
- Tool turns make up ~41% of all turns (54,971 tool turns / 133,991 total in PASS dataset), reflecting rich project exploration behavior
- Difficulty distribution (PASS-only): Easy 998, Medium 687, Hard 21
- Median trajectory duration: Python 120s, CLI 192s — CLI tools tend to require more exploration
- CLI trajectories generated by multiple coder models: glm-5, kimi-k2.5, and their combination, providing model diversity

### Dataset Length Profile
- 50% of conversations are in the **16k-32k** token range (median ~23k tokens)
- 92.4% fit within a 64k context window; 99.7% within 128k
- gpt messages are short but frequent (avg 388 chars) — dominated by tool-calling interactions
- tool messages average 2,674 chars (file contents, grep results)
- Recommended training context: 32k covers 73%, 64k covers 92%

### Training Data Format (ShareGPT)
Each conversation follows this structure:
```
system  → Coder system prompt (project context, tool definitions)
human   → User's coding request
gpt     → Coder's response (may include tool_calls)
tool    → Tool execution results
gpt     → Coder continues (more tool calls or final script)
...     → Multi-turn conversation continues
human   → Follow-up questions or clarifications (if needed)
gpt     → Final response with complete script
```

## Dependencies

```
httpx>=0.27.0      # Async HTTP client for OpenRouter API
pydantic>=2.0.0    # Data models and validation
rich>=13.0.0       # CLI output formatting
python-dotenv>=1.0.0  # .env file loading
```
