# 🛡️ AI Guardrails Protocol (v0.1.0)

> **A small, free, MIT-licensed research prototype built around one fundamental rule for autonomous AI agents: A CLAIM IS NOT EVIDENCE.**

### Jetzt ausprobieren: kostenloser KI-Workflow-Selbstcheck

[**8 Kontrollfragen direkt im Browser beantworten →**](https://unveiled-seed-x7w4mw8.shipstatic.com/?utm_source=github&utm_medium=readme&utm_campaign=cerberrus_xray_q4_2026)

Ohne Anmeldung, Modell-API oder Datenupload. Ein optionaler digitaler **CERBERRUS Operational X-Ray**-Arbeitsbogen (€29, Gumroad; ggf. zusätzliche Steuern im Checkout) ist separat verlinkt. Die Eigenbewertung ersetzt keine Sicherheits- oder Compliance-Prüfung.

---

### Für deutsche KI-Teams: acht Kontrollfragen

Sie bauen einen KI-Agenten mit MCP, n8n oder APIs? **Vor der ersten produktiven Freigabe** sollten Werkzeugrechte, sensible Aktionen, echte Quellenprüfung, Mandantentrennung, Auditlogs, Fehlermodi, Gedächtnis und Verantwortlichkeiten geklärt sein. Unser [kostenloser 8-Fragen-Selbstcheck](https://reverent-echo-c6ynd3a.shipstatic.com/#check) hilft bei einer ersten Einordnung. Das Ergebnis ist **keine** Sicherheitsprüfung oder Zertifizierung.

Für **einen konkreten Workflow** gibt es bei Bedarf separat eine [persönliche 30-Minuten-Discovery für 99 €](https://reverent-echo-c6ynd3a.shipstatic.com/#angebote). Sie ersetzt **keine** Implementierung und ist nicht Bestandteil der freien MIT-Lizenz dieses Repositorys.

---

> **Security notice (2026-10-11):** This public version does **not** authenticate caller-supplied verifier names or primary-source metadata. A malicious agent can supply fabricated verification information that is not independently checked. Do not use it as a production security, payment, compliance or source-authenticity verifier. **Update 2026-10-11:** The published truth-boundary function now rejects every caller-supplied `VERIFIED` value, including records with fabricated `independent_verifier` labels. This is a fail-closed mitigation, not a trusted source-verification adapter.

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

### Why this exists
Most autonomous agent frameworks allow an LLM to declare its own completion and success. This self-evaluative hallucination is unsafe. This prototype implements some deterministic validation rules. It rejects certain unsupported claims (for example, some records missing a verifier field) but **does not establish that a named verifier really checked the evidence**. A malicious or mistaken caller may still supply an untrusted verifier label. Correct source authentication and trusted authorization boundaries require additional engineering.

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

# 2. A VERIFIED record with no verifier field is rejected by this prototype:
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
      "command": "python3",
      "args": ["/absolute/path/to/ai-guardrails-protocol/mcp_server.py"]
    }
  }
}
```

Replace `/absolute/path/to/ai-guardrails-protocol` with the path to your own clone.

---

### Current Status & Limitations
- **Fail-closed guard:** `enforce_truth_boundary` blocks any incoming `VERIFIED` assertion. Independent verification requires an authenticated primary-source integration not included in this repository.
- **Regression tests:** 30 passing on 2026-10-11, including five new forged-verifier tests.
- **Prototype:** This is a minimalist reference implementation. Its verification field is not independently authenticated.
- **Security boundary:** Caller-supplied evidence provenance and verifier identity must not be treated as genuine verification. Do not deploy this as a standalone security enforcement service.
- **MCP annotations:** The provided tool annotations are metadata, not access-control enforcement.
- **No Paid Version:** The code is completely free and open source under MIT.
- **Warranty:** Provided as-is without warranty.

---

### Related PHI NEXUS service (optional)

For teams who want to assess a real AI-enabled workflow, [PHI NEXUS offers a free browser-based operational self-check](https://reverent-echo-c6ynd3a.shipstatic.com/), plus an optional human-guided 30-minute workflow discovery (€99) and a scoped review (€490). For a lower-cost **self-service** alternative, the [German CERBERRUS Operational X-Ray offline workbook (€29, Gumroad)](https://smokycharly.gumroad.com/l/cyrada?utm_source=github&utm_medium=project_readme&utm_campaign=xray_sales_q4_2026&utm_content=ai_guardrails) provides a process analysis template and decision scorecard without personal consulting. These are separate optional commercial offers, **not** a paid license, security certification or endorsement of this open-source module. The source code here remains MIT licensed and free.

---

## License
MIT License. Copyright (c) 2026 Yusuf Sen / PHI-BRAIN Systems.
