# Context Learning Trajectory Generator

Automatically generate agent trajectory training data from open-source projects. This system uses a multi-agent conversation pipeline to capture structured trajectory data for fine-tuning small LLMs.

## Quick Start

### 1. Install Claude Code (Recommended Version)

```bash
# Install Claude Code CLI
curl -fsSL https://claude.ai/install.sh | bash

# Downgrade to stable version 2.1.1 (best compatibility with Claude Agent SDK)
claude install 2.1.1
```

### 2. Install Dependencies

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Configure API Key

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or create a `.env` file:

```bash
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

### 4. Run Batch Generation

```bash
# Generate trajectories for Python packages
uv run python -m generator batch \
  --type python_package \
  --start 200 \
  --count 800 \
  --reqs-per-project 5 \
  --multi-coder '["z-ai/glm-5","moonshotai/kimi-k2.5"]' \
  --coder-split 2,3 \
  --project-concurrency 3 \
  --req-concurrency 5 \
  --state-file output/batch_python_800.json

# Or generate for CLI tools
uv run python -m generator batch \
  --type cli_tool \
  --start 200 \
  --count 800 \
  --reqs-per-project 5 \
  --multi-coder '["z-ai/glm-5","moonshotai/kimi-k2.5"]' \
  --coder-split 2,3 \
  --project-concurrency 3 \
  --req-concurrency 5 \
  --state-file output/batch_cli_800.json
```

### 5. Resume Interrupted Batch

```bash
uv run python -m generator batch \
  --resume output/batch_cli_800.json \
  --multi-coder '["z-ai/glm-5","moonshotai/kimi-k2.5"]' \
  --coder-split 2,3
```

### 6. Export to ShareGPT Format

```bash
uv run python -m generator export \
  --input output/trajectories/ \
  --format sharegpt \
  --output output/sharegpt/dataset_pass.json
```

## Architecture

The system uses a 5-stage pipeline:

1. **Analyzer**: AI analyzes project (README + source), generates requirement list
2. **User Agent**: AI simulates inexperienced user, initiates conversation
3. **Coder Agent**: AI explores project with tools, generates single-page script (core trajectory)
4. **Reviewer Agent**: AI reads source code to verify script correctness (PASS/FAIL)
5. **Fixer Agent**: If FAIL, AI fixes script based on review feedback (up to 2 rounds)

## Features

- **Multi-coder support**: Distribute requirements across multiple coder models for diversity
- **Three-level timeouts**: Tool loop (600s) → requirement (900s) → project (3600s) prevents hangs
- **Resume capability**: Checkpoint-based state persistence for crash recovery
- **Dual-layer parallelism**: Project-level + requirement-level concurrency
- **Quality filtering**: Automated review and verification for PASS/FAIL classification

## Project Structure

```
msj-context-learning-deploy/
├── generator/              # Main Python package
│   ├── __main__.py
│   ├── cli.py             # CLI interface
│   ├── pipeline.py        # Pipeline orchestrator
│   ├── config.py          # Model configurations
│   ├── llm/               # LLM client & prompts
│   ├── tools/             # Tool system (file_tree, grep, bash, etc.)
│   ├── stages/            # Pipeline stages (analyzer, coder, reviewer)
│   ├── models/            # Pydantic data models
│   ├── project_access/    # Git cloning & workspace management
│   └── capture/           # Trajectory recording & export
├── data/                  # Anchor projects
│   ├── python_packages.json  # 1000 Python packages
│   ├── cli_tools.json        # 1000 CLI tools
│   └── js_ts_packages.json   # 1000 JS/TS packages
├── docs/                  # Documentation
├── pyproject.toml         # uv project config
└── .gitignore
```

## Data Sources

- **Python Packages**: 1,000 curated Python projects across 50+ categories
- **CLI Tools**: 1,000 command-line tools across 20+ categories
- **JS/TS Packages**: 1,000 JavaScript/TypeScript packages

## Output

- **Raw trajectories**: `.jsonl` files in `output/trajectories/`
- **ShareGPT format**: Training-ready JSON in `output/sharegpt/`
- **Batch state**: Checkpoint files in `output/batch_*.json`

## Requirements

- Python 3.11+
- OpenRouter API key
- Git (for cloning projects)
- ~50GB free disk space (for workspace)

## Documentation

See `docs/project-info.md` for detailed architecture, usage examples, and production results.

## License

MIT
