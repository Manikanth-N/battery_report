# 🚁 UAV LiPo Battery Health Monitoring Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

Real-time battery health analysis system for UAV operations using RFID-based data logging with ESP32 NFC readers.

## 🎯 Features

### Advanced Analytics
- **State of Health (SoH) Calculation**: Multi-factor analysis considering voltage degradation, cell imbalance, critical events, and cycle count
- **Cell Imbalance Detection**: Real-time monitoring of voltage differences across cells in series configurations
- **Cycle Estimation**: Automatic detection and counting of charge/discharge cycles
- **Risk Assessment**: Identifies critical voltage events, high imbalance, and degradation patterns
- **Time Series Analysis**: Track battery performance over time with interactive charts

### Interactive Visualizations
1. **Health Overview Dashboard**: Scatter plot showing SoH vs imbalance with pack details
2. **Status Distribution**: Pie charts and histograms showing fleet health breakdown
3. **Configuration Analysis**: Compare different battery configurations (1S-6S)
4. **Pack Explorer**: Detailed view of individual pack performance and risk factors
5. **Time Series Charts**: Voltage and imbalance trends over time for top packs

### Automated Reporting
- CSV export of comprehensive battery health metrics
- Critical pack detailed logs for packs requiring immediate attention
- Executive summary with fleet statistics and recommendations
- Color-coded health status (🟢 Excellent, 🟡 Good, 🟠 Fair, 🔴 Poor)

## 📦 Installation

### Requirements
```bash
pip install pandas numpy plotly
```

### Dependencies
- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.20.0
- plotly >= 5.0.0

## 🚀 Quick Start

### 1. Prepare Your Data
Ensure your CSV file (`battery_real_time_log.csv`) has the following columns:
- `RFID`: Battery pack identifier (format: `PACK_XS_XXX` where X is number of cells)
- `RTC_Time`: Timestamp (ISO format or parseable datetime)
- `Total_Voltage`: Total pack voltage
- `C1`, `C2`, `C3`, `C4`, `C5`, `C6`: Individual cell voltages

### 2. Run Analysis
```bash
python analyze_battery.py
```

Or specify a custom CSV file:
```bash
python analyze_battery.py your_battery_log.csv
```

### 3. View Results
Open `index.html` in your browser to view the interactive dashboard, or deploy to GitHub Pages for online access.

## 📈 Output Files

After analysis, the following files are generated:

| File | Description |
|------|-------------|
| `battery_health_results.csv` | Comprehensive pack statistics and health metrics |
| `battery_health_dashboard.html` | Main health overview scatter plot |
| `status_overview.html` | Fleet status distribution and histograms |
| `config_analysis.html` | Configuration comparison charts |
| `pack_details.html` | Individual pack performance explorer |
| `time_series_analysis.html` | Time-based voltage and imbalance trends |
| `critical_packs_detailed.csv` | Detailed logs for packs with SoH < 70% |
| `index.html` | Main dashboard landing page |

## 📊 Understanding the Metrics

### State of Health (SoH)
Calculated from multiple factors:
- **Voltage Degradation**: Comparison of initial vs recent average cell voltage
- **Cell Imbalance**: Average and maximum voltage differences between cells
- **Critical Events**: Count of dangerous voltage conditions (< 3.3V per cell)
- **Cycle Wear**: Estimated number of charge/discharge cycles

**Formula**: `SoH = 100% - (degradation_penalty + imbalance_penalty + critical_events_penalty + cycle_penalty)`

### Health Status Categories
- **🟢 EXCELLENT**: SoH ≥ 85% - Battery in optimal condition
- **🟡 GOOD**: 70% ≤ SoH < 85% - Normal wear, regular monitoring recommended
- **🟠 FAIR**: 50% ≤ SoH < 70% - Significant degradation, increased monitoring required
- **🔴 POOR**: SoH < 50% - Critical condition, replacement recommended

### Risk Flags
- `CRITICAL_VOLTAGE`: One or more cells dropped below 3.3V
- `HIGH_IMBALANCE`: Maximum cell imbalance exceeded 0.2V
- `VOLTAGE_DROP`: Overall degradation exceeds 10%
- `HIGH_CYCLES`: Estimated cycles exceed 50 (indicates heavy use)

## 🔧 Customization

You can adjust voltage thresholds in `analyze_battery.py`:

```python
class BatteryHealthAnalyzer:
    def __init__(self, csv_file):
        self.VOLTAGE_FULL = 4.2      # Fully charged voltage
        self.VOLTAGE_NOMINAL = 3.7   # Nominal voltage
        self.VOLTAGE_LOW = 3.5       # Low voltage warning
        self.VOLTAGE_CRITICAL = 3.3  # Critical voltage threshold
        self.VOLTAGE_DEAD = 3.0      # Dead cell voltage
```

## 🌐 GitHub Pages Deployment

1. Enable GitHub Pages in repository settings
2. Select `master` branch as source
3. Your dashboard will be available at: `https://yourusername.github.io/battery_report/`

## 💡 Use Cases

- **Fleet Management**: Monitor health of multiple UAV batteries across operations
- **Maintenance Planning**: Identify batteries requiring attention before failure
- **Performance Analysis**: Compare battery configurations and usage patterns
- **Safety Compliance**: Track critical voltage events and ensure operational safety
- **Lifecycle Tracking**: Estimate remaining useful life and plan replacements

## 🔬 Technical Details

### LiPo Voltage-SoC Curve
The system uses a piecewise linear approximation:
- 4.2V = 100% SoC (fully charged)
- 3.7V = 50% SoC (nominal)
- 3.3V = 0% SoC (critically low)
- Below 3.3V = Potential cell damage

### Cycle Detection Algorithm
Cycles are estimated by detecting significant voltage drops (> 0.5V) indicating discharge events.

### Imbalance Calculation
```
Imbalance (V) = Max(Cell Voltages) - Min(Cell Voltages)
Imbalance (%) = (Imbalance / Average Voltage) × 100
```

## ⚠️ Safety Notes

- **Never use batteries with SoH < 50%** in critical operations
- **Inspect physically** any battery showing CRITICAL_VOLTAGE flags
- **Balance charge** batteries showing HIGH_IMBALANCE flags
- **Retire batteries** with persistent voltage degradation
- LiPo batteries can be dangerous if mishandled - always follow manufacturer guidelines

## 👥 Contributing

Contributions welcome! Areas for improvement:
- Machine learning models for failure prediction
- Integration with real-time monitoring systems
- Mobile app for field technicians
- Database backend for long-term tracking

## 📝 License

MIT License - feel free to use in commercial and research projects.

## 📧 Contact

**TARA UAV Private Limited**  
Developed by Manikanth Nanankala  
For UAV battery monitoring and fleet management solutions

---

## 📸 Screenshots

### Health Overview Dashboard
![Health Overview](https://via.placeholder.com/800x400?text=Battery+Health+Overview)
*Interactive scatter plot showing SoH vs cell imbalance with pack details*

### Status Distribution
![Status Distribution](https://via.placeholder.com/800x400?text=Status+Distribution)
*Fleet health breakdown with pie charts and histograms*

### Time Series Analysis
![Time Series](https://via.placeholder.com/800x400?text=Time+Series+Analysis)
*Voltage and imbalance trends over time for top performing packs*

---

**Last Updated**: December 2025  
**Version**: 2.0  
**Status**: 🟢 Active Development
