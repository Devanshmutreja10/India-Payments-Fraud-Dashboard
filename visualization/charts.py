# visualization/charts.py

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class FraudVisualizer:
    """Create interactive visualizations for fraud analytics"""
    
    @staticmethod
    def plot_fraud_timeline(df):
        """Plot fraud transactions over time"""
        daily_stats = df.set_index('timestamp').resample('D').agg({
            'amount': 'sum',
            'fraud_flag': 'sum'
        }).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=daily_stats['timestamp'], y=daily_stats['amount'],
                      name="Transaction Volume", line=dict(color='blue', width=2)),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=daily_stats['timestamp'], y=daily_stats['fraud_flag'],
                      name="Fraud Count", line=dict(color='red', width=2, dash='dash')),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Daily Transaction Volume vs Fraud Count",
            xaxis_title="Date",
            hovermode='x unified',
            height=450
        )
        
        fig.update_yaxes(title_text="Transaction Amount (₹)", secondary_y=False)
        fig.update_yaxes(title_text="Number of Fraud Cases", secondary_y=True)
        
        return fig
    
    @staticmethod
    def plot_fraud_by_payment_method(df):
        """Plot fraud rates by payment method"""
        payment_stats = df.groupby('payment_method').agg({
            'transaction_id': 'count',
            'fraud_flag': 'sum'
        }).reset_index()
        
        payment_stats.columns = ['Payment Method', 'Total Transactions', 'Fraud Count']
        payment_stats['Fraud Rate (%)'] = (payment_stats['Fraud Count'] / payment_stats['Total Transactions'] * 100).round(2)
        
        fig = px.bar(payment_stats, x='Payment Method', y='Fraud Rate (%)',
                    title="Fraud Rate by Payment Method",
                    color='Fraud Rate (%)', color_continuous_scale='Reds',
                    text='Fraud Rate (%)')
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=450)
        
        return fig
    
    @staticmethod
    def plot_fraud_by_city(df, top_n=10):
        """Plot top cities by fraud rate"""
        city_stats = df.groupby('location_city').agg({
            'transaction_id': 'count',
            'fraud_flag': 'sum'
        }).reset_index()
        
        city_stats.columns = ['City', 'Total Transactions', 'Fraud Count']
        city_stats['Fraud Rate (%)'] = (city_stats['Fraud Count'] / city_stats['Total Transactions'] * 100).round(2)
        city_stats = city_stats.nlargest(top_n, 'Fraud Rate (%)')
        
        fig = px.bar(city_stats, x='Fraud Rate (%)', y='City',
                    title=f"Top {top_n} Cities by Fraud Rate",
                    orientation='h', color='Fraud Rate (%)',
                    color_continuous_scale='Reds')
        
        fig.update_layout(height=500)
        return fig
    
    @staticmethod
    def plot_amount_distribution(df):
        """Plot amount distribution for fraud vs non-fraud"""
        fig = px.histogram(df, x='amount', nbins=50, color='fraud_flag',
                          title="Transaction Amount Distribution",
                          labels={'amount': 'Amount (₹)', 'count': 'Frequency'},
                          color_discrete_map={True: 'red', False: 'blue'},
                          opacity=0.7)
        
        fig.update_layout(barmode='overlay', height=450)
        return fig
    
    @staticmethod
    def plot_fraud_by_hour(df):
        """Plot fraud rate by hour of day"""
        hourly_stats = df.groupby('transaction_hour')['fraud_flag'].agg(['mean', 'count']).reset_index()
        hourly_stats.columns = ['Hour', 'Fraud Rate', 'Transaction Count']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=hourly_stats['Hour'], y=hourly_stats['Fraud Rate'] * 100,
                      name="Fraud Rate", line=dict(color='red', width=3)),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Bar(x=hourly_stats['Hour'], y=hourly_stats['Transaction Count'],
                   name="Transaction Volume", marker_color='lightblue', opacity=0.5),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Fraud Rate by Hour of Day",
            xaxis_title="Hour of Day (24-hour format)",
            hovermode='x unified',
            height=450
        )
        
        fig.update_yaxes(title_text="Fraud Rate (%)", secondary_y=False)
        fig.update_yaxes(title_text="Number of Transactions", secondary_y=True)
        
        return fig
    
    @staticmethod
    def plot_fraud_types_distribution(df):
        """Plot distribution of fraud types"""
        fraud_types = df[df['fraud_flag'] == True]['fraud_type'].value_counts()
        
        fig = px.pie(values=fraud_types.values, names=fraud_types.index,
                    title="Distribution of Fraud Types in India",
                    hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=450)
        
        return fig
    
    @staticmethod
    def plot_risk_metrics_comparison(df):
        """Compare risk metrics for different risk levels"""
        risk_metrics = df.groupby('fraud_risk_level').agg({
            'amount': 'mean',
            'velocity_30min': 'mean',
            'failed_attempts_before_success': 'mean',
            'distance_from_home_km': 'mean'
        }).reset_index()
        
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Average Amount (₹)', 'Transaction Velocity',
                                         'Failed Attempts', 'Distance from Home (km)'))
        
        metrics_config = [
            ('amount', 'Average Amount (₹)', 1, 1),
            ('velocity_30min', 'Velocity (txns/30min)', 1, 2),
            ('failed_attempts_before_success', 'Failed Attempts', 2, 1),
            ('distance_from_home_km', 'Distance (km)', 2, 2)
        ]
        
        colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        
        for metric, title, row, col in metrics_config:
            for risk_level in risk_metrics['fraud_risk_level']:
                value = risk_metrics[risk_metrics['fraud_risk_level'] == risk_level][metric].values[0]
                fig.add_trace(
                    go.Bar(name=risk_level, x=[risk_level], y=[value],
                          marker_color=colors.get(risk_level, 'gray'),
                          showlegend=(row == 1 and col == 1)),
                    row=row, col=col
                )
            
            fig.update_yaxes(title_text=title, row=row, col=col)
        
        fig.update_layout(height=600, title_text="Risk Metrics by Risk Level")
        return fig
    
    @staticmethod
    def plot_feature_importance(feature_importance_df, top_n=10):
        """Plot feature importance from ML model"""
        top_features = feature_importance_df.head(top_n)
        
        fig = px.bar(top_features, x='importance', y='feature',
                    title=f"Top {top_n} Features for Fraud Detection",
                    orientation='h', color='importance',
                    color_continuous_scale='Viridis')
        
        fig.update_layout(height=500)
        return fig
    
    @staticmethod
    def create_gauge_chart(risk_score, title="Fraud Risk Score"):
        """Create a gauge chart for risk score"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            title={'text': title},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "salmon"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig