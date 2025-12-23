# =============================================================================
# 🚁 UAV LiPo BATTERY HEALTH DASHBOARD - COMPLETE PIPELINE
# 1. CSV → Analysis → Plotly → GitHub Pages Ready HTML
# =============================================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = 'colab'

print("🔋 UAV LiPo Battery Health Analysis - GitHub Pages Ready")
print("=" * 70)

# LiPo OCV: Voltage → SoC%
def voltage_to_soc(voltage):
    if voltage >= 4.2: return 100.0
    elif voltage <= 3.3: return 0.0
    elif voltage > 3.7: return 50 + 50 * (voltage - 3.7) / 0.5
    else: return 50 * (voltage - 3.3) / 0.4

# 1. LOAD DATA
print("📊 Loading battery_real_time_log.csv...")
df = pd.read_csv('battery_real_time_log.csv')
print(f"✅ Loaded {len(df):,} rows, {df['RFID'].nunique()} packs")

# Preprocess
df['RTC_Time'] = pd.to_datetime(df['RTC_Time'])
df = df.sort_values(['RFID', 'RTC_Time'])
df['Config'] = df['RFID'].str.extract(r'_(\d+)S_')[0].astype(int)

# 2. CELL IMBALANCE
cell_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
def calc_imbalance(row):
    voltages = [float(row[col]) for col in cell_cols if pd.notna(row[col]) and str(row[col]) != '']
    return max(voltages) - min(voltages) if len(voltages) > 1 else 0.0

df['Imbalance'] = df.apply(calc_imbalance, axis=1)
df['V_Avg_Cell'] = df['Total_Voltage'] / df['Config']
df['SoC_Mean'] = df['V_Avg_Cell'].apply(voltage_to_soc)

# 3. PACK STATS
pack_stats = df.groupby('RFID').agg(
    Config=('Config', 'first'),
    Readings=('RTC_Time', 'count'),
    Avg_Voltage=('Total_Voltage', 'mean'),
    Min_Voltage=('Total_Voltage', 'min'),
    Max_Voltage=('Total_Voltage', 'max'),
    Avg_Imbalance=('Imbalance', 'mean'),
    Max_Imbalance=('Imbalance', 'max'),
    Low_V_Events=('Total_Voltage', lambda x: (x < 3.3 * df.loc[x.index, 'Config'].iloc[0]).sum()),
    Cycles=('RTC_Time', lambda x: ((x.diff() > pd.Timedelta('24h')).cumsum() + 1).max())
).reset_index()

# SoH Calculation
pack_stats['Initial_V'] = df.groupby('RFID')['Total_Voltage'].first().values
pack_stats['Full_Charge_V'] = (pack_stats['Initial_V'] / pack_stats['Config']) * 4.2
pack_stats['SoH'] = (
    (pack_stats['Full_Charge_V'] / pack_stats['Initial_V']) * 
    (1 - pack_stats['Low_V_Events'] / 10) * 
    (1 - pack_stats['Avg_Imbalance'] / 0.1)
).clip(0, 100)

# Status & Flags
conditions = [pack_stats['SoH'] < 70, pack_stats['Avg_Imbalance'] > 0.1, 
              pack_stats['Low_V_Events'] > 0, pack_stats['Max_Imbalance'] > 0.2]
flags = ['POOR_SOH', 'HIGH_IMB', 'LOW_V', 'CRIT_IMB']
pack_stats['Flags'] = [','.join(f for f, c in zip(flags, cond) if c) for cond in zip(*conditions)]
pack_stats['Status'] = np.where(pack_stats['SoH'] > 80, '🟢 GOOD',
                               np.where(pack_stats['SoH'] > 60, '🟡 FAIR', '🔴 POOR'))

# SAVE CSV
pack_stats.to_csv('battery_health_results.csv', index=False)

# =============================================================================
# 🖥️ INTERACTIVE PLOTLY DASHBOARDS
# =============================================================================

# DASHBOARD 1: MAIN HEALTH OVERVIEW
fig1 = px.scatter(pack_stats, x='Avg_Imbalance', y='SoH', 
                  size='Cycles', color='Config', 
                  hover_data=['RFID', 'Status', 'Flags', 'Readings'],
                  title="🔍 UAV Battery Health Overview<br><sub>Hover packs | Zoom | Filter by config</sub>",
                  labels={'Avg_Imbalance': 'Cell Imbalance (V)', 'SoH': 'State of Health %'},
                  color_continuous_scale='viridis',
                  height=600)
fig1.add_hline(y=80, line_dash="dash", line_color="green", 
               annotation_text="GOOD (>80%)", annotation_position="top right")
fig1.add_vline(x=0.10, line_dash="dash", line_color="red", 
               annotation_text="HIGH IMBALANCE (>0.10V)", annotation_position="bottom right")
fig1.show()

# DASHBOARD 2: STATUS + DISTRIBUTION
fig2 = make_subplots(rows=1, cols=2, 
                     subplot_titles=('📊 Pack Status', '📈 SoH Distribution'),
                     specs=[[{"type": "pie"}, {"type": "histogram"}]],
                     horizontal_spacing=0.1)

status_counts = pack_stats['Status'].value_counts()
fig2.add_trace(go.Pie(labels=status_counts.index, values=status_counts.values,
                      marker_colors=['green', 'orange', 'red'],
                      textinfo='label+percent+value', pull=[0.1, 0, 0]), row=1, col=1)

fig2.add_trace(go.Histogram(x=pack_stats['SoH'], nbinsx=20, 
                           marker_color='orange', name='SoH'), row=1, col=2)
fig2.add_vline(x=pack_stats['SoH'].mean(), line_dash="dash", line_color="red", 
               annotation_text=f"Mean: {pack_stats['SoH'].mean():.1f}%")
fig2.update_layout(height=500, title_text="Status & SoH Distribution")
fig2.show()

# DASHBOARD 3: CONFIG COMPARISON
fig3 = px.box(pack_stats, x='Config', y='SoH', 
              color='Status', hover_data=['RFID', 'Avg_Imbalance'],
              title="🔋 SoH by Battery Configuration (1S-6S)",
              labels={'Config': 'Cells in Series'})
fig3.show()

# DASHBOARD 4: ALL PACKS TABLE VIEW
fig4 = px.scatter(pack_stats.sort_values('SoH'), x='Avg_Imbalance', y='SoH', 
                  color='Status', size='Readings', hover_name='RFID',
                  hover_data=['Config', 'Cycles', 'Flags', 'Low_V_Events'],
                  title="🏷️ All Packs - Click & Drag to Explore", height=600)
fig4.show()

# =============================================================================
# 💾 EXPORT HTML FOR GITHUB PAGES
# =============================================================================
print("\n💾 SAVING GITHUB PAGES FILES...")

fig1.write_html("1_health_overview.html")
fig2.write_html("2_status_distribution.html")
fig3.write_html("3_config_analysis.html")
fig4.write_html("4_pack_explorer.html")
pack_stats.to_csv('battery_health_results.csv', index=False)

print("✅ DASHBOARD FILES READY:")
print("📱 1_health_overview.html     ← MAIN DASHBOARD")
print("📊 2_status_distribution.html")
print("🔋 3_config_analysis.html")
print("🏷️  4_pack_explorer.html")
print("📄 battery_health_results.csv")

# EXECUTIVE SUMMARY
print("\n" + "="*60)
print("📋 EXECUTIVE SUMMARY")
print("="*60)
print(f"• Total Packs: {len(pack_stats)}")
print(f"• Fleet SoH: {pack_stats['SoH'].mean():.1f}% ± {pack_stats['SoH'].std():.1f}%")
print(f"• Critical (<60%): {len(pack_stats[pack_stats['SoH']<60])}")
print(f"• High Imbalance (>0.1V): {len(pack_stats[pack_stats['Avg_Imbalance']>0.1])}")
print("\n🔴 WORST 5 PACKS:")
print(pack_stats.nsmallest(5, 'SoH')[['RFID', 'Config', 'SoH', 'Avg_Imbalance', 'Status']].round(2).to_string(index=False))

print("\n🎉 READY FOR GITHUB PAGES DEPLOYMENT!")
