# utils/helpers.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_risk_score(row):
    """Calculate fraud risk score based on multiple factors"""
    risk_score = 0
    
    # Amount-based risk
    if row['amount'] > 50000:
        risk_score += 30
    elif row['amount'] > 25000:
        risk_score += 15
    elif row['amount'] > 10000:
        risk_score += 5
    
    # Velocity risk
    if row['velocity_30min'] > 5:
        risk_score += 25
    elif row['velocity_30min'] > 3:
        risk_score += 15
    elif row['velocity_30min'] > 1:
        risk_score += 5
    
    # Failed attempts risk
    if row['failed_attempts_before_success'] > 3:
        risk_score += 20
    elif row['failed_attempts_before_success'] > 1:
        risk_score += 10
    
    # Distance risk
    if row['distance_from_home_km'] > 200:
        risk_score += 15
    elif row['distance_from_home_km'] > 100:
        risk_score += 10
    elif row['distance_from_home_km'] > 50:
        risk_score += 5
    
    # International transaction risk
    if row['is_international']:
        risk_score += 15
    
    # Device risk (new or unknown devices)
    if row['device_type'] in ['New Device', 'Unknown Device']:
        risk_score += 20
    
    return min(risk_score, 100)

def get_risk_level(risk_score):
    """Convert risk score to risk level"""
    if risk_score >= 70:
        return 'High'
    elif risk_score >= 30:
        return 'Medium'
    else:
        return 'Low'

def get_recommended_action(risk_level):
    """Get recommended action based on risk level"""
    actions = {
        'High': 'Block transaction and verify with customer immediately',
        'Medium': 'Additional verification required (2FA/OTP/Call)',
        'Low': 'Transaction can proceed with standard monitoring'
    }
    return actions.get(risk_level, 'Monitor transaction')

def format_indian_currency(amount):
    """Format amount in Indian currency format"""
    return f"₹{amount:,.2f}"

def calculate_fraud_metrics(df):
    """Calculate key fraud metrics"""
    total_transactions = len(df)
    fraud_transactions = df['fraud_flag'].sum()
    fraud_rate = (fraud_transactions / total_transactions) * 100
    
    total_amount = df['amount'].sum()
    fraud_amount = df[df['fraud_flag'] == True]['amount'].sum()
    fraud_amount_rate = (fraud_amount / total_amount) * 100 if total_amount > 0 else 0
    
    return {
        'total_transactions': total_transactions,
        'fraud_transactions': fraud_transactions,
        'fraud_rate': fraud_rate,
        'total_amount': total_amount,
        'fraud_amount': fraud_amount,
        'fraud_amount_rate': fraud_amount_rate
    }