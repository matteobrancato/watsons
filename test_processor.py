"""Test suite for Watsons Turkey Automation Dashboard."""
import sys
from pathlib import Path
from data_processor import AutomationDataProcessor


def run_tests():
    """Run all tests and return success status."""
    print("=" * 60)
    print("WATSONS TURKEY DASHBOARD - TEST SUITE")
    print("=" * 60)
    print()

    desktop = Path.home() / "Desktop"
    baseline_path = desktop / "baseline.csv"
    plan_path = desktop / "plan.csv"

    # Test 1: Check files exist
    print("Test 1: Checking data files...")
    if not baseline_path.exists():
        print(f"   ❌ FAIL: {baseline_path} not found")
        return False
    print("   ✅ baseline.csv found")

    if not plan_path.exists():
        print(f"   ❌ FAIL: {plan_path} not found")
        return False
    print("   ✅ plan.csv found")
    print()

    # Test 2: Load data
    print("Test 2: Loading data...")
    processor = AutomationDataProcessor(str(baseline_path), str(plan_path))
    metrics = processor.get_all_metrics()

    if metrics is None:
        print("   ❌ FAIL: Could not load data or calculate metrics")
        return False
    print("   ✅ Data loaded and metrics calculated")
    print()

    # Test 3: Verify structure
    print("Test 3: Verifying metric structure...")
    required = ["automated", "backlog", "blocked", "not_applicable"]
    for key in required:
        if key not in metrics:
            print(f"   ❌ FAIL: Missing key '{key}'")
            return False
    print("   ✅ All required metrics present")
    print()

    # Test 4: Verify data types
    print("Test 4: Verifying data types...")
    checks = [
        (metrics["automated"]["total"], "automated.total"),
        (metrics["backlog"]["smart_total"], "backlog.smart_total"),
        (metrics["blocked"], "blocked"),
        (metrics["not_applicable"]["total"], "not_applicable.total"),
    ]
    for value, name in checks:
        if not isinstance(value, int) or value < 0:
            print(f"   ❌ FAIL: {name} invalid (value={value})")
            return False
    print("   ✅ All data types valid")
    print()

    # Test 5: Display results
    print("Test 5: Metrics Summary")
    print("-" * 60)
    auto = metrics["automated"]
    print(f"   Automated:      {auto['total']:>5} (Desktop: {auto['desktop']}, Mobile: {auto['mobile']})")
    backlog = metrics["backlog"]
    print(f"   Backlog:        {backlog['smart_total']:>5} (Desktop: {backlog['desktop']}, Mobile: {backlog['mobile']}, Both: {backlog['both']})")
    print(f"   Blocked:        {metrics['blocked']:>5}")
    na = metrics["not_applicable"]
    print(f"   Not Applicable: {na['total']:>5} (Desktop: {na['desktop']}, Mobile: {na['mobile']}, Both: {na['both']})")
    print("-" * 60)

    total = auto["total"] + backlog["smart_total"] + metrics["blocked"] + na["total"]
    applicable = auto["total"] + backlog["smart_total"] + metrics["blocked"]
    if applicable > 0:
        coverage = (auto["total"] / applicable) * 100
        print(f"   Total: {total} | Coverage: {coverage:.1f}%")
    print()

    print("=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    return True


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
