# Agentic Sandbox

Python prototype workspace for experimenting with Agentic AI workflows, starting with
a text-based educational toy aligned with the thesis topic.

## What is included

- Conda-managed environment via `environment.yml`
- Editable package install via `pyproject.toml`
- `setup/` scripts for repeatable bootstrap
- CLI entrypoint for running the educational toy prototype
- Local learner memory persisted in `.agentic_sandbox/session.json`
- Modular prototype agents: professor, narrator, safety moderator, level adapter, and meta-agent
- LangGraph orchestration for the prototype turn flow
- Optional OpenAI-backed LLM narration layer enabled through environment variables

## Quick start

```bash
./setup/create_conda_env.sh
conda activate agentic-sandbox
./setup/install_project.sh
agentic-sandbox status
```

## Prototype commands

Start a learner session:

```bash
agentic-sandbox prototype start --name Lokmane --age 8
```

Submit one answer:

```bash
agentic-sandbox prototype turn cat
```

Run the interactive loop:

```bash
agentic-sandbox prototype chat --name Lokmane --age 8
```

Inspect learner state:

```bash
agentic-sandbox prototype profile
```

## LLM mode

Copy `.env.example` to `.env` and provide an OpenAI API key:

```bash
cp .env.example .env
```

The relevant variables are:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
AGENTIC_USE_LLM=true
```

When `OPENAI_API_KEY` is present and `AGENTIC_USE_LLM=true`, the application uses
LangGraph to orchestrate the turn flow and calls OpenAI to generate the tutoring
response. Without a key, it falls back to the local deterministic narrator.

## Layout

- `src/agentic_sandbox/`: package source
- `setup/`: environment and install scripts
- `main.py`: simple local entrypoint
- `pfe_documents/`: thesis and project preparation documents
