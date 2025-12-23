# 🧪 Test Data Documentation

This directory contains comprehensive test cases for validating the battery health analysis system.

## Test Files Overview

### 1. test_healthy_batteries.csv
**Purpose**: Validate system behavior with optimal battery conditions

**Characteristics**:
- 3 battery packs (3S, 4S, 6S configurations)
- Full charge voltages (4.2V per cell)
- Minimal cell imbalance (< 0.02V)
- Normal discharge curves
- No critical voltage events

**Expected Results**:
- SoH: 85-100%
- Status: 🟢 EXCELLENT or 🟡 GOOD
- No risk flags
- Low imbalance readings

---

### 2. test_imbalanced_batteries.csv
**Purpose**: Test detection of cell imbalance issues

**Characteristics**:
- 2 battery packs (3S, 4S)
- Significant voltage differences between cells (0.15-0.25V)
- Some cells charging/discharging at different rates
- Overall capacity still reasonable

**Expected Results**:
- SoH: 65-85% (reduced due to imbalance penalty)
- High imbalance flags triggered
- Average imbalance > 0.1V detected
- Status: 🟡 GOOD to 🟠 FAIR

---

### 3. test_degraded_batteries.csv
**Purpose**: Validate detection of voltage degradation and capacity loss

**Characteristics**:
- 2 battery packs (3S, 4S)
- Lower maximum voltages (3.8-3.9V vs 4.2V nominal)
- Reduced voltage range throughout discharge
- Earlier reaching low voltage thresholds
- Some voltage degradation over time

**Expected Results**:
- SoH: 50-75%
- Voltage degradation > 5% detected
- Status: 🟠 FAIR
- Possible LOW_VOLTAGE events
- VOLTAGE_DROP risk flag

---

### 4. test_critical_batteries.csv
**Purpose**: Test identification of dangerous battery conditions

**Characteristics**:
- 3 battery packs (3S, 4S, 6S)
- Critically low voltages (< 3.3V per cell)
- Multiple readings below safe thresholds
- Dangerous discharge levels (down to 2.9V)
- High risk of permanent damage

**Expected Results**:
- SoH: < 50%
- Status: 🔴 POOR
- Multiple critical voltage events flagged
- CRITICAL_VOLTAGE risk flag
- System should recommend immediate retirement

---

### 5. test_mixed_fleet.csv
**Purpose**: Validate system performance with diverse battery conditions

**Characteristics**:
- 6 battery packs with varying conditions:
  - PACK_3S_H01: Healthy 3S battery
  - PACK_3S_D01: Degraded 3S battery
  - PACK_4S_H01: Healthy 4S battery
  - PACK_4S_I01: Imbalanced 4S battery
  - PACK_6S_H01: Healthy 6S battery
  - PACK_6S_C01: Critical 6S battery

**Expected Results**:
- Wide range of SoH values (20-100%)
- Multiple health status categories represented
- System correctly differentiates between configurations
- Fleet average SoH: 60-75%
- Various risk flags across different packs

---

## CSV Format Specification

All test files follow this structure:

```csv
RFID,RTC_Time,Total_Voltage,C1,C2,C3,C4,C5,C6
```

**Column Descriptions**:
- `RFID`: Battery pack identifier (format: `PACK_XS_YYY`)
  - X = number of cells in series (1-6)
  - YYY = unique pack identifier
- `RTC_Time`: Timestamp in format `YYYY-MM-DD HH:MM:SS`
- `Total_Voltage`: Sum of all cell voltages
- `C1-C6`: Individual cell voltages (empty for unused cells)

**Voltage Ranges** (per LiPo cell):
- **4.2V**: Fully charged
- **3.7V**: Nominal voltage (50% SoC)
- **3.5V**: Low voltage warning
- **3.3V**: Critical threshold
- **< 3.0V**: Dangerous/dead cell

---

## Running the Tests

### Using Python Test Suite
```bash
python run_tests.py
```

This will:
1. Analyze all test CSV files
2. Validate expected vs actual results
3. Generate detailed test report (`test_report.json`)
4. Print pass/fail status for each test case

### Using Web Upload Interface
1. Open `upload.html` in browser
2. Drag & drop any test CSV file
3. Observe real-time analysis
4. Verify visualizations and metrics

### Manual Python Analysis
```bash
python analyze_battery.py test_data/test_healthy_batteries.csv
```

---

## Test Validation Criteria

### Test 1: Healthy Batteries
- ✅ Average SoH ≥ 80%
- ✅ Average imbalance < 0.1V
- ✅ Zero critical voltage events
- ✅ All packs classified as EXCELLENT or GOOD

### Test 2: Imbalanced Batteries
- ✅ Average imbalance > 0.05V detected
- ✅ At least one pack flagged with HIGH_IMBALANCE
- ✅ SoH reduced appropriately (< 85%)
- ✅ System penalizes imbalance in health calculation

### Test 3: Degraded Batteries
- ✅ Average cell voltage < 3.9V
- ✅ SoH < 80%
- ✅ Voltage degradation > 5% detected
- ✅ Packs classified as FAIR status

### Test 4: Critical Batteries
- ✅ Critical voltage events detected
- ✅ SoH < 60%
- ✅ At least one pack classified as POOR
- ✅ CRITICAL_VOLTAGE risk flags assigned
- ✅ System recommends retirement

### Test 5: Mixed Fleet
- ✅ Multiple configurations identified (3S, 4S, 6S)
- ✅ Various health statuses represented
- ✅ High SoH standard deviation (> 10%)
- ✅ System differentiates good vs problematic packs

---

## Adding Custom Test Cases

To create your own test data:

1. **Create CSV file** with proper column structure
2. **Include RFID** with configuration (e.g., `PACK_4S_TEST01`)
3. **Add timestamps** in chronological order
4. **Set cell voltages** according to test scenario:
   - Healthy: 3.7-4.2V per cell, < 0.05V imbalance
   - Imbalanced: 0.1-0.3V difference between cells
   - Degraded: 3.5-3.9V max, reduced capacity
   - Critical: < 3.3V, dangerous levels
5. **Include charge/discharge cycles** for realistic data

---

## Test Results Interpretation

**Success Indicators**:
- All assertions pass ✅
- SoH calculations match expected ranges
- Risk flags correctly assigned
- Health status appropriate for conditions

**Warning Signs**:
- SoH overestimated for poor conditions
- Critical events not detected
- Imbalance not penalized properly
- Incorrect status classification

---

## Troubleshooting

**Issue**: Tests fail to run
- **Solution**: Ensure `analyze_battery.py` is in parent directory
- **Solution**: Install dependencies: `pip install pandas numpy plotly`

**Issue**: CSV parsing errors
- **Solution**: Verify CSV format matches specification
- **Solution**: Check for empty cells vs missing data

**Issue**: Unexpected SoH values
- **Solution**: Review voltage thresholds in analyzer
- **Solution**: Check cell voltage ranges in test data

---

## Contributing Test Cases

We welcome additional test scenarios:
- Temperature effects simulation
- High cycle count batteries (> 100 cycles)
- Mixed manufacturer data
- Real-world field data samples
- Edge cases and boundary conditions

Submit test cases via pull request with:
1. CSV file in `test_data/`
2. Expected results documentation
3. Description of test scenario

---

**Last Updated**: December 2025  
**Test Suite Version**: 1.0
