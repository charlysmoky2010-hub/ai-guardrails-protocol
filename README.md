# 🛡️ AI Guardrails Protocol (v0.1.0)

> **A small, free, MIT-licensed Python module built around one fundamental rule for autonomous AI agents: A CLAIM IS NOT EVIDENCE.**

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

### Why this exists
Most autonomous agent frameworks allow an LLM to declare its own completion and success. This self-evaluative hallucination is unsafe. This prototype provides a deterministic gate: **an agent cannot mark its own observation as `VERIFIED` without an independent external verifier**. 

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

# 2. Self-proclaimed VERIFIED observation is blocked blocked:
hallucinated_record = {
    "entity": "revenue",
    "state": "OBSERVED",
    "verification_status": "VERIFIED" # Missing independent_verifier!
}

try:
    TruthBoundaryEnforcer.validate_observation(hallucinated_record)
except GuardrailViolation as e:
    print(f"Blocked: {e}")
```

---

### MCP Server Configuration
An entry point for Model Context Protocol is included in `mcp_server.py`. You can configure it in Claude Desktop by adding this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-guardrails": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["/Users/mantzoaziz/PHI-BRAIN/digital_commerce/dist/ai-guardrails-protocol/mcp_server.py"]
    }
  }
}
```

---

### Current Status & Limitations
- **Prototype:** This is a minimalist reference implementation.
- **No Paid Version:** The code is completely free and open source under MIT.
- **Warranty:** Provided as-is without warranty.

---

## License
MIT License. Copyright (c) 2026 Yusuf Sen / PHI-BRAIN Systems.
