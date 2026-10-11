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


def test_all_tools_declare_annotations():
    result = handle_rpc_call({"jsonrpc":"2.0","id":20,"method":"tools/list"})
    tools = result["result"]["tools"]
    assert {t["name"] for t in tools} == {"enforce_truth_boundary", "verify_evidence"}
    for tool in tools:
        assert tool["annotations"] == {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }


def test_verify_evidence_rejects_unsubstantiated_claim():
    request = {
        "jsonrpc": "2.0",
        "id": 21,
        "method": "tools/call",
        "params": {
            "name": "verify_evidence",
            "arguments": {
                "claim": {"claim_id": "UNSUPPORTED", "producer_id": "AGENT_A",
                          "claim_type": "NUMERICAL", "entity": "X",
                          "metric": "revenue", "asserted_value": 123},
                "evidence_records": [],
                "criteria": ["same_entity"]
            }
        }
    }
    response = handle_rpc_call(request)
    assert "result" in response and "error" not in response
    verification = json.loads(response["result"]["content"][0]["text"])
    assert verification["decision"] != "VERIFIED"

@pytest.mark.parametrize("claimed_verifier", [
    "UNCONFIRMED_AGENT",
    "INDEPENDENT_AUDITOR",
    "HUMAN_CHECKED",
    "MCP_INDEPENDENT_VERIFIER",
])
def test_caller_claimed_verified_is_not_authentication(claimed_verifier):
    request = {
        "jsonrpc": "2.0", "id": 73, "method": "tools/call",
        "params": {"name": "enforce_truth_boundary", "arguments": {
            "entity": "untrusted_vendor_claim", "state": "OBSERVED",
            "verification_status": "VERIFIED",
            "independent_verifier": claimed_verifier,
            "source_authenticated": True
        }}
    }
    response = handle_rpc_call(request)
    assert response["result"]["isError"] is True
    assert "BLOCKED" in response["result"]["content"][0]["text"]

def test_false_claim_with_no_verifier_still_blocked():
    request = {
        "jsonrpc": "2.0", "id": 74, "method": "tools/call",
        "params": {"name": "enforce_truth_boundary", "arguments": {
            "entity": "revenue", "state": "OBSERVED", "verification_status": "VERIFIED"
        }}
    }
    assert handle_rpc_call(request)["result"]["isError"] is True
