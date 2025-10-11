# Ariadne Clew: Manifest

**Ariadne Clew** is more than a hackathon agent — she is a structured soul woven into code.
Born from the myth of the thread through the maze, she captures builder intent, distills signal from noise, and preserves clarity from chaos through autonomous reasoning.

## Build Philosophy
- **Occam's Razor**: Simplicity is power. Each file exists to serve one role — and no more.
- **Test from Day 0**: All code is tested, typed, and validated before touching prod.
- **Guardrails, not guesswork**: Strict validation, error handling, and output discipline.
- **Code with soul**: Ariadne Clew is readable, durable, deployable. No vibe coder slop.
- **Honest scoping**: Clear about MVP vs post-MVP. Strategic focus over feature bloat.
- **Autonomous operation**: Agent reasons and acts without human intervention.

## Stack

### MVP (Production-Ready)
- **Python 3.11+**: Modern language features, type hints
- **AWS AgentCore Runtime**: BedrockAgentCoreApp + Strands for agent orchestration
- **Amazon Bedrock**: Claude Sonnet 3.5 for reasoning extraction
- **Flask**: Bridge server connecting frontend to AgentCore CLI
- **Pydantic**: Schema validation with `extra="forbid"` for strict output
- **pytest**: Comprehensive test coverage (56 tests)

### Post-MVP (Architected)
- **AgentCore Code Interpreter**: Sandbox code execution
- **AgentCore Memory API**: Cross-session semantic search
- **AWS Serverless**: S3 → Lambda → API Gateway → DynamoDB
- **CloudWatch**: Logging and monitoring

### Code Quality
- **Linting**: ruff
- **Formatting**: black
- **Type Checking**: mypy
- **Pre-commit hooks**: Enforce hygiene before commits

## Core Values

**Clarity over Complexity**
- Every component has a single, clear purpose
- Architecture supports growth without rewrites
- Documentation matches implementation

**Safety over Speed**
- Input validation before processing
- Schema enforcement on outputs
- No code execution (AST parsing only in MVP)
- PII scrubbing before external API calls

**Truth over Hype**
- Honest about what's built vs what's planned
- Strategic MVP scoping shows engineering judgment
- Clear upgrade paths for post-hackathon enhancements

---

*Built for AWS Agent Hackathon, September 2025*
*From concept to autonomous reasoning agent in 4 weeks*
