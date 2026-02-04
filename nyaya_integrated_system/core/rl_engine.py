"""
RL Feedback Engine - Reinforcement Learning System
Handles feedback ingestion, confidence adjustment, and learning persistence
Validates all updates through enforcement engine
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from enforcement_engine import create_enforcement_signal, is_execution_permitted

class RLFeedbackEngine:
    def __init__(self):
        self.feedback_store = []
        self.performance_memory = {}
        self.confidence_adjustments = {}
        self.learning_enabled = True
        self.initialized = False
        
    async def initialize(self):
        """Initialize RL engine and load existing data"""
        if self.initialized:
            return
            
        # Load existing performance memory
        self._load_performance_memory()
        
        # Initialize confidence adjustment factors
        self.confidence_adjustments = {
            "positive_feedback": 0.05,
            "negative_feedback": -0.03,
            "neutral_feedback": 0.01
        }
        
        self.initialized = True
    
    def _load_performance_memory(self):
        """Load performance memory from storage"""
        try:
            memory_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'performance_memory.json')
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    self.performance_memory = json.load(f)
        except Exception:
            self.performance_memory = {}
    
    def _save_performance_memory(self):
        """Save performance memory to storage"""
        try:
            os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
            memory_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'performance_memory.json')
            with open(memory_file, 'w') as f:
                json.dump(self.performance_memory, f, indent=2)
        except Exception:
            pass
    
    async def process_feedback(self, trace_id: str, rating: int, feedback_type: str, 
                             comment: Optional[str] = None, user_request: str = "") -> Dict[str, Any]:
        """Process user feedback with enforcement validation"""
        
        # Create enforcement signal for RL update
        signal = create_enforcement_signal(
            case_id=trace_id,
            country="global",
            domain="feedback",
            procedure_id="rl_update",
            original_confidence=0.5,
            user_request=f"Feedback: {rating}/5 - {feedback_type}",
            jurisdiction_routed_to="global",
            trace_id=trace_id,
            user_feedback=self._categorize_feedback(rating),
            outcome_tag="feedback_processing"
        )
        
        # Check if RL update is permitted
        if not is_execution_permitted(signal):
            return {
                "status": "blocked",
                "message": "RL update blocked by enforcement policy",
                "trace_id": trace_id,
                "enforcement_blocked": True
            }
        
        # Process feedback
        feedback_entry = {
            "trace_id": trace_id,
            "rating": rating,
            "feedback_type": feedback_type,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": True
        }
        
        self.feedback_store.append(feedback_entry)
        
        # Update performance memory
        self._update_performance_memory(trace_id, rating, feedback_type)
        
        # Adjust confidence factors if learning is enabled
        if self.learning_enabled:
            self._adjust_confidence_factors(rating, feedback_type)
        
        # Save to persistent storage
        self._save_performance_memory()
        
        return {
            "status": "recorded",
            "message": "Feedback processed and learning updated",
            "trace_id": trace_id,
            "learning_impact": self._calculate_learning_impact(rating, feedback_type)
        }
    
    def _categorize_feedback(self, rating: int) -> str:
        """Categorize feedback as positive, negative, or neutral"""
        if rating >= 4:
            return "positive"
        elif rating <= 2:
            return "negative"
        else:
            return "neutral"
    
    def _update_performance_memory(self, trace_id: str, rating: int, feedback_type: str):
        """Update performance memory with new feedback"""
        if trace_id not in self.performance_memory:
            self.performance_memory[trace_id] = {
                "feedback_count": 0,
                "average_rating": 0.0,
                "feedback_types": {},
                "last_updated": datetime.utcnow().isoformat()
            }
        
        memory = self.performance_memory[trace_id]
        
        # Update average rating
        current_avg = memory["average_rating"]
        current_count = memory["feedback_count"]
        new_avg = ((current_avg * current_count) + rating) / (current_count + 1)
        
        memory["average_rating"] = new_avg
        memory["feedback_count"] = current_count + 1
        memory["last_updated"] = datetime.utcnow().isoformat()
        
        # Update feedback type counts
        if feedback_type not in memory["feedback_types"]:
            memory["feedback_types"][feedback_type] = 0
        memory["feedback_types"][feedback_type] += 1
    
    def _adjust_confidence_factors(self, rating: int, feedback_type: str):
        """Adjust confidence factors based on feedback"""
        feedback_category = self._categorize_feedback(rating)
        
        # Apply learning adjustments
        if feedback_category == "positive":
            # Slightly increase confidence for similar queries
            self.confidence_adjustments["positive_feedback"] = min(
                self.confidence_adjustments["positive_feedback"] + 0.001, 0.1
            )
        elif feedback_category == "negative":
            # Decrease confidence for similar queries
            self.confidence_adjustments["negative_feedback"] = max(
                self.confidence_adjustments["negative_feedback"] - 0.001, -0.1
            )
    
    def _calculate_learning_impact(self, rating: int, feedback_type: str) -> Dict[str, Any]:
        """Calculate the impact of this feedback on learning"""
        feedback_category = self._categorize_feedback(rating)
        
        return {
            "feedback_category": feedback_category,
            "confidence_adjustment": self.confidence_adjustments.get(f"{feedback_category}_feedback", 0),
            "learning_enabled": self.learning_enabled,
            "total_feedback_processed": len(self.feedback_store)
        }
    
    def get_confidence_adjustment(self, domain: str, jurisdiction: str, base_confidence: float) -> float:
        """Get confidence adjustment based on historical performance"""
        # Simple adjustment based on overall performance
        total_feedback = len(self.feedback_store)
        if total_feedback == 0:
            return base_confidence
        
        # Calculate average rating across all feedback
        avg_rating = sum(f["rating"] for f in self.feedback_store) / total_feedback
        
        # Adjust confidence based on average performance
        if avg_rating >= 4.0:
            adjustment = 0.05
        elif avg_rating >= 3.0:
            adjustment = 0.0
        else:
            adjustment = -0.05
        
        return min(max(base_confidence + adjustment, 0.0), 1.0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        if not self.feedback_store:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "feedback_distribution": {},
                "learning_status": "no_data"
            }
        
        total_feedback = len(self.feedback_store)
        avg_rating = sum(f["rating"] for f in self.feedback_store) / total_feedback
        
        # Calculate feedback distribution
        distribution = {}
        for feedback in self.feedback_store:
            rating = feedback["rating"]
            if rating not in distribution:
                distribution[rating] = 0
            distribution[rating] += 1
        
        return {
            "total_feedback": total_feedback,
            "average_rating": round(avg_rating, 2),
            "feedback_distribution": distribution,
            "learning_status": "active" if self.learning_enabled else "disabled",
            "confidence_adjustments": self.confidence_adjustments
        }
    
    def get_trace_feedback(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all feedback for a specific trace ID"""
        return [f for f in self.feedback_store if f["trace_id"] == trace_id]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for RL engine"""
        return {
            "status": "healthy" if self.initialized else "initializing",
            "learning_enabled": self.learning_enabled,
            "total_feedback": len(self.feedback_store),
            "performance_memory_entries": len(self.performance_memory),
            "average_system_rating": self.get_performance_stats()["average_rating"]
        }
    
    async def shutdown(self):
        """Cleanup and save data"""
        self._save_performance_memory()
        self.feedback_store.clear()
        self.performance_memory.clear()
        self.initialized = False