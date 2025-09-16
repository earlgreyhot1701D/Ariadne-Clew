# Ariadne Clew (AC)
**Cognitive Version Control for LLM-Native Builders**

🧶 **Don’t commit without context.**

Ariadne Clew is a **meta-contextual reasoning agent** that classifies your LLM session logs into **structured memory artifacts** — so you never lose track of *why* things were built.

Where Git captures *what* changed, Ariadne Clew captures the **cognitive arc** behind your product.
It creates a **temporal reasoning ledger** from your chat transcripts — preserving *aha moments*, *design tradeoffs*, and *post-MVP insights* as first-class build artifacts.

---

## 🧶 Why Ariadne Clew?

In Greek mythology, Ariadne gave Theseus a *clew* — a ball of thread — so he could navigate the labyrinth and make it out alive.
Ariadne Clew plays the same role for builders today: it captures threads of thought, decisions, and insights so you don’t lose your way in the maze of iteration.

Where traditional version control tracks *what* changed, Ariadne Clew preserves the *why*, guiding you back to clarity when the path gets tangled.

### 🧩 The Real Problem
LLMs have become integral to product ideation. But their outputs are ephemeral, unstructured, and unauditable.

Builders are shipping faster than ever, but the **design decisions** and **reasoning paths** that shape those products live in fragile chat logs — invisible to teammates, untracked by Git, and lost to time.


### 🧰 The Solution
Ariadne Clew is a **memory agent** for LLM workflows.

It ingests raw session logs and produces a **structured recap** with:
- 🔍 **Aha moments** — preserved discoveries and clarifications
- 🧩 **MVP changes** — tradeoffs, pivots, scope edits
- 🌀 **Scope creep** — hallucinated ambition, caught in the act
- 🧾 **README notes** — concepts that belong in code docs
- ⏭ **Post-MVP ideas** — ideas to defer, not discard
- 🧠 **Summary + quality flags** — model-level reflection on the session itself

The result? A **reasoning trace** you can reference, share, or plug into other agents.

For solo devs and indie builders, Ariadne Clew is like a ghost cofounder — silently watching and capturing your product reasoning so you can focus on building, not backtracking. Every design choice, aha moment, or potential pitfall is preserved to keep your momentum and confidence high.

---

## 🔗 What It Enables

Ariadne Clew acts as a **foundational memory primitive** for agent-native infrastructure.

You can use it to:
- 📜 Auto-generate `README.md` content from LLM-driven builds
- 📊 Train future agents on historical product reasoning
- 🕵️ Trace decisions back to the prompts that shaped them
- 🧠 Maintain *semantic continuity* across sessions, collaborators, and tools

> Think of it as a **source-of-truth layer for product thinking**.

---

## 🧠 What It Does

- Listens to session logs stored in **S3**
- Sends logs to the **classifier** (Claude, GPT, DeepSeek, etc.) for structured analysis
- Parses outputs into structured JSON fields
- Stores results in **DynamoDB**
- Serves recaps via a simple **API Gateway** endpoint

It works *after* you finish a brainstorming session — a post-session oracle that recaps your progress.

---

## 🏗 Architecture

- **S3** → stores uploaded conversation logs from any LLM session
- **Lambda** → classifier function that calls the model, returns structured JSON
- **DynamoDB** → persistent store for structured results
- **API Gateway** → recap endpoint for retrieval and review

---

## 🤖 Why This Is an Agent

Ariadne Clew acts as an agent by running autonomously on new logs, reasoning over
builder sessions, and updating state in DynamoDB without human intervention.
It doesn’t use AgentCore primitives yet, but it already demonstrates agent behavior.

### ✅ AWS Agent Criteria Met
- Uses reasoning LLMs for decision-making (classifies decisions and design moments)
- Autonomous task execution: Classifies logs without user input
- Integrates multiple AWS tools (S3, Lambda, DynamoDB, API Gateway)
- Structured reasoning output (JSON with flags, summaries, insights)

---

## 🔗 Using Ariadne Clew with Any LLM

Ariadne Clew is model-agnostic. You can work with ChatGPT, Claude, DeepSeek, or any other LLM you prefer.
Here’s how it works in practice:

1. **Build as you normally do** — brainstorm, iterate, and debug with your LLM of choice.
2. **Export your chat** — save the transcript as plain `.txt` or `.json`.
3. **Upload to Ariadne Clew** — AC ingests the file, classifies the session, and outputs a structured recap.
   You can try this at [threadkeeper.io/ariadneclew](https://threadkeeper.io/ariadneclew), where a simple upload form is provided.

That’s it. No special formatting, no lock-in — just drop in your chat and AC turns it into clarity.

---

🧠 Prompt Template

The prompt used to classify sessions lives in [`prompts/classifier_prompt.md`](prompts/classifier_prompt.md).
It defines what Ariadne Clew considers thread-worthy — and can be tuned over time as your needs evolve.

---

## 📦 Output Schema

Ariadne Clew produces structured JSON for every session.
Each recap includes the following fields:

- `session_id` – Unique label for the session (e.g., "ac-session-003")
- `aha_moments` – Key insights or shifts in understanding
- `mvp_changes` – Edits, pivots, or commitments that affect the MVP
- `scope_creep` – Evidence of expanding beyond MVP
- `readme_notes` – Facts or concepts that belong in the README
- `post_mvp_ideas` – Ideas explicitly deferred until after MVP
- `summary` – A 3–5 sentence overview of what the session accomplished
- `quality_flags` – Warnings or praise on structure, clarity, or focus

🔧 See [`prompts/classifier_prompt.md`](prompts/classifier_prompt.md) for examples, tuning tips,
and optional future fields (e.g., `naming_decisions`, `deleted_features`, `open_questions`, `blocked_by`).

---

## 📁 Project Structure

- `lambda_classifier.py` – Lambda for S3-triggered classification
- `api_recap.py` – Lambda for recap endpoint
- `schema.py` – TypedDicts and field validators
- `diffcheck.py` – Local file diff checker for QA
- `tests/` – Unit and validation tests
- `infra/` – IaC placeholder
- `ariadne_clew_manifest.md` – Philosophy and design ethos

---

## ✨ Features

- ✅ Lambda classifier with robust error handling
- ✅ DynamoDB persistence for structured results
- ✅ Recap endpoint served via API Gateway
- ✅ `diffcheck.py` module for line-by-line sanity checks
- ✅ Simple upload form for `.txt`/`.json` LLM logs (available at [threadkeeper.io/ariadneclew](https://threadkeeper.io/ariadneclew))
- ✅ Occam’s razor build principle: small, slim files over bloat

---

## 🛡 Guardrails & QA

Ariadne Clew enforces strict safety rules in its classifier pipeline:

- **Strict JSON only** — Classifier prompts instruct the model to return valid JSON matching a fixed schema. No prose or creative writing.
- **Empty fields over speculation** — If information is unclear, the model must return empty arrays or nulls instead of inventing content.
- **Schema validation** — All classifier output is validated against TypedDicts in `schema.py`. Invalid JSON triggers error handling and logs a quality flag.
- **Fallbacks** — When parsing fails, the system stores a minimal default record with `quality_flags` set, ensuring downstream stability.
- **Occam’s razor design** — Files are kept slim, under ~200 lines. If a file grows too large, it is split into two smaller modules.

These guardrails prevent runaway creativity, hallucinations, or malformed output and keep the MVP predictable under limited hackathon credits.

---

## 🧪 QA & Hygiene

- **Linting**: [`ruff`](https://docs.astral.sh/ruff/)
- **Formatting**: [`black`](https://black.readthedocs.io/en/stable/)
- **Typing**: [`mypy`](http://mypy-lang.org/)
- **Pre-commit**: [`pre-commit`](https://pre-commit.com/)

### Run QA Commands
# If you have make installed:
```bash
make format
make lint
make typecheck
make test
```
# Or run directly with Python:
python -m black .
python -m ruff check .
python -m mypy .
python -m pytest

### Setup Pre-commit
```bash
pip install pre-commit
pre-commit install
```

---

## 💰 Model Choice & Cost Control

For hackathon MVP, we used **Claude Sonnet** for classification (predictable costs).
In practice, Ariadne Clew works with logs from any LLM. You’re free to continue using ChatGPT, DeepSeek, or Claude — Ariadne Clew only needs the exported text.
Future upgrades (e.g., Claude Opus or GPT-4.5) could improve classification quality if desired.

---

## 🚀 Deployment

For MVP, Ariadne Clew can be deployed manually to AWS:

1. **Provision resources**
   - Create an S3 bucket for uploads
   - Create a DynamoDB table for recaps
   - Set up API Gateway and connect it to your Lambda functions

2. **Deploy Lambdas**
   - Upload `lambda_classifier.py` and `api_recap.py` as separate Lambda functions
   - Update `script.js` in `/public` with your API Gateway endpoint

3. **Serve the frontend**
   - Place `index.html`, `script.js`, and `style.css` on a static host (e.g., S3 static site, Netlify, or Vercel)
   - Visit your URL and upload a `.txt` or `.json` log to see the recap

⚡ Once deployed, the pipeline runs automatically:
uploads trigger classification via Lambda, results persist in DynamoDB, and recaps are available via API.

---

## 👥 Audience

Ariadne Clew is built for indie operators, casual architects, and advanced civilian builders.
These are people who lose context when iterating fast — not those who live inside Git.
Ariadne Clew exists to serve builders first. It obsesses over clarity and continuity so you don’t lose the thread in the chaos of iteration.

---

## 🧩 Post-MVP Roadmap

The current version of Ariadne Clew is designed for MVP clarity and minimal dependencies. Planned features for future releases include:

- 🧠 **React-based Frontend**: Componentized UI with support for multiple recaps, filters, and future session tagging.
- 🧪 **Prompt Tuner Interface**: A way to edit and test classification prompts from the frontend.
- 🌍 **Internationalization & Accessibility Modes**: Keyboard navigation, high-contrast themes, and multi-language support.
- 🔗 **GitHub Integration**: Recap hooks for commit messages and issue generation.
- 🧰 **Prompt Engineering Toolkit**: Embed session testing and JSON contract validation for future classifier iterations.
- ⚙️ **Infrastructure as Code (Terraform or CloudFormation)**: Add automated provisioning and scalability for production deployments.

These will be implemented based on real-world usage and user feedback.

---

## 🙌 Acknowledgments

- **La Shara Cordero** — Vibecoder and creator of Ariadne Clew
- **ChatGPT** — Sixth person off the bench, serving as project manager and build partner
- **Dr. Kahlo (chatGPT)** - Built with QA support from [Dr. Kahlo on ChatGPT](https://chatgpt.com/g/g-68af555e39808191a53fcd1ef6451fda-dr-kahlo?model=gpt-4o) — production-first code reviewer and code quality mentor.
- Ariadne Clew was built with the same ethos AWS champions — customer obsession. Every feature is scoped around the real pain of losing context while building.
- > This repo reflects an MVP baseline built with QA guardrails up front, so iteration during the hackathon focused on the reasoning agent itself, not fixing broken scaffolding.


---

## 📜 License

## License

This project is proprietary. All rights reserved.

You may not copy, modify, distribute, or reuse this software without explicit permission.

Contact: [lsjcordero@gmail.com]

---

## 🧾 Origin

Created September 2025 by **La Shara Cordero**
Hackathon prototype built with AWS + LLM integration
Built with collaboration from Claude, ChatGPT, and the ThreadKeeper project


