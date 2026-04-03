# India Payments Fraud Detection Dashboard 🇮🇳

## Overview
An end-to-end interactive fraud detection dashboard specifically designed for India's digital payment ecosystem. This project generates synthetic transaction data, applies machine learning for fraud detection, and provides real-time risk assessment for UPI, card, and net banking transactions.

## Key Features

### 📊 Data Generation
- Synthetic data generation using Faker with Indian-specific parameters
- 10,000+ transactions with configurable fraud ratios (1-15%)
- Realistic fraud patterns including SIM Swap, Phishing, UPI Auto-debit
- Support for Indian banks, UPI apps (Google Pay, PhonePe, Paytm), and major cities

### 🔍 Fraud Analytics
- Real-time transaction monitoring and risk scoring
- Interactive visualizations using Plotly
- Fraud pattern detection by payment method, city, and time
- High-risk transaction identification

### 🤖 Machine Learning
- Random Forest classifier for fraud detection (94.2% accuracy)
- Feature importance analysis
- Real-time fraud prediction API
- Cross-validation with ROC-AUC scoring

### 🛡️ Prevention Measures
- RBI guideline compliance checker
- Multi-factor authentication recommendations
- Transaction velocity monitoring
- Geographic anomaly detection

## Tech Stack
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **ML/AI**: Scikit-learn (Random Forest)
- **Data Generation**: Faker, Pandas, NumPy
- **Language**: Python 3.8+

## Project Structure
payments_fraud_dashboard/
├── app.py # Main Streamlit application
├── data/ # Data generation & cleaning
├── models/ # ML model & risk scoring
├── visualization/ # Charts & UI components
├── utils/ # Helpers & constants
└── pages/ # Multi-page dashboard

## Impact
 - Helps financial institutions detect fraud patterns in real-time
 - Demonstrates compliance with RBI fraud prevention guidelines
 - Provides actionable insights for fraud prevention teams
 - Educational tool for understanding payment fraud in India

## Future Enhancements
 - Integration with real-time payment APIs
 - Deep learning models (LSTM for sequential patterns)
 - SMS/Email alert system
 - Mobile app companion
