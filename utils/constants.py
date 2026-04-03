# Indian payment methods
PAYMENT_METHODS = ['UPI', 'CREDIT CARD', 'DEBIT CARD', 'NET BANKING', 'WALLET']
PAYMENT_METHOD_WEIGHTS = [0.6, 0.15, 0.15, 0.05, 0.05]

# Indian banks
INDIAN_BANKS = [
    'State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 
    'Kotak Mahindra Bank', 'Punjab National Bank', 'Bank of Baroda', 
    'Yes Bank', 'IDFC First Bank', 'IndusInd Bank'
]

# UPI apps in India
UPI_APPS = ['Google Pay', 'PhonePe', 'Paytm', 'Amazon Pay', 'WhatsApp Pay', 'BHIM']

# Fraud types specific to India
FRAUD_TYPES = [
    'Phishing', 'SIM Swap', 'UPI Auto-debit', 'Card Cloning', 
    'OTP Bypass', 'QR Code Fraud', 'KYC Fraud', 'Account Takeover', 
    'Social Engineering', 'No Fraud'
]

# Indian cities
INDIAN_CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 
    'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 
    'Nagpur', 'Indore', 'Bhopal', 'Surat', 'Visakhapatnam'
]

# Merchant categories
MERCHANT_CATEGORIES = [
    'E-commerce', 'Food & Dining', 'Travel', 'Utilities', 
    'Entertainment', 'Education', 'Healthcare', 'Groceries', 
    'Fuel', 'Recharge & Bills'
]

# Device types
DEVICE_TYPES = ['Mobile Android', 'Mobile iOS', 'Desktop Windows', 'Desktop Mac', 'Tablet']

# Risk thresholds
RISK_THRESHOLDS = {
    'LOW': 30,
    'MEDIUM': 70,
    'HIGH': 100
}

# RBI guidelines
RBI_LIMITS = {
    'upi_daily_limit': 100000,
    'new_beneficiary_cooling': 4,  # hours
    'fraud_reporting_time': 3,      # hours
    'customer_liability_limit': 10000
}

# Fraud indicators
FRAUD_INDICATORS = {
    'high_amount_threshold': 25000,
    'velocity_threshold': 5,
    'failed_attempts_threshold': 3,
    'distance_threshold': 100
}