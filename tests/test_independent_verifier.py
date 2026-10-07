"""
Comprehensive 20-Point Test Suite for Independent Verifier Protocol.
Strictly verifies CERBERRUS144 Epistemic Boundaries and Fail-Closed Guardrails.
"""

import copy
import hashlib
import json
import pytest
from independent_verifier import (
    IndependentVerifier,
    ClaimType,
    IndependenceLevel,
    VerificationDecision
)
from adapters import SourceClass, SECEdgarAdapter, FREDAdapter

@pytest.fixture
def verifier():
    return IndependentVerifier(verifier_id="AUDIT_VERIFIER_001")

@pytest.fixture
def sec_evidence_2024_2025():
    raw_payload_2024 = {"filing": "10-K", "entity": "Company X", "fiscal_year": 2024, "total_revenue": 100}
    raw_payload_2025 = {"filing": "10-K", "entity": "Company X", "fiscal_year": 2025, "total_revenue": 120}

    hash_2024 = hashlib.sha256(json.dumps(raw_payload_2024, sort_keys=True).encode("utf-8")).hexdigest()
    hash_2025 = hashlib.sha256(json.dumps(raw_payload_2025, sort_keys=True).encode("utf-8")).hexdigest()

    ev_2024 = {
        "evidence_id": "SEC_10K_2024",
        "source_id": "SEC_EDGAR",
        "source_class": SourceClass.PRIMARY_REGULATORY_FILING.value,
        "entity": "Company X",
        "period": "2024",
        "metric": "revenue",
        "value": 100,
        "units": "USD_MILLIONS",
        "raw_payload": raw_payload_2024,
        "raw_response_hash": hash_2024
    }

    ev_2025 = {
        "evidence_id": "SEC_10K_2025",
        "source_id": "SEC_EDGAR",
        "source_class": SourceClass.PRIMARY_REGULATORY_FILING.value,
        "entity": "Company X",
        "period": "2025",
        "metric": "revenue",
        "value": 120,
        "units": "USD_MILLIONS",
        "raw_payload": raw_payload_2025,
        "raw_response_hash": hash_2025
    }
    return [ev_2024, ev_2025]

# 1. Numerical claim correctly verified (Section 5 Financial Example)
def test_1_numerical_claim_correctly_verified(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_REV_GROWTH_20",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "metric": "revenue",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20, # 20%
        "units": "USD_MILLIONS"
    }
    criteria = [
        "same_entity",
        "compatible_periods",
        "compatible_units",
        "calculation_reproducible"
    ]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.VERIFIED.value
    assert record["decision_reason"] == "ALL_CRITERIA_SATISFIED_BY_PRIMARY_EVIDENCE"
    assert record["calculation"]["reproducible"] is True
    assert record["calculation"]["difference"] == 0.0

# 2. Incorrect numerical claim rejected (Section 6 Negative Test)
def test_2_incorrect_numerical_claim_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_REV_GROWTH_50",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "metric": "revenue",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.50, # Claims 50%, actual is 20%
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "compatible_periods", "compatible_units", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "CALCULATED_VALUE_DOES_NOT_MATCH_CLAIM"

# 3. Missing evidence rejected
def test_3_missing_evidence_rejected(verifier):
    claim = {
        "claim_id": "CLAIM_NO_EVIDENCE",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.NUMERICAL.value,
        "entity": "Company X",
        "asserted_value": 100
    }
    criteria = ["same_entity", "calculation_reproducible"]
    record = verifier.verify(claim, [], criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "MISSING_EVIDENCE"

# 4. Hash mismatch rejected
def test_4_hash_mismatch_rejected(verifier, sec_evidence_2024_2025):
    corrupted_evidence = copy.deepcopy(sec_evidence_2024_2025)
    # Alter raw payload without updating hash
    corrupted_evidence[0]["raw_payload"]["total_revenue"] = 999
    
    claim = {
        "claim_id": "CLAIM_TAMPERED",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "compatible_periods", "calculation_reproducible"]
    record = verifier.verify(claim, corrupted_evidence, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "EVIDENCE_HASH_MISMATCH"

# 5. Wrong entity rejected
def test_5_wrong_entity_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_WRONG_ENTITY",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company Y", # Mismatch: Evidence is Company X
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "ENTITY_MISMATCH"

# 6. Wrong period rejected
def test_6_wrong_period_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_WRONG_PERIOD",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "periods": ["2021", "2022"], # Mismatch: Evidence is 2024, 2025
        "base_period": "2021",
        "target_period": "2022",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "compatible_periods", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "PERIOD_MISMATCH"

# 7. Wrong unit rejected
def test_7_wrong_unit_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_WRONG_UNIT",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "EUR_MILLIONS" # Mismatch: Evidence is USD_MILLIONS
    }
    criteria = ["same_entity", "compatible_units", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "UNIT_MISMATCH"

# 8. Wrong calculation rejected
def test_8_wrong_calculation_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_BAD_MATH",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.25, # Actual is 0.20
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "CALCULATED_VALUE_DOES_NOT_MATCH_CLAIM"

# 9. Same producer/verifier rejected (Self-verification attack)
def test_9_same_producer_verifier_rejected(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_SELF_VERIFY",
        "producer_id": verifier.verifier_id, # Self-verification attack!
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "calculation_reproducible"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "SELF_VERIFICATION_REJECTED"
    assert record["independence"]["independence_level"] == IndependenceLevel.NONE.value

# 10. Different agents but same source not treated as independent primary source
def test_10_different_agents_same_source_not_treated_as_independent(verifier):
    claim = {
        "claim_id": "CLAIM_SAME_SOURCE",
        "producer_id": "AGENT_ALPHA",
        "source_id": "SECONDARY_BLOG_POST",
        "claim_type": ClaimType.FACTUAL.value
    }
    ev = [{
        "evidence_id": "EV_1",
        "source_id": "SECONDARY_BLOG_POST",
        "source_class": SourceClass.SECONDARY_SOURCE.value,
        "value": "something"
    }]
    indep = verifier.evaluate_independence(
        producer_id="AGENT_ALPHA",
        verifier_id="AGENT_BETA",
        claim_source_id="SECONDARY_BLOG_POST",
        evidence_source_ids=["SECONDARY_BLOG_POST"],
        evidence_classes=[SourceClass.SECONDARY_SOURCE.value]
    )
    assert indep == IndependenceLevel.DIFFERENT_AGENT
    assert indep != IndependenceLevel.INDEPENDENT_PRIMARY_SOURCE
    assert indep != IndependenceLevel.DIFFERENT_SOURCE

# 11. FRED vintage mismatch rejected
def test_11_fred_vintage_mismatch_rejected(verifier):
    claim = {
        "claim_id": "CLAIM_FRED_VINTAGE",
        "producer_id": "ECON_AGENT",
        "claim_type": ClaimType.NUMERICAL.value,
        "entity": "US_CPI",
        "as_of_date": "2026-01-01", # Asserts this value was known on 2026-01-01
        "asserted_value": 315.2,
        "units": "INDEX_POINTS"
    }
    fred_evidence = [{
        "evidence_id": "FRED_CPI_REVISION",
        "source_id": "FRED_ST_LOUIS",
        "source_class": SourceClass.PRIMARY_GOVERNMENT_SOURCE.value,
        "entity": "US_CPI",
        "series_id": "CPIAUCSL",
        "observation_date": "2025-12-01",
        "value": 315.2,
        "units": "INDEX_POINTS",
        "realtime_start": "2026-06-15", # Was revised and published only in June 2026!
        "realtime_end": "CURRENT"
    }]
    criteria = ["same_entity", "compatible_units", "vintage_consistent", "calculation_reproducible"]
    record = verifier.verify(claim, fred_evidence, criteria=criteria)
    assert record["decision"] == VerificationDecision.REJECTED.value
    assert record["decision_reason"] == "VINTAGE_MISMATCH"

# 12. Unsupported causal claim remains UNVERIFIED
def test_12_unsupported_causal_claim_remains_unverified(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_CAUSAL",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.CAUSAL.value,
        "entity": "Company X",
        "statement": "Interest rate cuts caused Company X's revenue increase"
    }
    criteria = ["same_entity", "source_provenance_valid"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.UNVERIFIED.value
    assert record["decision_reason"] == "CAUSAL_CLAIMS_REQUIRE_CAUSAL_PROOF_NOT_JUST_OBSERVATIONAL_EVIDENCE"

# 13. Unsupported prediction remains UNVERIFIED
def test_13_unsupported_prediction_remains_unverified(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_PREDICTION",
        "producer_id": "ANALYST_AGENT_A",
        "claim_type": ClaimType.PREDICTIVE.value,
        "entity": "Company X",
        "statement": "Company X will grow revenue by 30% in 2026"
    }
    criteria = ["same_entity", "source_provenance_valid"]
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert record["decision"] == VerificationDecision.UNVERIFIED.value
    assert record["decision_reason"] == "PREDICTIVE_CLAIMS_CANNOT_BE_VERIFIED_BY_HISTORICAL_DATA"

# 14. Fake VERIFIED input rejected
def test_14_fake_verified_input_rejected(verifier):
    claim = {
        "claim_id": "CLAIM_FAKE_VERIFIED",
        "producer_id": "AGENT_HYPE",
        "verification_status": "VERIFIED", # Fake input claiming it's already verified!
        "state": "VERIFIED",
        "entity": "Company Z"
    }
    # Verifier does NOT trust input state. Without criteria/evidence, it must reject or leave unverified.
    record = verifier.verify(claim, [], criteria=[])
    assert record["decision"] != VerificationDecision.VERIFIED.value
    assert record["decision"] in [VerificationDecision.REJECTED.value, VerificationDecision.UNVERIFIED.value]

# 15. Deterministic verification hash
def test_15_deterministic_verification_hash(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_DETERMINISTIC",
        "producer_id": "AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "compatible_periods", "compatible_units", "calculation_reproducible"]

    record1 = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    # Re-computing canonical hash on same record data
    hash1 = record1["verification_hash"]
    test_dict = copy.deepcopy(record1)
    test_dict.pop("verification_hash")
    computed_hash = verifier.compute_sha256(test_dict)
    assert hash1 == computed_hash
    assert len(hash1) == 64

# 16. Original evidence immutable
def test_16_original_evidence_immutable(verifier, sec_evidence_2024_2025):
    evidence_clone = copy.deepcopy(sec_evidence_2024_2025)
    claim = {
        "claim_id": "CLAIM_IMMUTABILITY",
        "producer_id": "AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    criteria = ["same_entity", "compatible_periods", "compatible_units", "calculation_reproducible"]
    _ = verifier.verify(claim, sec_evidence_2024_2025, criteria=criteria)
    assert sec_evidence_2024_2025 == evidence_clone

# 17. Verifier cannot rewrite evidence
def test_17_verifier_cannot_rewrite_evidence(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_SEPARATE_RECORD",
        "producer_id": "AGENT_A",
        "claim_type": ClaimType.NUMERICAL.value,
        "entity": "Company X",
        "asserted_value": 120,
        "units": "USD_MILLIONS"
    }
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=["same_entity"])
    assert "verification_id" in record
    assert "verification_hash" in record
    # Evidence objects retain their own original keys without mutation
    for ev in sec_evidence_2024_2025:
        assert "verification_id" not in ev
        assert "decision" not in ev

# 18. Signature status remains UNIMPLEMENTED without real signing
def test_18_signature_status_remains_unimplemented(verifier, sec_evidence_2024_2025):
    claim = {
        "claim_id": "CLAIM_SIGNATURE_CHECK",
        "producer_id": "AGENT_A",
        "claim_type": ClaimType.COMPARATIVE.value,
        "entity": "Company X",
        "base_period": "2024",
        "target_period": "2025",
        "asserted_value": 0.20,
        "units": "USD_MILLIONS"
    }
    record = verifier.verify(claim, sec_evidence_2024_2025, criteria=["same_entity", "calculation_reproducible"])
    assert record["signature_status"] == "UNIMPLEMENTED"
    assert "fake_signature" not in record

# 19. Verifier decision itself cannot upgrade another verification
def test_19_verifier_decision_itself_cannot_upgrade_another_verification(verifier):
    previous_record = {
        "verification_id": "VERIF_OLD",
        "decision": "UNVERIFIED",
        "claim_id": "CLAIM_PREV"
    }
    # Passing a verification record as a claim cannot bypass criteria or upgrade without new primary evidence
    record = verifier.verify(previous_record, [], criteria=[])
    assert record["decision"] != VerificationDecision.VERIFIED.value

# 20. Failure is fail-closed
def test_20_failure_is_fail_closed(verifier):
    # Malformed inputs: None or broken types
    record_none_claim = verifier.verify(None, None, criteria=None)
    assert record_none_claim["decision"] in [VerificationDecision.REJECTED.value, VerificationDecision.UNVERIFIED.value]
    assert record_none_claim["decision"] != VerificationDecision.VERIFIED.value

    # Malformed criteria
    record_bad_types = verifier.verify({"entity": 12345}, "not_a_list", criteria=["same_entity"])
    assert record_bad_types["decision"] in [VerificationDecision.REJECTED.value, VerificationDecision.UNVERIFIED.value]
    assert record_bad_types["decision"] != VerificationDecision.VERIFIED.value
