import argparse
import csv
from datetime import datetime
from collections import defaultdict
from src.models.resident_data import ResidentDayRecord
from src.engine.analyzer import AnalyzerEngine
from src.ai_explainer.explainer import LocalAIExplainer

def load_data(filepath: str) -> dict:
    """Loads CSV data into ResidentDayRecord grouped by resident_id."""
    data = defaultdict(list)
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = ResidentDayRecord(
                resident_id=row['resident_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                caregiver_response_time=float(row['caregiver_response_time']),
                caregiver_time_with_resident=float(row['caregiver_time_with_resident']),
                movement_events_per_day=int(row['movement_events_per_day']),
                steps_per_day=int(row['steps_per_day']),
                time_spent_walking=float(row['time_spent_walking']),
                sit_to_stand_transitions=int(row['sit_to_stand_transitions']),
                sedentary_time=float(row['sedentary_time']),
                time_spent_upright=float(row['time_spent_upright']),
                rooms_visited_per_day=int(row['rooms_visited_per_day']),
                alert_triggered=row['alert_triggered'] == 'True',
                alert_type=row['alert_type'] if row['alert_type'] else None,
                log_text=row['log_text'] if row['log_text'] else None
            )
            data[row['resident_id']].append(record)
    return dict(data)

def main():
    parser = argparse.ArgumentParser(description="AI Sentinel for MyRaina - Local MVP")
    parser.add_argument('--data', type=str, required=True, help="Path to the synthetic_scenarios.csv data file")
    parser.add_argument('--resident', type=str, help="Specific resident ID to analyze. If omitted, analyzes all.")
    
    args = parser.parse_args()
    
    print(f"Loading data from {args.data}...")
    try:
        resident_data = load_data(args.data)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
        
    engine = AnalyzerEngine()
    explainer = LocalAIExplainer()
    
    residents_to_analyze = [args.resident] if args.resident else resident_data.keys()
    
    for rid in residents_to_analyze:
        if rid not in resident_data:
            print(f"Warning: Resident {rid} not found in dataset.")
            continue
            
        print("-" * 50)
        print(f"Analyzing {rid}...")
        records = resident_data[rid]
        
        # Determine classification
        result = engine.analyze(rid, records)
        
        # Generate insight
        explanation = explainer.generate_explanation(result)
        
        print("\n" + explanation + "\n")
        
if __name__ == "__main__":
    main()
