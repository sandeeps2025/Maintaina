#!/usr/bin/env python3
"""
Real-time Prediction API for Predictive Maintenance Platform
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RealTimePredictor:
    """Real-time machine monitoring and prediction"""
    
    def __init__(self, ensemble_model, preprocessor):
        self.ensemble = ensemble_model
        self.preprocessor = preprocessor
        self.scaler = RobustScaler()
        self.machine_history = {}
    
    def predict_single_machine(self, machine_id, sensor_readings):
        """
        Predict for single machine
        
        Args:
            machine_id: Machine identifier
            sensor_readings: Dict of sensor values
                {'Temperature': 75, 'Pressure': 105, ...}
        
        Returns:
            Dictionary with predictions
        """
        
        # Convert to DataFrame format expected by model
        df = pd.DataFrame([sensor_readings])
        
        # Preprocess
        X_scaled = self.preprocessor.scaler.transform(df)
        
        # Get predictions
        health_score = self.ensemble.calculate_machine_health_score(X_scaled, np.array([0]))[0]
        failure_proba, _ = self.ensemble.predict_failure_probability(X_scaled)
        anomaly_score = self.ensemble.predict_anomaly_score(X_scaled)[0]
        rul = self.ensemble.predict_rul(X_scaled)[0]
        component = self.ensemble.predict_failure_component(X_scaled)[0]
        repair_cost = self.ensemble.estimate_repair_cost(
            np.array([health_score]), failure_proba
        )[0]
        downtime = self.ensemble.estimate_downtime(np.array([rul]), failure_proba)[0]
        maintenance = self.ensemble.schedule_maintenance(
            np.array([health_score]), failure_proba, np.array([rul])
        )[0]
        risk_level = self.ensemble.get_risk_level(np.array([health_score]))[0]
        
        prediction = {
            'Machine_ID': machine_id,
            'Timestamp': datetime.now().isoformat(),
            'Health_Score': int(health_score),
            'Failure_Probability': f"{failure_proba[0]*100:.1f}%",
            'Anomaly_Score': f"{anomaly_score*100:.1f}%",
            'Remaining_Useful_Life_Hours': int(rul),
            'Predicted_Failure_Component': component,
            'Estimated_Repair_Cost': f"${repair_cost:,}",
            'Estimated_Downtime_Hours': int(downtime),
            'Maintenance_Schedule': maintenance,
            'Risk_Level': risk_level,
            'Sensor_Readings': sensor_readings
        }
        
        return prediction
    
    def predict_batch_machines(self, machines_data):
        """
        Predict for multiple machines
        
        Args:
            machines_data: List of dicts
                [
                    {'machine_id': 'M-001', 'sensors': {...}},
                    {'machine_id': 'M-002', 'sensors': {...}}
                ]
        
        Returns:
            List of predictions
        """
        
        predictions = []
        for machine in machines_data:
            pred = self.predict_single_machine(
                machine['machine_id'],
                machine['sensors']
            )
            predictions.append(pred)
        
        return predictions
    
    def simulate_live_monitoring(self, num_machines=10, num_readings=5):
        """Simulate live monitoring of multiple machines"""
        
        print("\n" + "="*70)
        print("LIVE MACHINE MONITORING SIMULATION")
        print("="*70)
        
        machines_data = []
        
        for m_id in range(1, num_machines + 1):
            for reading in range(num_readings):
                # Generate realistic sensor data
                sensors = {
                    'Temperature': 70 + np.random.normal(5, 2),
                    'Pressure': 100 + np.random.normal(5, 2),
                    'Vibration': 2 + np.random.normal(0.5, 0.2),
                    'Motor_Current': 15 + np.random.normal(2, 0.5),
                    'Voltage': 230 + np.random.normal(2, 0.5),
                    'Humidity': 45 + np.random.normal(10, 5),
                    'RPM': 1500 + np.random.normal(50, 10),
                    'Lubrication_Level': 80 + np.random.normal(0, 5),
                    'Operating_Hours': reading * 100,
                    'Load_Percentage': 70 + np.random.normal(10, 5)
                }
                
                machines_data.append({
                    'machine_id': f'M-{m_id:03d}',
                    'sensors': sensors
                })
        
        # Get predictions for all machines
        predictions = self.predict_batch_machines(machines_data)
        
        # Display sample predictions
        print("\nSample Predictions (First 5 readings):\n")
        for pred in predictions[:5]:
            print(f"Machine: {pred['Machine_ID']}")
            print(f"  Health Score: {pred['Health_Score']}/100")
            print(f"  Failure Probability: {pred['Failure_Probability']}")
            print(f"  Risk Level: {pred['Risk_Level']}")
            print(f"  RUL: {pred['Remaining_Useful_Life_Hours']} hours")
            print(f"  Maintenance: {pred['Maintenance_Schedule']}")
            print()
        
        # Aggregate statistics
        print("\n" + "="*70)
        print("FLEET STATISTICS")
        print("="*70)
        
        health_scores = [int(p['Health_Score']) for p in predictions]
        risk_levels = [p['Risk_Level'] for p in predictions]
        
        print(f"\nAverage Fleet Health: {np.mean(health_scores):.1f}/100")
        print(f"Fleet Health Std Dev: {np.std(health_scores):.1f}")
        
        print("\nRisk Distribution:")
        for risk in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            count = sum(1 for r in risk_levels if r == risk)
            pct = (count / len(risk_levels)) * 100
            print(f"  {risk}: {count} machines ({pct:.1f}%)")
        
        print("\n" + "="*70)
        
        return predictions
    
    def export_predictions_json(self, predictions, filename='predictions.json'):
        """Export predictions to JSON"""
        
        # Convert to JSON-serializable format
        json_predictions = []
        for pred in predictions:
            json_pred = pred.copy()
            json_predictions.append(json_pred)
        
        with open(filename, 'w') as f:
            json.dump(json_predictions, f, indent=2)
        
        print(f"Predictions exported to {filename}")
    
    def alert_critical_machines(self, predictions, health_threshold=40):
        """Alert for critical machines"""
        
        critical_machines = [
            p for p in predictions
            if int(p['Health_Score']) < health_threshold
        ]
        
        if critical_machines:
            print("\n" + "="*70)
            print("⚠️  CRITICAL ALERT - MACHINES REQUIRING IMMEDIATE ATTENTION")
            print("="*70)
            
            for machine in critical_machines:
                print(f"\n{machine['Machine_ID']} - CRITICAL")
                print(f"  Health: {machine['Health_Score']}/100")
                print(f"  Failure Risk: {machine['Failure_Probability']}")
                print(f"  RUL: {machine['Remaining_Useful_Life_Hours']} hours")
                print(f"  Action: {machine['Maintenance_Schedule']}")
        
        return critical_machines

def example_usage():
    """Example usage of real-time predictor"""
    
    from train_pipeline import main as train_main
    
    print("Training models...")
    ensemble, factory, _ = train_main()
    
    from preprocessing import DataPreprocessor
    preprocessor = DataPreprocessor()
    
    # Initialize real-time predictor
    predictor = RealTimePredictor(ensemble, preprocessor)
    
    # Simulate live monitoring
    predictions = predictor.simulate_live_monitoring(num_machines=10, num_readings=5)
    
    # Alert for critical machines
    critical = predictor.alert_critical_machines(predictions)
    
    # Export predictions
    predictor.export_predictions_json(predictions)
    
    print("\n✓ Real-time prediction demo completed!")

if __name__ == "__main__":
    example_usage()