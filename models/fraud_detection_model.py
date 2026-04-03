# models/fraud_detection_model.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class FraudDetectionModel:
    """Machine Learning model for fraud detection"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_importance = None
        
    def prepare_features(self, df):
        """Prepare features for model training"""
        df_model = df.copy()
        
        # Select numeric features
        numeric_features = [
            'amount', 'transaction_hour', 'failed_attempts_before_success',
            'velocity_30min', 'distance_from_home_km'
        ]
        
        # Boolean features
        boolean_features = ['is_high_value', 'is_international', 'is_weekend', 'is_night']
        
        # Encode categorical features
        categorical_features = ['payment_method', 'merchant_category', 'device_type']
        
        for col in categorical_features:
            if col in df_model.columns:
                le = LabelEncoder()
                df_model[f'{col}_encoded'] = le.fit_transform(df_model[col].astype(str))
                self.label_encoders[col] = le
        
        # Prepare feature matrix
        feature_cols = numeric_features + boolean_features
        feature_cols += [f'{col}_encoded' for col in categorical_features if f'{col}_encoded' in df_model.columns]
        
        # Ensure all features exist
        feature_cols = [col for col in feature_cols if col in df_model.columns]
        
        X = df_model[feature_cols]
        
        # Handle any missing values
        X = X.fillna(X.mean())
        
        # Scale numeric features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, X.columns
    
    def train(self, df, target_col='fraud_flag'):
        """Train the fraud detection model"""
        
        # Prepare features
        X, feature_names = self.prepare_features(df)
        y = df[target_col].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Initialize model
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='roc_auc')
        metrics['cv_auc_mean'] = cv_scores.mean()
        metrics['cv_auc_std'] = cv_scores.std()
        
        return metrics
    
    def predict(self, transaction_data):
        """Predict fraud for a single transaction"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Prepare features
        X, _ = self.prepare_features(pd.DataFrame([transaction_data]))
        
        # Predict
        fraud_probability = self.model.predict_proba(X)[0][1]
        fraud_prediction = self.model.predict(X)[0]
        
        return {
            'is_fraud': bool(fraud_prediction),
            'fraud_probability': float(fraud_probability),
            'risk_level': self.get_risk_level(fraud_probability)
        }
    
    def get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability >= 0.7:
            return 'High'
        elif probability >= 0.3:
            return 'Medium'
        else:
            return 'Low'
    
    def save_model(self, filepath='models/fraud_model.pkl'):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_importance': self.feature_importance,
            'model_type': self.model_type
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='models/fraud_model.pkl'):
        """Load trained model"""
        saved = joblib.load(filepath)
        self.model = saved['model']
        self.scaler = saved['scaler']
        self.label_encoders = saved['label_encoders']
        self.feature_importance = saved['feature_importance']
        self.model_type = saved['model_type']
        print(f"Model loaded from {filepath}")

# For direct testing
if __name__ == "__main__":
    from data.data_generator import PaymentDataGenerator
    from data.data_cleaner import DataCleaner
    
    # Generate and clean data
    generator = PaymentDataGenerator()
    raw_data = generator.generate_dataset(5000, 0.05)
    
    cleaner = DataCleaner()
    cleaned_data, _ = cleaner.clean_data(raw_data)
    
    # Train model
    model = FraudDetectionModel('random_forest')
    metrics = model.train(cleaned_data)
    
    print("Model Training Results:")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.3f}")
    print(f"CV AUC Mean: {metrics['cv_auc_mean']:.3f} (+/- {metrics['cv_auc_std']:.3f})")
    print("\nTop 5 Features:")
    print(model.feature_importance.head())