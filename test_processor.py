"""
Quick test script to verify data processor logic
"""
from data_processor import AutomationDataProcessor
from pathlib import Path

# Setup paths
desktop = Path.home() / "Desktop"
baseline_path = desktop / "baseline.csv"
plan_path = desktop / "plan.csv"

print("=" * 60)
print("Watsons Turkey Automation Metrics Test")
print("=" * 60)

# Check files exist
if not baseline_path.exists():
    print(f"❌ Error: {baseline_path} not found")
    exit(1)

if not plan_path.exists():
    print(f"❌ Error: {plan_path} not found")
    exit(1)

print(f"✅ Found baseline.csv")
print(f"✅ Found plan.csv")
print()

# Process data
processor = AutomationDataProcessor(
    baseline_path=str(baseline_path),
    plan_path=str(plan_path)
)

print("Loading data...")
if not processor.load_data():
    print("❌ Failed to load data")
    exit(1)

print("✅ Data loaded successfully")
print()

# Calculate metrics
print("=" * 60)
print("METRICS")
print("=" * 60)

automated = processor.calculate_automated()
print("\n✅ AUTOMATED:")
print(f"   Desktop: {automated['desktop']}")
print(f"   Mobile:  {automated['mobile']}")
print(f"   Total:   {automated['total']}")

backlog = processor.calculate_backlog_smart()
print("\n📋 BACKLOG (SMART):")
print(f"   Desktop: {backlog['desktop']}")
print(f"   Mobile:  {backlog['mobile']}")
print(f"   Both:    {backlog['both']}")
print(f"   Total:   {backlog['smart_total']}")

blocked = processor.calculate_blocked()
print(f"\n🚫 BLOCKED: {blocked}")

not_applicable = processor.calculate_not_applicable_smart()
print("\n➖ NOT APPLICABLE:")
print(f"   Desktop: {not_applicable['desktop']}")
print(f"   Mobile:  {not_applicable['mobile']}")
print(f"   Both:    {not_applicable['both']}")
print(f"   Total:   {not_applicable['total']}")

print("\n" + "=" * 60)
print("Test completed successfully! ✅")
print("=" * 60)
