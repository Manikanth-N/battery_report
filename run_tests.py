#!/usr/bin/env python3
"""
=============================================================================
🧪 BATTERY ANALYSIS TEST SUITE
Comprehensive testing of battery health analysis system
=============================================================================
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime

# Import the analyzer
from analyze_battery import BatteryHealthAnalyzer

class TestSuite:
    def __init__(self):
        self.test_results = []
        self.test_dir = 'test_data'
        
    def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "="*80)
        print("🧪 BATTERY ANALYSIS TEST SUITE")
        print("="*80)
        print(f"Starting tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # Test 1: Healthy Batteries
        self.test_healthy_batteries()
        
        # Test 2: Imbalanced Batteries
        self.test_imbalanced_batteries()
        
        # Test 3: Degraded Batteries
        self.test_degraded_batteries()
        
        # Test 4: Critical Batteries
        self.test_critical_batteries()
        
        # Test 5: Mixed Fleet
        self.test_mixed_fleet()
        
        # Generate summary report
        self.generate_report()
        
    def test_healthy_batteries(self):
        """Test Case 1: Healthy batteries with good balance"""
        print("\n" + "-"*80)
        print("🟢 TEST 1: HEALTHY BATTERIES")
        print("-"*80)
        
        test_file = os.path.join(self.test_dir, 'test_healthy_batteries.csv')
        
        try:
            analyzer = BatteryHealthAnalyzer(test_file)
            analyzer.load_and_preprocess() \
                   .calculate_cell_metrics() \
                   .calculate_pack_statistics()
            
            # Validate results
            results = {
                'test_name': 'Healthy Batteries',
                'test_file': test_file,
                'status': 'PASS',
                'total_packs': len(analyzer.pack_stats),
                'avg_soh': analyzer.pack_stats['SoH_Percent'].mean(),
                'min_soh': analyzer.pack_stats['SoH_Percent'].min(),
                'max_soh': analyzer.pack_stats['SoH_Percent'].max(),
                'avg_imbalance': analyzer.pack_stats['Avg_Imbalance'].mean(),
                'critical_events': analyzer.pack_stats['Critical_Voltage_Events'].sum(),
                'observations': []
            }
            
            # Assertions for healthy batteries
            if results['avg_soh'] >= 80:
                results['observations'].append("✅ Average SoH is healthy (>= 80%)")
            else:
                results['observations'].append("❌ Average SoH is below expected for healthy batteries")
                results['status'] = 'FAIL'
            
            if results['avg_imbalance'] < 0.1:
                results['observations'].append("✅ Cell imbalance is within acceptable range (< 0.1V)")
            else:
                results['observations'].append("⚠️ Cell imbalance higher than expected")
            
            if results['critical_events'] == 0:
                results['observations'].append("✅ No critical voltage events detected")
            else:
                results['observations'].append(f"⚠️ {results['critical_events']} critical voltage events found")
            
            self.test_results.append(results)
            self.print_test_results(results)
            
        except Exception as e:
            self.test_results.append({
                'test_name': 'Healthy Batteries',
                'test_file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n❌ ERROR: {str(e)}")
    
    def test_imbalanced_batteries(self):
        """Test Case 2: Batteries with cell imbalance issues"""
        print("\n" + "-"*80)
        print("🟠 TEST 2: IMBALANCED BATTERIES")
        print("-"*80)
        
        test_file = os.path.join(self.test_dir, 'test_imbalanced_batteries.csv')
        
        try:
            analyzer = BatteryHealthAnalyzer(test_file)
            analyzer.load_and_preprocess() \
                   .calculate_cell_metrics() \
                   .calculate_pack_statistics()
            
            results = {
                'test_name': 'Imbalanced Batteries',
                'test_file': test_file,
                'status': 'PASS',
                'total_packs': len(analyzer.pack_stats),
                'avg_soh': analyzer.pack_stats['SoH_Percent'].mean(),
                'avg_imbalance': analyzer.pack_stats['Avg_Imbalance'].mean(),
                'max_imbalance': analyzer.pack_stats['Max_Imbalance'].max(),
                'high_imbalance_packs': len(analyzer.pack_stats[analyzer.pack_stats['Avg_Imbalance'] > 0.1]),
                'observations': []
            }
            
            # Assertions for imbalanced batteries
            if results['avg_imbalance'] > 0.05:
                results['observations'].append(f"✅ System detected elevated imbalance: {results['avg_imbalance']:.3f}V")
            else:
                results['observations'].append("❌ System did not detect expected imbalance")
                results['status'] = 'FAIL'
            
            if results['high_imbalance_packs'] > 0:
                results['observations'].append(f"✅ Correctly flagged {results['high_imbalance_packs']} packs with high imbalance")
            
            if results['avg_soh'] < 85:
                results['observations'].append(f"✅ SoH appropriately reduced due to imbalance: {results['avg_soh']:.1f}%")
            
            self.test_results.append(results)
            self.print_test_results(results)
            
        except Exception as e:
            self.test_results.append({
                'test_name': 'Imbalanced Batteries',
                'test_file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n❌ ERROR: {str(e)}")
    
    def test_degraded_batteries(self):
        """Test Case 3: Batteries with voltage degradation"""
        print("\n" + "-"*80)
        print("🟡 TEST 3: DEGRADED BATTERIES")
        print("-"*80)
        
        test_file = os.path.join(self.test_dir, 'test_degraded_batteries.csv')
        
        try:
            analyzer = BatteryHealthAnalyzer(test_file)
            analyzer.load_and_preprocess() \
                   .calculate_cell_metrics() \
                   .calculate_pack_statistics()
            
            results = {
                'test_name': 'Degraded Batteries',
                'test_file': test_file,
                'status': 'PASS',
                'total_packs': len(analyzer.pack_stats),
                'avg_soh': analyzer.pack_stats['SoH_Percent'].mean(),
                'avg_voltage': analyzer.pack_stats['Avg_Cell_Voltage'].mean(),
                'degraded_packs': len(analyzer.pack_stats[analyzer.pack_stats['Voltage_Degradation'] > 5]),
                'fair_or_poor': len(analyzer.pack_stats[analyzer.pack_stats['SoH_Percent'] < 85]),
                'observations': []
            }
            
            # Assertions for degraded batteries
            if results['avg_voltage'] < 3.9:
                results['observations'].append(f"✅ System detected low average voltage: {results['avg_voltage']:.2f}V")
            else:
                results['observations'].append("❌ Average voltage higher than expected for degraded batteries")
                results['status'] = 'FAIL'
            
            if results['avg_soh'] < 80:
                results['observations'].append(f"✅ SoH appropriately classified as degraded: {results['avg_soh']:.1f}%")
            else:
                results['observations'].append("⚠️ SoH may be overestimated for degraded batteries")
            
            if results['fair_or_poor'] > 0:
                results['observations'].append(f"✅ {results['fair_or_poor']} packs correctly classified as Fair/Poor")
            
            self.test_results.append(results)
            self.print_test_results(results)
            
        except Exception as e:
            self.test_results.append({
                'test_name': 'Degraded Batteries',
                'test_file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n❌ ERROR: {str(e)}")
    
    def test_critical_batteries(self):
        """Test Case 4: Critical batteries with dangerous voltage levels"""
        print("\n" + "-"*80)
        print("🔴 TEST 4: CRITICAL BATTERIES")
        print("-"*80)
        
        test_file = os.path.join(self.test_dir, 'test_critical_batteries.csv')
        
        try:
            analyzer = BatteryHealthAnalyzer(test_file)
            analyzer.load_and_preprocess() \
                   .calculate_cell_metrics() \
                   .calculate_pack_statistics()
            
            results = {
                'test_name': 'Critical Batteries',
                'test_file': test_file,
                'status': 'PASS',
                'total_packs': len(analyzer.pack_stats),
                'avg_soh': analyzer.pack_stats['SoH_Percent'].mean(),
                'min_soh': analyzer.pack_stats['SoH_Percent'].min(),
                'critical_events': analyzer.pack_stats['Critical_Voltage_Events'].sum(),
                'low_voltage_events': analyzer.pack_stats['Low_Voltage_Events'].sum(),
                'poor_status_packs': len(analyzer.pack_stats[analyzer.pack_stats['SoH_Percent'] < 50]),
                'observations': []
            }
            
            # Assertions for critical batteries
            if results['critical_events'] > 0:
                results['observations'].append(f"✅ System detected {results['critical_events']} critical voltage events")
            else:
                results['observations'].append("❌ System failed to detect critical voltage conditions")
                results['status'] = 'FAIL'
            
            if results['avg_soh'] < 60:
                results['observations'].append(f"✅ SoH appropriately low for critical batteries: {results['avg_soh']:.1f}%")
            else:
                results['observations'].append("⚠️ SoH may be overestimated for critical batteries")
            
            if results['poor_status_packs'] > 0:
                results['observations'].append(f"✅ {results['poor_status_packs']} packs correctly flagged as POOR status")
            else:
                results['observations'].append("⚠️ No packs flagged as POOR despite critical conditions")
            
            # Check for risk flags
            critical_flag_count = analyzer.pack_stats['Risk_Flags'].str.contains('CRITICAL_VOLTAGE').sum()
            if critical_flag_count > 0:
                results['observations'].append(f"✅ {critical_flag_count} packs have CRITICAL_VOLTAGE risk flag")
            
            self.test_results.append(results)
            self.print_test_results(results)
            
        except Exception as e:
            self.test_results.append({
                'test_name': 'Critical Batteries',
                'test_file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n❌ ERROR: {str(e)}")
    
    def test_mixed_fleet(self):
        """Test Case 5: Mixed fleet with various battery conditions"""
        print("\n" + "-"*80)
        print("🔄 TEST 5: MIXED FLEET")
        print("-"*80)
        
        test_file = os.path.join(self.test_dir, 'test_mixed_fleet.csv')
        
        try:
            analyzer = BatteryHealthAnalyzer(test_file)
            analyzer.load_and_preprocess() \
                   .calculate_cell_metrics() \
                   .calculate_pack_statistics()
            
            # Count different configurations
            config_counts = analyzer.pack_stats['Config'].value_counts().to_dict()
            
            # Count different health statuses
            status_counts = analyzer.pack_stats['Health_Status'].value_counts().to_dict()
            
            results = {
                'test_name': 'Mixed Fleet',
                'test_file': test_file,
                'status': 'PASS',
                'total_packs': len(analyzer.pack_stats),
                'configurations': config_counts,
                'health_statuses': status_counts,
                'avg_soh': analyzer.pack_stats['SoH_Percent'].mean(),
                'soh_std': analyzer.pack_stats['SoH_Percent'].std(),
                'observations': []
            }
            
            # Assertions for mixed fleet
            if len(config_counts) >= 2:
                results['observations'].append(f"✅ Multiple configurations detected: {list(config_counts.keys())}")
            
            if len(status_counts) >= 2:
                results['observations'].append(f"✅ Various health statuses identified: {list(status_counts.keys())}")
            else:
                results['observations'].append("⚠️ Expected more diversity in health statuses")
            
            if results['soh_std'] > 10:
                results['observations'].append(f"✅ High SoH variance detected in mixed fleet: ±{results['soh_std']:.1f}%")
            
            # Check if system can differentiate between good and bad packs
            excellent_good = len(analyzer.pack_stats[analyzer.pack_stats['SoH_Percent'] >= 70])
            fair_poor = len(analyzer.pack_stats[analyzer.pack_stats['SoH_Percent'] < 70])
            
            if excellent_good > 0 and fair_poor > 0:
                results['observations'].append(f"✅ System differentiates: {excellent_good} healthy, {fair_poor} problematic packs")
            
            self.test_results.append(results)
            self.print_test_results(results)
            
        except Exception as e:
            self.test_results.append({
                'test_name': 'Mixed Fleet',
                'test_file': test_file,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"\n❌ ERROR: {str(e)}")
    
    def print_test_results(self, results):
        """Print formatted test results"""
        print(f"\n📊 Test Results:")
        print(f"   Status: {results['status']}")
        print(f"   Total Packs: {results.get('total_packs', 'N/A')}")
        
        if 'avg_soh' in results:
            print(f"   Average SoH: {results['avg_soh']:.1f}%")
        
        if 'observations' in results:
            print(f"\n   Observations:")
            for obs in results['observations']:
                print(f"   {obs}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n\n" + "="*80)
        print("📊 TEST SUMMARY REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed} 🟢")
        print(f"   Failed: {failed} 🔴")
        print(f"   Errors: {errors} ⚠️")
        print(f"   Success Rate: {(passed/total_tests*100):.1f}%")
        
        print(f"\n📋 Test Case Results:")
        for i, result in enumerate(self.test_results, 1):
            status_emoji = {
                'PASS': '✅',
                'FAIL': '❌',
                'ERROR': '⚠️'
            }.get(result['status'], '❓')
            
            print(f"\n   {i}. {result['test_name']}: {status_emoji} {result['status']}")
            if result['status'] == 'ERROR':
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        # Save detailed report
        report_file = 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed,
                    'failed': failed,
                    'errors': errors,
                    'success_rate': passed/total_tests*100
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        print("\n" + "="*80)
        print("🎉 TEST SUITE COMPLETE")
        print("="*80 + "\n")
        
        # Return exit code
        return 0 if failed == 0 and errors == 0 else 1


def main():
    """Main test execution"""
    suite = TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
