import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class EnsemblePredictor:
    """Combine predictions from multiple models"""
    
    def __init__(self, models_dict):
        self.models = models_dict
        self.scaler = MinMaxScaler()
    
    def predict_failure_probability(self, X):
        """Ensemble prediction for failure probability"""
        
        predictions = {}
        
        # Random Forest prediction
        if 'random_forest' in self.models:
            rf_proba = self.models['random_forest'].predict_proba(X)[:, 1]
            predictions['rf'] = rf_proba
        
        # XGBoost prediction
        if 'xgboost' in self.models:
            xgb_proba = self.models['xgboost'].predict_proba(X)[:, 1]
            predictions['xgb'] = xgb_proba
        
        # Isolation Forest (anomaly score to probability)
        if 'isolation_forest' in self.models:
            iso_scores = self.models['isolation_forest'].decision_function(X)
            iso_proba = 1 / (1 + np.exp(iso_scores))  # Convert to probability
            predictions['iso'] = iso_proba
        
        # Ensemble: weighted average
        if len(predictions) > 0:
            ensemble_proba = np.mean(list(predictions.values()), axis=0)
        else:
            ensemble_proba = np.zeros(len(X))
        
        return ensemble_proba, predictions
    
    def predict_anomaly_score(self, X):
        """Anomaly detection using Autoencoder"""
        
        if 'autoencoder' not in self.models:
            return np.zeros(len(X))
        
        # Get reconstruction error
        reconstructed = self.models['autoencoder'].predict(X, verbose=0)
        reconstruction_error = np.mean(np.square(X - reconstructed), axis=1)
        
        # Normalize to 0-1 scale
        anomaly_score = MinMaxScaler().fit_transform(reconstruction_error.reshape(-1, 1)).flatten()
        
        return anomaly_score
    
    def calculate_machine_health_score(self, X, anomaly_scores):
        """Calculate composite health score (0-100)"""
        
        failure_proba, _ = self.predict_failure_probability(X)
        
        # Health score inversely proportional to failure probability
        health_from_failure = (1 - failure_proba) * 100
        
        # Health score inversely proportional to anomaly
        health_from_anomaly = (1 - anomaly_scores) * 100
        
        # Weighted composite score
        health_score = (0.6 * health_from_failure + 0.4 * health_from_anomaly).astype(int)
        
        return np.clip(health_score, 0, 100)
    
    def predict_rul(self, X):
        """Predict Remaining Useful Life"""
        
        if 'lstm' not in self.models:
            # Fallback: estimate based on health score
            failure_proba, _ = self.predict_failure_probability(X)
            rul_estimate = (1 - failure_proba) * 500
            return rul_estimate
        
        # RUL from LSTM (if available)
        lstm_rul = self.models['lstm'].predict(X, verbose=0).flatten()
        
        return np.clip(lstm_rul, 0, 500)
    
    def predict_failure_component(self, X):
        """Predict which component will fail based on feature importance"""
        
        components = ['Bearing', 'Motor', 'Pump', 'Gearbox', 'Valve']
        
        if 'random_forest' not in self.models:
            return ['Unknown'] * len(X)
        
        # Get feature importances
        feature_importance = self.models['random_forest'].feature_importances_
        
        # Map top features to components (simplified logic)
        predictions = []
        for i in range(len(X)):
            # Use feature values to predict component
            feature_values = X[i]
            weighted_importance = feature_values * feature_importance
            
            # Predict based on which sensor has highest weighted importance
            top_feature_idx = np.argsort(weighted_importance)[-1]
            
            # Map feature to component (example mapping)
            feature_to_component = {
                0: 'Bearing',      # Vibration
                1: 'Motor',        # Temperature
                2: 'Pump',         # Pressure
                3: 'Motor',        # Motor Current
                4: 'Gearbox',      # Voltage
                5: 'Bearing',      # Humidity
                6: 'Gearbox',      # RPM
                7: 'Valve',        # Lubrication
                8: 'Motor'         # Load
            }
            
            component = feature_to_component.get(top_feature_idx % 9, 'Unknown')
            predictions.append(component)
        
        return predictions
    
    def estimate_repair_cost(self, health_scores, failure_proba):
        """Estimate repair cost based on health and failure probability"""
        
        # Base costs per component (in relative units)
        base_costs = {
            'Low': 500,
            'Medium': 2000,
            'High': 5000,
            'Critical': 10000
        }
        
        costs = []
        for health, failure_prob in zip(health_scores, failure_proba):
            if health > 80:
                cost = base_costs['Low'] * (1 + failure_prob * 0.5)
            elif health > 60:
                cost = base_costs['Medium'] * (1 + failure_prob * 1.0)
            elif health > 40:
                cost = base_costs['High'] * (1 + failure_prob * 1.5)
            else:
                cost = base_costs['Critical'] * (1 + failure_prob * 2.0)
            
            costs.append(int(cost))
        
        return np.array(costs)
    
    def estimate_downtime(self, rul, failure_proba):
        """Estimate expected downtime (in hours)"""
        
        # More severe failures = longer downtime
        base_downtime = failure_proba * 72  # 0-72 hours based on severity
        
        # Less RUL remaining = sooner breakdown = higher downtime urgency
        urgency_factor = 1 - (np.clip(rul, 0, 500) / 500)
        
        downtime = base_downtime * (1 + urgency_factor)
        
        return downtime.astype(int)
    
    def schedule_maintenance(self, health_scores, failure_proba, rul):
        """Recommend maintenance schedule"""
        
        schedules = []
        
        for health, failure, remaining_life in zip(health_scores, failure_proba, rul):
            if health < 40 or failure > 0.7:
                schedule = 'Immediate'
            elif health < 60 or failure > 0.5:
                schedule = 'Urgent (1-2 days)'
            elif health < 75 or failure > 0.3:
                schedule = 'Soon (1-2 weeks)'
            else:
                schedule = 'Routine (1-3 months)'
            
            schedules.append(schedule)
        
        return schedules
    
    def get_risk_level(self, health_scores):
        """Categorize risk level"""
        
        risk_levels = []
        for health in health_scores:
            if health > 80:
                risk = 'LOW'
            elif health > 60:
                risk = 'MEDIUM'
            elif health > 40:
                risk = 'HIGH'
            else:
                risk = 'CRITICAL'
            
            risk_levels.append(risk)
        
        return risk_levels
    
    def predict_batch(self, X, machine_ids=None):
        """Complete prediction for batch of machines"""
        
        # Calculate all metrics
        failure_proba, _ = self.predict_failure_probability(X)
        anomaly_scores = self.predict_anomaly_score(X)
        health_scores = self.calculate_machine_health_score(X, anomaly_scores)
        rul = self.predict_rul(X)
        components = self.predict_failure_component(X)
        repair_costs = self.estimate_repair_cost(health_scores, failure_proba)
        downtime = self.estimate_downtime(rul, failure_proba)
        maintenance_schedule = self.schedule_maintenance(health_scores, failure_proba, rul)
        risk_levels = self.get_risk_level(health_scores)
        
        # Create results dataframe
        results = pd.DataFrame({
            'Machine_ID': machine_ids if machine_ids is not None else range(len(X)),
            'Health_Score': health_scores,
            'Failure_Probability': (failure_proba * 100).astype(int),
            'Anomaly_Score': (anomaly_scores * 100).astype(int),
            'Remaining_Useful_Life_Hours': rul.astype(int),
            'Predicted_Failure_Component': components,
            'Estimated_Repair_Cost': repair_costs,
            'Estimated_Downtime_Hours': downtime,
            'Maintenance_Schedule': maintenance_schedule,
            'Risk_Level': risk_levels
        })
        
        return results

if __name__ == "__main__":
    print("Ensemble pipeline module loaded successfully")