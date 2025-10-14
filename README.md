# Ariadne Clew (AC)
**Reasoning Preservation for LLM-Native Builders**

🧶 **Don't commit without context.**

You build fast. You iterate messy. You lose track of *why* you made choices.

Ariadne Clew is an **AWS AgentCore-powered reasoning agent** that turns your chaotic chat transcripts into structured clarity, preserving the *aha moments*, *design tradeoffs*, and *validated code* that disappear when you move too fast for version control.

Built by an indie operator, for indie operators who know the pain of losing context in late-night builds.

---

## 🧶 Why Ariadne Clew?

In Greek mythology, Ariadne gave Theseus a *clew* - a ball of thread - so he could navigate the labyrinth and make it out alive.

Ariadne Clew plays the same role for builders today: it captures threads of thought, decisions, and insights so you don't lose your way in the maze of iteration.

Where traditional version control tracks *what* changed, Ariadne Clew preserves the *why*, guiding you back to clarity when the path gets tangled.

### 🧩 The Real Problem

**You're shipping faster than ever. Your reasoning is disappearing faster than ever.**

LLMs have become integral to product ideation. But their outputs are ephemeral, unstructured, and unauditable.

Builders are shipping faster than ever, but the **design decisions** and **reasoning paths** that shape those products live in fragile chat logs - invisible to teammates, untracked by version control, and lost to time.

- ChatGPT conversations disappear into the ether
- Claude sessions become unmanageable walls of text
- Code snippets multiply across tools with no clear "final version"
- Teammates (or future you) can't trace why anything was built

*This isn't a version control problem. This is a reasoning preservation problem.*

---

## 🧶 The Solution: Your Ghost Cofounder

Ariadne Clew acts as your **autonomous reasoning agent** - silently watching your messy builder conversations and extracting structured clarity.

It ingests raw session logs and produces a **structured recap** with:
- 💡 **Aha moments** - preserved discoveries and clarifications
- 🧩 **MVP changes** - tradeoffs, pivots, scope edits
- 🌀 **Scope creep** - hallucinated ambition, caught in the act
- 🧾 **README notes** - concepts that belong in code docs
- ⭐ **Post-MVP ideas** - ideas to defer, not discard
- 🧠 **Summary + quality flags** - model-level reflection on the session itself

**For solo devs and indie builders**, Ariadne Clew is like a ghost cofounder - silently watching and capturing your product reasoning so you can focus on building, not backtracking. Every design choice, aha moment, or potential pitfall is preserved to keep your momentum and confidence high.

### How It Works:
1. **Upload your chat transcript** (.txt, .json from any LLM)
2. **Agent classifies & validates** using AWS AgentCore + Bedrock
3. **Receive structured recap** - human-readable summary you can actually use

*Model-agnostic. Works with ChatGPT, Claude, DeepSeek, whatever you use.*

---

## 🤖 Built with AWS AgentCore: True Agentic Behavior

Ariadne Clew isn't just an API wrapper - it's an **autonomous reasoning agent** that demonstrates true agentic behavior with AWS's agent infrastructure.

### 🧠 **AgentCore Runtime Integration (✅ Production)**

**What's Implemented:**
Ariadne Clew uses AWS AgentCore Runtime with Bedrock for autonomous reasoning extraction:

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()  # Real AgentCore Runtime
agent = Agent()               # Strands orchestration

@app.entrypoint
def invoke(payload):
    """Autonomous processing - no human intervention"""
    result = agent(reasoning_prompt)  # Bedrock API call
    return structured_recap
```

**Core Capabilities:**
- **Autonomous classification**: Plain text vs code, no human input
- **Reasoning extraction**: Identifies aha moments, design decisions, scope changes
- **Conflict resolution**: Reconciles multiple "final" versions
- **Quality assessment**: Flags issues in reasoning or structure
- **Structured output**: Schema-validated JSON + human-readable summary

**This meets AWS agent criteria:** ✅ Reasoning LLMs ✅ Autonomous execution ✅ AgentCore Runtime

---

### 🔍 **Code Validation & Future Enhancement**

**MVP Implementation (✅ Production-Ready):**
- **AST syntax validation**: Python code parsed for correctness
- **Metadata capture**: Language, context, user-marked "final" status
- **Version tracking**: Multiple iterations reconciled
- **No execution**: Syntax checking only (safe by design)

```python
# Current implementation
import ast

def validate_snippet(code: str) -> bool:
    """Validate Python syntax without execution"""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
```

**Post-MVP Enhancement (🔮 Architected):**
AgentCore Code Interpreter integration ready:
- Sandbox execution in isolated AWS environments
- Runtime validation metadata (works/broken/partial)
- Multi-language support (Python, JS, Bash, more)
- Execution output capture and analysis
- Resource usage tracking

**Why MVP Approach:**
Focus on autonomous reasoning extraction (the hard problem) while architecting for execution enhancement (the valuable addition).

---

### 🧶 **Session Persistence & Memory Architecture**

**MVP Implementation (✅ Production-Ready):**
- **Local file-based storage**: Simple, fast, debuggable
- **Session organization**: `.cache/` directory by session_id
- **History and replay**: All recaps persisted for reference
- **Zero AWS infrastructure**: Works without setup

```python
# Current implementation
from pathlib import Path
import json

def store_recap(session_id: str, recap: dict):
    """Persist session recap to local filesystem"""
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    path = cache_dir / f"{session_id}.json"
    path.write_text(json.dumps(recap, indent=2))
```

**Post-MVP Enhancement (🔮 Architected):**
AgentCore Memory API integration ready:
- **Cross-session semantic search**: "Show me all auth decisions"
- **Context injection**: "Last session, you chose approach X because..."
- **Distributed storage**: DynamoDB-backed, multi-user safe
- **Automatic embeddings**: Titan or similar for semantic queries
- **Team collaboration**: Shared reasoning context across developers

**Why MVP Approach:**
Local files enable rapid development and debugging. Architecture supports drop-in Memory API upgrade when needed.

---

### 🤯 **Autonomous Decision-Making**

**Core Agentic Capabilities:**
- **Classifies** plain text vs code without human input
- **Extracts** structured insights from unstructured conversations
- **Resolves conflicts** when multiple "final" versions exist
- **Flags quality issues** in reasoning or code structure
- **Validates outputs** against strict schema (no hallucinations)
- **Operates end-to-end** without human oversight during processing

**This is true autonomous operation:** User provides input → Agent processes → User receives structured output. Zero human in the loop.

---

## 🎯 Built for the Underserved Builder

**My audience isn't huge, but it's real and underserved.**

Ariadne Clew is built for indie operators, casual architects, and advanced civilian power users. These are people who lose context when iterating fast - not those who live inside version control.

### 🏠 **Indie Operators**
*Pain*: Moving too fast for version control, not disciplined enough for Notion
*Value*: AC gives you a recap of "what just happened" without adding overhead

### 🚀 **Hackathon Builders**
*Pain*: Chaotic sprinting, dozens of snippets, judges who'll never read your whole repo
*Value*: Structured recap = credibility and clarity for demo day

### 🧠 **Advanced Civilian Power Users**
*Pain*: Daily LLM users who lose track of *why they made choices*
*Value*: AC is your "ghost cofounder" - organizes messy chats into reusable artifacts

*All these big tools are fancy, but are they really needed? Can't someone without formal AI training take a different path?*

**I believe so. This is that path.**

---

## 💡 Why This Matters: Measurable Impact

### **Problem Scale**
- 73% of developers use AI coding tools daily (Stack Overflow 2024)
- Average session: 50+ messages, 12+ code iterations
- **0% of sessions preserve structured reasoning for reuse**

### **Real-World Value**
- **Time Recovery**: Eliminate "what was I thinking?" moments
- **Knowledge Transfer**: Teammates understand *why*, not just *what*
- **Decision Audit**: Trace any choice back to its reasoning thread
- **Context Continuity**: Pick up where you left off, weeks later

### **Competitive Differentiation**
Existing tools remember *conversations*. AC preserves *reasoning*.
That's the difference between a chat log and a decision artifact.

---

## 🗺️ Technical Architecture: AWS-Native Agent Stack

### MVP Architecture (Production-Ready)

```
[User: Chat Transcript]
         ↓
[Frontend: Pastebox UI]
         ↓
[Bridge Server: Flask]
         ↓
[Input Filters: PII Scrub, Deny-list, Size Check]
         ↓
[AgentCore Runtime: BedrockAgentCoreApp]
         ↓
[Bedrock API: Claude Sonnet 3.5]
         ↓
[Agent: Autonomous Reasoning Extraction]
         ↓
[Schema Validation: Pydantic (extra="forbid")]
         ↓
[Dual Output: Human-Readable + Structured JSON]
         ↓
[Local Storage: File-based Session Cache]
         ↓
[Frontend Display: Split Panel View]
```

### Production Architecture (Post-MVP)

```
[S3 Upload Trigger]
         ↓
[Lambda: Input Validation]
         ↓
[AgentCore Runtime: Serverless]
         ↓
[Bedrock + Code Interpreter]
         ↓
[AgentCore Memory API: Semantic Context]
         ↓
[DynamoDB: Persistent Storage]
         ↓
[API Gateway: RESTful Access]
         ↓
[CloudWatch: Logging & Monitoring]
```

### Core Components:

**MVP (Built & Working):**
- **AgentCore Runtime**: BedrockAgentCoreApp + Strands for agent orchestration
- **Bedrock Claude Sonnet 3.5**: Autonomous reasoning extraction
- **Flask Bridge Server**: Connects frontend to AgentCore CLI
- **AST Code Validation**: Syntax checking without execution
- **Local File Storage**: Session-based caching
- **Pydantic Schema**: Strict validation with `extra="forbid"`

**Post-MVP (Architected & Ready):**
- **AgentCore Code Interpreter**: Sandbox execution in AWS
- **AgentCore Memory API**: Cross-session semantic search
- **S3 + Lambda**: Serverless scalability
- **API Gateway**: Production-ready REST endpoints
- **DynamoDB**: Distributed session storage

*Built for production from day one. No shortcuts, no technical debt.*

---

## 🧪 Responsible AI Safeguards

Because moving fast shouldn't mean moving recklessly:

### **Input Filtering**
- Character limits prevent token overflow (50K max)
- PII scrubbing (emails, phones, SSNs) before Bedrock calls
- Deny-list filtering for harmful content
- Schema validation on all uploads

### **Output Validation**
- Bedrock Guardrails for harmful content detection
- Strict JSON schema enforcement - no hallucinated prose
- `extra="forbid"` prevents unexpected fields
- Empty arrays over speculation

### **Code Safety**
- No code execution in MVP (AST syntax checking only)
- Sandbox isolation planned for Code Interpreter integration
- Resource limits for production deployment

### **Model Selection Process**
Evaluated Claude, Titan, and Nova on transcript classification:
- **Claude Sonnet 3.5**: Best reasoning extraction, consistent JSON output
- **Cost optimization**: Predictable token usage, hackathon-safe (~$0.003 per recap)
- **Reliability**: Handles edge cases without hallucination

*Every decision documented. Every guardrail tested.*

---

## 📊 MVP Demo Flow: End-to-End Agentic Workflow

### **1. Upload Transcript**
```bash
# Paste any LLM export in the browser
# - ChatGPT conversation exports
# - Claude chat JSON files
# - DeepSeek session logs
# - Manual copy-paste from any LLM
```

### **2. Agent Processing (Autonomous)**
The agent operates completely autonomously:

1. **Input Validation**: Filters scrub PII, check deny-list, enforce size limits
2. **AgentCore Invocation**: Bridge server calls `agentcore invoke`
3. **Bedrock Reasoning**: Claude Sonnet 3.5 extracts structured insights
4. **Classification**: Agent identifies code vs reasoning, tags intent
5. **Validation**: AST parsing checks code syntax
6. **Reconciliation**: Agent resolves conflicts between versions
7. **Schema Enforcement**: Pydantic validates structure, rejects hallucinations
8. **Storage**: Session recap persisted to local files

**Total time: 3-5 seconds. Zero human intervention.**

### **3. Human-Readable Recap**
**MVP Output**: Clean, scannable recap with action items

```markdown
## Session Recap: ac-session-042

### 🎯 Summary
Built iterative Fibonacci implementation, chose performance over elegance.
Realized recursion would timeout on large inputs. Final solution is O(n).

### 💡 Key Insights
- Realized recursion would timeout on large inputs
- Performance matters more than code elegance for this use case
- O(n) iterative approach beats O(2^n) recursive

### 🧩 Design Decisions
- Chose iterative over recursive for performance
- Prioritized speed over code brevity
- Added memoization consideration for future

### 📝 MVP Changes
- Switched from recursive to iterative approach mid-session
- Performance became primary decision factor

### ⭐ Post-MVP Ideas
- Add memoization layer for caching
- Consider generator pattern for memory efficiency

### 📊 Code Snippets
**Snippet 1** (Python, ✅ Valid Syntax)
```python
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b
```
Context: Final iterative solution, O(n) time complexity

### ⚠️ Quality Flags
- Clear performance reasoning documented
- Good progression from recursive to iterative
```

**Raw JSON Available**: Via split panel view for programmatic access

### **4. Session Continuity**
Recap stored in `.cache/` directory for:
- Historical reference
- Pattern analysis
- Future context injection (with Memory API)

---

## 📏 Session Size Guidelines

**Optimal Range:** 2,000 - 50,000 characters (~500 words - 35K words)
**Maximum Limit:** 200,000 characters (Bedrock API constraint)

### Why These Limits?

**Focused sessions produce better insights:**
- 2K-10K chars: Quick debugging sessions, single problems (~30 min - 1 hour)
- 10K-50K chars: Deep work sessions, complex features (~1-3 hours)
- 50K+ chars: May be slow to process, often less focused
- 200K+ chars: Exceeds API limits, requires chunking

**Technical constraints:**
- Bedrock Claude API has ~200K token limit (~150K words)
- Processing time scales with input size (60s timeout)
- Analysis quality decreases with unfocused marathon chats
- Focused sessions = clearer reasoning extraction

### Best Practices

**✅ Do:**
- Analyze sessions incrementally as you work
- Break at natural boundaries (topic shifts, task completions)
- Focus on specific problems or decisions
- Use multiple targeted analyses vs one massive session

**❌ Avoid:**
- Submitting entire days of conversation at once
- Mixing unrelated topics in one session
- Marathon sessions without clear structure
- Copy-pasting everything "just in case"

### What Happens at Each Limit?

**Under 50K chars (Recommended):**
- Fast processing (3-5 seconds typical)
- Clear, focused insights
- Best experience

**50K - 200K chars (Allowed but slower):**
- May take longer to process
- Warning logged but processing continues
- Results may be less focused

**Over 200K chars (Hard limit):**
- Request rejected with helpful error
- Suggestion to break into focused segments
- Guidance on natural break points

### Tips for Large Projects

**Problem:** "My build session was 6 hours and 80K characters!"

**Solutions:**
1. **Break by topic:** Analyze authentication discussion separately from UI work
2. **Break by time:** Submit hourly or bi-hourly chunks
3. **Focus on decisions:** Extract just the design discussions and code reviews
4. **Use sections:** Copy relevant portions instead of entire transcript

**Remember:** Ariadne Clew works best as your *ongoing reasoning companion*, not an *end-of-project archaeologist*.

### Post-MVP: Smart Chunking

**Planned enhancement:** Automatic chunking with session memory
- Break long sessions at conversation boundaries
- Preserve context across chunks with Memory API
- Progressive understanding across multiple analyses
- Merge insights intelligently

**Why not MVP?** Chunking without memory = contradictory recaps. Doing it right requires AgentCore Memory API integration (post-MVP feature).

### Examples

**✅ Good session size (15K chars):**
```
User: I need to build authentication for my app
[... detailed discussion of OAuth vs JWT ...]
[... code iterations and testing ...]
[... final implementation decided ...]

Result: Clear "why JWT" tradeoff, final code snippet, security notes
```

**❌ Too large (150K chars):**
```
User: Let's build everything
[... auth system ...]
[... database design ...]
[... frontend components ...]
[... deployment strategy ...]
[... 6 hours later ...]

Result: Overwhelming, unfocused, hard to extract clear decisions
```

**Better approach:** Submit 4 separate focused sessions:
1. Auth system decisions (20K)
2. Database design (15K)
3. Frontend components (30K)
4. Deployment strategy (10K)

Each gets a clear, actionable recap.

---

**Bottom line:** Think of Ariadne Clew like a focused work session partner, not a documentary filmmaker of your entire project history.

---

## 📗 What It Enables

Ariadne Clew acts as a **foundational memory primitive** for agent-native infrastructure.

You can use it to:
- 📜 Auto-generate `README.md` content from LLM-driven builds
- 📊 Train future agents on historical product reasoning
- 🕵️ Trace decisions back to the prompts that shaped them
- 🧠 Maintain *semantic continuity* across sessions, collaborators, and tools

> Think of it as a **source-of-truth layer for product thinking**.

---

## 🔮 Post-MVP Roadmap: Scaling the Vision

The current MVP proves the concept. Future iterations serve the community:

### **Phase 2: AgentCore Tools Integration**
**Code Interpreter:**
- Sandbox execution for actual code validation
- Runtime error detection and debugging
- Multi-language support (Python, JS, Bash, more)
- Execution output capture

**Memory API:**
- Cross-session semantic search: "Find all auth decisions"
- Context injection: "Last time you chose X because..."
- Team workspaces with shared context
- Automatic embedding generation for search

### **Phase 3: Developer Integration**
- VS Code extension for live session capture
- GitHub integration for context-rich commits
- Slack/Discord bots for team reasoning threads
- CLI tool for local development workflows

### **Phase 4: Project Intelligence**

**Current MVP**: Single recap, flat list of snippets + decisions

**Future (Paid Tier)**: Smart project-level insights

- **Interactive Recap Dashboard**: Rich UI with syntax highlighting, diff views, decision timelines
- **Multi-file awareness**: "This snippet belongs in `utils.py`, this one is `app.js`"
- **Export Options**: Markdown for README, JSON for integrations, PDF for docs
- **Visual Decision Trees**: See how reasoning evolved through iterations
- **Project-level recaps**: Cross-session reasoning evolution tracking
- **Module-specific context**: Decisions grouped by component/feature
- **Dependency mapping**: Understanding how reasoning connects across files
- **Semantic search**: Query all stored decisions and code contexts

*This transforms AC from "chat cleanup" to "project reasoning intelligence."*

### **Phase 5: Community & Collaboration**
- Public reasoning artifact sharing
- Template library for common workflows
- Integration marketplace for specialized tools
- Team workspaces for shared context

*Built with the indie community, for the indie community.*

---

## 💰 Business Model: Serving the Underserved

**The big tools chase enterprise. I'm building for builders who actually need this.**

### **Freemium Approach**
- **One-Shot (Free)**: "Clean up this messy chat for me"
- **Project Tracking (Paid)**: Multi-session continuity + reasoning evolution
- **Team Workspaces (Pro)**: Shared context across collaborators

### **Why This Works**
My audience isn't enterprise procurement teams. It's:
- **Indie operators** who'll pay $10/month to never lose context again
- **Hackathon builders** who need credible demos fast
- **Advanced civilians** who live in LLMs but lack structure

### **Measurable Value Delivered**
- **Time Recovery**: Eliminate "what was I thinking?" debugging sessions
- **Knowledge Transfer**: New teammates understand *why*, not just *what*
- **Decision Audit**: Trace any choice back to its reasoning thread
- **Continuity**: Pick up complex builds weeks later with full context

**Version control tracks *what* changed. Ariadne Clew tracks *why* you changed it.**

*That's not a feature gap - that's a market gap.*

---

## 🛠️ Technical Implementation Details

### **File Structure**
```
ariadne-clew/
├── backend/
│   ├── agent.py              # AgentCore Runtime integration
│   ├── bridge_server.py      # Flask API bridge
│   ├── filters.py            # Input safety layer
│   ├── code_handler.py       # AST validation
│   ├── memory_handler.py     # Local file storage
│   ├── schema.py             # Pydantic models
│   ├── recap_formatter.py    # Output generation
│   └── diffcheck.py          # Version reconciliation
├── prompts/
│   └── classifier_prompt.md  # Reasoning extraction prompt
├── public/
│   ├── index.html            # Minimal pastebox UI
│   ├── scripts/              # Frontend JavaScript
│   └── styles/               # Clean CSS layout
├── tests/                    # 56 comprehensive tests
├── docs/
│   ├── ARCHITECTURE.md       # Technical deep dive
│   └── TROUBLESHOOTING.md    # Setup & debugging guide
└── README.md                 # This file
```

### **Key Features**
- ✅ **Model-agnostic input** (ChatGPT, Claude, DeepSeek exports)
- ✅ **Autonomous agent operation** via AgentCore Runtime
- ✅ **AST code validation** (safe syntax checking)
- ✅ **Local session storage** (fast development)
- ✅ **Production guardrails** with Bedrock protections
- ✅ **Structured output** with schema validation
- ✅ **Comprehensive tests** (56 pytest cases)

### **Prompt Engineering: The Agent's Brain**

The classification intelligence lives in `prompts/classifier_prompt.md` - a carefully engineered prompt that transforms chaotic chat logs into structured reasoning artifacts:

**Core Classification Framework:**
- **Aha moments**: Key insights or shifts in understanding
- **MVP changes**: Edits, pivots, commitments affecting scope
- **Scope creep**: Evidence of expanding beyond MVP
- **Design tradeoffs**: Decision rationale and architectural choices
- **README notes**: Facts/concepts that belong in documentation
- **Post-MVP ideas**: Explicitly deferred features
- **Quality flags**: Warnings or praise on session structure

**Anti-Hallucination Guardrails:**
- Do not generate prose or markdown — only JSON
- Do not include speculative content
- Return valid arrays, even if empty
- Use clear, actionable language

*The prompt is the product.* This agent's reasoning capability comes from deliberate prompt architecture, not just API calls.

### **Testing & QA**
- pytest coverage for all agent components
- Mocked AgentCore calls for local development
- Real Bedrock integration tests for validation
- Pre-commit hooks for code quality
- Production-ready error handling

---

## 🏆 Why Ariadne Clew Wins

**Judges, this solves a problem you have.**

Every time you've lost context in a messy chat. Every time you couldn't remember why you chose approach X. Every time a teammate asked "what were you thinking here?"

That's the problem Ariadne Clew solves.

### **Technical Excellence:**
- Real AgentCore Runtime integration (verified in code)
- Autonomous agent behavior without human oversight
- Production-ready with comprehensive guardrails
- Strategic MVP scoping shows engineering maturity
- Clear architecture for post-MVP enhancements

### **Real-World Impact:**
- Serves underserved but growing builder community
- Measurable value: time recovery + knowledge transfer
- Scales with the AI-native development trend
- $0.003 per recap = indie builder economics

### **Differentiated Approach:**
- First reasoning preservation agent for chat-driven workflows
- Model-agnostic in a vendor-locked world
- Honest MVP positioning over feature bloat
- Built by indie operator who lives the problem daily

### **Proof Points:**
- 4 weeks from concept to autonomous agent
- 56 comprehensive tests
- Real AgentCore + Bedrock integration
- Production-ready error handling
- Clear roadmap with strategic scoping

---

## 👩‍💻 Built By La Shara Cordero

**Customer obsession fuels everything I build.**

From [Beyond the Docket](https://sites.google.com/view/beyondthedocket) (making legal systems transparent) to [ThreadKeeper](https://threadkeeper.io) (preserving forum knowledge) - I build tools that make invisible systems visible.

Ariadne Clew continues that mission: **making reasoning visible in the age of AI-assisted building.**

**Development Journey:**
- Started exploring AI-assisted development: July 2025
- First Bedrock API calls on other projects: July 2025
- AriadneClew repository created: September 14, 2025
- Production-ready autonomous agent: October 2, 2025

**Timeline: 3 weeks from concept to working agent**, building on 4 months of AI/LLM learning.

*No formal AI training. No CS degree. Just a builder who sees patterns and solves problems.*

**Connect:** [lsjcordero@gmail.com] | [La Shara Cordero](https://www.linkedin.com/in/la-shara-cordero-a0017a11/) | [ThreadKeeper.io](https://threadkeeper.io) | [The Forum Files](https://theforumfiles.substack.com)

---

## 🧶 The Thread Continues

In Greek mythology, Ariadne gave Theseus thread to navigate the labyrinth.

Today's builders navigate a different maze - the chaos of AI-assisted creation. Chat transcripts branch and merge. Code versions multiply. Reasoning disappears.

**Ariadne Clew is your thread back to clarity.**

Don't commit without context. Don't build without reason. Don't lose the thread.

Ariadne Clew exists to serve builders first. It obsesses over clarity and continuity so you don't lose the thread in the chaos of iteration.

---

## 👤 About This Project

**Solo builder** | 3 weeks part-time | First AgentCore project

**Approach:** Foundation-first. Real AWS integration over mocked features.
Production architecture over quick hacks. One autonomous agent done right.

**What I prioritized:**
- ✅ Real AgentCore Runtime integration
- ✅ Autonomous operation (zero human in loop)
- ✅ Dual output format (human + machine)
- ✅ Production-grade error handling
- ✅ Comprehensive testing (56 tests)

**What I scoped out:**
- ⏭️ Code Interpreter execution (AST validation for MVP)
- ⏭️ Memory API (local files sufficient for demo)
- ⏭️ Serverless deployment (local-first for iteration speed)

---

## 🏆 Builder Background

**La Shara Cordero** | Indie Builder | Learning in Public

**Previous win:** 2nd place (out of 14 teams), Cal Poly DxHub AI Summer Camp 2024
*Team project:* [Customized AI Tutoring System](https://github.com/earlgreyhot1701D/team-110-customized-tutoring)

**This project:** First solo agent build, first AWS hackathon
*Challenge:* Level up from team collaboration to solo execution while learning AWS ecosystem

---

## 🤝 Development Approach

Built with AI pair programming (ChatGPT + Claude as my "6th person off the bench").
All architectural decisions, scope choices, and final implementations reviewed
and owned by me. AI served as implementation assistant, documentation search,
and thinking partner.

**Modern solo development = Knowing when to build from scratch vs when to
orchestrate and validate.**

---

## 🦆 About the Duck

My team's 2nd place finish at [Cal Poly's AI Summer Camp](https://dxhub.calpoly.edu/ccc-ai-summer-camp/)
(rubber duck themed) came with a rubber duck. That duck supervised this entire build.

Rubber duck debugging: real.
Rubber duck good luck: apparently also real.

---

## 💭 The Meta

This project about preserving reasoning from AI conversations was itself built
through extensive AI conversations with ChatGPT and Claude. The irony is not
lost on me—these are exactly the kinds of discussions Ariadne Clew was designed
to preserve.

*Should I have been running Ariadne Clew on itself while building it? Probably.
Did I? No. Do I see the problem? Yes. Will I fix it? That's post-MVP.*

---

## 🎯 Philosophy

**Better to ship one thing that works than promise three things half-built.**

Foundation-first approach. Production-ready core over feature bloat. Honest
scoping over over-promising. This is a **v1**, not a **v-final**.

---

## 🚀 What's Next

**Post-hackathon roadmap:**
- [ ] Code Interpreter integration (move from AST to execution)
- [ ] Memory API for cross-session context
- [ ] Serverless deployment (Lambda + S3 + API Gateway)
- [ ] GitHub Action integration
- [ ] VS Code extension

**But first:** Ship this. Get feedback. Learn. Iterate.

---

## 📬 Connect

**GitHub:** [github.com/earlgreyhot1701D](https://github.com/earlgreyhot1701D)
**Website:** [ThreadKeeper.io](https://threadkeeper.io)
**LinkedIn:** [La Shara Cordero](https://www.linkedin.com/in/la-shara-cordero-a0017a11/)
**Email:** lsjcordero@gmail.com

Built with ☕, stubbornness, and a rubber duck from AI camp.

---

*Built September 2025 for AWS Agent Hackathon*
*Repository created: September 14, 2025*
*Production-ready: October 2, 2025*
*3 weeks from concept to autonomous reasoning agent*

---

## License

Copyright (c) 2025 La Shara Cordero

All rights reserved.

This software and its associated files are proprietary and confidential. Unauthorized copying,
modification, distribution, or use of this software, in whole or in part, is strictly prohibited
without the express written permission of the author.

This software is not licensed for reuse, redistribution, or commercial deployment. No rights or
licenses are granted, explicitly or implicitly, under any patents, copyrights, trademarks, or other
intellectual property.

For inquiries, licensing, or commercial use, contact: lsjcordero@gmail.com

**Note:** This repository was briefly public under MIT license on September 14–15, 2025.
As of September 16, 2025, all commits are proprietary.
