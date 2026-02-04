"""
API Orchestrator - Nilesh's Implementation
Handles orchestration, API exposure, request flow, and integration
between legal engine, enforcement, and RL components
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import BackgroundTasks

from .legal_engine import LegalDecisionEngine
from .enforcement_engine import SovereignEnforcementEngine, create_enforcement_signal
from .rl_engine import RLFeedbackEngine
from schemas.api_contracts import *

class APIOrchestrator:
    def __init__(self, legal_engine: LegalDecisionEngine, enforcement_engine: SovereignEnforcementEngine):
        self.legal_engine = legal_engine
        self.enforcement_engine = enforcement_engine
        self.rl_engine = RLFeedbackEngine()
        self.request_log = []
        
    async def process_legal_query(self, request: LegalQueryRequest, trace_id: str, 
                                background_tasks: BackgroundTasks) -> LegalQueryResponse:
        """Process single legal query with full enforcement pipeline"""
        
        # Log request
        self._log_request("legal_query", request.dict(), trace_id)
        
        # Step 1: Create enforcement signal for initial validation
        signal = create_enforcement_signal(
            case_id=trace_id,
            country=request.jurisdiction_hint.value if request.jurisdiction_hint else "unknown",
            domain=request.domain_hint.value if request.domain_hint else "general",
            procedure_id="legal_query_processing",
            original_confidence=0.5,  # Initial confidence
            user_request=request.query,
            jurisdiction_routed_to=request.jurisdiction_hint.value if request.jurisdiction_hint else "auto",
            trace_id=trace_id
        )
        
        # Step 2: Check enforcement permission
        enforcement_response = self.enforcement_engine.get_enforcement_response(signal)
        
        if enforcement_response["status"] == "blocked":
            # Return blocked response with enforcement metadata
            return LegalQueryResponse(
                trace_id=trace_id,
                domain=request.domain_hint.value if request.domain_hint else "general",
                jurisdiction=request.jurisdiction_hint.value if request.jurisdiction_hint else "unknown",
                confidence=0.0,
                legal_route=[],
                evidence_readiness="BLOCKED",
                enforcement_metadata=EnforcementMetadata(
                    rule_id=enforcement_response["rule_id"],
                    policy_source=enforcement_response["policy_source"],
                    reasoning=enforcement_response["reasoning"],
                    signed_proof=enforcement_response["trace_proof"]
                ),
                provenance_chain=[enforcement_response["trace_proof"]]
            )
        
        # Step 3: Process through legal engine
        jurisdiction = request.jurisdiction_hint.value if request.jurisdiction_hint else "IN"
        domain_hint = request.domain_hint.value if request.domain_hint else None
        
        legal_result = await self.legal_engine.process_legal_query(
            query=request.query,
            jurisdiction=jurisdiction,
            domain_hint=domain_hint,
            trace_id=trace_id
        )
        
        # Step 4: Apply RL confidence adjustments
        adjusted_confidence = self.rl_engine.get_confidence_adjustment(
            domain=legal_result["domain"],
            jurisdiction=legal_result["jurisdiction"],
            base_confidence=legal_result["confidence"]
        )
        
        # Step 5: Create final enforcement signal with actual confidence
        final_signal = create_enforcement_signal(
            case_id=trace_id,
            country=legal_result["jurisdiction"],
            domain=legal_result["domain"],
            procedure_id="legal_query_final",
            original_confidence=adjusted_confidence,
            user_request=request.query,
            jurisdiction_routed_to=legal_result["jurisdiction"],
            trace_id=trace_id
        )
        
        final_enforcement = self.enforcement_engine.get_enforcement_response(final_signal)
        
        # Step 6: Build legal route
        legal_route = []
        for step in legal_result.get("legal_route", []):
            legal_route.append(LegalRoute(
                step=step["step"],
                description=step["description"],
                timeline=step.get("timeline"),
                evidence_required=step.get("evidence_required", []),
                outcome_probability=step.get("outcome_probability")
            ))
        
        # Step 7: Determine evidence readiness
        evidence_readiness = self._assess_evidence_readiness(
            request.evidence_documents or [],
            legal_result.get("evidence_requirements", [])
        )
        
        # Step 8: Build response
        response = LegalQueryResponse(
            trace_id=trace_id,
            domain=legal_result["domain"],
            jurisdiction=legal_result["jurisdiction"],
            confidence=adjusted_confidence,
            legal_route=legal_route,
            glossary_terms=legal_result.get("glossary_terms", {}),
            evidence_readiness=evidence_readiness,
            timeline_estimate=legal_result.get("timeline_estimate"),
            enforcement_metadata=EnforcementMetadata(
                rule_id=final_enforcement["rule_id"],
                policy_source=final_enforcement["policy_source"],
                reasoning=final_enforcement["reasoning"],
                signed_proof=final_enforcement["trace_proof"]
            ),
            provenance_chain=[final_enforcement["trace_proof"]],
            reasoning_trace={
                "legal_processing": legal_result,
                "rl_adjustment": {
                    "original_confidence": legal_result["confidence"],
                    "adjusted_confidence": adjusted_confidence
                },
                "enforcement_decisions": [enforcement_response, final_enforcement]
            }
        )
        
        # Background task: Log processing completion
        if background_tasks:
            background_tasks.add_task(
                self._log_processing_completion,
                trace_id,
                "legal_query",
                adjusted_confidence
            )
        
        return response
    
    async def process_multi_jurisdiction(self, request: MultiJurisdictionRequest, trace_id: str,
                                       background_tasks: BackgroundTasks) -> MultiJurisdictionResponse:
        """Process multi-jurisdiction comparative analysis"""
        
        self._log_request("multi_jurisdiction", request.dict(), trace_id)
        
        comparative_analysis = {}
        confidences = []
        
        # Process each jurisdiction
        for jurisdiction in request.jurisdictions:
            jur_trace_id = f"{trace_id}_{jurisdiction.value}"
            
            # Create single query request for this jurisdiction
            single_request = LegalQueryRequest(
                query=request.query,
                jurisdiction_hint=jurisdiction,
                domain_hint=request.domain_hint,
                evidence_documents=[]
            )
            
            # Process through single query pipeline
            jur_response = await self.process_legal_query(single_request, jur_trace_id, None)
            
            comparative_analysis[jurisdiction] = jur_response
            confidences.append(jur_response.confidence)
        
        # Calculate aggregate confidence
        aggregate_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Generate cross-jurisdiction insights
        insights = self._generate_cross_jurisdiction_insights(comparative_analysis)
        
        # Create final enforcement metadata
        final_signal = create_enforcement_signal(
            case_id=trace_id,
            country="multi",
            domain=request.domain_hint.value if request.domain_hint else "general",
            procedure_id="multi_jurisdiction_analysis",
            original_confidence=aggregate_confidence,
            user_request=request.query,
            jurisdiction_routed_to="multi",
            trace_id=trace_id
        )
        
        final_enforcement = self.enforcement_engine.get_enforcement_response(final_signal)
        
        response = MultiJurisdictionResponse(
            trace_id=trace_id,
            comparative_analysis=comparative_analysis,
            confidence=aggregate_confidence,
            cross_jurisdiction_insights=insights,
            enforcement_metadata=EnforcementMetadata(
                rule_id=final_enforcement["rule_id"],
                policy_source=final_enforcement["policy_source"],
                reasoning=final_enforcement["reasoning"],
                signed_proof=final_enforcement["trace_proof"]
            )
        )
        
        if background_tasks:
            background_tasks.add_task(
                self._log_processing_completion,
                trace_id,
                "multi_jurisdiction",
                aggregate_confidence
            )
        
        return response
    
    async def process_feedback(self, request: FeedbackRequest, trace_id: str,
                             background_tasks: BackgroundTasks) -> FeedbackResponse:
        """Process RL feedback with enforcement validation"""
        
        self._log_request("feedback", request.dict(), trace_id)
        
        # Process through RL engine (includes enforcement validation)
        rl_result = await self.rl_engine.process_feedback(
            trace_id=request.trace_id,
            rating=request.rating,
            feedback_type=request.feedback_type.value,
            comment=request.comment,
            user_request=f"Feedback for {request.trace_id}"
        )
        
        # Create enforcement metadata if blocked
        enforcement_metadata = None
        if rl_result.get("enforcement_blocked"):
            signal = create_enforcement_signal(
                case_id=request.trace_id,
                country="global",
                domain="feedback",
                procedure_id="feedback_submission",
                original_confidence=0.5,
                user_request=f"Rating: {request.rating}",
                jurisdiction_routed_to="global",
                trace_id=request.trace_id
            )
            
            enforcement_response = self.enforcement_engine.get_enforcement_response(signal)
            enforcement_metadata = EnforcementMetadata(
                rule_id=enforcement_response["rule_id"],
                policy_source=enforcement_response["policy_source"],
                reasoning=enforcement_response["reasoning"],
                signed_proof=enforcement_response["trace_proof"]
            )
        
        response = FeedbackResponse(
            status=rl_result["status"],
            trace_id=request.trace_id,
            message=rl_result["message"],
            enforcement_metadata=enforcement_metadata
        )
        
        if background_tasks:
            background_tasks.add_task(
                self._log_processing_completion,
                trace_id,
                "feedback",
                request.rating / 5.0
            )
        
        return response
    
    async def get_trace(self, trace_id: str) -> TraceResponse:
        """Get complete audit trail for trace ID"""
        
        # Get request log entry
        request_entry = next((r for r in self.request_log if r["trace_id"] == trace_id), None)
        
        if not request_entry:
            raise ValueError(f"Trace {trace_id} not found")
        
        # Get enforcement decisions
        enforcement_decisions = self.enforcement_engine.get_trace_audit(trace_id)
        
        # Get RL feedback
        rl_updates = self.rl_engine.get_trace_feedback(trace_id)
        
        # Build processing steps
        processing_steps = [
            {
                "step": "request_received",
                "timestamp": request_entry["timestamp"],
                "data": request_entry["request_data"]
            },
            {
                "step": "enforcement_validation",
                "timestamp": request_entry["timestamp"],
                "data": enforcement_decisions
            }
        ]
        
        if rl_updates:
            processing_steps.append({
                "step": "rl_feedback_processed",
                "timestamp": rl_updates[-1]["timestamp"] if rl_updates else request_entry["timestamp"],
                "data": rl_updates
            })
        
        return TraceResponse(
            trace_id=trace_id,
            query=request_entry["request_data"].get("query", ""),
            timestamp=datetime.fromisoformat(request_entry["timestamp"]),
            processing_steps=processing_steps,
            enforcement_decisions=enforcement_decisions,
            rl_updates=rl_updates,
            final_response=request_entry.get("final_response", {})
        )
    
    def _log_request(self, request_type: str, request_data: Dict[str, Any], trace_id: str):
        """Log incoming request"""
        self.request_log.append({
            "trace_id": trace_id,
            "request_type": request_type,
            "request_data": request_data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _log_processing_completion(self, trace_id: str, request_type: str, confidence: float):
        """Background task to log processing completion"""
        # Update request log with completion data
        for entry in self.request_log:
            if entry["trace_id"] == trace_id:
                entry["completed_at"] = datetime.utcnow().isoformat()
                entry["final_confidence"] = confidence
                break
    
    def _assess_evidence_readiness(self, provided_documents: List[str], 
                                 required_documents: List[str]) -> str:
        """Assess evidence readiness based on provided vs required documents"""
        if not required_documents:
            return "EVIDENCE_COMPLETE"
        
        provided_set = set(provided_documents)
        required_set = set(required_documents)
        
        if required_set.issubset(provided_set):
            return "EVIDENCE_COMPLETE"
        elif len(provided_set.intersection(required_set)) > 0:
            return "EVIDENCE_PARTIAL"
        else:
            return "EVIDENCE_MISSING"
    
    def _generate_cross_jurisdiction_insights(self, comparative_analysis: Dict[JurisdictionEnum, LegalQueryResponse]) -> List[str]:
        """Generate insights from cross-jurisdiction comparison"""
        insights = []
        
        # Compare confidence levels
        confidences = {jur: resp.confidence for jur, resp in comparative_analysis.items()}
        max_confidence_jur = max(confidences.items(), key=lambda x: x[1])
        
        insights.append(f"Highest confidence in {max_confidence_jur[0].value} jurisdiction ({max_confidence_jur[1]:.2f})")
        
        # Compare legal routes
        route_lengths = {jur: len(resp.legal_route) for jur, resp in comparative_analysis.items()}
        if route_lengths:
            min_route_jur = min(route_lengths.items(), key=lambda x: x[1])
            insights.append(f"Shortest legal procedure in {min_route_jur[0].value} ({min_route_jur[1]} steps)")
        
        # Compare domains
        domains = {jur: resp.domain for jur, resp in comparative_analysis.items()}
        unique_domains = set(domains.values())
        if len(unique_domains) > 1:
            insights.append(f"Different legal domains identified: {', '.join(unique_domains)}")
        
        return insights