# Agentic Edu Toy

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-1f6feb)](https://www.langchain.com/langgraph)
[![OpenAI Ready](https://img.shields.io/badge/LLM-OpenAI%20Ready-0ea5e9)](https://platform.openai.com/)
[![Status](https://img.shields.io/badge/status-prototype-f59e0b)](#current-scope)

Agentic educational toy prototype for resource-aware AI systems. The project implements a child-safe, text-based learning assistant with modular agents, persistent learner memory, LangGraph orchestration, and an optional OpenAI-backed tutoring layer.

## Overview

This repository is the software prototype for a thesis-oriented project on Agentic AI architectures for constrained or embedded software systems.

The current prototype focuses on the mandatory use case:

- an intelligent educational toy
- English vocabulary practice for children
- adaptive learner progression
- child-safe moderation
- local persistent session memory
- optional LLM-generated tutoring responses

The system is intentionally built as a controlled vertical slice: the orchestration and pedagogical logic are explicit, while heavier capabilities such as speech and richer emotion models can be added incrementally.

## Architecture

The application is organized around specialized roles:

- `Safety Moderator Agent`: filters unsafe or out-of-scope learner input
- `Professor Agent`: manages lesson prompts and evaluates answers
- `Level Adapter Agent`: updates learner progression and simple emotion state
- `Narrator Agent`: produces child-friendly feedback
- `LangGraph Workflow`: orchestrates the turn flow across all agents
- `Shared Memory`: persists learner profile and interaction history locally

Current turn flow:

1. learner input is received
2. safety moderation is applied
3. the answer is evaluated against the active lesson
4. learner state is updated
5. the next pedagogical prompt is prepared
6. a response is generated locally or through OpenAI
7. the session is saved

## Current Scope

What is already implemented:

- modular agent-based educational toy prototype
- CLI interface for starting, chatting, inspecting, and resetting sessions
- local session persistence in `.agentic_sandbox/session.json`
- LangGraph-based orchestration
- optional OpenAI-backed LLM response generation
- editable Python package setup with reproducible environment scripts

What is intentionally left for later:

- speech-to-text and text-to-speech
- richer emotion detection
- web or mobile interface
- real embedded deployment
- evaluation dashboards and benchmark scripts

## Quick Start

```bash
./setup/create_conda_env.sh
conda activate agentic-sandbox
./setup/install_project.sh
agentic-sandbox status
```

If you want to run without installing the entrypoint first:

```bash
python main.py status
```

## Prototype Commands

Start or resume a learner session:

```bash
python main.py prototype start --name Lokmane --age 8
```

Submit one answer:

```bash
python main.py prototype turn cat
```

Run the interactive chat loop:

```bash
python main.py prototype chat --name Lokmane --age 8
```

Inspect learner state:

```bash
python main.py prototype profile
```

Reset the session:

```bash
python main.py prototype reset
```

## LLM Mode

Copy the template and provide an OpenAI API key:

```bash
cp .env.example .env
```

Environment variables:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
AGENTIC_USE_LLM=true
```

Behavior:

- when `OPENAI_API_KEY` is present and `AGENTIC_USE_LLM=true`, the prototype uses OpenAI to generate the tutoring response
- when the key is missing, the system falls back to the local deterministic narrator

## Project Layout

```text
.
├── main.py
├── pyproject.toml
├── environment.yml
├── setup/
│   ├── create_conda_env.sh
│   ├── install_project.sh
│   └── smoke_test.sh
└── src/agentic_sandbox/
    ├── agents.py
    ├── cli.py
    ├── config.py
    ├── curriculum.py
    ├── llm.py
    ├── memory.py
    ├── models.py
    ├── prototype.py
    └── workflow.py
```

## Why LangGraph

LangGraph is used here because the application has a fixed, stateful, supervised interaction loop. That makes it a better fit than looser autonomous-agent frameworks for this stage of the project.

It gives the prototype:

- explicit orchestration
- controlled state transitions
- a clear path for adding more advanced agents later
- compatibility with hybrid local-plus-LLM logic

## Thesis Relevance

This prototype already reflects the core thesis ideas:

- agentic decomposition of responsibilities
- meta-control through supervised orchestration
- safety as part of the runtime flow
- persistent context and learner modeling
- resource-aware incremental design

## Next Steps

Planned extensions include:

- LLM-based hint generation
- richer learner modeling and emotion analysis
- web interface with FastAPI or a lightweight frontend
- resource monitoring and latency evaluation
- migration toward constrained hardware experiments
