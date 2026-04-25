# BRAND-WORDS — canonical copy reference for the `ainfera` CLI repo

Pin this while editing anything user-facing: README, CLI output strings,
CHANGELOG, docstrings, CLAUDE.md, `pyproject.toml`. Every drift is
visible to anyone who runs `pip install ainfera` and reads the package
on PyPI.

The numbered sections are stable anchors. Tooling, audit reports, and
PR templates may reference them by number (`§3.4`, `§6`, etc.).

---

## §1 — Entity, packages, contact

**Entity name (only canonical form):** `Ainfera`

- No legal-form suffix (`Pte. Ltd.`, `Inc.`, `LLC`, `GmbH`, …)
- No jurisdictional marker (`Singapore`, `Delaware`, …)
- Support contact: `hello@ainfera.ai`
- Footer copyright: `© 2026 Ainfera`

**Packages on PyPI:**

| Package | Install | What it is |
| --- | --- | --- |
| `ainfera` | `pip install ainfera` | This repo — the CLI |
| `ainfera-sdk` | `pip install ainfera-sdk` | Separate repo — the Python SDK |

**Canonical SDK import (in user-facing examples only):**

```python
from ainfera_sdk import Ainfera
```

The client class is `Ainfera`. Historical forms (`AinferaClient`,
`AinferaSDK`, `from ainfera.sdk import …`, `from ainfera import agent`)
are not canonical in *external* examples.

`from ainfera.<module>` inside this repo's own source code is fine —
the CLI package *is* `ainfera`. The rule applies to user-facing
examples of how external callers import the SDK.

---

## §2 — Product canon

### §2.1 — Five layers

1. Agent Trust Score
2. Sandboxed Compute
3. Metered Billing & Settlement
4. Agent Identity & Registry
5. Multi-Protocol Orchestration

### §2.2 — Agent Trust Score (ATS) dimensions

`Safety · Reliability · Quality · Performance · Reputation`

Any CLI output, README block, or test snapshot listing different
dimensions is out of spec. In particular: no `Compliance`, no
`Cost-efficiency`, no `Cost_efficiency`.

### §2.3 — ATS grade boundaries

```
AAA ≥ 900
AA  ≥ 800
A   ≥ 700
BBB ≥ 600
BB  ≥ 500
B   ≥ 400
CCC < 400 → auto-quarantine
```

### §2.4 — Agent DID format

```
did:web:ainfera.ai:agents:{id}
```

Never `did:ainfera:agent:{id}` — that method was never registered.

### §2.5 — Revenue split

`85 / 5 / 10` — creator / platform / compute. Spaces around the
slashes are optional. Never `60/25/15` and never any other split.

---

## §3 — Pre-push grep battery (zero hits required)

Every change to a user-facing file (`README.md`, `CHANGELOG.md`,
`CLAUDE.md`, `docs/**`, `src/**`, `tests/**`, `*.py`, `*.toml`,
`*.cfg`, `*.md`) must pass these greps locally before push.

Meta-references inside `CLAUDE.md` and `docs/BRAND-WORDS.md` that
*define* the regex itself are expected and don't count.

### §3.1 — Named third parties (marketing framing)

```bash
grep -rEin "nvidia|nim|nemo|guardrails|stripe|anthropic|claude|langchain|crewai|autogen|llamaindex|google ?adk|\bopenai\b|hugging ?face|mistral|\bdocker\b|gvisor|firecracker|kubernetes|\baws\b|\bgcp\b|\bazure\b|cloudflare|\bvercel\b|railway" . --include="*.py" --include="*.md" --include="*.toml"
```

**Exception 1** — `pyproject.toml` optional-dependency keys
(`[project.optional-dependencies]`) and dependency package names.
Functional package names, not marketing.

**Exception 2** — CLI `--framework <value>` flag values
(`langchain`, `crewai`, `openclaw`, `custom`). Functional flag values
are allowed; help-text descriptions must stay generic
("Target agent framework" — never "Choose between LangChain, CrewAI,
AutoGen…").

### §3.2 — Stage / timeline / funding language

```bash
grep -rEin "private beta|public beta|\balpha\b|\bbeta\b|\bGA\b|coming soon|coming Q|arriving|roadmap|Q[1-4] 20|\bM[0-9]+\b|seed|series [abc]|pre-seed|SAFE|MFN" . --include="*.md" --include="*.py" --include="*.toml"
```

The `\bSAFE` term is the financing instrument. Substring matches like
`safe_dump`, `Safe to install`, `safety` are false positives because
the canonical regex is intended case-sensitive on `SAFE`. If your
local `grep` runs case-insensitively, audit hits manually.

### §3.3 — Jurisdictional framing

```bash
grep -rEn "Pte\. Ltd|Pte Ltd|Singapore|Republic of Singapore|Delaware" .
```

### §3.4 — Founder / maintainer anonymity

```bash
grep -rEin "hizrian|izzy|\braz\b" . --include="*.py" --include="*.md" --include="*.toml"
```

Zero hits in `README.md`, `pyproject.toml`, docstrings, source, or
docs. The git author exception lives at §6.

### §3.5 — Forbidden vocabulary

```bash
grep -rEin "blockchain|crypto|stablecoin|web3|x402|mainnet|hash chain|merkle|decentralized|wallet|smart contract|mining" . --include="*.py" --include="*.md"
```

Also forbidden in user-facing copy: `tamper-evident`, `coin`, `token`,
`ledger` (in the financial sense).

### §3.6 — Retired entity forms

```bash
grep -rEin "Ainfera Pte\.? ?Ltd|Ainfera Inc|Ainfera LLC" . --include="*.md" --include="*.toml"
```

### §3.7 — Retired phrasing

```bash
grep -rEn "60/25/15|60 / 25 / 15" .
grep -rEn "did:ainfera" . --include="*.py" --include="*.md" --include="*.toml"
grep -rEn "from ainfera import (Ainfera|AinferaClient)|from ainfera\.sdk import" *.md docs/
```

---

## §4 — Framework language

When describing what agent frameworks the CLI works with, use generic
phrasing: "works with major agent frameworks." Do not enumerate named
products in marketing framing.

CLI flag values (`--framework langchain`) and dependency package
names are functional, not marketing — see §3.1 Exceptions 1 & 2.

---

## §5 — `pyproject.toml` author / maintainer

```toml
[project]
authors = [{name = "Ainfera", email = "hello@ainfera.ai"}]
maintainers = [{name = "Ainfera", email = "hello@ainfera.ai"}]
```

This is **public PyPI metadata**. The git author exception at §6
does NOT extend here.

---

## §6 — Git author identity (founder exception)

The `git config user.name` and `git config user.email` for this
repository are:

```
git config user.name  "Hizrian Raz"
git config user.email "hizrian@ainfera.ai"
```

The names listed in §3.4 are forbidden in source, docs, and
`pyproject.toml` — but the git author/committer field is local
identity, not public package metadata. Reviewers will see
`Hizrian Raz <hizrian@ainfera.ai>` on every commit; that is correct.

This exception is scoped strictly to git author/committer config. It
does NOT apply to:

- `pyproject.toml` `authors` / `maintainers` (see §5)
- README footers, CLAUDE.md, docstrings, CLI output
- `CODEOWNERS`, `.mailmap`, or any file checked into the tree

---

## §7 — Pre-push enforcement summary

Before every push touching a file in the user-facing set:

1. Run all §3 greps. Zero hits on actual content.
2. Run `pytest` (or equivalent) — must pass.
3. `python -c "import ainfera"` — must succeed.
4. `ainfera --help` — must run.

If any §3 query reports a hit and it is not a meta-reference inside
`CLAUDE.md` or this file, fix the hit before pushing.
