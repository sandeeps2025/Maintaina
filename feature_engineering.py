import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

class FeatureEngineer:
    """Create intelligent features from raw sensor data"""
    
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.pca = PCA(n_components=0.95)
    
    def create_rolling_features(self, df, columns, window=10):
        """Create rolling average and std features"""
        for col in columns:
            df[f'{col}_rolling_mean'] = df[col].rolling(window=window, min_periods=1).mean()
            df[f'{col}_rolling_std'] = df[col].rolling(window=window, min_periods=1).std()
            df[f'{col}_rolling_max'] = df[col].rolling(window=window, min_periods=1).max()
            df[f'{col}_rolling_min'] = df[col].rolling(window=window, min_periods=1).min()
        
        return df
    
    def create_trend_features(self, df, columns):
        """Create trend features - rate of change"""
        for col in columns:
            df[f'{col}_trend'] = df[col].diff().fillna(0)
            df[f'{col}_momentum'] = df[col].diff(5).fillna(0)
        
        return df
    
    def create_domain_features(self, df):
        """Create domain-specific features for maintenance"""
        
        # Bearing degradation indicator (vibration-based)
        if 'Vibration' in df.columns:
            df['Bearing_Health'] = 100 - (df['Vibration'] * 5).clip(0, 100)
        
        # Motor efficiency (voltage-current relationship)
        if 'Motor_Current' in df.columns and 'Voltage' in df.columns:
            df['Motor_Efficiency'] = (df['Voltage'] / df['Motor_Current']).clip(0, 50)
        
        # Temperature-Pressure relationship
        if 'Temperature' in df.columns and 'Pressure' in df.columns:
            df['Temp_Pressure_Ratio'] = df['Temperature'] / (df['Pressure'] + 1)
        
        # Load-Vibration interaction
        if 'Load_Percentage' in df.columns and 'Vibration' in df.columns:
            df['Load_Vibration_Stress'] = (df['Load_Percentage'] * df['Vibration']).clip(0, 500)
        
        # Lubrication depletion rate
        if 'Lubrication_Level' in df.columns:
            df['Lube_Depletion_Rate'] = 100 - df['Lubrication_Level']
        
        # Energy consumption estimation
        if 'Motor_Current' in df.columns and 'Voltage' in df.columns:
            df['Power_Consumption'] = df['Voltage'] * df['Motor_Current']
        
        # Thermal stress indicator
        if 'Temperature' in df.columns:
            df['Thermal_Stress'] = (df['Temperature'] - 70).clip(0, 50)
        
        return df
    
    def create_statistical_features(self, df, columns):
        """Create statistical features"""
        for col in columns:
            df[f'{col}_skewness'] = df[col].rolling(window=20, min_periods=1).apply(
                lambda x: pd.Series(x).skew(), raw=False
            )
            df[f'{col}_kurtosis'] = df[col].rolling(window=20, min_periods=1).apply(
                lambda x: pd.Series(x).kurtosis(), raw=False
            )
        
        return df
    
    def create_interaction_features(self, df):
        """Create interaction between features"""
        if 'Temperature' in df.columns and 'Humidity' in df.columns:
            df['Temp_Humidity_Index'] = (df['Temperature'] * df['Humidity']).clip(0, 10000)
        
        if 'RPM' in df.columns and 'Vibration' in df.columns:
            df['RPM_Vibration_Product'] = df['RPM'] * df['Vibration']
        
        return df
    
    def engineer_features(self, df):
        """Complete feature engineering pipeline"""
        
        # Separate by machine to maintain time series integrity
        engineered_dfs = []
        
        for machine_id in df['Machine_ID'].unique():
            machine_df = df[df['Machine_ID'] == machine_id].copy().reset_index(drop=True)
            
            sensor_columns = ['Temperature', 'Pressure', 'Vibration', 'Motor_Current', 
                            'Voltage', 'Humidity', 'RPM', 'Lubrication_Level', 'Load_Percentage']
            
            # Create rolling features
            machine_df = self.create_rolling_features(machine_df, sensor_columns, window=10)
            
            # Create trend features
            machine_df = self.create_trend_features(machine_df, sensor_columns)
            
            # Create domain-specific features
            machine_df = self.create_domain_features(machine_df)
            
            # Create statistical features
            machine_df = self.create_statistical_features(machine_df, sensor_columns[:3])
            
            # Create interaction features
            machine_df = self.create_interaction_features(machine_df)
            
            engineered_dfs.append(machine_df)
        
        df_engineered = pd.concat(engineered_dfs, ignore_index=True)
        
        # Drop NaN values created by rolling windows
        df_engineered.dropna(inplace=True)
        
        print(f"Original features: 9 sensor readings")
        print(f"Engineered features: {df_engineered.shape[1] - 4}")
        print(f"Total columns after engineering: {df_engineered.shape[1]}")
        
        return df_engineered

if __name__ == "__main__":
    from data_generator import generate_machine_data
    
    df = generate_machine_data(n_samples=2000, n_machines=5)
    
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df)
    
    print("\nFeature engineering complete!")
    print(df_features.head())