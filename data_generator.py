import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_machine_data(n_samples=10000, n_machines=50):
    """Generate synthetic industrial sensor data for training"""
    
    data = []
    
    for machine_id in range(1, n_machines + 1):
        # Simulate machine degradation over time
        for hour in range(n_samples // n_machines):
            base_time = datetime.now() - timedelta(hours=n_samples//n_machines - hour)
            
            # Normal operating conditions with gradual degradation
health_factor = 1 - (hour / (n_samples // n_machines)) * 0.7            
            # Generate sensor readings
            temperature = 70 + np.random.normal(5, 2) + (hour * 0.01)
            pressure = 100 + np.random.normal(5, 2) + (hour * 0.005)
            vibration = 2 + np.random.normal(0.5, 0.2) + (hour * 0.002)
            motor_current = 15 + np.random.normal(2, 0.5) + (hour * 0.01)
            voltage = 230 + np.random.normal(2, 0.5)
            humidity = 45 + np.random.normal(10, 5)
            rpm = 1500 + np.random.normal(50, 10) - (hour * 0.1)
            lubrication_level = 80 - (hour * 0.02) + np.random.normal(0, 2)
            operating_hours = hour
            load_percentage = 70 + np.random.normal(10, 5)
            
            # Failure label based on degradation
            if health_factor < 0.4:
                failure_in_next_7days = 1
            elif health_factor < 0.6:
                failure_in_next_7days = 1 if np.random.random() < 0.3 else 0
            else:
                failure_in_next_7days = 0
            
            # Remaining Useful Life
            rul = max(0, int((1 - health_factor) * 500))
            
            data.append({
                'Machine_ID': machine_id,
                'Timestamp': base_time,
                'Temperature': temperature,
                'Pressure': pressure,
                'Vibration': vibration,
                'Motor_Current': motor_current,
                'Voltage': voltage,
                'Humidity': humidity,
                'RPM': rpm,
                'Lubrication_Level': lubrication_level,
                'Operating_Hours': operating_hours,
                'Load_Percentage': load_percentage,
                'Failure_Next_7Days': failure_in_next_7days,
                'RUL': rul
            })
    
    df = pd.DataFrame(data)
    return df

def save_training_data(filepath='machine_data.csv'):
    """Generate and save training data"""
    df = generate_machine_data(n_samples=10000, n_machines=50)
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")
    print(f"Shape: {df.shape}")
    print(df.head())
    return df

if __name__ == "__main__":
    save_training_data()