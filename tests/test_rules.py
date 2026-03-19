import unittest
from datetime import date, timedelta
from src.models.resident_data import ResidentDayRecord
from src.rules.mobility_suppression import MobilitySuppressionRule
from src.rules.confinement_signal import ConfinementSignalRule
from src.rules.sedentary_spiral import SedentarySpiralRule
from src.rules.caregiver_overdependence import CaregiverOverdependenceRule
from src.rules.alert_suppression_effect import AlertSuppressionEffectRule

class TestRules(unittest.TestCase):
    def setUp(self):
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

    def test_mobility_suppression_trigger(self):
        rule = MobilitySuppressionRule()
        records = self._create_baseline(10)
        
        # Day 5: Alert triggers
        records[4].alert_triggered = True
        # Day 8: Steps drop from 4000 to 2000 (>30%)
        records[7].steps_per_day = 2000
        
        triggers = rule.evaluate(records)
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0].rule_id, "R1_MOBILITY_SUPPRESSION")

    def test_confinement_signal_trigger(self):
        rule = ConfinementSignalRule()
        records = self._create_baseline()
        
        # Day 3, 4, 5: Rooms < 2
        records[3].rooms_visited_per_day = 1
        records[4].rooms_visited_per_day = 1
        records[5].rooms_visited_per_day = 1
        
        triggers = rule.evaluate(records)
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0].rule_id, "R2_CONFINEMENT_SIGNAL")

    def test_sedentary_spiral_trigger(self):
        rule = SedentarySpiralRule()
        records = self._create_baseline()
        
        # Day 2 to 6 (5 days): Sedentary > 18
        for i in range(2, 7):
            records[i].sedentary_time = 19.0
            
        triggers = rule.evaluate(records)
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0].rule_id, "R3_SEDENTARY_SPIRAL")

    def test_caregiver_overdependence_trigger(self):
        rule = CaregiverOverdependenceRule()
        records = self._create_baseline(10)
        
        # Day 8: Caregiver time double baseline, steps halved
        # Baseline (days 1-7) avg is 30 mins, 4000 steps
        records[8].caregiver_time_with_resident = 65.0
        records[8].steps_per_day = 1500
        
        triggers = rule.evaluate(records)
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0].rule_id, "R4_CAREGIVER_OVERDEPENDENCE")

    def test_alert_suppression_trigger(self):
        rule = AlertSuppressionEffectRule()
        records = self._create_baseline(5)
        
        # Day 2: Alert triggers. Movement = 50.
        records[1].alert_triggered = True
        # Day 3: Movement drops to 20 (>40% drop)
        records[2].movement_events_per_day = 20
        
        triggers = rule.evaluate(records)
        self.assertEqual(len(triggers), 1)
        self.assertEqual(triggers[0].rule_id, "R5_ALERT_SUPPRESSION_EFFECT")

if __name__ == '__main__':
    unittest.main()
