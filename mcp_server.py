"""
Model Context Protocol (MCP) Server for PHI-BRAIN Truth Boundary Guardrails & Independent Verifier.
Enables instant plug-and-play guardrail evaluation and independent evidence verification for Claude Desktop, Cursor, and Agent runtimes.
"""

import sys
import json
from guardrails import TruthBoundaryEnforcer, GuardrailViolation
from independent_verifier import IndependentVerifier

def handle_rpc_call(request: dict) -> dict:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "enforce_truth_boundary",
                        "description": "Evaluates an observation state. Blocks unverified claims before state transition.",
                        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "entity": {"type": "string"},
                                "state": {"type": "string", "enum": ["OBSERVED", "INFERRED", "PROPOSED", "UNVERIFIED", "FAILED"]},
                                "verification_status": {"type": "string", "enum": ["VERIFIED", "UNVERIFIED"]},
                                "independent_verifier": {"type": "string"}
                            },
                            "required": ["entity", "state", "verification_status"]
                        }
                    },
                    {
                        "name": "verify_evidence",
                        "description": "Independent Verifier: Evaluates whether raw/unverified evidence records strictly satisfy explicit criteria to substantiate a claim. Never trusts input state.",
                        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "claim": {
                                    "type": "object",
                                    "description": "The claim object (claim_id, claim_type, entity, asserted_value, producer_id, etc.)"
                                },
                                "evidence_records": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "List of raw/normalized unverified evidence dictionaries."
                                },
                                "criteria": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Explicit verification criteria (e.g. same_entity, calculation_reproducible, compatible_periods, etc.)"
                                },
                                "verifier_id": {
                                    "type": "string",
                                    "description": "Identifier of the independent verifier."
                                }
                            },
                            "required": ["claim", "evidence_records", "criteria"]
                        }
                    }
                ]
            }
        }
        
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "enforce_truth_boundary":
            try:
                TruthBoundaryEnforcer.validate_observation(args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": "✅ GUARDRAIL PASSED: Observation adheres to epistemic boundary."}]
                    }
                }
            except GuardrailViolation as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"🛑 BLOCKED: {str(e)}"}],
                        "isError": True
                    }
                }

        elif tool_name == "verify_evidence":
            claim_in = args.get("claim", {})
            ev_list = args.get("evidence_records", [])
            crit = args.get("criteria", [])
            v_id = args.get("verifier_id", "MCP_INDEPENDENT_VERIFIER")

            verifier = IndependentVerifier(verifier_id=v_id)
            record = verifier.verify(claim=claim_in, evidence_records=ev_list, criteria=crit)

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({
                            "decision": record["decision"],
                            "decision_reason": record["decision_reason"],
                            "verification_record": record,
                            "limitations": record["limitations"]
                        }, indent=2)
                    }]
                }
            }
                
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": "Method not found"}
    }

def main():
    """Simple JSON-RPC stdio transport loop for MCP."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_rpc_call(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
