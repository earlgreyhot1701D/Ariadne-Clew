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

Ariadne Clew isn't just an API wrapper - it's a **reasoning agent** that demonstrates autonomous decision-making with AWS's latest agent infrastructure:

### 🧠 **AgentCore Code Interpreter Integration**
The AgentCore Code Interpreter allows AI agents to write, execute, and debug code securely in sandbox environments, enabling AC to:
- **Validate code snippets** in isolated sandboxes
- **Execute and test** candidate solutions
- **Generate validation metadata** (works/broken/partial)
- **Reconcile conflicts** between "user says final" vs "actually validates"

**For the hackathon MVP**, AgentCore Code Interpreter validates snippets found in chats - showing developers what actually runs and surfacing conflicts with their declared "finals."

### 🧶 **AgentCore Memory Integration**
- **Persists reasoning context** across sessions
- **Recalls previous decisions**: *"Last session, you validated Snippet 3 as final"*
- **Maintains session continuity** without heavyweight project management

**AgentCore Memory is used lightly** to persist chosen baselines across sessions, laying the groundwork for long-term project recaps.

### 🤯 **Autonomous Decision-Making**
- **Classifies** plain text vs code without human input
- **Resolves conflicts** when multiple "final" versions exist
- **Flags quality issues** in reasoning or code structure
- **Updates memory** based on validation outcomes

**This meets AWS agent criteria:** ✅ Reasoning LLMs ✅ Autonomous execution ✅ Tool integration

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

## 🏗️ Technical Architecture: AWS-Native Agent Stack

```
[Chat Transcript]
    ↓
[S3 Trigger] → [Lambda Classifier]
    ↓
[Bedrock LLM] → Classify content → Structure reasoning
    ↓
[AgentCore Code Interpreter] → Validate snippets → Generate metadata
    ↓
[AgentCore Memory] → Store final decisions → Enable session continuity
    ↓
[API Gateway] ← [Human-Readable Recap]
```

### Core Components:
- **Bedrock Claude/Nova** for content classification and reasoning extraction
- **AgentCore Code Interpreter** for secure code validation in sandboxed environments
- **AgentCore Memory** for cross-session reasoning persistence
- **S3 + Lambda** for scalable document processing
- **API Gateway** for clean integration points

*Built for production from day one. No shortcuts, no technical debt.*

### MVP Scope Lock
To ensure focus and reproducibility, MVP scope is frozen in [MVP_ROADMAP.md](./MVP_ROADMAP.md).
Inspect it directly:
```bash
cat MVP_ROADMAP.md
```

**Note:** For the MVP, AgentCore Memory is used only to persist the chosen final snippet across sessions.
Full memory features (multi-session reasoning threads, advanced recall) are post-MVP.

---

## 🧪 Responsible AI Safeguards

Because moving fast shouldn't mean moving recklessly:

### **Input Filtering**
- Character limits prevent token overflow
- PII scrubbing (emails, phones, SSNs)
- Deny-list filtering for harmful content
- Schema validation on all uploads

### **Output Validation**
- Bedrock Guardrails with sub-second latency for harmful content detection
- Strict JSON schema enforcement - no hallucinated prose
- Confidence thresholds for factual grounding
- Empty fields over speculation

### **Model Selection Process**
Evaluated Claude, Titan, and Nova on transcript classification:
- **Claude Sonnet**: Best reasoning extraction, consistent JSON output
- **Cost optimization**: Predictable token usage, hackathon-safe
- **Reliability**: Handles edge cases without hallucination

*Every decision documented. Every guardrail tested.*

---

## 📊 MVP Demo Flow: End-to-End Agentic Workflow

### **1. Upload Transcript**
```bash
# Any LLM export works
curl -X POST /upload \
  -F "file=@my_chatgpt_session.txt"
```

### **2. Agent Processing (Autonomous)**
- **Classifier**: Bedrock LLM extracts code vs reasoning
- **Validator**: AgentCore Code Interpreter tests snippets
- **Reconciler**: Agent resolves conflicts between versions
- **Memory**: AgentCore stores final decision + rationale

### **3. Human-Readable Recap**
**MVP Output**: Clean, scannable recap with action items
```markdown
## Session Recap: ac-session-042

### 🎯 What You Built
**Final Code**: Iterative Fibonacci implementation
✅ **Validated**: Runs successfully, O(n) time complexity
**Why This Version**: Chosen for performance over recursive approach

### 💡 Key Insights
- Realized recursion would timeout on large inputs
- Performance matters more than code elegance for this use case

### 🚫 What Didn't Work
- Recursive implementation: O(2^n) performance issue
- Initial while-loop approach: Off-by-one errors

### 📝 Next Session Reminder
Your chosen solution + efficiency reasoning stored for continuity
```

**Raw JSON Available**: Via `/api/recap/{session_id}/raw` for integrations

### **4. Session Continuity**
Next upload recalls: *"Last session: You chose iterative Fibonacci for performance. Continue?"*

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

### **Phase 2: Developer Integration**
- VS Code extension for live session capture
- GitHub integration for context-rich commits
- Slack/Discord bots for team reasoning threads

### **Phase 3: Project Mode & Advanced Analysis**
**Current MVP**: Single recap, flat list of snippets + decisions
**Future (Paid Tier)**: Smart file/module grouping and project-level insights

- **Interactive Recap Dashboard**: Rich UI with code syntax highlighting, diff views, decision timelines
- **Multi-file awareness**: "This snippet belongs in `utils.py`, this one is part of `app.js`"
- **Export Options**: Markdown for README, JSON for integrations, PDF for documentation
- **Visual Decision Trees**: See how reasoning evolved through iterations
- **Project-level recaps**: Cross-session reasoning evolution tracking
- **Module-specific context**: Decisions grouped by component/feature
- **Dependency mapping**: Understanding how reasoning connects across files
- **Semantic search** across all stored decisions and code contexts

*This transforms AC from "chat cleanup" to "project reasoning intelligence."*

### **Phase 4: Community & Collaboration**
- Public reasoning artifact sharing
- Team workspaces for shared context
- Integration marketplace for specialized tools

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
├── lambda_classifier.py      # AgentCore entry point
├── code_handler.py          # Code Interpreter integration
├── memory_handler.py        # AgentCore Memory wrapper
├── schema.py                # Output validation
├── diffcheck.py             # Version reconciliation
├── guardrails/              # Input/output filters
├── tests/                   # Full coverage suite
└── public/                  # Minimal demo frontend
```

### **Key Features**
- ✅ **Model-agnostic input** (ChatGPT, Claude, DeepSeek exports)
- ✅ **Secure code execution** via AgentCore Code Interpreter
- ✅ **Cross-session memory** via AgentCore Memory
- ✅ **Production guardrails** with Bedrock protections
- ✅ **Structured output** with schema validation
- ✅ **Autonomous processing** - no human input required

### **Prompt Engineering: The Agent's Brain**

The classification intelligence lives in `prompts/classifier_prompt.md` - a carefully engineered prompt that transforms chaotic chat logs into structured reasoning artifacts:

```markdown
## Core Classification Framework
- **Aha moments**: Key insights or shifts in understanding
- **MVP changes**: Edits, pivots, commitments affecting scope
- **Scope creep**: Evidence of expanding beyond MVP
- **README notes**: Facts/concepts that belong in documentation
- **Post-MVP ideas**: Explicitly deferred features
- **Quality flags**: Warnings or praise on session structure
```

**Why This Matters for Agents:**
- **Structured reasoning extraction** from unstructured input
- **Consistent JSON schema** enforcement across all LLM providers
- **Anti-hallucination guardrails**: Empty arrays over speculation
- **Tunable intelligence**: Add new classification fields as needs evolve

*The prompt is the product.* This agent's reasoning capability comes from deliberate prompt architecture, not just API calls.

### **Testing & QA**
- pytest coverage for all agent components
- Mocked AgentCore calls for local development
- Pre-commit hooks for code quality
- Production-ready error handling

---

## 🏆 Why Ariadne Clew Wins

**Judges, this solves a problem you have.**

Every time you've lost context in a messy chat. Every time you couldn't remember why you chose approach X. Every time a teammate asked "what were you thinking here?"

That's the problem Ariadne Clew solves.

**Technical Excellence:**
- Real AgentCore integration, not just API calls
- Autonomous agent behavior with memory persistence
- Production-ready with comprehensive guardrails
- Reproducible architecture on AWS infrastructure

**Real-World Impact:**
- Serves underserved but growing builder community
- Measurable value: time recovery + knowledge transfer
- Scales with the AI-native development trend

**Differentiated Approach:**
- First reasoning preservation agent for chat-driven workflows
- Model-agnostic in a vendor-locked world
- Built by indie operator who lives the problem daily

---

## 👩‍💻 Built By La Shara Cordero

**Customer obsession fuels everything I build.**

From [Beyond the Docket](https://sites.google.com/view/beyondthedocket) (making legal systems transparent) to [ThreadKeeper](https://threadkeeper.io) (preserving forum knowledge) - I build tools that make invisible systems visible.

Ariadne Clew continues that mission: **making reasoning visible in the age of AI-assisted building.**

*No formal AI training. No CS degree. Started exploring coding with LLMs in January 2025, first working builds by July.*
**Just a builder who sees patterns and solves problems.**

**Connect:** [lsjcordero@gmail.com] | [ThreadKeeper.io](https://threadkeeper.io) | [The Forum Files](https://theforumfiles.substack.com)

---

## 🧶 The Thread Continues

In Greek mythology, Ariadne gave Theseus thread to navigate the labyrinth.

Today's builders navigate a different maze - the chaos of AI-assisted creation. Chat transcripts branch and merge. Code versions multiply. Reasoning disappears.

**Ariadne Clew is your thread back to clarity.**

Don't commit without context. Don't build without reason. Don't lose the thread.

Ariadne Clew exists to serve builders first. It obsesses over clarity and continuity so you don't lose the thread in the chaos of iteration.

---

*Built September 2025 for AWS Agent Hackathon*
*Hackathon prototype → Production-ready foundation*

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
