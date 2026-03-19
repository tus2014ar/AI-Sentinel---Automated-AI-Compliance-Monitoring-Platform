from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AnalysisResult:
    """Represents the final, multidimensional analysis result for a resident."""
    resident_id: str
    status: str  # 'no_issue', 'monitor', 'review_recommended'
    confidence: str  # 'high', 'medium', 'low'
    ambiguous_cause: bool
    triggered_rules: List[str] = field(default_factory=list)
    triggered_rule_details: List[Dict] = field(default_factory=list)
    mobility_score: float = 0.0      # 0-100
    autonomy_score: float = 0.0      # 0-100
    dignity_score: float = 0.0       # 0-100
    regulatory_notes: List[str] = field(default_factory=list)
    explanation: str = ""
    workflow_insights: List[str] = field(default_factory=list)
