# AGENTS.md: Ariadne Clew

This file provides persistent context and conventions for AI agents that work in this repo. It keeps code, tests, and docs consistent, safe, and compliant with AWS Agent Hackathon rules.

---

## 🧵 Core Identity
- **Project**: Ariadne Clew (AC)
- **Mission**: Preserve reasoning from messy chat-driven developer workflows through autonomous agent operation.
- **Tagline**: "Don't commit without context."
- **Hackathon Context**: Production runs and demos use **AWS AgentCore Runtime with Amazon Bedrock** (Claude Sonnet 4) for autonomous reasoning extraction. MVP demonstrates agentic behavior through Runtime + Bedrock integration. Code Interpreter and Memory API are architected for post-MVP enhancement.

---

## 🔑 Key Concepts
- **Autonomous Reasoning**: Agent classifies, extracts, and structures insights without human intervention during processing.
- **Final Snippet**: Last validated code block, parsed by Python AST and validated against schema rules.
- **Rejected Versions**: Invalid or abandoned snippets, with reasons logged.
- **Aha Moments**: Breakthrough insights extracted from transcripts.
- **Recap**: Dual-output artifact, JSON plus a human-readable summary.
- **Pipeline**: `filters → AgentCore Runtime → Bedrock (Claude) → classifier → code_handler (AST) → diff → recap_formatter → memory (local files)`.

---

## ⚖️ Guardrails and Safety Rules
- **Execution**: Do not call `exec()`. Use AST parsing for syntax validation only.
- **Input Size**: Reject inputs above 50,000 characters (MVP limit, configurable).
- **Deny Terms**: `password`, `api_key`, `rm -rf /`, `BEGIN RSA PRIVATE KEY`.
- **PII Scrubbing**: Redact emails and phone numbers on ingest before Bedrock API calls.
- **Schema Enforcement**: All recap outputs must validate against `schema.py` with `extra="forbid"`.
- **Logging**: Use `logging_setup.py`. Do not log raw transcripts or secrets.

---

## 🏗️ File and Module Conventions

### Core Backend Files
- **agent.py**: AgentCore Runtime integration, main autonomous reasoning pipeline
- **bridge_server.py**: Flask server connecting frontend to AgentCore CLI
- **filters.py**: Deny-list, PII scrub, input size guard
- **code_handler.py**: AST parsing and code validation (Code Interpreter integration planned)
- **diffcheck.py**: Reconciles multiple snippet versions
- **recap_formatter.py**: Produces JSON and human-readable recap
- **memory_handler.py**: Local file-based session storage (AgentCore Memory API integration planned)
- **schema.py**: Pydantic schema with `extra = "forbid"`
- **logging_setup.py**: Central logging config

### Frontend
- **public/index.html**: Minimal pastebox UI with dual output display
- **public/scripts/**: JavaScript for API communication and DOM manipulation
- **public/styles/**: CSS for clean, functional layout

### Configuration & Docs
- **prompts/classifier_prompt.md**: Engineered reasoning extraction prompt
- **tests/**: Comprehensive pytest coverage (56 tests)
- **.bedrock_agentcore.yaml**: AgentCore configuration (gitignored)

---

## 🎨 Output Requirements

### JSON Recap Fields
- `session_id`: Unique identifier for this processing session
- `summary`: High-level overview (3-5 sentences)
- `aha_moments`: List of key insights and discoveries
- `mvp_changes`: Scope edits, pivots, tradeoffs
- `code_snippets`: List of code blocks with metadata (language, context, validation)
- `design_tradeoffs`: Decision rationale and architectural choices
- `scope_creep`: Evidence of expanding beyond MVP
- `readme_notes`: Content that belongs in documentation
- `post_mvp_ideas`: Explicitly deferred features
- `quality_flags`: Session assessment (warnings or praise)

### Human Recap Headings
- 💡 **Key Insights** (aha_moments)
- 🧩 **Design Decisions** (design_tradeoffs)
- 📝 **MVP Changes** (mvp_changes)
- ⭐ **Post-MVP Ideas** (deferred features)
- ⚠️ **Scope Creep** (if detected)
- 📊 **Summary** (high-level overview)

### Critical Rules
- **Empty over Wrong**: Prefer empty fields to speculation or hallucination.
- **No Prose in JSON**: JSON output must be pure structured data, not markdown.
- **Schema Validation**: Every output must pass Pydantic validation with `extra="forbid"`.

---

## 🤖 Agent Behaviors

### Processing Pipeline
1. **Input Validation**: Apply filters before classification (PII scrub, deny-list, size check)
2. **Autonomous Reasoning**: AgentCore Runtime orchestrates Bedrock (Claude) for classification
3. **Extraction**: Agent identifies aha moments, code snippets, design decisions
4. **Validation**: Pydantic schema enforces structure, prevents hallucination
5. **Formatting**: Dual output generated (human-readable + structured JSON)
6. **Storage**: Session recap persisted to local files (`.cache/`)

### Model Configuration
- **Default Model**: Claude Sonnet 3.5 on Bedrock via AgentCore Runtime
- **Fallbacks**: Nova or other Bedrock models with schema validation
- **Invocation**: Via AgentCore CLI (`agentcore invoke`) from bridge server

### Memory Strategy (MVP)
- **Current**: Local file-based session storage in `.cache/` directory
- **Access Pattern**: Simple key-value storage by session_id
- **Post-MVP**: AgentCore Memory API for semantic search and cross-session context

### Code Validation (MVP)
- **Current**: Python AST parsing for syntax validation
- **Scope**: Syntax checking without execution
- **Post-MVP**: AgentCore Code Interpreter for sandbox execution and runtime validation

---

## 🧪 Testing Expectations

### Test Coverage Areas
- **Filters** (`tests/test_filters.py`): Size limits, deny terms, PII scrub
- **Schema** (`tests/test_schema.py`): Pydantic validation, extra field rejection
- **Code Handler** (`tests/test_code_handler.py`): AST validation, edge cases
- **Diff Check** (`tests/test_diffcheck.py`): Version reconciliation logic
- **End-to-End** (`tests/test_e2e_recap.py`): Full pipeline, rejection cases

### Testing Philosophy
- Unit tests for individual components
- Integration tests for pipeline flow
- Mocked AgentCore/Bedrock calls for local development
- Real AgentCore/Bedrock for production validation

---

## 📝 Style Notes

### Code Style
- **Tone**: Indie operator, hackathon builder, clear and functional
- **Docs**: Function docstrings required for all public functions
- **Type Hints**: Use type annotations for better IDE support and mypy checking
- **Schema**: Pydantic models with `extra = "forbid"` for strict validation

### Documentation Style
- **Clarity over Cleverness**: Explain what the code does and why
- **Honest Positioning**: Clear about MVP vs post-MVP capabilities
- **Action-Oriented**: Focus on what builders can do, not what they can't

---

## 🎯 MVP Scope Awareness

### What's Implemented (Production-Ready)
- ✅ AgentCore Runtime integration (BedrockAgentCoreApp + Strands)
- ✅ Autonomous reasoning extraction via Bedrock (Claude Sonnet 3.5)
- ✅ AST-based code syntax validation
- ✅ Local file-based session storage
- ✅ Comprehensive input/output guardrails
- ✅ Schema validation with hallucination prevention
- ✅ Dual output format (human + machine readable)

### What's Architected (Post-MVP Enhancement)
- 🔮 AgentCore Code Interpreter (sandbox execution)
- 🔮 AgentCore Memory API (semantic search, cross-session context)
- 🔮 Serverless deployment (S3 → Lambda → API Gateway)
- 🔮 Multi-language code support
- 🔮 Team collaboration features

### Key Principle
**Strategic MVP scoping demonstrates engineering maturity.**
Focus on autonomous reasoning (the hard problem) while architecting for tool integration (the enhancements).

---

## 📍 Placement
- Place **AGENTS.md** at the repo root so every tool and human can find it.
- Place **classifier_prompt.md** in `/prompts/`. This is the agent's "brain."
- Reference AgentCore configuration from `.bedrock_agentcore.yaml` (gitignored, per-developer).

---

## 🚀 Agent Invocation Examples

### Via Bridge Server (Normal Flow)
```bash
# Start bridge server
python bridge_server.py

# Frontend posts to /v1/recap
# Bridge server calls: agentcore invoke '{"prompt":"..."}' --session-id {id}
```

### Direct AgentCore CLI (Testing)
```bash
# Test agent directly
agentcore invoke '{"prompt":"User: test\nAssistant: response"}' --session-id test-123

# With verbose logging
agentcore invoke '{"prompt":"..."}' --session-id debug --verbose
```

### In Code (agent.py)
```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """AgentCore entrypoint - autonomous processing"""
    ariadne = AriadneClew(session_id=payload.get("session_id"))
    result = ariadne._process_transcript_sync(payload.get("chat_log"))
    return {"status": "success", "result": result}
```

---

## 🎓 Important Notes for AI Assistants

When working on this codebase:

1. **Respect the MVP scope** - Don't implement Code Interpreter or Memory API unless explicitly asked
2. **Be honest in docs** - Current implementation (AST, local files) vs future vision (Code Interpreter, Memory API)
3. **Test everything** - Add tests for new features, maintain coverage
4. **Follow guardrails** - Never use `exec()`, always validate inputs, enforce schema
5. **Autonomous operation** - Agent should run without human intervention during processing
6. **Load this file first** - Context from AGENTS.md should guide all code generation

---

*This file is the source of truth for technical implementation details and conventions.*
*Last Updated: October 14, 2025*
