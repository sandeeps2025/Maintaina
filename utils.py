import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class Dashboard:
    """Real-time Dashboard Visualization"""
    
    def __init__(self, predictions_df):
        self.df = predictions_df
    
    def health_score_gauge(self, machine_id):
        """Create health score gauge for single machine"""
        
        machine = self.df[self.df['Machine_ID'] == machine_id].iloc[0]
        health = machine['Health_Score']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health,
            title={'text': f"Health Score - {machine_id}"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 60], 'color': "orange"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        
        return fig
    
    def fleet_health_distribution(self):
        """Health score distribution across fleet"""
        
        fig = go.Figure(data=[
            go.Histogram(
                x=self.df['Health_Score'],
                nbinsx=20,
                name='Health Score',
                marker_color='rgba(0, 100, 200, 0.7)'
            )
        ])
        
        fig.update_layout(
            title='Fleet Health Score Distribution',
            xaxis_title='Health Score',
            yaxis_title='Number of Machines',
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def risk_distribution_pie(self):
        """Risk level distribution pie chart"""
        
        risk_counts = self.df['Risk_Level'].value_counts()
        
        colors_map = {
            'LOW': 'green',
            'MEDIUM': 'yellow',
            'HIGH': 'orange',
            'CRITICAL': 'red'
        }
        
        colors = [colors_map.get(risk, 'gray') for risk in risk_counts.index]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                marker=dict(colors=colors),
                textposition='inside',
                textinfo='label+percent'
            )
        ])
        
        fig.update_layout(
            title='Fleet Risk Distribution',
            showlegend=True
        )
        
        return fig
    
    def maintenance_schedule_bar(self):
        """Maintenance schedule requirements"""
        
        schedule_counts = self.df['Maintenance_Schedule'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=schedule_counts.index,
                y=schedule_counts.values,
                marker_color=['red', 'orange', 'yellow', 'green'][:len(schedule_counts)]
            )
        ])
        
        fig.update_layout(
            title='Maintenance Schedule Distribution',
            xaxis_title='Schedule',
            yaxis_title='Number of Machines',
            template='plotly_white'
        )
        
        return fig
    
    def rul_scatter(self):
        """RUL vs Health Score scatter plot"""
        
        fig = px.scatter(
            self.df,
            x='Health_Score',
            y='Remaining_Useful_Life_Hours',
            color='Risk_Level',
            hover_name='Machine_ID',
            size='Failure_Probability',
            title='Remaining Useful Life vs Health Score',
            color_discrete_map={
                'LOW': 'green',
                'MEDIUM': 'yellow',
                'HIGH': 'orange',
                'CRITICAL': 'red'
            }
        )
        
        return fig
    
    def failure_probability_histogram(self):
        """Failure probability distribution"""
        
        failure_proba = self.df['Failure_Probability'].astype(int)
        
        fig = go.Figure(data=[
            go.Histogram(
                x=failure_proba,
                nbinsx=20,
                marker_color='rgba(255, 100, 0, 0.7)',
                name='Failure Probability'
            )
        ])
        
        fig.update_layout(
            title='Failure Probability Distribution',
            xaxis_title='Probability (%)',
            yaxis_title='Number of Machines',
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def cost_analysis_bar(self):
        """Repair cost analysis by risk level"""
        
        cost_by_risk = self.df.groupby('Risk_Level')['Estimated_Repair_Cost'].agg(['sum', 'mean', 'count'])
        
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=("Total Cost by Risk", "Average Cost by Risk")
        )
        
        fig.add_trace(
            go.Bar(
                x=cost_by_risk.index,
                y=cost_by_risk['sum'],
                name='Total Cost',
                marker_color=['green', 'yellow', 'orange', 'red']
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=cost_by_risk.index,
                y=cost_by_risk['mean'],
                name='Avg Cost',
                mode='lines+markers',
                marker=dict(size=10),
                line=dict(width=3, color='darkblue')
            ),
            secondary_y=True
        )
        
        fig.update_yaxes(title_text="Total Cost ($)", secondary_y=False)
        fig.update_yaxes(title_text="Average Cost ($)", secondary_y=True)
        fig.update_layout(title='Maintenance Cost Analysis', template='plotly_white')
        
        return fig
    
    def top_machines_alert(self, top_n=5):
        """Top machines requiring attention"""
        
        critical_machines = self.df[self.df['Risk_Level'].isin(['CRITICAL', 'HIGH'])].head(top_n)
        
        fig = go.Figure(data=[
            go.Bar(
                x=critical_machines['Machine_ID'],
                y=critical_machines['Health_Score'],
                marker_color=critical_machines['Risk_Level'].map({
                    'CRITICAL': 'red',
                    'HIGH': 'orange'
                }),
                text=critical_machines['Health_Score'],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title=f'Top {top_n} Machines Requiring Attention',
            xaxis_title='Machine ID',
            yaxis_title='Health Score',
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    def component_failure_distribution(self):
        """Distribution of predicted failure components"""
        
        component_counts = self.df['Predicted_Failure_Component'].value_counts()
        
        fig = px.pie(
            values=component_counts.values,
            names=component_counts.index,
            title='Predicted Failure Components',
            hole=0.3
        )
        
        return fig
    
    def create_dashboard_html(self, output_file='dashboard.html'):
        """Create interactive HTML dashboard"""
        
        from plotly.subplots import make_subplots
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Health Score Distribution',
                'Risk Distribution',
                'Maintenance Schedule',
                'RUL vs Health Score',
                'Failure Probability',
                'Failure Components'
            ),
            specs=[
                [{"type": "histogram"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "histogram"}, {"type": "pie"}]
            ]
        )
        
        # 1. Health score histogram
        fig.add_trace(
            go.Histogram(x=self.df['Health_Score'], nbinsx=20, name='Health'),
            row=1, col=1
        )
        
        # 2. Risk pie
        risk_counts = self.df['Risk_Level'].value_counts()
        fig.add_trace(
            go.Pie(labels=risk_counts.index, values=risk_counts.values),
            row=1, col=2
        )
        
        # 3. Maintenance bar
        schedule_counts = self.df['Maintenance_Schedule'].value_counts()
        fig.add_trace(
            go.Bar(x=schedule_counts.index, y=schedule_counts.values, name='Schedule'),
            row=2, col=1
        )
        
        # 4. RUL scatter
        fig.add_trace(
            go.Scatter(
                x=self.df['Health_Score'],
                y=self.df['Remaining_Useful_Life_Hours'],
                mode='markers',
                name='RUL',
                marker=dict(size=8)
            ),
            row=2, col=2
        )
        
        # 5. Failure probability histogram
        fig.add_trace(
            go.Histogram(x=self.df['Failure_Probability'].astype(int), nbinsx=20, name='Failure'),
            row=3, col=1
        )
        
        # 6. Component pie
        component_counts = self.df['Predicted_Failure_Component'].value_counts()
        fig.add_trace(
            go.Pie(labels=component_counts.index, values=component_counts.values),
            row=3, col=2
        )
        
        fig.update_layout(
            title_text="Predictive Maintenance Intelligence Platform - Dashboard",
            height=1200,
            showlegend=False,
            template='plotly_white'
        )
        
        fig.write_html(output_file)
        print(f"Dashboard saved to {output_file}")

class ReportGenerator:
    """Generate maintenance reports"""
    
    def __init__(self, predictions_df):
        self.df = predictions_df
    
    def executive_summary(self):
        """Generate executive summary"""
        
        report = f"""
{'='*70}
EXECUTIVE SUMMARY - FLEET HEALTH REPORT
{'='*70}

FLEET STATISTICS:
- Total Machines: {len(self.df)}
- Average Health Score: {self.df['Health_Score'].mean():.1f}/100
- Machines in Critical State: {(self.df['Risk_Level'] == 'CRITICAL').sum()}
- Machines Requiring Urgent Attention: {(self.df['Risk_Level'].isin(['CRITICAL', 'HIGH'])).sum()}

FINANCIAL IMPACT:
- Total Estimated Repair Cost: ${self.df['Estimated_Repair_Cost'].sum():,}
- Average Repair Cost per Machine: ${self.df['Estimated_Repair_Cost'].mean():.2f}
- Total Expected Downtime: {self.df['Estimated_Downtime_Hours'].sum()} hours

MAINTENANCE SCHEDULE:
- Immediate Action: {(self.df['Maintenance_Schedule'] == 'Immediate').sum()} machines
- Urgent (1-2 days): {(self.df['Maintenance_Schedule'] == 'Urgent (1-2 days)').sum()} machines
- Soon (1-2 weeks): {(self.df['Maintenance_Schedule'] == 'Soon (1-2 weeks)').sum()} machines
- Routine (1-3 months): {(self.df['Maintenance_Schedule'] == 'Routine (1-3 months)').sum()} machines

COMPONENT ANALYSIS:
{self.df['Predicted_Failure_Component'].value_counts().to_string()}

RECOMMENDATIONS:
1. Schedule immediate maintenance for {(self.df['Risk_Level'] == 'CRITICAL').sum()} critical machines
2. Budget ${self.df[self.df['Risk_Level'].isin(['CRITICAL', 'HIGH'])]['Estimated_Repair_Cost'].sum():,} for urgent repairs
3. Monitor {(self.df['Risk_Level'] == 'MEDIUM').sum()} medium-risk machines closely
4. Plan preventive maintenance for {(self.df['Maintenance_Schedule'] == 'Soon (1-2 weeks)').sum()} machines

{'='*70}
"""
        return report
    
    def critical_machines_report(self):
        """Report on critical machines"""
        
        critical = self.df[self.df['Risk_Level'] == 'CRITICAL'].sort_values('Health_Score')
        
        report = f"\n{'='*70}\nCRITICAL MACHINES REQUIRING IMMEDIATE ACTION\n{'='*70}\n\n"
        
        for idx, row in critical.iterrows():
            report += f"""
Machine ID: {row['Machine_ID']}
  Health Score: {row['Health_Score']}/100
  Failure Probability: {row['Failure_Probability']}%
  Remaining Useful Life: {row['Remaining_Useful_Life_Hours']} hours
  Predicted Failure Component: {row['Predicted_Failure_Component']}
  Estimated Repair Cost: ${row['Estimated_Repair_Cost']:,}
  Expected Downtime: {row['Estimated_Downtime_Hours']} hours
  Action Required: {row['Maintenance_Schedule']}
"""
        
        return report

if __name__ == "__main__":
    # Example usage
    print("Dashboard and Reporting utilities loaded successfully")