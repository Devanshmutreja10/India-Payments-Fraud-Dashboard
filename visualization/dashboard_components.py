# visualization/dashboard_components.py

import streamlit as st
import pandas as pd
from utils.helpers import format_indian_currency

class DashboardComponents:
    """Reusable Streamlit components for the dashboard"""
    
    @staticmethod
    def display_metrics(df):
        """Display key metrics in a row"""
        total_transactions = len(df)
        fraud_count = df['fraud_flag'].sum()
        fraud_rate = (fraud_count / total_transactions) * 100
        
        total_amount = df['amount'].sum()
        fraud_amount = df[df['fraud_flag'] == True]['amount'].sum()
        fraud_amount_rate = (fraud_amount / total_amount) * 100 if total_amount > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", f"{total_transactions:,}")
        
        with col2:
            st.metric("Fraudulent Transactions", f"{fraud_count:,}", 
                     delta=f"{fraud_rate:.1f}%")
        
        with col3:
            st.metric("Total Transaction Value", format_indian_currency(total_amount))
        
        with col4:
            st.metric("Fraud Amount", format_indian_currency(fraud_amount),
                     delta=f"{fraud_amount_rate:.1f}% of total")
    
    @staticmethod
    def display_risk_summary(df):
        """Display risk level summary"""
        risk_counts = df['fraud_risk_level'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🟢 Low Risk")
            st.metric("Count", risk_counts.get('Low', 0))
            st.metric("Percentage", f"{(risk_counts.get('Low', 0)/len(df)*100):.1f}%")
        
        with col2:
            st.markdown("### 🟡 Medium Risk")
            st.metric("Count", risk_counts.get('Medium', 0))
            st.metric("Percentage", f"{(risk_counts.get('Medium', 0)/len(df)*100):.1f}%")
        
        with col3:
            st.markdown("### 🔴 High Risk")
            st.metric("Count", risk_counts.get('High', 0))
            st.metric("Percentage", f"{(risk_counts.get('High', 0)/len(df)*100):.1f}%")
    
    @staticmethod
    def display_high_risk_transactions(df, top_n=10):
        """Display high risk transactions table"""
        st.subheader("⚠️ High Risk Transactions")
        
        high_risk = df[df['fraud_risk_level'] == 'High'].sort_values('risk_score', ascending=False).head(top_n)
        
        display_cols = ['transaction_id', 'timestamp', 'amount', 'payment_method', 
                       'location_city', 'fraud_type', 'risk_score']
        
        # Format for display
        high_risk_display = high_risk[display_cols].copy()
        high_risk_display['amount'] = high_risk_display['amount'].apply(format_indian_currency)
        high_risk_display['risk_score'] = high_risk_display['risk_score'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(high_risk_display, use_container_width=True)
        
        # Download button
        csv = high_risk.to_csv(index=False)
        st.download_button(
            label="📥 Download High Risk Transactions",
            data=csv,
            file_name="high_risk_transactions.csv",
            mime="text/csv"
        )
    
    @staticmethod
    def display_filter_sidebar(df):
        """Display filter controls in sidebar"""
        st.sidebar.markdown("### 🔍 Filters")
        
        # Date range filter
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Amount range filter
        min_amount = float(df['amount'].min())
        max_amount = float(df['amount'].max())
        
        amount_range = st.sidebar.slider(
            "Amount Range (₹)",
            min_amount, max_amount,
            (min_amount, max_amount)
        )
        
        # Payment method filter
        payment_methods = ['All'] + list(df['payment_method'].unique())
        selected_payment = st.sidebar.selectbox("Payment Method", payment_methods)
        
        # City filter
        cities = ['All'] + list(df['location_city'].unique())
        selected_city = st.sidebar.selectbox("City", cities)
        
        # Risk level filter
        risk_levels = ['All', 'Low', 'Medium', 'High']
        selected_risk = st.sidebar.selectbox("Risk Level", risk_levels)
        
        # Apply filters
        filtered_df = df.copy()
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['timestamp'].dt.date >= date_range[0]) &
                (filtered_df['timestamp'].dt.date <= date_range[1])
            ]
        
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) &
            (filtered_df['amount'] <= amount_range[1])
        ]
        
        if selected_payment != 'All':
            filtered_df = filtered_df[filtered_df['payment_method'] == selected_payment]
        
        if selected_city != 'All':
            filtered_df = filtered_df[filtered_df['location_city'] == selected_city]
        
        if selected_risk != 'All':
            filtered_df = filtered_df[filtered_df['fraud_risk_level'] == selected_risk]
        
        st.sidebar.markdown(f"**Filtered Records:** {len(filtered_df):,}")
        
        return filtered_df