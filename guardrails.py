"""
PHI-BRAIN Guardrails Protocol (v1.0.0)
Lightweight, Fail-Closed Truth Boundary & Execution Guardrails for Autonomous AI Agents.
"""

from typing import Dict, Any, Optional

class GuardrailViolation(Exception):
    """Raised when an agent attempts to violate epistemic or safety boundaries."""
    pass

class TruthBoundaryEnforcer:
    """
    Enforces the epistemic constraint: CLAIM != EVIDENCE.
    No model output can transition to VERIFIED without independent external proof.
    """
    
    ALLOWED_STATES = {"OBSERVED", "INFERRED", "PROPOSED", "UNVERIFIED", "FAILED"}
    
    @staticmethod
    def validate_observation(record: Dict[str, Any]) -> bool:
        state = record.get("state")
        verification = record.get("verification_status")
        
        # Guardrail 1: Disallow self-proclaimed VERIFIED state
        if verification == "VERIFIED" and not record.get("independent_verifier"):
            raise GuardrailViolation(
                f"EPISTEMIC BREACH: Record '{record.get('entity')}' cannot claim VERIFIED "
                f"without an external 'independent_verifier'."
            )
            
        # Guardrail 2: Ensure valid epistemic state tag
        if state not in TruthBoundaryEnforcer.ALLOWED_STATES:
            raise GuardrailViolation(
                f"INVALID STATE: '{state}' is not a recognized epistemic state. Must be in {TruthBoundaryEnforcer.ALLOWED_STATES}."
            )
            
        return True

    @staticmethod
    def sanitize_financial_action(action_type: str, amount_eur: float, human_approved: bool = False) -> bool:
        """Fail-closed barrier on autonomous fund movements."""
        if amount_eur > 0 and not human_approved:
            raise GuardrailViolation(
                f"SAFETY SHIELD ACTIVATED: Autonomous transaction of €{amount_eur} blocked. "
                "Explicit human approval required."
            )
        return True
