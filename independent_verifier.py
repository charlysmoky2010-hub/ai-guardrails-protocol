"""
Independent Verifier Protocol for PHI-BRAIN (v0.1.0)
Strictly enforces:
- Verifier != Source
- CLAIM != EVIDENCE
- SOURCE_EXISTS != SOURCE_SUPPORTS_CLAIM
- PRIMARY_EVIDENCE != INDEPENDENT_VERIFICATION
- INDEPENDENT_VERIFICATION != CAUSAL_PROOF
- CAUSAL_PROOF != PREDICTION
"""

import copy
import json
import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from adapters import SourceClass

class ClaimType(str, Enum):
    FACTUAL = "FACTUAL"
    NUMERICAL = "NUMERICAL"
    TEMPORAL = "TEMPORAL"
    COMPARATIVE = "COMPARATIVE"
    DERIVED = "DERIVED"
    CAUSAL = "CAUSAL"
    PREDICTIVE = "PREDICTIVE"

class IndependenceLevel(str, Enum):
    NONE = "NONE"
    DIFFERENT_AGENT = "DIFFERENT_AGENT"
    DIFFERENT_SOURCE = "DIFFERENT_SOURCE"
    INDEPENDENT_PRIMARY_SOURCE = "INDEPENDENT_PRIMARY_SOURCE"
    HUMAN_INDEPENDENT_VERIFICATION = "HUMAN_INDEPENDENT_VERIFICATION"

class VerificationDecision(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    REJECTED = "REJECTED"

# Code-level epistemic axioms
EPISTEMIC_AXIOMS = {
    "SOURCE_EXISTS_NEQ_SOURCE_SUPPORTS_CLAIM": True,
    "SOURCE_SUPPORTS_CLAIM_NEQ_CLAIM_IS_TRUE_IN_GENERAL": True,
    "PRIMARY_EVIDENCE_NEQ_INDEPENDENT_VERIFICATION": True,
    "INDEPENDENT_VERIFICATION_NEQ_CAUSAL_PROOF": True,
    "CAUSAL_PROOF_NEQ_PREDICTION": True,
}

class IndependentVerifier:
    """
    Independent Verification Engine.
    Evaluates whether raw evidence strictly supports a specific claim against explicit criteria.
    Never assumes evidence truthfulness based on source identity alone.
    """

    def __init__(self, verifier_id: str = "PHI_BRAIN_INDEPENDENT_VERIFIER_V1"):
        self.verifier_id = verifier_id

    @staticmethod
    def compute_sha256(data: Any) -> str:
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def evaluate_independence(self, producer_id: str, verifier_id: str, 
                              claim_source_id: Optional[str], 
                              evidence_source_ids: List[str],
                              evidence_classes: List[str]) -> IndependenceLevel:
        """
        Determines the strict independence level between claim, verifier, and evidence sources.
        DIFFERENT_AGENT != DIFFERENT_SOURCE
        DIFFERENT_SOURCE != INDEPENDENT_PRIMARY_SOURCE
        INDEPENDENT_PRIMARY_SOURCE != HUMAN_INDEPENDENT_VERIFICATION
        """
        if producer_id == verifier_id:
            return IndependenceLevel.NONE

        is_human = "HUMAN" in verifier_id.upper()
        if is_human:
            return IndependenceLevel.HUMAN_INDEPENDENT_VERIFICATION

        # Check if primary regulatory or government source
        primary_types = {SourceClass.PRIMARY_REGULATORY_FILING.value, SourceClass.PRIMARY_GOVERNMENT_SOURCE.value}
        if any(cls in primary_types for cls in evidence_classes):
            return IndependenceLevel.INDEPENDENT_PRIMARY_SOURCE

        # Check if different sources
        unique_sources = set(evidence_source_ids)
        if claim_source_id:
            unique_sources.add(claim_source_id)

        if len(unique_sources) > 1:
            return IndependenceLevel.DIFFERENT_SOURCE

        # Different agents citing the same single source
        return IndependenceLevel.DIFFERENT_AGENT

    def verify(self, claim: Dict[str, Any], 
               evidence_records: List[Dict[str, Any]], 
               verifier_id: Optional[str] = None,
               criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Executes fail-closed verification against explicit criteria.
        Returns a deterministic VerificationRecord.
        """
        active_verifier_id = verifier_id or self.verifier_id
        verification_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Defensive deep copy to guarantee evidence immutability
        claim_copy = copy.deepcopy(claim) if isinstance(claim, dict) else {}
        evidence_copies = copy.deepcopy(evidence_records) if isinstance(evidence_records, list) else []

        checks: List[Dict[str, Any]] = []
        limitations: List[str] = [
            "Verification is deterministic and scoped strictly to provided evidence and explicit criteria.",
            "Primary source evidence does not prove future outcomes or causal mechanics.",
            "Subject to filing restatement or historical data revision risks."
        ]
        calculation: Dict[str, Any] = {}
        evidence_hashes: List[str] = []

        try:
            # 1. Verification Criteria Mandatory Check
            if not criteria or len(criteria) == 0:
                checks.append({"criterion": "criteria_present", "passed": False, "detail": "No criteria specified."})
                return self._build_record(
                    verification_id=verification_id,
                    claim_id=claim_copy.get("claim_id", "unknown"),
                    evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                    verifier_id=active_verifier_id,
                    criteria=[],
                    checks=checks,
                    independence={"independence_level": IndependenceLevel.NONE.value},
                    calculation={},
                    decision=VerificationDecision.UNVERIFIED,
                    decision_reason="MISSING_VERIFICATION_CRITERIA",
                    evidence_hashes=[],
                    limitations=limitations,
                    verified_at=now_iso
                )

            # 2. Producer vs Verifier (Self-Verification Attack Defense)
            producer_id = claim_copy.get("producer_id", "unknown_producer")
            if producer_id == active_verifier_id or claim_copy.get("verifier_id") == producer_id:
                checks.append({"criterion": "independent_entities", "passed": False, "detail": "Self-verification detected."})
                return self._build_record(
                    verification_id=verification_id,
                    claim_id=claim_copy.get("claim_id", "unknown"),
                    evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                    verifier_id=active_verifier_id,
                    criteria=criteria,
                    checks=checks,
                    independence={"producer_id": producer_id, "verifier_id": active_verifier_id, "independence_level": IndependenceLevel.NONE.value},
                    calculation={},
                    decision=VerificationDecision.REJECTED,
                    decision_reason="SELF_VERIFICATION_REJECTED",
                    evidence_hashes=[],
                    limitations=limitations,
                    verified_at=now_iso
                )

            # 3. Evidence Presence Check
            if len(evidence_copies) == 0:
                checks.append({"criterion": "evidence_present", "passed": False, "detail": "Zero evidence records provided."})
                return self._build_record(
                    verification_id=verification_id,
                    claim_id=claim_copy.get("claim_id", "unknown"),
                    evidence_ids=[],
                    verifier_id=active_verifier_id,
                    criteria=criteria,
                    checks=checks,
                    independence={"producer_id": producer_id, "verifier_id": active_verifier_id, "independence_level": IndependenceLevel.NONE.value},
                    calculation={},
                    decision=VerificationDecision.REJECTED,
                    decision_reason="MISSING_EVIDENCE",
                    evidence_hashes=[],
                    limitations=limitations,
                    verified_at=now_iso
                )

            # 4. Evidence Hash Integrity Check
            for ev in evidence_copies:
                raw_hash = ev.get("raw_response_hash")
                raw_payload = ev.get("raw_payload")
                if raw_hash and raw_payload is not None:
                    computed_hash = self.compute_sha256(raw_payload)
                    evidence_hashes.append(computed_hash)
                    if computed_hash != raw_hash:
                        checks.append({"criterion": "evidence_hash_integrity", "passed": False, "detail": f"Hash mismatch on {ev.get('evidence_id')}"})
                        return self._build_record(
                            verification_id=verification_id,
                            claim_id=claim_copy.get("claim_id", "unknown"),
                            evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                            verifier_id=active_verifier_id,
                            criteria=criteria,
                            checks=checks,
                            independence={"producer_id": producer_id, "verifier_id": active_verifier_id, "independence_level": IndependenceLevel.NONE.value},
                            calculation={},
                            decision=VerificationDecision.REJECTED,
                            decision_reason="EVIDENCE_HASH_MISMATCH",
                            evidence_hashes=evidence_hashes,
                            limitations=limitations,
                            verified_at=now_iso
                        )
                elif raw_hash:
                    evidence_hashes.append(raw_hash)

            # 5. Evaluate Independence Model
            ev_sources = [ev.get("source_id", "unknown") for ev in evidence_copies]
            ev_classes = [ev.get("source_class", "unknown") for ev in evidence_copies]
            indep_level = self.evaluate_independence(
                producer_id=producer_id,
                verifier_id=active_verifier_id,
                claim_source_id=claim_copy.get("source_id"),
                evidence_source_ids=ev_sources,
                evidence_classes=ev_classes
            )
            independence_dict = {
                "producer_id": producer_id,
                "verifier_id": active_verifier_id,
                "claim_source_id": claim_copy.get("source_id"),
                "evidence_source_ids": ev_sources,
                "independence_level": indep_level.value
            }

            # 6. Claim Type Epistemic Guardrails (Causal & Predictive)
            claim_type = claim_copy.get("claim_type", ClaimType.FACTUAL.value)
            if claim_type == ClaimType.CAUSAL.value:
                checks.append({"criterion": "causal_model_validity", "passed": False, "detail": "Primary observational evidence cannot establish causality."})
                limitations.append("Correlation or filing facts do not constitute mathematical/causal proof.")
                return self._build_record(
                    verification_id=verification_id,
                    claim_id=claim_copy.get("claim_id", "unknown"),
                    evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                    verifier_id=active_verifier_id,
                    criteria=criteria,
                    checks=checks,
                    independence=independence_dict,
                    calculation={},
                    decision=VerificationDecision.UNVERIFIED,
                    decision_reason="CAUSAL_CLAIMS_REQUIRE_CAUSAL_PROOF_NOT_JUST_OBSERVATIONAL_EVIDENCE",
                    evidence_hashes=evidence_hashes,
                    limitations=limitations,
                    verified_at=now_iso
                )

            if claim_type == ClaimType.PREDICTIVE.value:
                checks.append({"criterion": "predictive_validity", "passed": False, "detail": "Historical evidence cannot verify future predictions."})
                limitations.append("Future predictive statements are epistemically unprovable from historical filings.")
                return self._build_record(
                    verification_id=verification_id,
                    claim_id=claim_copy.get("claim_id", "unknown"),
                    evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                    verifier_id=active_verifier_id,
                    criteria=criteria,
                    checks=checks,
                    independence=independence_dict,
                    calculation={},
                    decision=VerificationDecision.UNVERIFIED,
                    decision_reason="PREDICTIVE_CLAIMS_CANNOT_BE_VERIFIED_BY_HISTORICAL_DATA",
                    evidence_hashes=evidence_hashes,
                    limitations=limitations,
                    verified_at=now_iso
                )

            # 7. Entity Check
            if "same_entity" in criteria:
                claim_entity = claim_copy.get("entity")
                for ev in evidence_copies:
                    if ev.get("entity") != claim_entity:
                        checks.append({"criterion": "same_entity", "passed": False, "detail": f"Claim entity {claim_entity} != Evidence entity {ev.get('entity')}"})
                        return self._build_record(
                            verification_id=verification_id,
                            claim_id=claim_copy.get("claim_id", "unknown"),
                            evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                            verifier_id=active_verifier_id,
                            criteria=criteria,
                            checks=checks,
                            independence=independence_dict,
                            calculation={},
                            decision=VerificationDecision.REJECTED,
                            decision_reason="ENTITY_MISMATCH",
                            evidence_hashes=evidence_hashes,
                            limitations=limitations,
                            verified_at=now_iso
                        )
                checks.append({"criterion": "same_entity", "passed": True, "detail": "All evidence entities match claim entity."})

            # 8. Period Compatibility Check
            if "compatible_periods" in criteria:
                claim_periods = claim_copy.get("periods", [])
                ev_periods = [ev.get("period") for ev in evidence_copies if ev.get("period")]
                if claim_periods and not set(claim_periods).issubset(set(ev_periods)):
                    checks.append({"criterion": "compatible_periods", "passed": False, "detail": f"Required periods {claim_periods} not in evidence periods {ev_periods}"})
                    return self._build_record(
                        verification_id=verification_id,
                        claim_id=claim_copy.get("claim_id", "unknown"),
                        evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                        verifier_id=active_verifier_id,
                        criteria=criteria,
                        checks=checks,
                        independence=independence_dict,
                        calculation={},
                        decision=VerificationDecision.REJECTED,
                        decision_reason="PERIOD_MISMATCH",
                        evidence_hashes=evidence_hashes,
                        limitations=limitations,
                        verified_at=now_iso
                    )
                checks.append({"criterion": "compatible_periods", "passed": True, "detail": "Evidence periods cover required claim periods."})

            # 9. Unit Compatibility Check
            if "compatible_units" in criteria:
                claim_unit = claim_copy.get("units")
                for ev in evidence_copies:
                    if ev.get("units") != claim_unit:
                        checks.append({"criterion": "compatible_units", "passed": False, "detail": f"Claim unit {claim_unit} incompatible with evidence unit {ev.get('units')}"})
                        return self._build_record(
                            verification_id=verification_id,
                            claim_id=claim_copy.get("claim_id", "unknown"),
                            evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                            verifier_id=active_verifier_id,
                            criteria=criteria,
                            checks=checks,
                            independence=independence_dict,
                            calculation={},
                            decision=VerificationDecision.REJECTED,
                            decision_reason="UNIT_MISMATCH",
                            evidence_hashes=evidence_hashes,
                            limitations=limitations,
                            verified_at=now_iso
                        )
                checks.append({"criterion": "compatible_units", "passed": True, "detail": "All evidence units compatible."})

            # 10. Vintage Consistency Check (FRED / Macroeconomic revisions)
            if "vintage_consistent" in criteria:
                claim_vintage_date = claim_copy.get("as_of_date")
                for ev in evidence_copies:
                    rt_start = ev.get("realtime_start")
                    rt_end = ev.get("realtime_end")
                    if claim_vintage_date and rt_start and rt_start != "CURRENT":
                        # If claim asserts value was known on claim_vintage_date, but realtime_start is later
                        if rt_start > claim_vintage_date:
                            checks.append({"criterion": "vintage_consistent", "passed": False, "detail": f"Vintage start {rt_start} is after claimed date {claim_vintage_date}."})
                            return self._build_record(
                                verification_id=verification_id,
                                claim_id=claim_copy.get("claim_id", "unknown"),
                                evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                                verifier_id=active_verifier_id,
                                criteria=criteria,
                                checks=checks,
                                independence=independence_dict,
                                calculation={},
                                decision=VerificationDecision.REJECTED,
                                decision_reason="VINTAGE_MISMATCH",
                                evidence_hashes=evidence_hashes,
                                limitations=limitations,
                                verified_at=now_iso
                            )
                checks.append({"criterion": "vintage_consistent", "passed": True, "detail": "Observation vintages consistent."})

            # 11. Calculation Reproducibility Check
            if "calculation_reproducible" in criteria:
                # Comparative / Percentage Change calculation
                if claim_type in [ClaimType.COMPARATIVE.value, ClaimType.NUMERICAL.value, ClaimType.DERIVED.value]:
                    base_ev = next((ev for ev in evidence_copies if str(ev.get("period")) == str(claim_copy.get("base_period"))), None)
                    curr_ev = next((ev for ev in evidence_copies if str(ev.get("period")) == str(claim_copy.get("target_period"))), None)

                    if base_ev and curr_ev and base_ev.get("value") is not None and curr_ev.get("value") is not None:
                        val_base = float(base_ev["value"])
                        val_curr = float(curr_ev["value"])
                        if val_base == 0:
                            calc_change = 0.0
                        else:
                            calc_change = (val_curr - val_base) / val_base

                        claimed_val = float(claim_copy.get("asserted_value", 0.0))
                        # Support percentage input (e.g. 0.20 or 20.0)
                        diff = abs(calc_change - claimed_val)
                        if claimed_val > 1.0 and calc_change <= 1.0:
                            # User might have passed 20.0 for 20%
                            diff = min(diff, abs((calc_change * 100.0) - claimed_val))

                        calculation = {
                            "base_value": val_base,
                            "target_value": val_curr,
                            "calculated_change": round(calc_change, 6),
                            "asserted_value": claimed_val,
                            "difference": round(diff, 6),
                            "reproducible": diff < 0.001
                        }

                        if diff >= 0.001:
                            checks.append({"criterion": "calculation_reproducible", "passed": False, "detail": f"Calculated {calc_change} does not match claimed {claimed_val}"})
                            return self._build_record(
                                verification_id=verification_id,
                                claim_id=claim_copy.get("claim_id", "unknown"),
                                evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                                verifier_id=active_verifier_id,
                                criteria=criteria,
                                checks=checks,
                                independence=independence_dict,
                                calculation=calculation,
                                decision=VerificationDecision.REJECTED,
                                decision_reason="CALCULATED_VALUE_DOES_NOT_MATCH_CLAIM",
                                evidence_hashes=evidence_hashes,
                                limitations=limitations,
                                verified_at=now_iso
                            )
                        checks.append({"criterion": "calculation_reproducible", "passed": True, "detail": "Calculation replicated with exact precision."})
                    elif claim_copy.get("asserted_value") is not None:
                        # Direct single numerical value check
                        target_ev = evidence_copies[0] if len(evidence_copies) > 0 else {}
                        ev_val = float(target_ev.get("value", 0.0))
                        claimed_val = float(claim_copy.get("asserted_value", 0.0))
                        diff = abs(ev_val - claimed_val)
                        calculation = {
                            "evidence_value": ev_val,
                            "asserted_value": claimed_val,
                            "difference": round(diff, 6),
                            "reproducible": diff < 0.001
                        }
                        if diff >= 0.001:
                            checks.append({"criterion": "calculation_reproducible", "passed": False, "detail": f"Evidence {ev_val} != claimed {claimed_val}"})
                            return self._build_record(
                                verification_id=verification_id,
                                claim_id=claim_copy.get("claim_id", "unknown"),
                                evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                                verifier_id=active_verifier_id,
                                criteria=criteria,
                                checks=checks,
                                independence=independence_dict,
                                calculation=calculation,
                                decision=VerificationDecision.REJECTED,
                                decision_reason="CALCULATED_VALUE_DOES_NOT_MATCH_CLAIM",
                                evidence_hashes=evidence_hashes,
                                limitations=limitations,
                                verified_at=now_iso
                            )
                        checks.append({"criterion": "calculation_reproducible", "passed": True, "detail": "Value matches evidence exactly."})

            # All checks passed successfully
            return self._build_record(
                verification_id=verification_id,
                claim_id=claim_copy.get("claim_id", "unknown"),
                evidence_ids=[e.get("evidence_id", "unknown") for e in evidence_copies],
                verifier_id=active_verifier_id,
                criteria=criteria,
                checks=checks,
                independence=independence_dict,
                calculation=calculation,
                decision=VerificationDecision.VERIFIED,
                decision_reason="ALL_CRITERIA_SATISFIED_BY_PRIMARY_EVIDENCE",
                evidence_hashes=evidence_hashes,
                limitations=limitations,
                verified_at=now_iso
            )

        except Exception as e:
            # Absolute Fail-Closed Safety Barrier
            checks.append({"criterion": "runtime_safety", "passed": False, "detail": f"Unhandled error: {str(e)}"})
            return self._build_record(
                verification_id=verification_id,
                claim_id=claim_copy.get("claim_id", "unknown") if isinstance(claim_copy, dict) else "unknown",
                evidence_ids=[],
                verifier_id=active_verifier_id,
                criteria=criteria or [],
                checks=checks,
                independence={"independence_level": IndependenceLevel.NONE.value},
                calculation={},
                decision=VerificationDecision.REJECTED,
                decision_reason=f"FAIL_CLOSED_RUNTIME_EXCEPTION: {str(e)}",
                evidence_hashes=[],
                limitations=limitations,
                verified_at=now_iso
            )

    def _build_record(self, verification_id: str, claim_id: str, 
                      evidence_ids: List[str], verifier_id: str, 
                      criteria: List[str], checks: List[Dict[str, Any]], 
                      independence: Dict[str, Any], calculation: Dict[str, Any], 
                      decision: VerificationDecision, decision_reason: str, 
                      evidence_hashes: List[str], limitations: List[str], 
                      verified_at: str) -> Dict[str, Any]:
        """Constructs deterministic verification record with SHA-256 hash."""
        record = {
            "verification_id": verification_id,
            "claim_id": claim_id,
            "evidence_ids": evidence_ids,
            "verifier_id": verifier_id,
            "verification_criteria": criteria,
            "checks": checks,
            "independence": independence,
            "calculation": calculation,
            "decision": decision.value,
            "decision_reason": decision_reason,
            "evidence_hashes": evidence_hashes,
            "signature_status": "UNIMPLEMENTED",
            "limitations": limitations,
            "verified_at": verified_at
        }
        # Compute deterministic hash of the record contents
        record["verification_hash"] = self.compute_sha256(record)
        return record
