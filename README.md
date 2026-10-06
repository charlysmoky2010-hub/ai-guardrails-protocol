# 🛡️ AI Guardrails Protocol (v0.1.0 - Early Prototype)

> **A small, free, MIT-licensed Python module built around one fundamental rule for autonomous AI agents: A CLAIM IS NOT EVIDENCE.**

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Early_Prototype-orange.svg)](https://github.com/charlysmoky2010-hub/ai-guardrails-protocol)

---

### Why this exists
Most autonomous agent frameworks allow an LLM to declare its own completion and success:
```text
Agent: "Task is verified and complete!" -> Accepted silently by runtime
```
This self-evaluative hallucination is unsafe. This tiny prototype provides a deterministic gate: **an agent cannot mark its own observation as `VERIFIED` without an independent external verifier**. 

Attempting to self-verify raises an immediate `GuardrailViolation` exception instead of passing silently.

---

### Usage Example

```python
from guardrails import TruthBoundaryEnforcer, GuardrailViolation

# 1. Unverified observation passes cleanly into the state graph:
valid_record = {
    "entity": "github_stats",
    "state": "OBSERVED",
    "verification_status": "UNVERIFIED"
}
TruthBoundaryEnforcer.validate_observation(valid_record) # OK

# 2. Self-proclaimed VERIFIED observation is blocked fail-closed:
hallucinated_record = {
    "entity": "revenue",
    "state": "OBSERVED",
    "verification_status": "VERIFIED" # Missing independent_verifier!
}

try:
    TruthBoundaryEnforcer.validate_observation(hallucinated_record)
except GuardrailViolation as e:
    print(f"Blocked: {e}")
    # Output: EPISTEMIC BREACH: Record 'revenue' cannot claim VERIFIED without an external 'independent_verifier'.
```

---

### MCP Server (Experimental)
An entry point for Model Context Protocol is included in `mcp_server.py`. You can inspect and test it with Claude Desktop or Cursor.

---

### Current Status & Limitations
- **Early Prototype:** This is a minimalist reference implementation (alpha).
- **No Paid Version:** There is no paid tier or upsell. The code is completely free and open source under MIT.
- **Warranty:** Provided as-is without warranty. Feedback, issues, and contributions are welcome.

---

## License
MIT License. Copyright (c) 2026 Yusuf Sen / PHI-BRAIN Systems.
