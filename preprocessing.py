import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    def __init__(self):
        self.scaler = RobustScaler()
        self.categorical_columns = []
        self.numerical_columns = []
        
    def load_data(self, filepath):
        """Load raw data"""
        df = pd.read_csv(filepath)
        print(f"Data loaded: {df.shape}")
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values"""
        print(f"Missing values before: \n{df.isnull().sum()}")
        
        # Fill numerical columns with median
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Drop rows with any remaining missing values
        df.dropna(inplace=True)
        
        print(f"Missing values after: {df.isnull().sum().sum()}")
        return df
    
    def detect_outliers(self, df):
        """Detect and handle outliers using IQR method"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                print(f"{col}: {outlier_count} outliers detected")
                # Replace outliers with median
                df.loc[outliers, col] = df[col].median()
        
        return df
    
    def normalize_features(self, X_train, X_test):
        """Normalize numerical features"""
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def prepare_data(self, df):
        """Complete preprocessing pipeline"""
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Detect outliers
        df = self.detect_outliers(df)
        
        # Separate features and targets
        X = df.drop(['Machine_ID', 'Timestamp', 'Failure_Next_7Days', 'RUL'], axis=1)
        y_failure = df['Failure_Next_7Days']
        y_rul = df['RUL']
        
        # Split data
        X_train, X_test, y_fail_train, y_fail_test, y_rul_train, y_rul_test = train_test_split(
            X, y_failure, y_rul, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
        
        print(f"Training set: {X_train_scaled.shape}")
        print(f"Test set: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled, y_fail_train, y_fail_test, y_rul_train, y_rul_test

if __name__ == "__main__":
    from data_generator import save_training_data
    
    # Generate and preprocess
    df = save_training_data()
    
    preprocessor = DataPreprocessor()
    X_train, X_test, y_fail_train, y_fail_test, y_rul_train, y_rul_test = preprocessor.prepare_data(df)
    
    print("Preprocessing complete!")
    print(f"Train failure distribution: {pd.Series(y_fail_train).value_counts()}")