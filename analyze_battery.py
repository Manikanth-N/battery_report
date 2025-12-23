"""
=============================================================================
🚁 UAV LiPo BATTERY HEALTH ANALYSIS SYSTEM
Advanced battery health monitoring with time-series analysis and predictive metrics
=============================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

class BatteryHealthAnalyzer:
    def __init__(self, csv_file):
        """Initialize analyzer with CSV file"""
        self.csv_file = csv_file
        self.df = None
        self.pack_stats = None
        self.cell_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        
        # LiPo voltage thresholds
        self.VOLTAGE_FULL = 4.2
        self.VOLTAGE_NOMINAL = 3.7
        self.VOLTAGE_LOW = 3.5
        self.VOLTAGE_CRITICAL = 3.3
        self.VOLTAGE_DEAD = 3.0
        
        print("🔋 UAV Battery Health Analysis System")
        print("=" * 80)
    
    def voltage_to_soc(self, voltage):
        """Convert single cell voltage to State of Charge percentage"""
        if voltage >= self.VOLTAGE_FULL:
            return 100.0
        elif voltage <= self.VOLTAGE_CRITICAL:
            return 0.0
        elif voltage > self.VOLTAGE_NOMINAL:
            # 3.7V to 4.2V = 50% to 100%
            return 50 + 50 * (voltage - self.VOLTAGE_NOMINAL) / (self.VOLTAGE_FULL - self.VOLTAGE_NOMINAL)
        else:
            # 3.3V to 3.7V = 0% to 50%
            return 50 * (voltage - self.VOLTAGE_CRITICAL) / (self.VOLTAGE_NOMINAL - self.VOLTAGE_CRITICAL)
    
    def load_and_preprocess(self):
        """Load CSV and perform initial preprocessing"""
        print(f"\n📊 Loading {self.csv_file}...")
        
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"❌ CSV file not found: {self.csv_file}")
        
        self.df = pd.read_csv(self.csv_file)
        print(f"✅ Loaded {len(self.df):,} rows")
        
        # Convert timestamp
        self.df['RTC_Time'] = pd.to_datetime(self.df['RTC_Time'])
        self.df = self.df.sort_values(['RFID', 'RTC_Time']).reset_index(drop=True)
        
        # Extract configuration (number of cells in series)
        self.df['Config'] = self.df['RFID'].str.extract(r'_(\d+)S_')[0].astype(int)
        
        # Calculate time deltas for each pack
        self.df['Time_Delta'] = self.df.groupby('RFID')['RTC_Time'].diff().dt.total_seconds() / 3600  # hours
        
        print(f"📦 Found {self.df['RFID'].nunique()} unique battery packs")
        print(f"⚙️ Configurations: {sorted(self.df['Config'].unique())}S")
        
        return self
    
    def calculate_cell_metrics(self):
        """Calculate cell-level metrics: imbalance, degradation, etc."""
        print("\n🔬 Analyzing cell-level metrics...")
        
        def calc_cell_stats(row):
            # Get valid cell voltages
            voltages = []
            for col in self.cell_cols[:row['Config']]:
                try:
                    v = float(row[col])
                    if v > 0:  # Valid voltage
                        voltages.append(v)
                except (ValueError, TypeError):
                    continue
            
            if len(voltages) == 0:
                return pd.Series({
                    'V_Max_Cell': np.nan,
                    'V_Min_Cell': np.nan,
                    'V_Avg_Cell': np.nan,
                    'Imbalance': np.nan,
                    'Imbalance_Percent': np.nan
                })
            
            v_max = max(voltages)
            v_min = min(voltages)
            v_avg = np.mean(voltages)
            imb = v_max - v_min
            imb_pct = (imb / v_avg) * 100 if v_avg > 0 else 0
            
            return pd.Series({
                'V_Max_Cell': v_max,
                'V_Min_Cell': v_min,
                'V_Avg_Cell': v_avg,
                'Imbalance': imb,
                'Imbalance_Percent': imb_pct
            })
        
        # Apply calculations
        cell_stats = self.df.apply(calc_cell_stats, axis=1)
        self.df = pd.concat([self.df, cell_stats], axis=1)
        
        # Calculate SoC from average cell voltage
        self.df['SoC_Percent'] = self.df['V_Avg_Cell'].apply(self.voltage_to_soc)
        
        # Flag critical conditions
        self.df['Low_Voltage_Flag'] = self.df['V_Min_Cell'] < self.VOLTAGE_LOW
        self.df['Critical_Voltage_Flag'] = self.df['V_Min_Cell'] < self.VOLTAGE_CRITICAL
        self.df['High_Imbalance_Flag'] = self.df['Imbalance'] > 0.1
        
        print(f"✅ Cell analysis complete")
        return self
    
    def calculate_pack_statistics(self):
        """Calculate comprehensive pack-level statistics"""
        print("\n📈 Computing pack statistics...")
        
        pack_groups = self.df.groupby('RFID')
        
        # Basic statistics
        stats = {
            'RFID': [],
            'Config': [],
            'Total_Readings': [],
            'Duration_Hours': [],
            'Avg_Voltage': [],
            'Min_Voltage': [],
            'Max_Voltage': [],
            'Voltage_Range': [],
            'Avg_Cell_Voltage': [],
            'Min_Cell_Voltage': [],
            'Max_Cell_Voltage': [],
            'Avg_Imbalance': [],
            'Max_Imbalance': [],
            'Std_Imbalance': [],
            'Low_Voltage_Events': [],
            'Critical_Voltage_Events': [],
            'High_Imbalance_Events': [],
            'Estimated_Cycles': [],
            'Voltage_Degradation': [],
            'SoH_Percent': [],
            'Health_Status': [],
            'Risk_Flags': []
        }
        
        for rfid, group in pack_groups:
            stats['RFID'].append(rfid)
            stats['Config'].append(group['Config'].iloc[0])
            stats['Total_Readings'].append(len(group))
            
            # Time analysis
            duration = (group['RTC_Time'].max() - group['RTC_Time'].min()).total_seconds() / 3600
            stats['Duration_Hours'].append(duration)
            
            # Voltage statistics
            stats['Avg_Voltage'].append(group['Total_Voltage'].mean())
            stats['Min_Voltage'].append(group['Total_Voltage'].min())
            stats['Max_Voltage'].append(group['Total_Voltage'].max())
            stats['Voltage_Range'].append(group['Total_Voltage'].max() - group['Total_Voltage'].min())
            
            # Cell voltage statistics
            stats['Avg_Cell_Voltage'].append(group['V_Avg_Cell'].mean())
            stats['Min_Cell_Voltage'].append(group['V_Min_Cell'].min())
            stats['Max_Cell_Voltage'].append(group['V_Max_Cell'].max())
            
            # Imbalance statistics
            stats['Avg_Imbalance'].append(group['Imbalance'].mean())
            stats['Max_Imbalance'].append(group['Imbalance'].max())
            stats['Std_Imbalance'].append(group['Imbalance'].std())
            
            # Event counting
            stats['Low_Voltage_Events'].append(group['Low_Voltage_Flag'].sum())
            stats['Critical_Voltage_Events'].append(group['Critical_Voltage_Flag'].sum())
            stats['High_Imbalance_Events'].append(group['High_Imbalance_Flag'].sum())
            
            # Cycle estimation (count significant voltage drops)
            voltage_drops = (group['Total_Voltage'].diff() < -0.5).sum()
            stats['Estimated_Cycles'].append(max(1, voltage_drops))
            
            # Voltage degradation (compare first vs recent readings)
            initial_v = group['V_Avg_Cell'].iloc[:10].mean()
            recent_v = group['V_Avg_Cell'].iloc[-10:].mean()
            degradation = ((initial_v - recent_v) / initial_v) * 100 if initial_v > 0 else 0
            stats['Voltage_Degradation'].append(max(0, degradation))
            
            # State of Health calculation (0-100%)
            # Factors: voltage degradation, imbalance, critical events, cycles
            soh = 100.0
            soh -= stats['Voltage_Degradation'][-1] * 2  # Voltage drop impact
            soh -= min(stats['Avg_Imbalance'][-1] * 200, 30)  # Imbalance penalty
            soh -= min(stats['Critical_Voltage_Events'][-1] * 5, 20)  # Critical event penalty
            soh -= min(stats['Estimated_Cycles'][-1] * 0.5, 15)  # Cycle wear
            soh = max(0, min(100, soh))
            stats['SoH_Percent'].append(soh)
            
            # Health status classification
            if soh >= 85:
                status = '🟢 EXCELLENT'
            elif soh >= 70:
                status = '🟡 GOOD'
            elif soh >= 50:
                status = '🟠 FAIR'
            else:
                status = '🔴 POOR'
            stats['Health_Status'].append(status)
            
            # Risk flags
            flags = []
            if stats['Critical_Voltage_Events'][-1] > 0:
                flags.append('CRITICAL_VOLTAGE')
            if stats['Max_Imbalance'][-1] > 0.2:
                flags.append('HIGH_IMBALANCE')
            if stats['Voltage_Degradation'][-1] > 10:
                flags.append('VOLTAGE_DROP')
            if stats['Estimated_Cycles'][-1] > 50:
                flags.append('HIGH_CYCLES')
            stats['Risk_Flags'].append(','.join(flags) if flags else 'NONE')
        
        self.pack_stats = pd.DataFrame(stats)
        
        print(f"✅ Statistics computed for {len(self.pack_stats)} packs")
        print(f"   Fleet Average SoH: {self.pack_stats['SoH_Percent'].mean():.1f}%")
        print(f"   Packs needing attention: {len(self.pack_stats[self.pack_stats['SoH_Percent'] < 70])}")
        
        return self
    
    def create_visualizations(self):
        """Generate interactive Plotly dashboards"""
        print("\n📊 Creating interactive visualizations...")
        
        # Dashboard 1: Health Overview Scatter
        fig1 = go.Figure()
        
        for status in self.pack_stats['Health_Status'].unique():
            mask = self.pack_stats['Health_Status'] == status
            subset = self.pack_stats[mask]
            
            fig1.add_trace(go.Scatter(
                x=subset['Avg_Imbalance'],
                y=subset['SoH_Percent'],
                mode='markers',
                name=status,
                marker=dict(
                    size=subset['Estimated_Cycles'] / 2 + 5,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=subset['RFID'],
                hovertemplate='<b>%{text}</b><br>' +
                             'SoH: %{y:.1f}%<br>' +
                             'Imbalance: %{x:.3f}V<br>' +
                             '<extra></extra>'
            ))
        
        fig1.add_hline(y=70, line_dash="dash", line_color="orange", 
                      annotation_text="Fair Threshold (70%)")
        fig1.add_hline(y=85, line_dash="dash", line_color="green", 
                      annotation_text="Good Threshold (85%)")
        fig1.add_vline(x=0.1, line_dash="dash", line_color="red",
                      annotation_text="High Imbalance (0.1V)")
        
        fig1.update_layout(
            title="🔋 Battery Pack Health Overview<br><sub>Size = Cycle Count | Hover for details</sub>",
            xaxis_title="Average Cell Imbalance (V)",
            yaxis_title="State of Health (%)",
            height=600,
            hovermode='closest',
            showlegend=True
        )
        
        # Dashboard 2: Status Distribution
        fig2 = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📊 Health Status Distribution',
                '📈 SoH Histogram',
                '⚠️ Risk Flags',
                '🔄 Configuration Breakdown'
            ),
            specs=[[{"type": "pie"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Pie chart - Status distribution
        status_counts = self.pack_stats['Health_Status'].value_counts()
        fig2.add_trace(
            go.Pie(labels=status_counts.index, values=status_counts.values,
                  marker_colors=['green', 'yellow', 'orange', 'red'],
                  textinfo='label+percent+value'),
            row=1, col=1
        )
        
        # Histogram - SoH distribution
        fig2.add_trace(
            go.Histogram(x=self.pack_stats['SoH_Percent'], nbinsx=20,
                        marker_color='steelblue', name='SoH Distribution'),
            row=1, col=2
        )
        
        # Bar chart - Risk flags
        risk_data = []
        for flags_str in self.pack_stats['Risk_Flags']:
            if flags_str != 'NONE':
                risk_data.extend(flags_str.split(','))
        
        if risk_data:
            risk_counts = pd.Series(risk_data).value_counts()
            fig2.add_trace(
                go.Bar(x=risk_counts.index, y=risk_counts.values,
                      marker_color='crimson', name='Risk Flags'),
                row=2, col=1
            )
        
        # Bar chart - Configuration breakdown
        config_counts = self.pack_stats['Config'].value_counts().sort_index()
        fig2.add_trace(
            go.Bar(x=[f"{c}S" for c in config_counts.index], 
                  y=config_counts.values,
                  marker_color='teal', name='Configuration'),
            row=2, col=2
        )
        
        fig2.update_layout(height=800, showlegend=False,
                          title_text="📊 Fleet Status Dashboard")
        
        # Dashboard 3: Configuration Comparison
        fig3 = px.box(
            self.pack_stats,
            x='Config',
            y='SoH_Percent',
            color='Health_Status',
            hover_data=['RFID', 'Avg_Imbalance', 'Estimated_Cycles'],
            title="🔋 State of Health by Configuration",
            labels={'Config': 'Battery Configuration (Cells in Series)',
                   'SoH_Percent': 'State of Health (%)'}
        )
        fig3.update_xaxes(title_text="Configuration")
        fig3.update_layout(height=600)
        
        # Dashboard 4: Detailed Pack Explorer
        fig4 = go.Figure()
        
        for config in sorted(self.pack_stats['Config'].unique()):
            subset = self.pack_stats[self.pack_stats['Config'] == config]
            
            fig4.add_trace(go.Scatter(
                x=subset['Estimated_Cycles'],
                y=subset['SoH_Percent'],
                mode='markers',
                name=f'{config}S Configuration',
                marker=dict(
                    size=subset['Max_Imbalance'] * 50 + 5,
                    opacity=0.6
                ),
                text=subset['RFID'],
                customdata=subset[['Risk_Flags', 'Avg_Imbalance', 'Critical_Voltage_Events']],
                hovertemplate='<b>%{text}</b><br>' +
                             'SoH: %{y:.1f}%<br>' +
                             'Cycles: %{x}<br>' +
                             'Risk: %{customdata[0]}<br>' +
                             'Imbalance: %{customdata[1]:.3f}V<br>' +
                             'Critical Events: %{customdata[2]}<br>' +
                             '<extra></extra>'
            ))
        
        fig4.update_layout(
            title="🔍 Pack Performance Explorer<br><sub>Size = Max Imbalance | Color = Config</sub>",
            xaxis_title="Estimated Cycle Count",
            yaxis_title="State of Health (%)",
            height=600,
            hovermode='closest'
        )
        
        # Dashboard 5: Time Series Analysis (for top packs with most data)
        top_packs = self.pack_stats.nlargest(6, 'Total_Readings')['RFID'].values
        
        fig5 = make_subplots(
            rows=3, cols=2,
            subplot_titles=[f"📈 {rfid}" for rfid in top_packs],
            vertical_spacing=0.08
        )
        
        for idx, rfid in enumerate(top_packs):
            row = (idx // 2) + 1
            col = (idx % 2) + 1
            
            pack_data = self.df[self.df['RFID'] == rfid].copy()
            
            fig5.add_trace(
                go.Scatter(x=pack_data['RTC_Time'], y=pack_data['V_Avg_Cell'],
                          mode='lines', name=f'{rfid} Voltage',
                          line=dict(color='blue', width=2)),
                row=row, col=col
            )
            
            fig5.add_trace(
                go.Scatter(x=pack_data['RTC_Time'], y=pack_data['Imbalance'] * 10,
                          mode='lines', name=f'{rfid} Imbalance×10',
                          line=dict(color='red', width=1, dash='dot')),
                row=row, col=col
            )
        
        fig5.update_layout(height=900, showlegend=False,
                          title_text="📊 Time Series Analysis - Top 6 Packs by Data Volume")
        fig5.update_xaxes(title_text="Time")
        fig5.update_yaxes(title_text="Voltage (V)")
        
        # Save all figures
        print("💾 Saving HTML dashboards...")
        fig1.write_html("battery_health_dashboard.html")
        fig2.write_html("status_overview.html")
        fig3.write_html("config_analysis.html")
        fig4.write_html("pack_details.html")
        fig5.write_html("time_series_analysis.html")
        
        print("✅ Created 5 interactive dashboards:")
        print("   • battery_health_dashboard.html")
        print("   • status_overview.html")
        print("   • config_analysis.html")
        print("   • pack_details.html")
        print("   • time_series_analysis.html")
        
        return self
    
    def save_results(self):
        """Save analysis results to CSV"""
        print("\n💾 Saving results...")
        
        # Save pack statistics
        self.pack_stats.to_csv('battery_health_results.csv', index=False)
        print("✅ Saved: battery_health_results.csv")
        
        # Save detailed event log for critical packs
        critical_packs = self.pack_stats[self.pack_stats['SoH_Percent'] < 70]['RFID'].values
        if len(critical_packs) > 0:
            critical_data = self.df[self.df['RFID'].isin(critical_packs)]
            critical_data.to_csv('critical_packs_detailed.csv', index=False)
            print(f"⚠️ Saved: critical_packs_detailed.csv ({len(critical_packs)} packs)")
        
        return self
    
    def print_summary(self):
        """Print executive summary"""
        print("\n" + "=" * 80)
        print("📋 EXECUTIVE SUMMARY")
        print("=" * 80)
        
        print(f"\n🔋 FLEET OVERVIEW:")
        print(f"   • Total Battery Packs: {len(self.pack_stats)}")
        print(f"   • Total Readings: {len(self.df):,}")
        print(f"   • Configurations: {', '.join([f'{c}S' for c in sorted(self.pack_stats['Config'].unique())])}")
        print(f"   • Average SoH: {self.pack_stats['SoH_Percent'].mean():.1f}% ± {self.pack_stats['SoH_Percent'].std():.1f}%")
        
        print(f"\n📊 HEALTH STATUS:")
        status_counts = self.pack_stats['Health_Status'].value_counts()
        for status, count in status_counts.items():
            pct = (count / len(self.pack_stats)) * 100
            print(f"   {status}: {count} packs ({pct:.1f}%)")
        
        print(f"\n⚠️ RISK ASSESSMENT:")
        print(f"   • Critical Voltage Events: {self.pack_stats['Critical_Voltage_Events'].sum()}")
        print(f"   • High Imbalance Events: {self.pack_stats['High_Imbalance_Events'].sum()}")
        print(f"   • Packs needing immediate attention: {len(self.pack_stats[self.pack_stats['SoH_Percent'] < 50])}")
        print(f"   • Packs requiring monitoring: {len(self.pack_stats[(self.pack_stats['SoH_Percent'] >= 50) & (self.pack_stats['SoH_Percent'] < 70)])}")
        
        print(f"\n🔴 WORST 5 PACKS:")
        worst = self.pack_stats.nsmallest(5, 'SoH_Percent')[
            ['RFID', 'Config', 'SoH_Percent', 'Avg_Imbalance', 'Health_Status', 'Risk_Flags']
        ]
        print(worst.to_string(index=False))
        
        print(f"\n🟢 BEST 5 PACKS:")
        best = self.pack_stats.nlargest(5, 'SoH_Percent')[
            ['RFID', 'Config', 'SoH_Percent', 'Avg_Imbalance', 'Health_Status']
        ]
        print(best.to_string(index=False))
        
        print("\n" + "=" * 80)
        print("🎉 ANALYSIS COMPLETE - Ready for deployment!")
        print("=" * 80)
        
        return self


def main():
    """Main execution function"""
    # Check for CSV file
    csv_file = 'battery_real_time_log.csv'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    try:
        # Create analyzer and run pipeline
        analyzer = BatteryHealthAnalyzer(csv_file)
        analyzer.load_and_preprocess() \
               .calculate_cell_metrics() \
               .calculate_pack_statistics() \
               .create_visualizations() \
               .save_results() \
               .print_summary()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
