# 🧶 Ariadne Clew – MVP Roadmap (Hackathon Lock)

This file hardcodes the MVP scope for the AWS Agent Hackathon.
It exists to prevent scope creep and keep development focused on delivering a working, reproducible, well-architected demo by **October 20, 2025**.

---

## ✅ MVP Definition

**Core Pipeline**
- Input → pastebox UI (`index.html`) → filters → classifier → code_handler (AST) → diff → recap_formatter → memory
- Output = dual recap (JSON + human-readable) rendered in-browser (`#humanOutput` + `#jsonOutput`)
- UI = minimal but polished pastebox: labeled input, single submit button,
and dual output panels (human-readable + raw JSON).

**Guardrails**
- Replace `exec()` with AST parse
- Input length guard (100,000 chars)
- Deny terms: `password`, `api_key`, `rm -rf /`, `BEGIN RSA PRIVATE KEY`
- PII scrub (emails + phone numbers)
- Schema enforcement with `extra="forbid"`

**Docs & Logging**
- JSON logging with `request_id` (no raw transcripts)
- Minimal unit tests (smoke coverage only) included in MVP
- Full coverage test suite explicitly post-MVP
- README.md updated to show AWS integration + safety
- PRE_PROD_FIXES.md kept current
- docs/model_eval.md with Claude vs Nova quick table

**AWS Integration (MVP)**
- **AgentCore Runtime**: BedrockAgentCoreApp + Strands agents for orchestration
- **Bedrock Model**: Claude Sonnet 4 for reasoning extraction
- **Code Validation**: AST syntax parsing (Python-specific)
- **Session Storage**: Local file-based caching (`.cache/` directory)
- **Safety**: Input filters (PII scrub, deny-list, size limits)
- **Demo Architecture**: Flask bridge server → `agentcore invoke` → Frontend display

**Production Path (Post-MVP)**
- S3 upload trigger → Lambda function → AgentCore SDK → API Gateway
- AgentCore Code Interpreter for sandbox execution
- AgentCore Memory API for cross-session context
- DynamoDB for distributed session storage

---

## 🚫 Explicitly Out of MVP

These items are deferred until after the hackathon. They should **not** be built before October 20.

- Classifier prompt exemplars (only single baseline prompt used in MVP)
- Advanced frontend polish (animations, styled split view, downloads). MVP requires only clean layout and clear labeling.
- Reasoning trace logs (AC_TRACE)
- AgentCore Memory API integration (MVP uses local file-based session storage)
- AgentCore Code Interpreter integration (MVP uses AST syntax validation)
- VS Code extension, GitHub enrichment, semantic search, team collaboration
- Full coverage unit test suite
- Production serverless deployment (S3/Lambda/API Gateway)

---

## 🔮 Post-MVP Roadmap Notes

- **Classifier Prompt Exemplars**: Add to improve classification robustness.
- **Frontend Display**: Future versions may style dual output with tabs/split view.
- **Trace Logs (AC_TRACE)**: Implemented but off by default; highlight later as a transparency feature.
- **Memory Layer**: Switch from local file storage to AgentCore Memory API for true cross-session persistence with semantic search.
- **Code Execution**: Integrate AgentCore Code Interpreter for sandbox validation beyond AST syntax checking.
- **Expanded Testing**: Move from smoke/unit tests to full coverage suite across all modules.
- **Production Deployment**: Move from local bridge server to serverless (S3 → Lambda → API Gateway).

---

## 🏁 Hackathon Delivery Criteria

- End-to-end pipeline runs from transcript to recap in the browser
- No unsafe code execution (AST validation only)
- Inputs >100k chars rejected
- Guardrails scrub PII and deny dangerous terms
- Schema validates every recap
- Judges see dual output: structured JSON + scannable builder recap
- Autonomous agent operation (no human intervention during processing)
- AgentCore Runtime + Bedrock demonstrating true agentic behavior

---

## 🎯 MVP Scope Discipline

**What Makes This MVP:**
- **Working**: Full pipeline from chat transcript to structured recap
- **Safe**: Comprehensive guardrails and validation
- **Autonomous**: Agent operates without human oversight
- **Honest**: Clear about what's implemented vs architected

**What Makes This Production-Ready:**
- Clean architecture supporting future tool integration
- Comprehensive test coverage (56 tests)
- Production error handling and logging
- Clear upgrade paths documented

**Strategic Scoping:**
MVP focuses on the hard problem (autonomous reasoning extraction) while architecting for enhancement (Code Interpreter, Memory API, serverless deployment).

---

*This file is the single source of truth for MVP scope. Anything outside of it is post-hackathon work.*
