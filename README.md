# 🛡️ AI Guardrails Protocol

> **Fail-closed, zero-latency execution & truth boundary guardrails for autonomous AI agent architectures.**

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Truth Boundary](https://img.shields.io/badge/Epistemic_Standard-CERBERRUS144-purple.svg)](https://github.com/charlysmoky2010-hub)

---

### The Problem
Most AI agent frameworks allow LLMs to declare their own success ("The task is complete and verified!"). In high-stakes production environments, this self-evaluative hallucination leads to financial leakage, unverified API calls, and corrupt state graphs.

### The Solution: `CLAIM ≠ EVIDENCE`
This protocol enforces strict, deterministic **epistemic boundaries**:
- **Fail-Closed Execution:** Any action without explicit evidence fails immediately.
- **Independent Verification Gate:** No agent can set its own state to `VERIFIED`.
- **Zero-Dependency Core:** Ultra-lightweight Python implementation with zero runtime bloat.

```python
from guardrails import TruthBoundaryEnforcer, GuardrailViolation

observation = {
    "entity": "github_metrics",
    "metric": "stars",
    "value": 1500,
    "state": "OBSERVED",
    "verification_status": "UNVERIFIED" # Kept strictly unverified until cross-audited
}

# Passes seamlessly
TruthBoundaryEnforcer.validate_observation(observation)

# Blocks immediately:
fake_claim = {"entity": "sales", "verification_status": "VERIFIED"}
TruthBoundaryEnforcer.validate_observation(fake_claim) 
# -> Raises GuardrailViolation: EPISTEMIC BREACH
```

---

## 📦 Production Architecture Blueprint (€29)
Need full multi-agent orchestration, append-only SHA-256 evidence ledgers, and automated compliance auditing?
- [👉 Get the Full Production Kit & Architecture Blueprint (€29)](https://charlysmoky2010-hub.github.io/ai-guardrails-protocol/)

---

## License
MIT License. Created by PHI-BRAIN Systems.

---

## ⚡ Model Context Protocol (MCP) Support

Run as a native MCP server for Claude Desktop, Cursor, or your local agent framework:

```bash
# Add to your claude_desktop_config.json:
{
  "mcpServers": {
    "truth-guardrails": {
      "command": "python3",
      "args": ["-m", "mcp_server"]
    }
  }
}
```
