import unittest
from datetime import date, timedelta
from src.models.resident_data import ResidentDayRecord
from src.engine.analyzer import AnalyzerEngine

class TestAnalyzerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AnalyzerEngine()
        self.start_date = date(2025, 1, 1)

    def _create_baseline(self, days=30):
        records = []
        for i in range(days):
            records.append(ResidentDayRecord(
                resident_id="TEST",
                date=self.start_date + timedelta(days=i),
                caregiver_response_time=5.0,
                caregiver_time_with_resident=30.0,
                movement_events_per_day=50,
                steps_per_day=4000,
                time_spent_walking=40.0,
                sit_to_stand_transitions=10,
                sedentary_time=14.0,
                time_spent_upright=10.0,
                rooms_visited_per_day=4,
                alert_triggered=False,
                alert_type=None,
                log_text=None
            ))
        return records

    def test_no_issue_classification(self):
        records = self._create_baseline(10)
        result = self.engine.analyze("TEST", records)
        self.assertEqual(result.classification, "no_issue")
        self.assertEqual(len(result.triggered_rules), 0)

    def test_monitor_classification(self):
        records = self._create_baseline(10)
        # Trigger Sedentary Spiral (Rule 3)
        for i in range(2, 7):
            records[i].sedentary_time = 19.0
            
        result = self.engine.analyze("TEST", records)
        self.assertEqual(result.classification, "monitor")
        self.assertEqual(len(set(t.rule_id for t in result.triggered_rules)), 1)

    def test_review_recommended_classification(self):
        records = self._create_baseline(20)
        # Trigger Confinement (Rule 2)
        records[3].rooms_visited_per_day = 1
        records[4].rooms_visited_per_day = 1
        records[5].rooms_visited_per_day = 1
        
        # Trigger Sedentary Spiral (Rule 3)
        for i in range(2, 7):
            records[i].sedentary_time = 19.0
            
        result = self.engine.analyze("TEST", records)
        self.assertEqual(result.classification, "review_recommended")
        self.assertTrue(len(set(t.rule_id for t in result.triggered_rules)) >= 2)

if __name__ == '__main__':
    unittest.main()
