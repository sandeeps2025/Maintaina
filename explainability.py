import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
import warnings
warnings.filterwarnings('ignore')

class ExplainableAI:
    """Provide explainability for model predictions using SHAP"""
    
    def __init__(self, model, X_train, feature_names=None):
        self.model = model
        self.X_train = X_train
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
    
    def initialize_shap_explainer(self, model_type='tree'):
        """Initialize SHAP explainer"""
        
        if model_type == 'tree':
            self.explainer = shap.TreeExplainer(self.model)
        else:
            self.explainer = shap.KernelExplainer(
                self.model.predict,
                shap.sample(self.X_train, min(100, len(self.X_train)))
            )
        
        print("SHAP Explainer initialized")
    
    def compute_shap_values(self, X):
        """Compute SHAP values for predictions"""
        
        if self.explainer is None:
            self.initialize_shap_explainer()
        
        self.shap_values = self.explainer.shap_values(X)
        
        return self.shap_values
    
    def explain_prediction(self, X_instance, prediction, top_n=5):
        """Explain individual prediction"""
        
        if isinstance(X_instance, np.ndarray):
            X_instance = X_instance.reshape(1, -1)
        
        if self.shap_values is None:
            self.compute_shap_values(X_instance)
        
        # Get SHAP values for this instance
        if isinstance(self.shap_values, list):
            shap_vals = self.shap_values[1][0]  # For binary classification
        else:
            shap_vals = self.shap_values[0]
        
        # Get feature values
        feature_values = X_instance[0] if len(X_instance.shape) > 1 else X_instance
        
        # Create explanation
        importance_df = pd.DataFrame({
            'Feature': self.feature_names if self.feature_names else [f'Feature_{i}' for i in range(len(shap_vals))],
            'SHAP_Value': np.abs(shap_vals),
            'Feature_Value': feature_values
        })
        
        importance_df = importance_df.nlargest(top_n, 'SHAP_Value')
        
        return importance_df
    
    def get_failure_explanation(self, X, failure_probabilities, top_n=3):
        """Get failure prediction explanation"""
        
        explanations = []
        
        for idx in range(min(5, len(X))):  # Explain top 5 instances
            if failure_probabilities[idx] > 0.5:
                explanation = self.explain_prediction(X[idx], failure_probabilities[idx], top_n)
                
                # Convert to percentage contribution
                total_contribution = explanation['SHAP_Value'].sum()
                explanation['Contribution_Percentage'] = (
                    explanation['SHAP_Value'] / total_contribution * 100
                ).round(1)
                
                explanations.append({
                    'Instance': idx,
                    'Failure_Probability': f"{failure_probabilities[idx]:.1%}",
                    'Top_Factors': explanation[['Feature', 'Contribution_Percentage']].to_dict('records')
                })
        
        return explanations
    
    def print_explanation(self, X, failure_probabilities):
        """Print human-readable explanation"""
        
        print("\n" + "="*70)
        print("EXPLAINABLE AI - FAILURE PREDICTION EXPLANATION")
        print("="*70)
        
        explanations = self.get_failure_explanation(X, failure_probabilities)
        
        for exp in explanations:
            print(f"\nMachine Instance {exp['Instance']}")
            print(f"Failure Probability: {exp['Failure_Probability']}")
            print("Contributing Factors:")
            
            for i, factor in enumerate(exp['Top_Factors'], 1):
                print(f"  {i}. {factor['Feature']}: {factor['Contribution_Percentage']:.1f}% contribution")
    
    def feature_importance_summary(self):
        """Get overall feature importance"""
        
        if self.shap_values is None:
            print("Please compute SHAP values first")
            return None
        
        # Calculate mean absolute SHAP values
        if isinstance(self.shap_values, list):
            shap_vals = self.shap_values[1]
        else:
            shap_vals = self.shap_values
        
        mean_abs_shap = np.abs(shap_vals).mean(axis=0)
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names if self.feature_names else [f'Feature_{i}' for i in range(len(mean_abs_shap))],
            'Mean_SHAP': mean_abs_shap
        }).sort_values('Mean_SHAP', ascending=False)
        
        return importance_df
    
    def print_feature_importance(self):
        """Print feature importance"""
        
        importance_df = self.feature_importance_summary()
        
        print("\n" + "="*70)
        print("GLOBAL FEATURE IMPORTANCE (SHAP)")
        print("="*70)
        
        for idx, row in importance_df.head(10).iterrows():
            bar_length = int(row['Mean_SHAP'] * 50)
            bar = "█" * bar_length
            print(f"{row['Feature']:<30} {bar} {row['Mean_SHAP']:.4f}")

class SimpleExplainer:
    """Simplified explainability without SHAP (for models without SHAP support)"""
    
    def __init__(self, model, feature_names=None):
        self.model = model
        self.feature_names = feature_names
    
    def explain_from_feature_importance(self, X, top_n=5):
        """Use model's feature importance for explanation"""
        
        if not hasattr(self.model, 'feature_importances_'):
            return None
        
        feature_importance = self.model.feature_importances_
        
        importance_df = pd.DataFrame({
            'Feature': self.feature_names if self.feature_names else [f'Feature_{i}' for i in range(len(feature_importance))],
            'Importance': feature_importance
        }).sort_values('Importance', ascending=False)
        
        # Get top contributing features per instance
        explanations = []
        for idx in range(min(5, len(X))):
            top_features = importance_df.head(top_n).copy()
            top_features['Instance_Value'] = X[idx, importance_df.index]
            
            explanations.append({
                'Instance': idx,
                'Top_Factors': top_features
            })
        
        return explanations
    
    def print_simple_explanation(self, X):
        """Print simplified explanation"""
        
        explanations = self.explain_from_feature_importance(X)
        
        if explanations is None:
            print("Model does not support feature importance")
            return
        
        print("\n" + "="*70)
        print("FEATURE IMPORTANCE EXPLANATION")
        print("="*70)
        
        for exp in explanations:
            print(f"\nInstance {exp['Instance']} - Top Contributing Features:")
            for feature, importance, value in zip(
                exp['Top_Factors']['Feature'],
                exp['Top_Factors']['Importance'],
                exp['Top_Factors']['Instance_Value']
            ):
                print(f"  {feature}: {importance:.1%} (Value: {value:.2f})")

if __name__ == "__main__":
    print("Explainability module loaded successfully")