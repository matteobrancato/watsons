"""
Data processor for Watsons Turkey Automation Dashboard
Handles data extraction and smart deduplication logic
"""
import pandas as pd
from pathlib import Path
from typing import Dict


class AutomationDataProcessor:
    """Processes automation test data from baseline and plan CSV files"""

    def __init__(self, baseline_path: str, plan_path: str):
        """
        Initialize processor with file paths

        Args:
            baseline_path: Path to baseline.csv file
            plan_path: Path to plan.csv file
        """
        self.baseline_path = Path(baseline_path)
        self.plan_path = Path(plan_path)
        self.baseline_df = None
        self.plan_df = None

    def load_data(self) -> bool:
        """
        Load CSV files into dataframes

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.baseline_df = pd.read_csv(self.baseline_path)
            self.plan_df = pd.read_csv(self.plan_path)
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def calculate_automated(self) -> Dict[str, int]:
        """
        Calculate automated test cases from baseline
        Counts tests with status 'Automated UAT' or 'Automated Prod'

        Returns:
            Dict with desktop, mobile, and total counts
        """
        if self.baseline_df is None:
            return {"desktop": 0, "mobile": 0, "total": 0}

        desktop_col = "Automation Status Testim Desktop"
        mobile_col = "Automation Status Testim Mobile View"

        automated_statuses = ["Automated UAT", "Automated Prod"]

        # Count desktop automated (case-insensitive)
        desktop_automated = self.baseline_df[desktop_col].fillna("").str.strip().str.lower().isin(
            [s.lower() for s in automated_statuses]
        ).sum()

        # Count mobile automated (case-insensitive)
        mobile_automated = self.baseline_df[mobile_col].fillna("").str.strip().str.lower().isin(
            [s.lower() for s in automated_statuses]
        ).sum()

        return {
            "desktop": int(desktop_automated),
            "mobile": int(mobile_automated),
            "total": int(desktop_automated + mobile_automated)
        }

    def calculate_backlog_smart(self) -> Dict[str, int]:
        """
        Calculate backlog with smart deduplication
        Counts 'In progress' and 'Ready to be automated' statuses
        Eliminates duplicates where both Desktop and Mobile have the same status

        Returns:
            Dict with counts per device type and smart total
        """
        if self.plan_df is None:
            return {"desktop": 0, "mobile": 0, "both": 0, "smart_total": 0}

        desktop_col = "Automation Status Testim Desktop"
        mobile_col = "Automation Status Testim Mobile View"
        device_col = "Device"

        backlog_statuses = ["In progress", "Ready to be automated"]

        # Normalize statuses (case-insensitive, strip whitespace)
        df = self.plan_df.copy()
        df['desktop_status'] = df[desktop_col].fillna("").str.strip().str.lower()
        df['mobile_status'] = df[mobile_col].fillna("").str.strip().str.lower()
        df['device_type'] = df[device_col].fillna("").str.strip()

        backlog_statuses_lower = [s.lower() for s in backlog_statuses]

        # Check if desktop or mobile has backlog status
        df['desktop_backlog'] = df['desktop_status'].isin(backlog_statuses_lower)
        df['mobile_backlog'] = df['mobile_status'].isin(backlog_statuses_lower)

        # Smart counting logic:
        # - If Device = "Both" and both desktop_backlog and mobile_backlog are True: count as 1 (not 2)
        # - If Device = "Desktop" and desktop_backlog: count desktop
        # - If Device = "Mobile" and mobile_backlog: count mobile
        # - If Device = "Both" and only one is backlog: count that one

        desktop_count = 0
        mobile_count = 0
        both_count = 0

        for _, row in df.iterrows():
            device = row['device_type']
            desktop_back = row['desktop_backlog']
            mobile_back = row['mobile_backlog']

            if device == "Both":
                if desktop_back and mobile_back:
                    # Both have backlog status - count as 1 shared item
                    both_count += 1
                elif desktop_back:
                    desktop_count += 1
                elif mobile_back:
                    mobile_count += 1
            elif device == "Desktop":
                if desktop_back:
                    desktop_count += 1
            elif device == "Mobile":
                if mobile_back:
                    mobile_count += 1
            else:
                # Unknown device type - use fallback logic
                if desktop_back and mobile_back:
                    both_count += 1
                elif desktop_back:
                    desktop_count += 1
                elif mobile_back:
                    mobile_count += 1

        smart_total = desktop_count + mobile_count + both_count

        return {
            "desktop": int(desktop_count),
            "mobile": int(mobile_count),
            "both": int(both_count),
            "smart_total": int(smart_total)
        }

    def calculate_blocked(self) -> int:
        """
        Calculate blocked test cases from plan

        Returns:
            int: Number of blocked tests
        """
        if self.plan_df is None:
            return 0

        desktop_col = "Automation Status Testim Desktop"
        mobile_col = "Automation Status Testim Mobile View"

        # Check both columns for "Blocked" status (case-insensitive)
        df = self.plan_df.copy()
        df['desktop_status'] = df[desktop_col].fillna("").str.strip().str.lower()
        df['mobile_status'] = df[mobile_col].fillna("").str.strip().str.lower()

        # Count rows where either desktop or mobile is blocked
        blocked_count = ((df['desktop_status'] == 'blocked') |
                        (df['mobile_status'] == 'blocked')).sum()

        return int(blocked_count)

    def calculate_not_applicable_smart(self) -> Dict[str, int]:
        """
        Calculate automation not applicable with smart device breakdown
        Uses Device column to categorize properly

        Returns:
            Dict with counts per device type and total
        """
        if self.plan_df is None:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": 0}

        desktop_col = "Automation Status Testim Desktop"
        mobile_col = "Automation Status Testim Mobile View"
        device_col = "Device"

        df = self.plan_df.copy()
        df['desktop_status'] = df[desktop_col].fillna("").str.strip().str.lower()
        df['mobile_status'] = df[mobile_col].fillna("").str.strip().str.lower()
        df['device_type'] = df[device_col].fillna("").str.strip()

        # Check if desktop or mobile has "automation not applicable"
        df['desktop_na'] = df['desktop_status'] == 'automation not applicable'
        df['mobile_na'] = df['mobile_status'] == 'automation not applicable'

        desktop_count = 0
        mobile_count = 0
        both_count = 0

        for _, row in df.iterrows():
            device = row['device_type']
            desktop_na = row['desktop_na']
            mobile_na = row['mobile_na']

            if device == "Both":
                if desktop_na and mobile_na:
                    # Both are N/A - count as shared
                    both_count += 1
                elif desktop_na:
                    desktop_count += 1
                elif mobile_na:
                    mobile_count += 1
            elif device == "Desktop":
                if desktop_na:
                    desktop_count += 1
            elif device == "Mobile":
                if mobile_na:
                    mobile_count += 1
            else:
                # Unknown device - fallback logic
                if desktop_na and mobile_na:
                    both_count += 1
                elif desktop_na:
                    desktop_count += 1
                elif mobile_na:
                    mobile_count += 1

        total = desktop_count + mobile_count + both_count

        return {
            "desktop": int(desktop_count),
            "mobile": int(mobile_count),
            "both": int(both_count),
            "total": int(total)
        }

    def get_all_metrics(self) -> Dict:
        """
        Calculate all metrics in one call

        Returns:
            Dict containing all automation metrics
        """
        if not self.load_data():
            return None

        return {
            "automated": self.calculate_automated(),
            "backlog": self.calculate_backlog_smart(),
            "blocked": self.calculate_blocked(),
            "not_applicable": self.calculate_not_applicable_smart()
        }
