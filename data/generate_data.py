import csv
import os
import random
from datetime import date, timedelta
import numpy as np
from faker import Faker

# Use numpy random seed for reproducibility
np.random.seed(42)
fake = Faker()
Faker.seed(42)

DATA_DIR = os.path.dirname(__file__)

def _generate_baseline_day(res_id: str, day_date: date, steps: int, rooms: int, sed: float, care: float) -> dict:
    return {
        "resident_id": res_id,
        "date": day_date.isoformat(),
        "caregiver_response_time": max(1.0, np.random.normal(5.0, 1.0)),
        "caregiver_time_with_resident": max(5.0, np.random.normal(care, 2.0)),
        "movement_events_per_day": max(10, int(np.random.normal(50, 5))),
        "steps_per_day": max(100, int(np.random.normal(steps, 200))),
        "time_spent_walking": max(1.0, steps / 100.0),
        "sit_to_stand_transitions": max(0, int(np.random.normal(15, 3))),
        "sedentary_time": min(24.0, max(2.0, np.random.normal(sed, 0.5))),
        "time_spent_upright": min(24.0, max(0.0, 24.0 - sed)),
        "rooms_visited_per_day": max(1, int(np.random.normal(rooms, 0.5))),
        "alert_triggered": False,
        "alert_type": "",
        "log_text": "System check OK. Routine observations noted."
    }

def generate_normal_dataset(num_residents=10, days=30):
    """
    Scenario 1: Stable baselines.
    Expected output: all residents 'no_issue'.
    Tests the engine's ability to clear normal residents without false positives.
    """
    data = []
    start = date(2025, 1, 1)
    for res_idx in range(1, num_residents + 1):
        res_id = f"RES_NORM_{res_idx:02d}"
        for d in range(days):
            current_date = start + timedelta(days=d)
            steps = 3200
            rooms = 4
            sed = 11.0
            care = 30.0
            data.append(_generate_baseline_day(res_id, current_date, steps, rooms, sed, care))
    
    return data

def generate_at_risk_dataset(num_residents=10, days=30):
    """
    Scenario 2: At Risk. Days 1-7 normal. Alert Day 8.
    Days 8-15 mobility suppression.
    Expected output: 3-5 residents 'monitor' or 'review_recommended'.
    Tests Rule 1 (steps drop >30%) and partial Rule 2 (rooms drop to 2).
    """
    data = []
    start = date(2025, 1, 1)
    
    # We will make half of them actually trigger the rules to meet the "3-5 residents" criteria
    for res_idx in range(1, num_residents + 1):
        res_id = f"RES_RISK_{res_idx:02d}"
        trigger_risk = res_idx <= 5 # Only the first 5 exhibit the risky behavior
        
        for d in range(days):
            current_date = start + timedelta(days=d)
            base_steps = 3500
            base_rooms = 4
            base_sed = 12.0
            base_care = 30.0
            
            row = _generate_baseline_day(res_id, current_date, base_steps, base_rooms, base_sed, base_care)
            
            if trigger_risk:
                if d == 7: # Day 8 (0-indexed 7)
                    row["alert_triggered"] = True
                    row["alert_type"] = "bed_exit"
                    row["log_text"] = "Bed exit alarm triggered. Caregiver responded."
                elif 8 <= d <= 14: # Days 8-15 (0-indexed 8 to 14)
                    row["steps_per_day"] = int(base_steps * 0.65) # 35% decline
                    row["rooms_visited_per_day"] = 2
                    row["caregiver_time_with_resident"] = base_care * 1.25 # 25% increase
                elif d >= 15:
                    # Partial stabilization
                    row["steps_per_day"] = int(base_steps * 0.85)
                    row["rooms_visited_per_day"] = 3
            
            data.append(row)
    return data

def generate_restrained_dataset(num_residents=10, days=30):
    """
    Scenario 3: Severe Restraint Indicators.
    Expected output: majority 'review_recommended'.
    Tests Rule 1, Rule 2, Rule 3, Rule 4 (doubled care time), Rule 5, 
    AND PII logging (20% of rows contain fake PII).
    """
    data = []
    start = date(2025, 1, 1)
    
    for res_idx in range(1, num_residents + 1):
        res_id = f"RES_SEVERE_{res_idx:02d}"
        trigger_severe = res_idx <= 8 # Majority (8/10) trigger
        
        for d in range(days):
            current_date = start + timedelta(days=d)
            base_steps = 3000
            base_rooms = 4
            base_sed = 12.0
            base_care = 30.0
            
            row = _generate_baseline_day(res_id, current_date, base_steps, base_rooms, base_sed, base_care)
            
            if trigger_severe:
                if d == 2: # Day 3
                    row["alert_triggered"] = True
                    row["alert_type"] = "motion_sensor"
                    row["log_text"] = "Motion sensor triggered in room."
                if 2 < d <= 4: # within 48h of Day 3
                     row["movement_events_per_day"] = int(50 * 0.55) # 45% drop
                     row["steps_per_day"] = int(base_steps * 0.8)
                if d >= 6: # Day 7 onwards: Steps drop 52%
                     row["steps_per_day"] = int(base_steps * 0.48)
                if 10 <= d < 25: # Rooms < 2 for 10+ days; Sedentary > 18 for 6+ days
                     row["rooms_visited_per_day"] = 1
                     row["sedentary_time"] = 19.5
                     row["time_spent_upright"] = 4.5
                if d >= 9: # Day 10 onwards: Caregiver time doubles, steps halved (handled by 52% drop above)
                     row["caregiver_time_with_resident"] = base_care * 2.1
            
            # Inject fake PII in ~20% of rows
            if np.random.rand() < 0.20:
                name = fake.name()
                email = fake.email()
                phone = fake.phone_number()
                row["log_text"] = f"Caregiver {name} contacted family at {email} phone {phone}. " + row["log_text"]
                
            data.append(row)
    return data

def generate_edge_cases_dataset():
    """
    Scenario 4: Specific Edge Cases (5 residents, 30 days each).
    1. RES_LOW_BASELINE: Steps ~900 throughout. No alerts.
    2. RES_NULL_GAPS: Missing data on Days 12, 13, 14.
    3. RES_RECOVERY: Flags trigger D5-12, recovers D20.
    4. RES_SINGLE: Normal 30 days.
    5. RES_AMBIGUOUS: Mobility declines with NO alert, NO care burden increase.
    """
    data = []
    start = date(2025, 1, 1)
    
    # 1. RES_LOW_BASELINE
    for d in range(30):
        data.append(_generate_baseline_day("RES_LOW_BASELINE", start + timedelta(days=d), 900, 2, 16.0, 40.0))
        
    # 2. RES_NULL_GAPS
    for d in range(30):
        if d in [11, 12, 13]: # Days 12-14
            # We insert a row with None/blank values to test system resilience
             row = _generate_baseline_day("RES_NULL_GAPS", start + timedelta(days=d), 0, 0, 0, 0)
             for key in row:
                 if key not in ["resident_id", "date"]:
                     row[key] = ""
             data.append(row)
        else:
            data.append(_generate_baseline_day("RES_NULL_GAPS", start + timedelta(days=d), 3500, 4, 12.0, 30.0))
            
    # 3. RES_RECOVERY
    for d in range(30):
        row = _generate_baseline_day("RES_RECOVERY", start + timedelta(days=d), 3500, 4, 12.0, 30.0)
        if d == 4: # Day 5
            row["alert_triggered"] = True
            row["alert_type"] = "bed_exit"
        if 5 <= d <= 11: # Days 6-12 (Drops)
            row["steps_per_day"] = 1500
            row["rooms_visited_per_day"] = 1
            row["sedentary_time"] = 19.5
        if d >= 19: # Day 20 onwards (Recovery)
            row["steps_per_day"] = 3400
            row["rooms_visited_per_day"] = 4
            row["sedentary_time"] = 12.5
        data.append(row)
        
    # 4. RES_SINGLE
    for d in range(30):
        data.append(_generate_baseline_day("RES_SINGLE", start + timedelta(days=d), 4000, 5, 10.0, 25.0))
        
    # 5. RES_AMBIGUOUS
    for d in range(30):
        row = _generate_baseline_day("RES_AMBIGUOUS", start + timedelta(days=d), 3500, 4, 12.0, 30.0)
        if d >= 10:
            row["steps_per_day"] = 1200 # Mobility decline
            # But NO alert, and caregiver time stays SAME (30.0 baseline)
        data.append(row)
        
    return data

def save_to_csv(filename: str, dataset: list):
    filepath = os.path.join(DATA_DIR, filename)
    if not dataset:
        return 0
    headers = dataset[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset)
    return len(dataset)

if __name__ == "__main__":
    print("Generating synthetic datasets...")
    
    ds_normal = generate_normal_dataset()
    c1 = save_to_csv('dataset_normal.csv', ds_normal)
    print(f"Created dataset_normal.csv with {c1} rows.")
    
    ds_risk = generate_at_risk_dataset()
    c2 = save_to_csv('dataset_at_risk.csv', ds_risk)
    print(f"Created dataset_at_risk.csv with {c2} rows.")
    
    ds_restrained = generate_restrained_dataset()
    c3 = save_to_csv('dataset_restrained.csv', ds_restrained)
    print(f"Created dataset_restrained.csv with {c3} rows.")
    
    ds_edge = generate_edge_cases_dataset()
    c4 = save_to_csv('dataset_edge_cases.csv', ds_edge)
    print(f"Created dataset_edge_cases.csv with {c4} rows.")
    
    print("\nGeneration complete!")
