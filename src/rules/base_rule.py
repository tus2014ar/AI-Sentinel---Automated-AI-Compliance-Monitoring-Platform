from typing import List, Optional
from ..models.resident_data import ResidentDayRecord
from ..models.analysis_result import RuleTrigger

class BaseRule:
    """Base class for all deterministic detection rules."""
    
    @property
    def rule_id(self) -> str:
        raise NotImplementedError
        
    @property
    def rule_name(self) -> str:
        raise NotImplementedError
        
    @property
    def description(self) -> str:
        raise NotImplementedError

    def evaluate(self, records: List[ResidentDayRecord]) -> List[RuleTrigger]:
        """
        Evaluates the rule against a list of resident records chronologically.
        Returns a list of RuleTriggers, which may be empty if the rule did not trigger.
        Records are expected to be sorted by date ascending.
        """
        raise NotImplementedError
