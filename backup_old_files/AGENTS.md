# AGENTS.md: Ariadne Clew

This file provides persistent context and conventions for AI agents that work in this repo. It keeps code, tests, and docs consistent, safe, and compliant with AWS Agent Hackathon rules.

---

## 🧵 Core Identity

- **Project**: Ariadne Clew (AC)
- **Mission**: Preserve reasoning from messy chat-driven developer workflows.
- **Tagline**: "Git tracks what changed. AC tracks why."
- **Hackathon Context**: Production runs and demos must use **Amazon Bedrock LLMs with AgentCore**, plus at least one AWS service such as Lambda or S3. Any outside assistant may only be used for offline refactoring, test generation, or documentation drafts.

---

## 🔑 Key Concepts

- **Final Snippet**: last validated code block, parsed by the Python AST and validated against schema rules.
- **Rejected Versions**: invalid or abandoned snippets, with reasons logged.
- **Aha Moments**: breakthrough insights extracted from transcripts.
- **Recap**: dual-output artifact, JSON plus a human readable summary.
- **Pipeline**: `filters → classifier → code_handler (AST) → diff → recap_formatter → memory`.

---

## ⚖️ Guardrails and Safety Rules

- **Execution**: do not call `exec()`. Use AST parsing and controlled evaluation only.
- **Input Size**: reject inputs above 100000 characters, about 20k tokens.
- **Deny Terms**: `password`, `api_key`, `rm -rf /`, `BEGIN RSA PRIVATE KEY`.
- **PII Scrubbing**: redact emails and phone numbers on ingest.
- **Schema Enforcement**: all recap outputs must validate against `schema.py`.
- **Logging**: use `logging_setup.py`. Do not log raw transcripts or secrets.

---

## 🏗️ File and Module Conventions

- **api_recap.py**: pipeline entry point.
- **filters.py**: deny list, PII scrub, input size guard.
- **classifier.py**: separates plain text and code, tags code intent.
- **code_handler.py**: AST parsing and code validation.
- **diffcheck.py**: reconciles multiple snippet versions.
- **recap_formatter.py**: produces JSON and human readable recap.
- **memory_handler.py**: AgentCore memory, schema aligned.
- **schema.py**: Pydantic schema with `extra = "forbid"`.
- **logging_setup.py**: central logging config.
- **tests/**: pytest coverage for filters, classifier edges, and end to end recap.

Directory suggestions:

- **/prompts/**: `system_prompt.md` and any model context files.
- **/configs/**: model and AgentCore configuration if needed.

---

## 🎨 Output Requirements

- **JSON recap fields**: `session_id`, `final`, `rejected_versions`, `aha_moments`, `summary`, `quality_flags`.
- **Human recap headings**:
  - 📌 What You Built
  - ❌ Rejected Versions
  - 💡 Why This Version
  - 📝 Aha Moments
  - 📊 Status
- **Empty over Wrong**: prefer empty fields to speculation or hallucination.

---

## 🤖 Agent Behaviors

- Apply **filters** before classification.
- Load **AGENTS.md** as context before generating or editing code.
- **Default model**: Claude Sonnet on Bedrock. **Fallbacks**: Nova or Titan, with schema validation.
- For recap, preserve reasoning verbatim. Only summarize when the schema requires it.
- For memory, prefer AgentCore Memory. A local dictionary is acceptable as a fallback only.

---

## 🧪 Testing Expectations

- `tests/test_filters.py`: size limits, deny terms, PII scrub.
- `tests/test_classifier_edges.py`: tricky fences and escaped backticks.
- `tests/test_e2e_recap.py`: happy path, oversized input rejection, unsafe term rejection.

---

## 📝 Style Notes

- **Tone**: indie operator, hackathon builder, cheeky yet clear.
- **Docs**: function docstrings required. Inline prose should be minimal.
- **Schema**: Pydantic with `extra = "forbid"`.

---

## 📍 Placement

- Place **AGENTS.md** at the repo root so every tool and human can find it.
- Place **system_prompt.md** in `/prompts/`. Reference it from AgentCore configuration.
