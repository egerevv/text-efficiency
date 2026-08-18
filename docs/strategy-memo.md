Yes — the plan has potential, especially now that coding agents make **documentation bloat directly measurable in tokens, latency, cost, and agent performance**.

I would sharpen the idea from:

> “Study how to write less documentation.”

to:

> **Study the minimum amount of text required for humans and AI agents to understand and safely modify software.**

That framing is much more researchable, benchmarkable, and shareable.

Recent research supports the premise. Repository-level context compression can reduce noise as well as cost; one 2026 study found compressed repository context could sometimes outperform full context while substantially reducing latency. ([arXiv][1]) Another 2026 study on GitHub issue resolution reported roughly **52–71% lower token budgets** while also improving issue-resolution rates. ([arXiv][2]) Work on long-running agents similarly finds that intelligently reducing context can preserve or improve task success while cutting token usage. ([arXiv][3])

So I think there's a legitimate research question here, not merely a style preference.

## I would build the repo around a benchmark

Don't start by building a Claude extension.

Start with:

**Text Efficiency Benchmark**

Give an agent a repository and tasks such as:

* find where authentication happens
* explain an architectural decision
* fix a bug
* add a small feature
* review a PR
* identify an invariant
* find how to run/test/deploy something

Then test it under different conditions:

```text
A. code only
B. code + existing documentation
C. code + all comments
D. code + compressed documentation
E. code + carefully designed minimal context
```

Measure:

```text
task success
tokens consumed
time
cost
wrong assumptions
files inspected
context loaded
```

The interesting metric isn't:

```text
fewest tokens
```

It's something closer to:

```text
        task success
────────────────────────
tokens / time / complexity
```

In other words:

**information utility per token.**

That could become the scientific core of the project.

---

## Then build a tool around it

Something like:

```bash
texteff audit .
```

and it outputs:

```text
Context Efficiency Report

README.md
  4,821 tokens
  31% likely redundant
  3 duplicated sections
  2 references inconsistent with code

AGENTS.md
  3,104 tokens
  44% potentially unnecessary
  6 instructions already implied by tooling

src/
  12,401 comment tokens
  18% comments repeat implementation
  7 potentially stale comments

Estimated agent context reduction: 36%
```

Then:

```bash
texteff suggest .
```

could recommend changes without automatically deleting anything.

And eventually:

```bash
texteff benchmark .
```

runs actual agent tasks before/after and tells you whether reducing text **actually hurt comprehension**.

That last part is extremely important. Otherwise you end up creating another opinionated linter.

---

## Your GitHub repo could look like this

```text
text-efficiency/
│
├── README.md
├── MANIFESTO.md
│
├── benchmark/
│   ├── tasks/
│   ├── datasets/
│   ├── runners/
│   └── scoring/
│
├── core/
│   ├── redundancy/
│   ├── contradictions/
│   ├── staleness/
│   ├── token-analysis/
│   └── compression/
│
├── integrations/
│   ├── github-action/
│   ├── claude-code/
│   ├── codex/
│   └── mcp/
│
├── research/
│   ├── papers.md
│   ├── experiments/
│   └── results/
│
└── examples/
    ├── bloated-repo/
    └── efficient-repo/
```

Ironically, **don't create 40 Markdown files explaining the project.** The repository itself should demonstrate the philosophy.

---

# Claude / Codex integration: yes, but make them thin adapters

I'd avoid maintaining two independent implementations.

Build:

```text
                 ┌─ Claude Code
                 │
core engine ─────┼─ Codex
                 │
                 ├─ GitHub Action
                 │
                 └─ MCP
```

### Claude Code

Claude Code is particularly interesting because its hooks can react to things like instructions being loaded, prompts, file changes, tool calls, and context compaction. ([Claude Platform Docs][4])

For example, your plugin could warn:

```text
CLAUDE.md loaded: 7,420 tokens

2,870 tokens appear redundant with:
- package.json
- eslint.config.js
- existing source conventions

Potential context saving: 38%
```

Or before compaction:

```text
Context contains 14,300 tokens of documentation.
Estimated task-relevant portion: 5,900.
```

Claude Code hooks are therefore a very natural integration point. ([Claude Platform Docs][4])

### Codex

For Codex, I'd make a **Skill first**, rather than some large extension.

Codex currently supports reusable skills, and OpenAI explicitly presents skills as a way of packaging repeated engineering workflows. ([OpenAI Developers][5]) It also uses `AGENTS.md` for persistent repository instructions. ([OpenAI Developers][6])

So you could ship:

```text
skills/text-efficiency/
    SKILL.md
```

giving Codex commands conceptually like:

```text
/audit-context
/reduce-docs
/check-comments
/benchmark-context
```

Then additionally provide an `AGENTS.md` example:

```text
Prefer self-explanatory code over comments that restate implementation.

Document:
- non-obvious constraints
- architectural decisions
- invariants
- surprising behavior
- external requirements

Do not document information that can be reliably derived
from source code or tooling.
```

Codex can also work with MCP servers, so eventually one MCP implementation could serve several agent environments rather than creating bespoke integrations everywhere. ([OpenAI Developers][7])

---

# The really interesting research isn't “comments are bad”

Be very careful with that message.

The thesis should **not** be:

> less documentation = better.

Sometimes a 50-token comment saves someone reading 2,000 tokens of implementation.

The question is:

> **Which information deserves to consume permanent context?**

I'd classify text into things like:

```text
1. Derivable
   "This function increments count."
   → usually delete

2. Structural
   "Payments use an outbox to guarantee..."
   → valuable

3. Constraint
   "Never retry this endpoint because..."
   → extremely valuable

4. Historical
   "We chose X because vendor Y..."
   → potentially valuable

5. Instructional
   "Run npm test..."
   → valuable if not obvious elsewhere

6. Duplicated
   Same information in README + AGENTS + CLAUDE + code
   → consolidate

7. Stale
   Describes behavior that no longer exists
   → actively harmful
```

That taxonomy itself could become cited research if you validate it empirically.

---

# For virality, build a GitHub score

This could be your wedge.

Imagine a badge:

```text
Context Efficiency
████████░░ 82/100
```

or:

```text
Agent Context: 18.2k → 9.4k tokens
Task success: 91% → 93%
```

A GitHub Action could comment on PRs:

```text
Text Efficiency

+1,830 documentation tokens
+740 comment tokens

Potential redundancy: 41%

Agent benchmark
before: 14,820 tokens / 92% success
after: 16,710 tokens / 92% success

⚠ Added context did not improve task performance.
```

**That is shareable.**

People will put the badge in their README.

Then you can create something like:

> **Most Context-Efficient Open Source Repositories**

and benchmark popular projects.

That has a much better chance of spreading than another documentation style guide.

---

## And this gives you good academic questions

You could approach software-engineering, programming-languages, NLP, or HCI research groups with questions like:

**RQ1 — Does more repository documentation improve coding-agent performance?**

**RQ2 — At what point does additional documentation reduce performance through context distraction?**

**RQ3 — Which categories of comments have the highest information value per token?**

**RQ4 — Can we automatically detect documentation that is derivable from source code?**

**RQ5 — Can task-aware compression outperform manually maintained agent instructions?**

**RQ6 — Do humans and coding agents benefit from the same information?**

**RQ7 — What is the minimum sufficient repository representation for a given software-engineering task?**

That last one is particularly strong:

> **Minimum Sufficient Repository Context**

It sounds like a real research area rather than merely “clean documentation.”

---

# I would sequence the project like this

**v0.1**

```text
CLI
↓
count docs/comments/tokens
↓
detect obvious duplication
↓
produce repository report
```

**v0.2**

```text
benchmark harness
↓
full context vs reduced context
↓
Claude/Codex/model-independent evaluation
```

**v0.3**

```text
GitHub Action
↓
PR efficiency report
↓
README badge
```

**v0.4**

```text
Codex Skill
Claude Code plugin/hooks
MCP server
```

**v1**

```text
public benchmark dataset
leaderboard
research paper
academic collaborators
```

I wouldn't put Claude/Codex extensions at the center.

Put the **benchmark + measurement methodology** at the center.

The extensions then become distribution channels.

And I'd seriously consider naming the underlying concept something like **Context Efficiency**, **Context Debt**, or **Minimum Sufficient Context**, because those communicate the problem more clearly than “text efficiency.”

A particularly compelling one is:

> **Context Debt — unnecessary text that humans and agents must repeatedly process to understand a software project.**

That gives you a memorable concept, a measurable benchmark, a developer tool, and an academic research agenda all from the same repo.

[1]: https://arxiv.org/html/2604.13725v1?utm_source=chatgpt.com "On the Effectiveness of Context Compression for Repository-Level Tasks: An Empirical Investigation"
[2]: https://arxiv.org/abs/2603.28119?utm_source=chatgpt.com "Compressing Code Context for LLM-based Issue Resolution"
[3]: https://arxiv.org/html/2510.00615v3?utm_source=chatgpt.com "Acon: Optimizing Context Compression for Long-horizon LLM Agents"
[4]: https://docs.anthropic.com/en/docs/claude-code/hooks "Hooks reference - Claude Code Docs"
[5]: https://developers.openai.com/codex/use-cases?category=engineering&category=evaluation&category=quality&category=sciences&task_type=analysis&task_type=design&task_type=workflow&team=engineering&team=finance&team=operations&team=research&team=sales&utm_source=chatgpt.com "Codex use cases"
[6]: https://developers.openai.com/codex/guides/agents-md "Custom instructions with AGENTS.md | ChatGPT Learn"
[7]: https://developers.openai.com/learn/docs-mcp?utm_source=chatgpt.com "Docs MCP | OpenAI Developers"
