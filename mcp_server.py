"""
Model Context Protocol (MCP) Server for PHI-BRAIN Truth Boundary Guardrails.
Enables instant plug-and-play guardrail evaluation for Claude Desktop, Cursor, and Agent runtimes.
"""

import sys
import json
from guardrails import TruthBoundaryEnforcer, GuardrailViolation

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
