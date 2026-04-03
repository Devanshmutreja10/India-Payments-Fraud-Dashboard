# data/data_generator.py

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import *
from utils.helpers import calculate_risk_score, get_risk_level

fake = Faker('en_IN')

class PaymentDataGenerator:
    """Generate synthetic payment transaction data for India"""
    
    def __init__(self):
        self.fake = fake
        
    def generate_transaction(self, transaction_id, timestamp, is_fraud=False):
        """Generate a single transaction"""
        
        # Base amount (exponential distribution)
        amount = np.random.exponential(5000)
        amount = max(10, min(100000, amount))
        
        # Adjust amount for fraud
        if is_fraud:
            amount = amount * np.random.uniform(1.5, 10)
        
        # Payment method
        payment_method = np.random.choice(PAYMENT_METHODS, p=PAYMENT_METHOD_WEIGHTS)
        
        # UPI app (if applicable)
        upi_app = None
        if payment_method == 'UPI' and np.random.random() < 0.8:
            upi_app = np.random.choice(UPI_APPS)
        
        # Fraud-specific attributes
        if is_fraud:
            fraud_type = np.random.choice([f for f in FRAUD_TYPES if f != 'No Fraud'])
            
            # FIXED: Match the number of probabilities with choices
            device_choices = ['New Device', 'Unknown Device', 'Suspicious IP'] + DEVICE_TYPES
            device_probs = [0.4, 0.3, 0.2] + [0.02, 0.02, 0.02, 0.02, 0.02]  # 5 DEVICE_TYPES
            # Ensure lengths match
            device_type = np.random.choice(device_choices, p=device_probs)
            
            failed_attempts = np.random.poisson(2)
            velocity = np.random.poisson(4)
            distance = np.random.exponential(150)
        else:
            fraud_type = 'No Fraud'
            # FIXED: Match probabilities with DEVICE_TYPES length
            device_type = np.random.choice(DEVICE_TYPES, p=[0.5, 0.3, 0.1, 0.05, 0.05])
            failed_attempts = np.random.poisson(0.2)
            velocity = np.random.poisson(0.5)
            distance = np.random.exponential(15)
        
        transaction = {
            'transaction_id': transaction_id,
            'timestamp': timestamp,
            'amount': round(amount, 2),
            'payment_method': payment_method,
            'bank': np.random.choice(INDIAN_BANKS),
            'upi_app': upi_app,
            'merchant_category': np.random.choice(MERCHANT_CATEGORIES),
            'location_city': np.random.choice(INDIAN_CITIES),
            'device_type': device_type,
            'is_high_value': amount > 25000,
            'is_international': np.random.random() < 0.02,
            'failed_attempts_before_success': failed_attempts,
            'velocity_30min': velocity,
            'distance_from_home_km': round(distance, 2),
            'fraud_flag': is_fraud,
            'fraud_type': fraud_type
        }
        
        # Calculate risk score
        transaction['risk_score'] = calculate_risk_score(transaction)
        transaction['fraud_risk_level'] = get_risk_level(transaction['risk_score'])
        
        return transaction
    
    def generate_dataset(self, n_transactions=10000, fraud_ratio=0.05):
        """Generate complete dataset"""
        
        transactions = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(n_transactions):
            is_fraud = np.random.random() < fraud_ratio
            timestamp = start_date + timedelta(
                seconds=np.random.randint(0, 30 * 24 * 3600)
            )
            transaction_id = f"TXN{timestamp.strftime('%Y%m%d')}{i:06d}"
            
            transaction = self.generate_transaction(transaction_id, timestamp, is_fraud)
            transactions.append(transaction)
        
        df = pd.DataFrame(transactions)
        return df

# For direct testing
if __name__ == "__main__":
    generator = PaymentDataGenerator()
    df = generator.generate_dataset(1000, 0.05)
    print(f"Generated {len(df)} transactions")
    print(f"Fraud rate: {df['fraud_flag'].mean()*100:.2f}%")
    print(df.head())