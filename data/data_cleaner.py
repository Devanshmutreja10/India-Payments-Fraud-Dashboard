# data/data_cleaner.py

import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    """Clean and preprocess payment transaction data"""
    
    def __init__(self):
        self.cleaning_log = []
    
    def log_action(self, action):
        """Log cleaning actions"""
        self.cleaning_log.append({
            'timestamp': datetime.now(),
            'action': action
        })
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        df_clean = df.copy()
        
        # Fill missing values
        df_clean['upi_app'] = df_clean['upi_app'].fillna('Not Applicable')
        df_clean['fraud_type'] = df_clean['fraud_type'].fillna('No Fraud')
        
        # For numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        self.log_action(f"Filled missing values: {df.isnull().sum().sum()} nulls handled")
        return df_clean
    
    def remove_duplicates(self, df):
        """Remove duplicate transactions"""
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=['transaction_id'])
        removed = initial_count - len(df_clean)
        
        self.log_action(f"Removed {removed} duplicate transactions")
        return df_clean
    
    def handle_outliers(self, df):
        """Handle outliers in amount and other numeric fields"""
        df_clean = df.copy()
        
        # Cap extreme outliers (99.9th percentile)
        amount_99_9 = df_clean['amount'].quantile(0.999)
        df_clean['amount'] = df_clean['amount'].clip(upper=amount_99_9)
        
        # Remove transactions below 1st percentile
        amount_1 = df_clean['amount'].quantile(0.001)
        df_clean = df_clean[df_clean['amount'] >= amount_1]
        
        removed = len(df) - len(df_clean)
        self.log_action(f"Handled outliers: {removed} extreme values capped/removed")
        
        return df_clean
    
    def create_features(self, df):
        """Create additional features for analysis"""
        df_clean = df.copy()
        
        # Time-based features
        df_clean['transaction_hour'] = df_clean['timestamp'].dt.hour
        df_clean['transaction_day'] = df_clean['timestamp'].dt.day_name()
        df_clean['transaction_month'] = df_clean['timestamp'].dt.month
        df_clean['is_weekend'] = df_clean['timestamp'].dt.dayofweek >= 5
        df_clean['is_night'] = (df_clean['transaction_hour'] >= 22) | (df_clean['transaction_hour'] <= 5)
        
        # Amount categories
        df_clean['amount_category'] = pd.cut(
            df_clean['amount'],
            bins=[0, 500, 2000, 10000, 50000, float('inf')],
            labels=['Micro', 'Small', 'Medium', 'Large', 'Very Large']
        )
        
        # Standardize text columns
        text_columns = ['payment_method', 'merchant_category', 'device_type', 'location_city']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].str.upper().str.strip()
        
        self.log_action(f"Created {len(df_clean.columns) - len(df.columns)} new features")
        
        return df_clean
    
    def validate_data(self, df):
        """Validate data quality"""
        validation_results = {
            'total_transactions': len(df),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_ids': df['transaction_id'].duplicated().sum(),
            'negative_amounts': (df['amount'] < 0).sum(),
            'invalid_dates': df['timestamp'].isnull().sum(),
            'valid_fraud_flags': df['fraud_flag'].isin([True, False]).all()
        }
        
        self.log_action(f"Data validation completed: {validation_results}")
        return validation_results
    
    def clean_data(self, df):
        """Complete data cleaning pipeline"""
        print("Starting data cleaning pipeline...")
        
        # Apply cleaning steps
        df = self.handle_missing_values(df)
        df = self.remove_duplicates(df)
        df = self.handle_outliers(df)
        df = self.create_features(df)
        
        # Validate final dataset
        validation = self.validate_data(df)
        
        print(f"Cleaning completed. Final shape: {df.shape}")
        print(f"Validation: {validation}")
        
        return df, self.cleaning_log

# For direct testing
if __name__ == "__main__":
    from data_generator import PaymentDataGenerator
    
    # Generate sample data
    generator = PaymentDataGenerator()
    raw_data = generator.generate_dataset(1000, 0.05)
    
    # Clean data
    cleaner = DataCleaner()
    cleaned_data, log = cleaner.clean_data(raw_data)
    
    print("\nCleaning Log:")
    for entry in log:
        print(f"- {entry['timestamp']}: {entry['action']}")