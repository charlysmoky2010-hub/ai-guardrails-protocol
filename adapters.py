"""
Financial Source Adapters Architecture (SEC EDGAR & FRED).
Explicitly marks execution status as CODE_PRESENT_NOT_EXECUTED until real network credentials and endpoints are actively invoked.
"""

from typing import Dict, Any, Optional
from enum import Enum
import hashlib
import json

class SourceClass(str, Enum):
    PRIMARY_GOVERNMENT_SOURCE = "PRIMARY_GOVERNMENT_SOURCE"
    PRIMARY_REGULATORY_FILING = "PRIMARY_REGULATORY_FILING"
    PUBLIC_DATASET = "PUBLIC_DATASET"
    SECONDARY_SOURCE = "SECONDARY_SOURCE"
    LLM_OUTPUT = "LLM_OUTPUT"
    USER_ASSERTION = "USER_ASSERTION"
    DERIVED_CALCULATION = "DERIVED_CALCULATION"

class ExecutionStatus(str, Enum):
    CODE_PRESENT_NOT_EXECUTED = "CODE_PRESENT_NOT_EXECUTED"
    EXECUTED = "EXECUTED"

class BaseFinancialAdapter:
    """Base interface for authoritative primary evidence sources."""
    execution_status: str = ExecutionStatus.CODE_PRESENT_NOT_EXECUTED

    @staticmethod
    def compute_raw_hash(data: Any) -> str:
        canonical_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

class SECEdgarAdapter(BaseFinancialAdapter):
    """
    Interface adapter for SEC EDGAR Regulatory Filings (10-K, 10-Q, 8-K).
    Source Classification: PRIMARY_REGULATORY_FILING
    """
    source_class = SourceClass.PRIMARY_REGULATORY_FILING
    source_id = "SEC_EDGAR"

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent

    def fetch_filing_evidence(self, entity_cik: str, form_type: str, period: str, financial_metric: str) -> Dict[str, Any]:
        """
        Architectural interface for SEC EDGAR retrieval.
        NOTE: Returns CODE_PRESENT_NOT_EXECUTED when network fetch is not live.
        """
        return {
            "source_id": self.source_id,
            "source_class": self.source_class.value,
            "execution_status": self.execution_status.value,
            "entity": entity_cik,
            "form": form_type,
            "period": period,
            "metric": financial_metric,
            "value": None,
            "raw_response_hash": None,
            "provenance_note": "Interface present. Network execution not performed in this offline environment."
        }

class FREDAdapter(BaseFinancialAdapter):
    """
    Interface adapter for Federal Reserve Economic Data (FRED).
    Source Classification: PRIMARY_GOVERNMENT_SOURCE / PUBLIC_DATASET
    Supports vintage management (CURRENT_VINTAGE vs HISTORICAL_VINTAGE).
    """
    source_class = SourceClass.PRIMARY_GOVERNMENT_SOURCE
    source_id = "FRED_ST_LOUIS"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def fetch_series_observation(self, series_id: str, observation_date: str, vintage_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Architectural interface for FRED macroeconomic observation.
        NOTE: Returns CODE_PRESENT_NOT_EXECUTED when network fetch is not live.
        """
        is_historical = vintage_date is not None
        vintage_type = "HISTORICAL_VINTAGE" if is_historical else "CURRENT_VINTAGE"
        
        return {
            "source_id": self.source_id,
            "source_class": self.source_class.value,
            "execution_status": self.execution_status.value,
            "series_id": series_id,
            "observation_date": observation_date,
            "vintage_type": vintage_type,
            "realtime_start": vintage_date or "CURRENT",
            "realtime_end": vintage_date or "CURRENT",
            "value": None,
            "units": None,
            "raw_response_hash": None,
            "provenance_note": "Interface present. Network execution not performed in this offline environment."
        }
