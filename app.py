# app.py - Main Streamlit Application

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_generator import PaymentDataGenerator
from data.data_cleaner import DataCleaner
from models.fraud_detection_model import FraudDetectionModel
from models.risk_scoring import RiskScoringEngine
from visualization.charts import FraudVisualizer
from visualization.dashboard_components import DashboardComponents
from utils.helpers import calculate_fraud_metrics

# Page configuration
st.set_page_config(
    page_title="Payments Fraud Dashboard - India",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False
if 'cleaned_data' not in st.session_state:
    st.session_state['cleaned_data'] = None
if 'model' not in st.session_state:
    st.session_state['model'] = None

# Title
st.title("🛡️ India Payments Fraud Detection Dashboard")
st.markdown("### Real-time Fraud Monitoring & Analytics for Indian Payment Systems")

# Sidebar controls
st.sidebar.header("⚙️ Dashboard Controls")

# Data generation section
st.sidebar.markdown("### 📊 Data Generation")
n_transactions = st.sidebar.slider("Number of Transactions", 1000, 50000, 10000, 1000)
fraud_ratio = st.sidebar.slider("Fraud Ratio (%)", 1, 15, 5, 1) / 100

if st.sidebar.button("🔄 Generate & Load Data", type="primary", use_container_width=True):
    with st.spinner("Generating synthetic payment data for India..."):
        # Generate data
        generator = PaymentDataGenerator()
        raw_data = generator.generate_dataset(n_transactions, fraud_ratio)
        
        # Clean data
        cleaner = DataCleaner()
        cleaned_data, cleaning_log = cleaner.clean_data(raw_data)
        
        # Train model
        model = FraudDetectionModel('random_forest')
        metrics = model.train(cleaned_data)
        
        # Store in session state
        st.session_state['cleaned_data'] = cleaned_data
        st.session_state['model'] = model
        st.session_state['model_metrics'] = metrics
        st.session_state['data_loaded'] = True
        st.session_state['cleaning_log'] = cleaning_log
        
        st.success(f"✅ Generated {len(cleaned_data):,} transactions with {fraud_ratio*100:.1f}% fraud rate")
        st.info(f"📈 Model trained - Accuracy: {metrics['accuracy']:.2%}, ROC-AUC: {metrics['roc_auc']:.3f}")

# Main content
if st.session_state['data_loaded']:
    df = st.session_state['cleaned_data']
    model = st.session_state['model']
    
    # Display metrics
    DashboardComponents.display_metrics(df)
    
    # Create tabs
    tab_overview, tab_fraud_analysis, tab_ml_model, tab_prevention, tab_data_view = st.tabs([
        "📊 Overview", "🔍 Fraud Analysis", "🤖 ML Model", "🛡️ Prevention", "📋 Data View"
    ])
    
    with tab_overview:
        st.subheader("Transaction Overview")
        
        # Filters
        filtered_df = DashboardComponents.display_filter_sidebar(df)
        
        # Time series chart
        fig = FraudVisualizer.plot_fraud_timeline(filtered_df)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = FraudVisualizer.plot_fraud_by_payment_method(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = FraudVisualizer.plot_amount_distribution(filtered_df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Risk summary
        DashboardComponents.display_risk_summary(filtered_df)
        
        # High risk transactions
        DashboardComponents.display_high_risk_transactions(filtered_df)
    
    with tab_fraud_analysis:
        st.subheader("Fraud Pattern Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = FraudVisualizer.plot_fraud_types_distribution(df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = FraudVisualizer.plot_fraud_by_hour(df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Fraud by city
        fig = FraudVisualizer.plot_fraud_by_city(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk metrics comparison
        fig = FraudVisualizer.plot_risk_metrics_comparison(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Fraud insights
        st.subheader("Key Insights")
        metrics = calculate_fraud_metrics(df)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fraud_types = df[df['fraud_flag']==True]['fraud_type']
            if len(fraud_types) > 0:
                st.info(f"**Most Common Fraud Type:** {fraud_types.mode().values[0]}")
            else:
                st.info("**Most Common Fraud Type:** No fraud detected")
        with col2:
            fraud_hours = df[df['fraud_flag']==True]['transaction_hour']
            if len(fraud_hours) > 0:
                st.info(f"**Peak Fraud Hour:** {int(fraud_hours.mode().values[0])}:00")
            else:
                st.info("**Peak Fraud Hour:** No data")
        with col3:
            high_risk_cities = df[df['fraud_risk_level']=='High']['location_city']
            if len(high_risk_cities) > 0:
                st.info(f"**Highest Risk City:** {high_risk_cities.mode().values[0]}")
            else:
                st.info("**Highest Risk City:** No data")
    
    with tab_ml_model:
        st.subheader("Machine Learning Fraud Detection Model")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model Accuracy", f"{st.session_state['model_metrics']['accuracy']:.1%}")
        with col2:
            st.metric("ROC-AUC Score", f"{st.session_state['model_metrics']['roc_auc']:.3f}")
        with col3:
            st.metric("CV AUC Mean", f"{st.session_state['model_metrics']['cv_auc_mean']:.3f}")
        
        # Feature importance
        if model.feature_importance is not None:
            fig = FraudVisualizer.plot_feature_importance(model.feature_importance)
            st.plotly_chart(fig, use_container_width=True)
        
        # Real-time prediction demo
        st.subheader("🎯 Real-time Fraud Prediction Demo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_amount = st.number_input("Transaction Amount (₹)", min_value=10, max_value=500000, value=15000, step=1000)
            test_payment = st.selectbox("Payment Method", df['payment_method'].unique())
            test_city = st.selectbox("Location", df['location_city'].unique())
            test_device = st.selectbox("Device Type", df['device_type'].unique())
        
        with col2:
            test_velocity = st.number_input("Transactions in last 30min", min_value=0, max_value=20, value=1)
            test_failed = st.number_input("Failed Attempts", min_value=0, max_value=10, value=0)
            test_distance = st.number_input("Distance from Home (km)", min_value=0, max_value=500, value=10)
            test_international = st.checkbox("International Transaction")
            test_hour = st.slider("Transaction Hour", 0, 23, 14)
        
        if st.button("🔍 Predict Fraud Risk", type="primary"):
            # Use risk scoring engine
            risk_engine = RiskScoringEngine()
            
            test_transaction = {
                'amount': test_amount,
                'velocity_30min': test_velocity,
                'failed_attempts_before_success': test_failed,
                'distance_from_home_km': test_distance,
                'device_type': test_device,
                'is_international': test_international,
                'transaction_hour': test_hour
            }
            
            risk_result = risk_engine.calculate_total_score(test_transaction)
            action = risk_engine.get_prevention_action(risk_result['risk_level'], test_amount)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                fig = FraudVisualizer.create_gauge_chart(risk_result['total_score'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown(f"### Risk Assessment")
                st.markdown(f"**Risk Level:** :{'red[High]' if risk_result['risk_level'] == 'High' else 'orange[Medium]' if risk_result['risk_level'] == 'Medium' else 'green[Low]'}")
                st.markdown(f"**Risk Score:** {risk_result['total_score']:.1f}/100")
                st.markdown(f"**Recommended Action:** {action['action']}")
                st.markdown(f"**Message:** {action['message']}")
                st.markdown(f"**Verification Required:** {action['verification']}")
                
                if risk_result['risk_level'] == 'High':
                    st.error("🚨 High fraud risk detected! Block transaction immediately.")
                elif risk_result['risk_level'] == 'Medium':
                    st.warning("⚠️ Medium fraud risk. Additional verification required.")
                else:
                    st.success("✅ Low fraud risk. Transaction can proceed.")
    
    with tab_prevention:
        st.subheader("🛡️ Fraud Prevention Measures for India")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🔐 Immediate Actions
            1. **Multi-factor Authentication (MFA)**
               - Mandatory for all UPI transactions > ₹5000
               - Biometric verification for high-value payments
               
            2. **Real-time Monitoring**
               - Velocity checks (max 5 transactions/30min)
               - Geographic anomaly detection
               - Device fingerprinting
               
            3. **Transaction Limits**
               - Daily UPI limit: ₹1,00,000
               - New beneficiary cooling period: 4 hours
               - Suspicious amount flagging
               
            4. **AI-Powered Detection**
               - Behavioral pattern analysis
               - Anomaly detection algorithms
               - Real-time risk scoring
            """)
            
        with col2:
            st.markdown("""
            ### 📊 Analytics & Best Practices
            1. **Machine Learning Models**
               - Random Forest for fraud classification
               - Real-time scoring engine
               - Continuous model retraining
               
            2. **Rule-based System**
               - Blacklist suspicious accounts
               - Velocity check rules
               - Amount threshold alerts
               
            3. **Customer Education**
               - Regular awareness campaigns
               - Real-time fraud alerts
               - Easy reporting mechanism
               
            4. **RBI Compliance**
               - 2FA for all digital payments
               - Tokenization for card transactions
               - Central fraud registry
            """)
        
        # RBI Guidelines
        st.info("""
        **💡 RBI Guidelines for Payment Fraud Prevention:**
        - ✅ Mandatory 2FA for all digital payments
        - ✅ Tokenization for card transactions
        - ✅ Central fraud registry for coordination
        - ✅ Customer liability limited to ₹10,000 for unauthorized transactions
        - ✅ Mandatory fraud reporting within 3 hours
        """)
        
        # Prevention effectiveness - FIXED VERSION
        st.subheader("📈 Prevention Measures Effectiveness")
        
        prevention_data = pd.DataFrame({
            'Measure': ['UPI Limits', 'MFA', 'Real-time Monitoring', 'ML Detection', 'Customer Alerts', '2FA'],
            'Fraud Reduction (%)': [35, 45, 60, 75, 40, 55],
            'Implementation Cost (%)': [20, 40, 70, 85, 30, 50],
            'Adoption Rate (%)': [95, 85, 70, 60, 80, 90]
        })
        
        # Use exact column names with percentage symbols
        fig = px.scatter(prevention_data, 
                        x='Implementation Cost (%)',
                        y='Fraud Reduction (%)',
                        size='Adoption Rate (%)',
                        text='Measure',
                        title="Fraud Prevention Measures: Cost vs Effectiveness",
                        labels={
                            'Implementation Cost (%)': 'Implementation Cost (%)',
                            'Fraud Reduction (%)': 'Fraud Reduction (%)',
                            'Adoption Rate (%)': 'Adoption Rate (%)'
                        },
                        color='Fraud Reduction (%)',
                        color_continuous_scale='RdYlGn')
        
        fig.update_traces(textposition='top center')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_data_view:
        st.subheader("Data Overview")
        
        # Data info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Data Summary")
            st.write(f"**Total Records:** {len(df):,}")
            st.write(f"**Date Range:** {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
            st.write(f"**Features:** {len(df.columns)}")
        
        with col2:
            st.markdown("### Data Quality")
            st.write(f"**Missing Values:** {df.isnull().sum().sum()}")
            st.write(f"**Duplicate Records:** {df.duplicated().sum()}")
            st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Display data sample
        st.markdown("### Data Sample")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv,
            file_name=f"fraud_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Column descriptions
        with st.expander("📖 Column Descriptions"):
            st.markdown("""
            - **transaction_id**: Unique identifier for each transaction
            - **timestamp**: Date and time of transaction
            - **amount**: Transaction amount in rupees
            - **payment_method**: UPI, Credit Card, Debit Card, Net Banking, Wallet
            - **bank**: Customer's bank
            - **upi_app**: UPI app used (if applicable)
            - **merchant_category**: Type of merchant
            - **location_city**: Transaction location
            - **device_type**: Device used for transaction
            - **fraud_flag**: Whether transaction was fraudulent
            - **fraud_type**: Type of fraud (if any)
            - **risk_score**: Calculated risk score (0-100)
            - **fraud_risk_level**: Low, Medium, or High risk
            """)

else:
    # Welcome screen
    st.info("👈 Click 'Generate & Load Data' in the sidebar to start the dashboard")
    
    st.markdown("""
    ## Welcome to the Payments Fraud Dashboard 🇮🇳
    
    This interactive dashboard provides comprehensive fraud detection and analytics for India's digital payment ecosystem.
    
    ### Features:
    - 📊 **Real-time fraud analytics** with interactive visualizations
    - 🔍 **Pattern detection** across Indian payment methods (UPI, Cards, Net Banking)
    - 🤖 **ML-based fraud prediction** with Random Forest model
    - 🛡️ **Prevention strategies** specific to the Indian market
    - 📈 **RBI compliance** monitoring and guidelines
    
    ### Data Generation:
    - Synthetic data generation based on real-world fraud patterns
    - Indian cities, banks, and UPI apps
    - Various fraud types including SIM Swap, Phishing, UPI Auto-debit
    - Configurable fraud ratio and transaction volume
    
    ### Getting Started:
    1. Use the sidebar to configure data generation parameters
    2. Click "Generate & Load Data" to create synthetic transactions
    3. Explore the different tabs for insights and predictions
    
    ### Key Metrics Tracked:
    - Transaction volume and value
    - Fraud rate by payment method, city, and time
    - High-risk transactions identification
    - Model performance metrics
    """)
    
    # Sample statistics
    st.markdown("### Sample Fraud Statistics (India 2023)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("UPI Fraud Cases", "95,000+", delta="+45%")
    with col2:
        st.metric("Amount Lost", "₹1,200 Cr+", delta="+38%")
    with col3:
        st.metric("Detection Rate", "87.3%", delta="+5.2%")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    📅 Synthetic India Payment Transactions Data | 
    🛡️ Powered by Machine Learning | 
    📊 Real-time Fraud Detection Dashboard
</div>
""", unsafe_allow_html=True)