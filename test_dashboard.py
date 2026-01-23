"""
Integration test for dashboard functionality
"""
import sys
from pathlib import Path
from data_processor import AutomationDataProcessor


def test_dashboard_integration():
    """Test that all dashboard components work correctly"""
    print("=" * 70)
    print("WATSONS TURKEY DASHBOARD - INTEGRATION TEST")
    print("=" * 70)
    print()

    # Test 1: Check file paths
    print("Test 1: Checking data file paths...")
    desktop = Path.home() / "Desktop"
    baseline_path = desktop / "baseline.csv"
    plan_path = desktop / "plan.csv"

    if not baseline_path.exists():
        print(f"   ❌ FAIL: {baseline_path} not found")
        return False
    print(f"   ✅ PASS: baseline.csv found")

    if not plan_path.exists():
        print(f"   ❌ FAIL: {plan_path} not found")
        return False
    print(f"   ✅ PASS: plan.csv found")
    print()

    # Test 2: Load data
    print("Test 2: Loading data...")
    processor = AutomationDataProcessor(
        baseline_path=str(baseline_path),
        plan_path=str(plan_path)
    )

    if not processor.load_data():
        print("   ❌ FAIL: Could not load data")
        return False
    print("   ✅ PASS: Data loaded successfully")
    print()

    # Test 3: Calculate all metrics
    print("Test 3: Calculating metrics...")
    try:
        metrics = processor.get_all_metrics()
        if metrics is None:
            print("   ❌ FAIL: Metrics calculation returned None")
            return False
        print("   ✅ PASS: All metrics calculated")
    except Exception as e:
        print(f"   ❌ FAIL: Exception during calculation: {e}")
        return False
    print()

    # Test 4: Verify metric structure
    print("Test 4: Verifying metric structure...")
    required_keys = ["automated", "backlog", "blocked", "not_applicable"]
    for key in required_keys:
        if key not in metrics:
            print(f"   ❌ FAIL: Missing key '{key}' in metrics")
            return False
    print("   ✅ PASS: All required metrics present")
    print()

    # Test 5: Verify data types and ranges
    print("Test 5: Verifying data integrity...")

    # Check automated
    if not isinstance(metrics["automated"]["total"], int):
        print("   ❌ FAIL: automated.total is not an integer")
        return False
    if metrics["automated"]["total"] < 0:
        print("   ❌ FAIL: automated.total is negative")
        return False

    # Check backlog
    if not isinstance(metrics["backlog"]["smart_total"], int):
        print("   ❌ FAIL: backlog.smart_total is not an integer")
        return False
    if metrics["backlog"]["smart_total"] < 0:
        print("   ❌ FAIL: backlog.smart_total is negative")
        return False

    # Check blocked
    if not isinstance(metrics["blocked"], int):
        print("   ❌ FAIL: blocked is not an integer")
        return False
    if metrics["blocked"] < 0:
        print("   ❌ FAIL: blocked is negative")
        return False

    # Check not_applicable
    if not isinstance(metrics["not_applicable"]["total"], int):
        print("   ❌ FAIL: not_applicable.total is not an integer")
        return False
    if metrics["not_applicable"]["total"] < 0:
        print("   ❌ FAIL: not_applicable.total is negative")
        return False

    print("   ✅ PASS: All data types and ranges valid")
    print()

    # Test 6: Display final metrics
    print("Test 6: Final Metrics Summary")
    print("-" * 70)
    print(f"   Automated:      {metrics['automated']['total']:>5} "
          f"(Desktop: {metrics['automated']['desktop']}, "
          f"Mobile: {metrics['automated']['mobile']})")
    print(f"   Backlog:        {metrics['backlog']['smart_total']:>5} "
          f"(Desktop: {metrics['backlog']['desktop']}, "
          f"Mobile: {metrics['backlog']['mobile']}, "
          f"Both: {metrics['backlog']['both']})")
    print(f"   Blocked:        {metrics['blocked']:>5}")
    print(f"   Not Applicable: {metrics['not_applicable']['total']:>5} "
          f"(Desktop: {metrics['not_applicable']['desktop']}, "
          f"Mobile: {metrics['not_applicable']['mobile']}, "
          f"Both: {metrics['not_applicable']['both']})")
    print("-" * 70)
    print()

    # Calculate total and coverage
    total = (metrics['automated']['total'] +
             metrics['backlog']['smart_total'] +
             metrics['blocked'] +
             metrics['not_applicable']['total'])

    applicable = (metrics['automated']['total'] +
                  metrics['backlog']['smart_total'] +
                  metrics['blocked'])

    if applicable > 0:
        coverage = (metrics['automated']['total'] / applicable) * 100
        print(f"   Total Tests:         {total}")
        print(f"   Automation Coverage: {coverage:.1f}%")
        print()

    print("=" * 70)
    print("ALL TESTS PASSED ✅")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_dashboard_integration()
    sys.exit(0 if success else 1)
