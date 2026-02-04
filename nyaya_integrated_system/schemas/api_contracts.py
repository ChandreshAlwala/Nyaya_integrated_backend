"""
Frozen API Contracts - Production Schema
Single request → response schema as per Day 1 requirements
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
from datetime import datetime

# Enums
class JurisdictionEnum(str, Enum):
    INDIA = "IN"
    UAE = "UAE"
    UK = "UK"

class DomainEnum(str, Enum):
    CRIMINAL = "CRIMINAL"
    CIVIL = "CIVIL"
    FAMILY = "FAMILY"
    CONSUMER_COMMERCIAL = "CONSUMER_COMMERCIAL"

class FeedbackTypeEnum(str, Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    USABILITY = "usability"

# Core Request Models
class LegalQueryRequest(BaseModel):
    query: str = Field(..., description="Legal question or scenario")
    jurisdiction_hint: Optional[JurisdictionEnum] = None
    domain_hint: Optional[DomainEnum] = None
    evidence_documents: Optional[List[str]] = []
    
class MultiJurisdictionRequest(BaseModel):
    query: str = Field(..., description="Legal question for comparative analysis")
    jurisdictions: List[JurisdictionEnum] = Field(..., min_items=2, max_items=3)
    domain_hint: Optional[DomainEnum] = None

class FeedbackRequest(BaseModel):
    trace_id: str = Field(..., description="Original query trace ID")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback_type: FeedbackTypeEnum
    comment: Optional[str] = None

# Core Response Models
class LegalRoute(BaseModel):
    step: str
    description: str
    timeline: Optional[str] = None
    evidence_required: List[str] = []
    outcome_probability: Optional[float] = None

class EnforcementMetadata(BaseModel):
    rule_id: str
    policy_source: str
    reasoning: str
    signed_proof: Dict[str, Any]

class LegalQueryResponse(BaseModel):
    trace_id: str
    domain: str
    jurisdiction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    legal_route: List[LegalRoute]
    glossary_terms: Dict[str, str] = {}
    evidence_readiness: str
    timeline_estimate: Optional[str] = None
    enforcement_metadata: Optional[EnforcementMetadata] = None
    provenance_chain: List[Dict[str, Any]] = []
    reasoning_trace: Dict[str, Any] = {}

class MultiJurisdictionResponse(BaseModel):
    trace_id: str
    comparative_analysis: Dict[JurisdictionEnum, LegalQueryResponse]
    confidence: float = Field(..., ge=0.0, le=1.0)
    cross_jurisdiction_insights: List[str] = []
    enforcement_metadata: Optional[EnforcementMetadata] = None

class FeedbackResponse(BaseModel):
    status: Literal["recorded", "blocked"]
    trace_id: str
    message: str
    enforcement_metadata: Optional[EnforcementMetadata] = None

class TraceResponse(BaseModel):
    trace_id: str
    query: str
    timestamp: datetime
    processing_steps: List[Dict[str, Any]]
    enforcement_decisions: List[Dict[str, Any]]
    rl_updates: List[Dict[str, Any]]
    final_response: Dict[str, Any]

# Error Response
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    trace_id: str
    timestamp: datetime