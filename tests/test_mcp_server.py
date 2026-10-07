import json
import pytest
from mcp_server import handle_rpc_call

def test_tools_list():
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    res = handle_rpc_call(req)
    assert res["id"] == 1
    assert "tools" in res["result"]
    tool_names = [t["name"] for t in res["result"]["tools"]]
    assert "enforce_truth_boundary" in tool_names

def test_enforce_truth_boundary_unverified_passes():
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "enforce_truth_boundary",
            "arguments": {
                "entity": "test_entity",
                "state": "OBSERVED",
                "verification_status": "UNVERIFIED"
            }
        }
    }
    res = handle_rpc_call(req)
    assert res["id"] == 2
    assert "error" not in res
    assert not res.get("result", {}).get("isError")
    assert "GUARDRAIL PASSED" in res["result"]["content"][0]["text"]

def test_enforce_truth_boundary_verified_without_verifier_blocked():
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "enforce_truth_boundary",
            "arguments": {
                "entity": "test_entity",
                "state": "OBSERVED",
                "verification_status": "VERIFIED"
            }
        }
    }
    res = handle_rpc_call(req)
    assert res["id"] == 3
    assert res["result"]["isError"] is True
    assert "BLOCKED" in res["result"]["content"][0]["text"]
