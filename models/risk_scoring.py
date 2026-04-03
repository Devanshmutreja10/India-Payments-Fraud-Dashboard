# models/risk_scoring.py

import pandas as pd
import numpy as np
from utils.constants import FRAUD_INDICATORS, RBI_LIMITS

class RiskScoringEngine:
    """Real-time risk scoring engine for transactions"""
    
    def __init__(self):
        self.weights = {
            'amount': 0.25,
            'velocity': 0.20,
            'failed_attempts': 0.15,
            'distance': 0.15,
            'device': 0.10,
            'international': 0.10,
            'time': 0.05
        }
        
    def score_amount(self, amount):
        """Score based on transaction amount"""
        if amount > 100000:
            return 100
        elif amount > 50000:
            return 70
        elif amount > 25000:
            return 50
        elif amount > 10000:
            return 30
        elif amount > 5000:
            return 15
        else:
            return 0
    
    def score_velocity(self, velocity):
        """Score based on transaction velocity"""
        if velocity > 10:
            return 100
        elif velocity > 5:
            return 80
        elif velocity > 3:
            return 50
        elif velocity > 1:
            return 25
        else:
            return 0
    
    def score_failed_attempts(self, failed_attempts):
        """Score based on failed attempts"""
        if failed_attempts > 5:
            return 100
        elif failed_attempts > 3:
            return 70
        elif failed_attempts > 1:
            return 40
        else:
            return 0
    
    def score_distance(self, distance_km):
        """Score based on distance from home"""
        if distance_km > 500:
            return 100
        elif distance_km > 200:
            return 70
        elif distance_km > 100:
            return 50
        elif distance_km > 50:
            return 30
        else:
            return 0
    
    def score_device(self, device_type):
        """Score based on device type"""
        risky_devices = ['New Device', 'Unknown Device', 'Suspicious IP']
        if device_type in risky_devices:
            return 80
        elif 'Desktop' in device_type:
            return 30
        else:
            return 0
    
    def score_international(self, is_international):
        """Score based on international flag"""
        return 60 if is_international else 0
    
    def score_time(self, hour):
        """Score based on transaction time"""
        # High risk during late night/early morning
        if hour >= 23 or hour <= 4:
            return 70
        elif hour >= 22 or hour <= 5:
            return 50
        else:
            return 0
    
    def calculate_total_score(self, transaction):
        """Calculate total risk score"""
        scores = {
            'amount': self.score_amount(transaction.get('amount', 0)),
            'velocity': self.score_velocity(transaction.get('velocity_30min', 0)),
            'failed_attempts': self.score_failed_attempts(transaction.get('failed_attempts_before_success', 0)),
            'distance': self.score_distance(transaction.get('distance_from_home_km', 0)),
            'device': self.score_device(transaction.get('device_type', 'Unknown')),
            'international': self.score_international(transaction.get('is_international', False)),
            'time': self.score_time(transaction.get('transaction_hour', 12))
        }
        
        # Weighted sum
        total_score = sum(scores[key] * self.weights[key] for key in scores)
        
        return {
            'total_score': round(total_score, 2),
            'component_scores': scores,
            'risk_level': self.get_risk_level(total_score)
        }
    
    def get_risk_level(self, score):
        """Determine risk level from score"""
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def get_prevention_action(self, risk_level, amount):
        """Get recommended prevention action"""
        actions = {
            'High': {
                'action': 'BLOCK_TRANSACTION',
                'message': 'Transaction blocked. Contact customer immediately.',
                'verification': 'Manual verification required',
                'timeout_minutes': 30
            },
            'Medium': {
                'action': 'ADDITIONAL_VERIFICATION',
                'message': 'Additional verification required',
                'verification': '2FA/OTP/Call verification',
                'timeout_minutes': 15
            },
            'Low': {
                'action': 'ALLOW_TRANSACTION',
                'message': 'Transaction allowed with monitoring',
                'verification': 'Standard monitoring',
                'timeout_minutes': 5
            }
        }
        
        action = actions.get(risk_level, actions['Low'])
        
        # Adjust for high value transactions
        if amount > RBI_LIMITS['upi_daily_limit']:
            action['message'] += " - Exceeds daily limit"
            action['verification'] += " + Limit check"
        
        return action

# For direct testing
if __name__ == "__main__":
    engine = RiskScoringEngine()
    
    # Test transaction
    test_transaction = {
        'amount': 75000,
        'velocity_30min': 4,
        'failed_attempts_before_success': 2,
        'distance_from_home_km': 150,
        'device_type': 'New Device',
        'is_international': True,
        'transaction_hour': 2
    }
    
    result = engine.calculate_total_score(test_transaction)
    print(f"Risk Score: {result['total_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Component Scores: {result['component_scores']}")
    
    action = engine.get_prevention_action(result['risk_level'], test_transaction['amount'])
    print(f"\nRecommended Action: {action['action']}")
    print(f"Message: {action['message']}")