"""
Sovereign Enforcement Engine - Chandresh's Implementation
Routes all legal decisions through deterministic governance
Every response carries trace_id and signed proof
"""
import json
import hashlib
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid

class EnforcementDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    SOFT_REDIRECT = "SOFT_REDIRECT"

class PolicySource(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    SYSTEM_SAFETY = "SYSTEM_SAFETY"
    LEGAL_COMPLIANCE = "LEGAL_COMPLIANCE"

class EnforcementSignal:
    def __init__(self, case_id: str, country: str, domain: str, procedure_id: str,
                 original_confidence: float, user_request: str, jurisdiction_routed_to: str,
                 trace_id: str, user_feedback: Optional[str] = None, outcome_tag: Optional[str] = None):
        self.case_id = case_id
        self.country = country
        self.domain = domain
        self.procedure_id = procedure_id
        self.original_confidence = original_confidence
        self.user_request = user_request
        self.jurisdiction_routed_to = jurisdiction_routed_to
        self.trace_id = trace_id
        self.user_feedback = user_feedback
        self.outcome_tag = outcome_tag
        self.timestamp = datetime.utcnow()

class EnforcementResult:
    def __init__(self, decision: EnforcementDecision, rule_id: str, policy_source: PolicySource,
                 reasoning_summary: str, trace_id: str, timestamp: datetime,
                 signed_decision_object: Dict[str, Any], proof_hash: str):
        self.decision = decision
        self.rule_id = rule_id
        self.policy_source = policy_source
        self.reasoning_summary = reasoning_summary
        self.trace_id = trace_id
        self.timestamp = timestamp
        self.signed_decision_object = signed_decision_object
        self.proof_hash = proof_hash

class SovereignEnforcementEngine:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.enforcement_rules = []
        self.decision_ledger = []
        self.signing_key = "nyaya_sovereign_key_2024"
        self._thread_lock = threading.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize enforcement rules and policies"""
        if self._initialized:
            return
            
        # Load enforcement rules
        self.enforcement_rules = [
            {
                "rule_id": "SAFETY_001",
                "description": "Block queries with harmful intent",
                "policy_source": PolicySource.SYSTEM_SAFETY,
                "condition": lambda signal: self._check_harmful_content(signal.user_request),
                "decision": EnforcementDecision.BLOCK
            },
            {
                "rule_id": "GOVERNANCE_001", 
                "description": "Allow legal queries with sufficient confidence",
                "policy_source": PolicySource.GOVERNANCE,
                "condition": lambda signal: signal.original_confidence >= 0.3,
                "decision": EnforcementDecision.ALLOW
            },
            {
                "rule_id": "GOVERNANCE_002",
                "description": "Escalate low confidence queries",
                "policy_source": PolicySource.GOVERNANCE,
                "condition": lambda signal: signal.original_confidence < 0.3,
                "decision": EnforcementDecision.ESCALATE
            },
            {
                "rule_id": "LEGAL_001",
                "description": "Allow feedback for completed queries",
                "policy_source": PolicySource.LEGAL_COMPLIANCE,
                "condition": lambda signal: signal.procedure_id == "feedback_submission",
                "decision": EnforcementDecision.ALLOW
            }
        ]
        
        self._initialized = True
    
    def make_enforcement_decision(self, signal: EnforcementSignal) -> EnforcementResult:
        """Make deterministic enforcement decision"""
        with self._thread_lock:
            # Evaluate rules in order
            for rule in self.enforcement_rules:
                try:
                    if rule["condition"](signal):
                        decision = rule["decision"]
                        rule_id = rule["rule_id"]
                        policy_source = rule["policy_source"]
                        reasoning = rule["description"]
                        break
                except Exception:
                    continue
            else:
                # Default decision if no rules match
                decision = EnforcementDecision.ALLOW
                rule_id = "DEFAULT_ALLOW"
                policy_source = PolicySource.GOVERNANCE
                reasoning = "Default allow policy"
            
            # Generate proof hash
            proof_data = f"{signal.trace_id}:{decision.value}:{rule_id}:{signal.timestamp.isoformat()}"
            proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()
            
            # Create signed decision object
            signed_decision = self._create_signed_decision(signal, decision, rule_id, proof_hash)
            
            # Create result
            result = EnforcementResult(
                decision=decision,
                rule_id=rule_id,
                policy_source=policy_source,
                reasoning_summary=reasoning,
                trace_id=signal.trace_id,
                timestamp=signal.timestamp,
                signed_decision_object=signed_decision,
                proof_hash=proof_hash
            )
            
            # Log to ledger
            self.decision_ledger.append({
                "trace_id": signal.trace_id,
                "timestamp": signal.timestamp.isoformat(),
                "decision": decision.value,
                "rule_id": rule_id,
                "proof_hash": proof_hash,
                "signal_data": {
                    "case_id": signal.case_id,
                    "country": signal.country,
                    "domain": signal.domain,
                    "confidence": signal.original_confidence
                }
            })
            
            return result
    
    def _check_harmful_content(self, user_request: str) -> bool:
        """Check for harmful content in user request"""
        harmful_keywords = ["hack", "illegal", "fraud", "violence", "harm"]
        request_lower = user_request.lower()
        return any(keyword in request_lower for keyword in harmful_keywords)
    
    def _create_signed_decision(self, signal: EnforcementSignal, decision: EnforcementDecision, 
                              rule_id: str, proof_hash: str) -> Dict[str, Any]:
        """Create cryptographically signed decision object"""
        decision_data = {
            "trace_id": signal.trace_id,
            "decision": decision.value,
            "rule_id": rule_id,
            "timestamp": signal.timestamp.isoformat(),
            "proof_hash": proof_hash,
            "jurisdiction": signal.jurisdiction_routed_to,
            "domain": signal.domain
        }
        
        # Simple signing (in production, use proper cryptographic signing)
        signature_data = json.dumps(decision_data, sort_keys=True) + self.signing_key
        signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return {
            "decision_data": decision_data,
            "signature": signature,
            "signed_at": datetime.utcnow().isoformat(),
            "signer": "nyaya_sovereign_engine"
        }
    
    def is_execution_permitted(self, signal: EnforcementSignal) -> bool:
        """Check if execution is permitted"""
        result = self.make_enforcement_decision(signal)
        return result.decision in [EnforcementDecision.ALLOW, EnforcementDecision.SOFT_REDIRECT]
    
    def get_enforcement_response(self, signal: EnforcementSignal) -> Dict[str, Any]:
        """Get complete enforcement response with proof"""
        result = self.make_enforcement_decision(signal)
        
        return {
            "status": "allowed" if result.decision in [EnforcementDecision.ALLOW, EnforcementDecision.SOFT_REDIRECT] else "blocked",
            "decision": result.decision.value,
            "rule_id": result.rule_id,
            "policy_source": result.policy_source.value,
            "reasoning": result.reasoning_summary,
            "trace_proof": result.signed_decision_object,
            "proof_hash": result.proof_hash,
            "timestamp": result.timestamp.isoformat()
        }
    
    def get_trace_audit(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get complete audit trail for trace ID"""
        return [entry for entry in self.decision_ledger if entry["trace_id"] == trace_id]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for enforcement engine"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "rules_loaded": len(self.enforcement_rules),
            "decisions_logged": len(self.decision_ledger),
            "last_decision": self.decision_ledger[-1]["timestamp"] if self.decision_ledger else None
        }
    
    async def shutdown(self):
        """Cleanup resources"""
        # Save decision ledger to persistent storage in production
        self.decision_ledger.clear()
        self._initialized = False

# Global functions for external use
def create_enforcement_signal(case_id: str, country: str, domain: str, procedure_id: str,
                            original_confidence: float, user_request: str, 
                            jurisdiction_routed_to: str, trace_id: str,
                            user_feedback: Optional[str] = None, 
                            outcome_tag: Optional[str] = None) -> EnforcementSignal:
    """Create enforcement signal"""
    return EnforcementSignal(
        case_id=case_id,
        country=country,
        domain=domain,
        procedure_id=procedure_id,
        original_confidence=original_confidence,
        user_request=user_request,
        jurisdiction_routed_to=jurisdiction_routed_to,
        trace_id=trace_id,
        user_feedback=user_feedback,
        outcome_tag=outcome_tag
    )

def enforce_request(signal: EnforcementSignal) -> EnforcementResult:
    """Global function to enforce a request"""
    engine = SovereignEnforcementEngine()
    return engine.make_enforcement_decision(signal)

def is_execution_permitted(signal: EnforcementSignal) -> bool:
    """Global function to check if execution is permitted"""
    engine = SovereignEnforcementEngine()
    return engine.is_execution_permitted(signal)

def get_enforcement_response(signal: EnforcementSignal) -> Dict[str, Any]:
    """Global function to get enforcement response"""
    engine = SovereignEnforcementEngine()
    return engine.get_enforcement_response(signal)