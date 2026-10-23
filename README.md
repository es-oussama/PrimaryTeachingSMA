# PrimaryTeachingSMA

**A multi-agent teaching assistant for generating primary-school activities and printable PDF worksheets.**

An academic Generative AI project combining CrewAI, Claude, document retrieval and a Streamlit interface. The application accepts a learner's age, school level, activity type and teaching objective, then produces structured activity content for teacher review.

## Problem and objective

Preparing activities requires adapting instructions, difficulty and presentation to a learning objective. This project explores whether specialized AI agents, supported by retrieved teaching resources, can assist that preparation process.

The objective is a traceable activity-generation workflow. No measured improvement in learning outcomes or classroom effectiveness is claimed.

## Architecture and methodology

1. **Input:** the teacher selects an age, school level, activity type and objective in Streamlit.
2. **Retrieval:** the RAG module chunks teaching resources, embeds them with Sentence Transformers and retrieves context from persistent ChromaDB storage.
3. **Agents:** three CrewAI agents run sequentially: pedagogical analysis, activity generation and PDF-content structuring.
4. **Output:** ReportLab generates a printable worksheet; logging and workflow utilities record execution information.

The retrieval module supports sentence-aware chunking and context compression. When retrieval is unavailable or empty, it can return built-in reference context. The agent workflow also has predefined fallback content; fallback output is not evidence of a successful live LLM call or successful document retrieval.

## Technology stack

- **Language:** Python
- **Agents and models:** CrewAI, Claude via Anthropic, LangChain-related integrations
- **Retrieval:** ChromaDB, Sentence Transformers, PDF extraction with pypdf
- **Interface and export:** Streamlit, ReportLab, Pillow
- **Configuration:** python-dotenv

Dependencies are listed in [Source/requirements.txt](Source/requirements.txt). They use minimum-version ranges rather than a fully locked environment.

## Installation

The existing dependency file identifies Python 3.11+ as its baseline. Dependency compatibility and model access must be checked in the environment where the application is run.

```bash
git clone https://github.com/es-oussama/PrimaryTeachingSMA.git
cd PrimaryTeachingSMA/Source
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Copy `Source/.env.example` to `Source/.env` locally. Set `ANTHROPIC_API_KEY` and choose a `CLAUDE_MODEL` supported by your account. These values stay on the machine running the application. The current Streamlit interface requires an API key before starting generation; live model calls use the configured provider account.

## Teaching resources and RAG

No evaluation corpus or teaching-PDF collection is included in this repository. To use your own resources, create `Source/data/`, add PDFs you have permission to process, and index them from the `Source` directory:

```bash
python -c "from rag import get_rag; print(get_rag().index_data_folder('./data'))"
```

Without an indexed collection, the retrieval layer uses its documented fallback context. Corpus relevance, provenance and retrieval quality need to be evaluated separately.

## Usage

Run from `Source`:

```bash
streamlit run app.py
```

1. Enter the age, school level, activity type and pedagogical objective.
2. Start activity generation.
3. Review the analysis, generated activities and fallback indicators.
4. Download the worksheet PDF and check its content before classroom use.

The repository also contains a command-line workflow in `Source/workflow.py` and an optional [n8n workflow export](Source/n8n_workflow.json). n8n is an optional integration, not a requirement for the Streamlit application.

## Results and validation status

The implementation provides a three-agent workflow, a retrieval module and PDF-generation utilities. This README is based on the committed source, not a fresh live API benchmark.

No representative evaluation set, measured educational benefit, independently reproduced latency or verified cost benchmark is supplied here. The existing [token-optimization notes](Rapport/token_optimization.md) are project notes rather than guarantees of current API pricing or runtime performance.

`Source/test_api.py` is an integration diagnostic that calls Anthropic and can download embedding resources. It is not a comprehensive offline test suite. It also prints a prefix of the configured API key; review/redact that logging before running or sharing its output.

## Limitations

- Generated activities require teacher review for correctness, age suitability and relevance.
- Retrieval depends on the documents actually indexed; RAG does not establish factual correctness by itself.
- Fallback content may hide unavailable retrieval or model services unless its status is checked.
- Model availability, provider usage and dependency compatibility vary by environment.
- No production deployment, classroom trial or educational effectiveness study is claimed.

## Repository structure

```text
Source/
  app.py             Streamlit interface
  agents.py          Agents, tasks and model configuration
  rag.py             PDF indexing, embeddings and retrieval
  workflow.py        Orchestration and execution tracing
  pdf_generator.py   Worksheet export
  logger.py          Logging helpers
  test_api.py        Live integration diagnostic
  requirements.txt   Dependencies
Rapport/             Project analysis notes
Video/               Demonstration script
```

The vector database, indexed documents and generated outputs are local runtime artifacts.

## Future improvements

- Lock and test a reproducible Python environment.
- Add offline tests for retrieval, fallback handling and PDF generation.
- Make live, retrieved and fallback-generated content unambiguous throughout the interface.
- Evaluate activities with a documented rubric and teacher feedback.
- Measure latency, token use and cost with an explicit model version and protocol.
- Remove API-key fragments from diagnostic logging.

## Project context

Academic work in multi-agent systems and Generative AI. [Portfolio case study](https://essalhi-oussama.tech/en/projects/primary-teaching-sma).
