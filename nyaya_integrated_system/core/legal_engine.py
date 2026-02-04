"""
Legal Decision Engine - Raj's Implementation
Binds Nyaya datasets (IN/UAE/UK) into decision flow
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

class LegalDecisionEngine:
    def __init__(self):
        self.datasets = {}
        self.domain_maps = {}
        self.procedures = {}
        self.initialized = False
        
    async def initialize(self):
        """Load all legal datasets and procedures"""
        if self.initialized:
            return
            
        # Load datasets from Nyaya_AI/db/
        dataset_path = os.path.join(os.path.dirname(__file__), '..', '..', 'Nyaya_AI', 'db')
        
        # Load domain maps
        self.domain_maps = {
            'IN': self._load_json(os.path.join(dataset_path, 'indian_domain_map.json')),
            'UAE': self._load_json(os.path.join(dataset_path, 'uae_domain_map.json')),
            'UK': self._load_json(os.path.join(dataset_path, 'uk_domain_map.json'))
        }
        
        # Load legal datasets
        self.datasets = {
            'IN': self._load_json(os.path.join(dataset_path, 'indian_law_dataset.json')),
            'UAE': self._load_json(os.path.join(dataset_path, 'uae_law_dataset.json')),
            'UK': self._load_json(os.path.join(dataset_path, 'uk_law_dataset.json'))
        }
        
        # Load procedures from datasets repo
        procedures_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nyaya-legal-procedure-datasets', 'data', 'procedures')
        
        for jurisdiction in ['india', 'uae', 'uk']:
            jur_key = {'india': 'IN', 'uae': 'UAE', 'uk': 'UK'}[jurisdiction]
            self.procedures[jur_key] = {}
            
            for domain in ['civil', 'criminal', 'family', 'consumer_commercial']:
                proc_file = os.path.join(procedures_path, jurisdiction, f'{domain}.json')
                self.procedures[jur_key][domain.upper()] = self._load_json(proc_file)
        
        self.initialized = True
        
    def _load_json(self, filepath: str) -> Dict[str, Any]:
        """Load JSON file safely"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    async def process_legal_query(self, query: str, jurisdiction: str, domain_hint: Optional[str] = None, trace_id: str = None) -> Dict[str, Any]:
        """Process legal query and return structured response"""
        
        # Domain detection
        detected_domain = self._detect_domain(query, jurisdiction, domain_hint)
        
        # Get legal route from procedures
        legal_route = self._get_legal_route(detected_domain, jurisdiction)
        
        # Calculate confidence based on domain match and data availability
        confidence = self._calculate_confidence(query, jurisdiction, detected_domain)
        
        # Get evidence requirements
        evidence_requirements = self._get_evidence_requirements(legal_route)
        
        # Get timeline estimates
        timeline_estimate = self._get_timeline_estimate(legal_route)
        
        # Get glossary terms
        glossary_terms = self._extract_glossary_terms(query, jurisdiction)
        
        return {
            "domain": detected_domain,
            "jurisdiction": jurisdiction,
            "confidence": confidence,
            "legal_route": legal_route,
            "evidence_requirements": evidence_requirements,
            "timeline_estimate": timeline_estimate,
            "glossary_terms": glossary_terms,
            "trace_id": trace_id
        }
    
    def _detect_domain(self, query: str, jurisdiction: str, domain_hint: Optional[str] = None) -> str:
        """Detect legal domain from query"""
        if domain_hint:
            return domain_hint
            
        query_lower = query.lower()
        
        # Domain keywords mapping
        domain_keywords = {
            "CRIMINAL": ["crime", "criminal", "theft", "murder", "assault", "fraud", "police", "arrest"],
            "CIVIL": ["contract", "property", "tort", "damages", "breach", "civil", "dispute"],
            "FAMILY": ["marriage", "divorce", "custody", "family", "spouse", "child", "adoption"],
            "CONSUMER_COMMERCIAL": ["consumer", "commercial", "business", "trade", "company", "purchase"]
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            scores[domain] = sum(1 for keyword in keywords if keyword in query_lower)
        
        # Return domain with highest score, default to CIVIL
        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else "CIVIL"
    
    def _get_legal_route(self, domain: str, jurisdiction: str) -> List[Dict[str, Any]]:
        """Get legal procedure route for domain and jurisdiction"""
        if jurisdiction not in self.procedures or domain not in self.procedures[jurisdiction]:
            return self._get_default_route(domain)
        
        procedures = self.procedures[jurisdiction][domain]
        route = []
        
        # Extract procedure steps
        if isinstance(procedures, dict) and "procedures" in procedures:
            for proc in procedures["procedures"]:
                if isinstance(proc, dict):
                    route.append({
                        "step": proc.get("step", "Unknown Step"),
                        "description": proc.get("description", ""),
                        "timeline": proc.get("timeline", "Not specified"),
                        "evidence_required": proc.get("evidence_required", []),
                        "outcome_probability": proc.get("outcome_probability", 0.5)
                    })
        
        return route if route else self._get_default_route(domain)
    
    def _get_default_route(self, domain: str) -> List[Dict[str, Any]]:
        """Get default legal route for domain"""
        default_routes = {
            "CRIMINAL": [
                {"step": "CRIME_REPORTING", "description": "Initial reporting of alleged offence", "timeline": "1-7 days"},
                {"step": "INVESTIGATION", "description": "Fact-finding and evidence collection", "timeline": "30-90 days"},
                {"step": "TRIAL", "description": "Judicial adjudication on merits", "timeline": "6-18 months"},
                {"step": "JUDGMENT", "description": "Final determination by court", "timeline": "1-30 days"}
            ],
            "CIVIL": [
                {"step": "CASE_ALLOCATION", "description": "Allocation to appropriate court", "timeline": "7-14 days"},
                {"step": "SETTLEMENT_ATTEMPT", "description": "Formal attempt to resolve dispute", "timeline": "30-60 days"},
                {"step": "TRIAL", "description": "Judicial adjudication on merits", "timeline": "6-24 months"},
                {"step": "JUDGMENT", "description": "Final determination by court", "timeline": "1-30 days"}
            ],
            "FAMILY": [
                {"step": "MEDIATION_ATTEMPT", "description": "Facilitated reconciliation", "timeline": "30-90 days"},
                {"step": "TRIAL", "description": "Judicial adjudication on merits", "timeline": "3-12 months"},
                {"step": "JUDGMENT", "description": "Final determination by court", "timeline": "1-30 days"}
            ],
            "CONSUMER_COMMERCIAL": [
                {"step": "SETTLEMENT_ATTEMPT", "description": "Commercial dispute resolution", "timeline": "15-45 days"},
                {"step": "TRIAL", "description": "Judicial adjudication on merits", "timeline": "6-18 months"},
                {"step": "JUDGMENT", "description": "Final determination by court", "timeline": "1-30 days"}
            ]
        }
        
        return default_routes.get(domain, default_routes["CIVIL"])
    
    def _calculate_confidence(self, query: str, jurisdiction: str, domain: str) -> float:
        """Calculate confidence score based on data availability and query match"""
        base_confidence = 0.7
        
        # Adjust based on jurisdiction data availability
        if jurisdiction in self.datasets and self.datasets[jurisdiction]:
            base_confidence += 0.1
        
        # Adjust based on domain procedures availability
        if (jurisdiction in self.procedures and 
            domain in self.procedures[jurisdiction] and 
            self.procedures[jurisdiction][domain]):
            base_confidence += 0.1
        
        # Adjust based on query length and specificity
        if len(query.split()) > 10:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _get_evidence_requirements(self, legal_route: List[Dict[str, Any]]) -> List[str]:
        """Extract evidence requirements from legal route"""
        evidence = []
        for step in legal_route:
            evidence.extend(step.get("evidence_required", []))
        return list(set(evidence))  # Remove duplicates
    
    def _get_timeline_estimate(self, legal_route: List[Dict[str, Any]]) -> str:
        """Calculate total timeline estimate"""
        if not legal_route:
            return "6-12 months"
        
        # Simple estimation based on number of steps
        num_steps = len(legal_route)
        if num_steps <= 2:
            return "3-6 months"
        elif num_steps <= 4:
            return "6-12 months"
        else:
            return "12-24 months"
    
    def _extract_glossary_terms(self, query: str, jurisdiction: str) -> Dict[str, str]:
        """Extract relevant legal terms and definitions"""
        # Basic glossary terms
        basic_terms = {
            "jurisdiction": "The official power to make legal decisions and judgments",
            "procedure": "A series of actions conducted in a certain order or manner",
            "evidence": "Information or objects that may be admitted into court for consideration",
            "timeline": "A schedule of events and procedures in legal proceedings"
        }
        
        # Extract terms that appear in query
        query_lower = query.lower()
        relevant_terms = {}
        
        for term, definition in basic_terms.items():
            if term in query_lower:
                relevant_terms[term] = definition
        
        return relevant_terms
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for legal engine"""
        return {
            "status": "healthy" if self.initialized else "initializing",
            "datasets_loaded": len(self.datasets),
            "procedures_loaded": sum(len(procs) for procs in self.procedures.values()),
            "jurisdictions": list(self.datasets.keys())
        }
    
    async def shutdown(self):
        """Cleanup resources"""
        self.datasets.clear()
        self.procedures.clear()
        self.initialized = False