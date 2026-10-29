#!/usr/bin/env python3
"""
Streamlit Dashboard - Predictive Maintenance Intelligence Platform
Real-time visualization and analytics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime
import requests

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .critical { 
        color: #FF0000;
        font-weight: bold;
    }
    .warning { 
        color: #FFA500;
        font-weight: bold;
    }
    .success { 
        color: #00AA00;
        font-weight: bold;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-text {
        color: #1f77b4;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================

@st.cache_data
def load_predictions():
    """Load predictions from CSV"""
    try:
        if os.path.exists('predictions.csv'):
            df = pd.read_csv('predictions.csv')
            # Parse numeric columns
            df['Failure_Probability'] = df['Failure_Probability'].astype(int)
            df['Estimated_Repair_Cost'] = df['Estimated_Repair_Cost'].astype(int)
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def get_api_status():
    """Check API status"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ==================== MAIN DASHBOARD ====================

def main():
    # Header
    col1, col2 = st.columns([0.8, 0.2])
    
    with col1:
        st.markdown("<div class='header-text'>🏭 Predictive Maintenance Platform</div>", unsafe_allow_html=True)
        st.markdown("**Real-Time Fleet Health Monitoring & AI-Powered Maintenance Predictions**")
    
    with col2:
        # API Status
        api_status = get_api_status()
        if api_status:
            st.success(f"✓ API Online")
        else:
            st.warning("⚠️ API Offline")
    
    st.divider()
    
    # Load data
    df = load_predictions()
    
    if df is None:
        st.error("""
        **❌ No predictions found!**
        
        Please run the training pipeline first:
        ```bash
        python train_pipeline.py
        ```
        
        Then refresh this page.
        """)
        return
    
    # ==================== SIDEBAR FILTERS ====================
    
    st.sidebar.title("⚙️ Dashboard Filters")
    st.sidebar.divider()
    
    # Risk level filter
    selected_risks = st.sidebar.multiselect(
        "Risk Levels",
        options=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        default=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        help="Filter machines by risk level"
    )
    
    # Health score range
    health_range = st.sidebar.slider(
        "Health Score Range",
        min_value=0,
        max_value=100,
        value=(0, 100),
        help="Filter by health score range"
    )
    
    # Filter dataframe
    df_filtered = df[
        (df['Risk_Level'].isin(selected_risks)) &
        (df['Health_Score'] >= health_range[0]) &
        (df['Health_Score'] <= health_range[1])
    ]
    
    st.sidebar.divider()
    st.sidebar.write(f"**Filtered Machines:** {len(df_filtered)} / {len(df)}")
    
    # ==================== TOP METRICS ====================
    
    st.markdown("## 📊 Fleet Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_health = df_filtered['Health_Score'].mean()
        delta_val = avg_health - 50
        st.metric(
            "Avg Health Score",
            f"{avg_health:.1f}/100",
            delta=f"{delta_val:+.1f}",
            delta_color="normal"
        )
    
    with col2:
        critical_count = (df_filtered['Risk_Level'] == 'CRITICAL').sum()
        st.metric(
            "🚨 Critical",
            critical_count,
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        high_count = (df_filtered['Risk_Level'] == 'HIGH').sum()
        st.metric(
            "⚠️ High Risk",
            high_count,
            delta=None
        )
    
    with col4:
        total_cost = df_filtered['Estimated_Repair_Cost'].sum()
        st.metric(
            "💰 Total Cost",
            f"${total_cost/1000:.1f}K",
            delta=None
        )
    
    with col5:
        avg_rul = df_filtered['Remaining_Useful_Life_Hours'].mean()
        st.metric(
            "⏱️ Avg RUL",
            f"{avg_rul:.0f} hrs",
            delta=None
        )
    
    st.divider()
    
    # ==================== VISUALIZATIONS ROW 1 ====================
    
    st.markdown("## 📈 Analytics & Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Health Score Distribution
        fig_health = go.Figure(data=[
            go.Histogram(
                x=df_filtered['Health_Score'],
                nbinsx=20,
                marker_color='rgba(0, 100, 200, 0.7)',
                name='Health Score'
            )
        ])
        fig_health.update_layout(
            title='Health Score Distribution',
            xaxis_title='Health Score',
            yaxis_title='Number of Machines',
            template='plotly_white',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    with col2:
        # Risk Distribution Pie
        risk_counts = df_filtered['Risk_Level'].value_counts()
        colors_map = {'LOW': '#00AA00', 'MEDIUM': '#FFAA00', 'HIGH': '#FF6600', 'CRITICAL': '#FF0000'}
        colors = [colors_map.get(risk, 'gray') for risk in risk_counts.index]
        
        fig_risk = go.Figure(data=[
            go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                marker=dict(colors=colors),
                textinfo='label+percent+value',
                textposition='inside'
            )
        ])
        fig_risk.update_layout(
            title='Fleet Risk Distribution',
            height=400
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # ==================== VISUALIZATIONS ROW 2 ====================
    
    col1, col2 = st.columns(2)
    
    with col1:
        # RUL vs Health Score Scatter
        fig_rul = px.scatter(
            df_filtered,
            x='Health_Score',
            y='Remaining_Useful_Life_Hours',
            color='Risk_Level',
            hover_name='Machine_ID',
            size='Failure_Probability',
            size_max=50,
            title='RUL vs Health Score',
            color_discrete_map={
                'LOW': '#00AA00',
                'MEDIUM': '#FFAA00',
                'HIGH': '#FF6600',
                'CRITICAL': '#FF0000'
            },
            labels={
                'Health_Score': 'Health Score',
                'Remaining_Useful_Life_Hours': 'RUL (Hours)'
            }
        )
        fig_rul.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig_rul, use_container_width=True)
    
    with col2:
        # Maintenance Schedule
        schedule_counts = df_filtered['Maintenance_Schedule'].value_counts()
        
        fig_schedule = go.Figure(data=[
            go.Bar(
                x=schedule_counts.index,
                y=schedule_counts.values,
                marker_color=['#FF0000', '#FF6600', '#FFAA00', '#00AA00'],
                text=schedule_counts.values,
                textposition='auto'
            )
        ])
        fig_schedule.update_layout(
            title='Maintenance Schedule Distribution',
            xaxis_title='Schedule',
            yaxis_title='Number of Machines',
            template='plotly_white',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_schedule, use_container_width=True)
    
    # ==================== CRITICAL MACHINES ====================
    
    st.divider()
    st.markdown("## 🚨 Critical Machines - Immediate Action Required")
    
    critical_machines = df_filtered[df_filtered['Risk_Level'] == 'CRITICAL'].sort_values('Health_Score')
    
    if len(critical_machines) > 0:
        st.error(f"**⚠️ {len(critical_machines)} machine(s) require immediate attention!**")
        
        st.dataframe(
            critical_machines[[
                'Machine_ID',
                'Health_Score',
                'Failure_Probability',
                'Remaining_Useful_Life_Hours',
                'Predicted_Failure_Component',
                'Estimated_Repair_Cost',
                'Maintenance_Schedule'
            ]].style.format({
                'Health_Score': '{:.0f}',
                'Remaining_Useful_Life_Hours': '{:.0f}'
            }).background_gradient(
                subset=['Health_Score'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ),
            use_container_width=True,
            height=200
        )
    else:
        st.success("✅ No critical machines! Fleet is in good condition.")
    
    # ==================== HIGH RISK MACHINES ====================
    
    st.markdown("## ⚠️ High Risk Machines")
    
    high_machines = df_filtered[df_filtered['Risk_Level'] == 'HIGH'].sort_values('Health_Score')
    
    if len(high_machines) > 0:
        with st.expander(f"View {len(high_machines)} high-risk machines", expanded=False):
            st.dataframe(
                high_machines[[
                    'Machine_ID',
                    'Health_Score',
                    'Failure_Probability',
                    'Remaining_Useful_Life_Hours',
                    'Predicted_Failure_Component',
                    'Estimated_Repair_Cost'
                ]],
                use_container_width=True
            )
    else:
        st.info("No high-risk machines in current selection")
    
    # ==================== DETAILED STATISTICS ====================
    
    st.divider()
    st.markdown("## 📉 Detailed Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Health Score")
        st.metric("Maximum", f"{df_filtered['Health_Score'].max():.0f}/100")
        st.metric("Minimum", f"{df_filtered['Health_Score'].min():.0f}/100")
        st.metric("Std Dev", f"{df_filtered['Health_Score'].std():.1f}")
    
    with col2:
        st.subheader("Remaining Useful Life")
        st.metric("Average", f"{df_filtered['Remaining_Useful_Life_Hours'].mean():.0f} hrs")
        st.metric("Machines < 100 hrs", (df_filtered['Remaining_Useful_Life_Hours'] < 100).sum())
        st.metric("Machines < 50 hrs", (df_filtered['Remaining_Useful_Life_Hours'] < 50).sum())
    
    with col3:
        st.subheader("Estimated Costs")
        st.metric("Total", f"${df_filtered['Estimated_Repair_Cost'].sum():,}")
        st.metric("Average", f"${df_filtered['Estimated_Repair_Cost'].mean():.0f}")
        st.metric("Maximum", f"${df_filtered['Estimated_Repair_Cost'].max():,}")
    
    # ==================== COMPONENT ANALYSIS ====================
    
    st.divider()
    st.markdown("## 🔧 Predicted Failure Components")
    
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        component_counts = df_filtered['Predicted_Failure_Component'].value_counts()
        fig_components = px.pie(
            values=component_counts.values,
            names=component_counts.index,
            title='Distribution of Failure Components',
            hole=0.3
        )
        fig_components.update_layout(height=400)
        st.plotly_chart(fig_components, use_container_width=True)
    
    with col2:
        st.write("### Component Breakdown")
        for component, count in component_counts.items():
            percentage = (count / len(df_filtered)) * 100
            st.write(f"**{component}:** {count} machines ({percentage:.1f}%)")
    
    # ==================== FULL DATA TABLE ====================
    
    st.divider()
    st.markdown("## 📋 Complete Fleet Data")
    
    with st.expander("View all machine data", expanded=False):
        st.dataframe(
            df_filtered.style.background_gradient(
                subset=['Health_Score'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ),
            use_container_width=True,
            height=400
        )
    
    # ==================== RECOMMENDATIONS ====================
    
    st.divider()
    st.markdown("## 💡 Executive Summary & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        immediate_count = (df_filtered['Maintenance_Schedule'] == 'Immediate').sum()
        urgent_count = (df_filtered['Maintenance_Schedule'] == 'Urgent (1-2 days)').sum()
        
        st.info(f"""
        **Immediate Actions Required:**
        
        - **{immediate_count}** machines need immediate maintenance
        - **{urgent_count}** machines need urgent maintenance (1-2 days)
        - **${df_filtered[df_filtered['Risk_Level'].isin(['CRITICAL', 'HIGH'])]['Estimated_Repair_Cost'].sum():,}** estimated cost for critical/high-risk repairs
        """)
    
    with col2:
        avg_downtime = df_filtered[df_filtered['Risk_Level'].isin(['CRITICAL', 'HIGH'])]['Estimated_Downtime_Hours'].sum()
        
        st.warning(f"""
        **Fleet Health Status:**
        
        - **Average Health:** {df_filtered['Health_Score'].mean():.1f}/100
        - **Machines < 40 health:** {(df_filtered['Health_Score'] < 40).sum()}
        - **Expected downtime (critical/high):** {avg_downtime:.0f} hours
        """)
    
    # ==================== FOOTER ====================
    
    st.divider()
    
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.write("**Total Machines:** " + str(len(df_filtered)))
    
    with footer_col2:
        st.write("**Data Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with footer_col3:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

# ==================== RUN MAIN ====================

if __name__ == "__main__":
    main()