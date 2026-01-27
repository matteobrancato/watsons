"""Data processor for Watsons Turkey Automation Dashboard."""
import pandas as pd
from typing import Dict, Optional


class AutomationDataProcessor:
    """Processes automation test data from baseline and plan CSV files."""

    DESKTOP_COL = "Automation Status Testim Desktop"
    MOBILE_COL = "Automation Status Testim Mobile View"
    DEVICE_COL = "Device"
    NA_REASON_COL = "Automation Not Applicable Reason"
    AUTOMATED_STATUSES = {"automated uat", "automated prod"}
    BACKLOG_STATUSES = {"in progress", "ready to be automated"}

    def __init__(self, baseline_path: str, plan_path: str):
        self.baseline_path = baseline_path
        self.plan_path = plan_path
        self._baseline_df: Optional[pd.DataFrame] = None
        self._plan_df: Optional[pd.DataFrame] = None

    def _load_data(self) -> bool:
        """Load CSV files into dataframes."""
        try:
            self._baseline_df = pd.read_csv(self.baseline_path)
            self._plan_df = pd.read_csv(self.plan_path)
            return True
        except Exception:
            return False

    def _normalize_column(self, df: pd.DataFrame, col: str) -> pd.Series:
        """Normalize a column: lowercase, stripped, with NaN as empty string."""
        return df[col].fillna("").str.strip().str.lower()

    def _count_by_device(self, df: pd.DataFrame, desktop_mask: pd.Series,
                         mobile_mask: pd.Series) -> Dict[str, int]:
        """
        Count items with smart deduplication based on device type.

        Returns dict with desktop, mobile, both counts and total.
        """
        device_col = self._normalize_column(df, self.DEVICE_COL) if self.DEVICE_COL in df.columns else pd.Series([""] * len(df))

        desktop_count = mobile_count = both_count = 0

        for i in range(len(df)):
            raw_device = df[self.DEVICE_COL].iloc[i] if self.DEVICE_COL in df.columns else ""
            device = str(raw_device).strip() if pd.notna(raw_device) else ""
            d_match = desktop_mask.iloc[i]
            m_match = mobile_mask.iloc[i]

            if device == "Both":
                if d_match and m_match:
                    both_count += 1
                elif d_match:
                    desktop_count += 1
                elif m_match:
                    mobile_count += 1
            elif device == "Desktop":
                if d_match:
                    desktop_count += 1
            elif device == "Mobile":
                if m_match:
                    mobile_count += 1
            else:
                # Fallback for unknown/empty device
                if d_match and m_match:
                    both_count += 1
                elif d_match:
                    desktop_count += 1
                elif m_match:
                    mobile_count += 1

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "both": both_count,
            "total": desktop_count + mobile_count + both_count
        }

    def _count_by_device_simple(self, df: pd.DataFrame, mask: pd.Series) -> Dict[str, int]:
        """
        Simple pivot-style count by device (no cross-column deduplication).

        Counts rows where mask is True, grouped by Device column.
        This mimics Excel pivot table behavior.
        """
        if self.DEVICE_COL not in df.columns:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": int(mask.sum())}

        desktop_count = mobile_count = both_count = 0

        for i in range(len(df)):
            if not mask.iloc[i]:
                continue

            raw_device = df[self.DEVICE_COL].iloc[i]
            device = str(raw_device).strip() if pd.notna(raw_device) else ""

            if device == "Both":
                both_count += 1
            elif device == "Desktop":
                desktop_count += 1
            elif device == "Mobile":
                mobile_count += 1
            else:
                # Unknown device - count as both for safety
                both_count += 1

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "both": both_count,
            "total": desktop_count + mobile_count + both_count
        }

    def _calculate_automated(self) -> Dict[str, int]:
        """Calculate automated test cases from baseline."""
        if self._baseline_df is None:
            return {"desktop": 0, "mobile": 0, "total": 0}

        desktop_status = self._normalize_column(self._baseline_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._baseline_df, self.MOBILE_COL)

        desktop_count = desktop_status.isin(self.AUTOMATED_STATUSES).sum()
        mobile_count = mobile_status.isin(self.AUTOMATED_STATUSES).sum()

        return {
            "desktop": int(desktop_count),
            "mobile": int(mobile_count),
            "total": int(desktop_count + mobile_count)
        }

    def _calculate_backlog(self) -> Dict[str, int]:
        """Calculate backlog with smart deduplication."""
        if self._plan_df is None:
            return {"desktop": 0, "mobile": 0, "both": 0, "smart_total": 0}

        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)

        desktop_mask = desktop_status.isin(self.BACKLOG_STATUSES)
        mobile_mask = mobile_status.isin(self.BACKLOG_STATUSES)

        result = self._count_by_device(self._plan_df, desktop_mask, mobile_mask)
        return {
            "desktop": result["desktop"],
            "mobile": result["mobile"],
            "both": result["both"],
            "smart_total": result["total"]
        }

    def _calculate_blocked(self) -> int:
        """Calculate blocked test cases from plan."""
        if self._plan_df is None:
            return 0

        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)

        return int(((desktop_status == "blocked") | (mobile_status == "blocked")).sum())

    def _split_plan_by_empty_row(self) -> tuple:
        """Split plan dataframe into Desktop Plan and Mobile Plan by empty row."""
        if self._plan_df is None:
            return None, None

        # Find the empty row (where ID is NaN)
        empty_rows = self._plan_df[self._plan_df['ID'].isna()].index
        if len(empty_rows) == 0:
            return self._plan_df, pd.DataFrame()

        split_idx = empty_rows[0]
        plan_desktop = self._plan_df.iloc[:split_idx].copy()
        plan_mobile = self._plan_df.iloc[split_idx + 1:].copy().reset_index(drop=True)

        return plan_desktop, plan_mobile

    def _calculate_not_applicable_for_df(self, df: pd.DataFrame, status_col: str) -> Dict[str, int]:
        """
        Calculate not applicable for a specific dataframe and status column.

        Uses simple pivot-style counting (no cross-column deduplication).
        """
        if df is None or len(df) == 0:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": 0}

        status = self._normalize_column(df, status_col)
        mask = status == "automation not applicable"

        return self._count_by_device_simple(df, mask)

    def _calculate_not_applicable(self) -> Dict[str, int]:
        """
        Calculate not applicable tests with simple pivot-style counting.

        Uses the detailed calculation and returns the armonic totals for backward compatibility.
        """
        detailed = self._calculate_not_applicable_detailed()
        armonic = detailed["armonic"]

        return {
            "desktop": armonic["desktop"],
            "mobile": armonic["mobile"],
            "both": armonic["both"],
            "total": armonic["total"]
        }

    def _calculate_not_applicable_detailed(self) -> Dict:
        """
        Calculate not applicable with Plan Desktop and Plan Mobile breakdown + armonic sum.

        Uses simple pivot-style counting (like Excel pivot tables).
        Each status column (Desktop/Mobile) is counted separately, grouped by Device.
        """
        plan_desktop, plan_mobile = self._split_plan_by_empty_row()

        # For Plan Desktop section: count by Automation Status Testim Desktop column
        na_plan_desktop = self._calculate_not_applicable_for_df(plan_desktop, self.DESKTOP_COL)
        # For Plan Mobile section: count by Automation Status Testim Mobile View column
        na_plan_mobile = self._calculate_not_applicable_for_df(plan_mobile, self.MOBILE_COL)

        # Armonic sum: take the max of each category between the two plans
        armonic_desktop = max(na_plan_desktop["desktop"], na_plan_mobile["desktop"])
        armonic_mobile = max(na_plan_desktop["mobile"], na_plan_mobile["mobile"])
        armonic_both = max(na_plan_desktop["both"], na_plan_mobile["both"])
        armonic_total = armonic_desktop + armonic_mobile + armonic_both

        return {
            "plan_desktop": na_plan_desktop,
            "plan_mobile": na_plan_mobile,
            "armonic": {
                "desktop": armonic_desktop,
                "mobile": armonic_mobile,
                "both": armonic_both,
                "total": armonic_total
            }
        }

    def _calculate_na_reasons(self) -> Dict[str, int]:
        """Calculate breakdown of Not Applicable reasons."""
        if self._plan_df is None:
            return {}

        # Check if the NA reason column exists (by name, not position)
        if self.NA_REASON_COL not in self._plan_df.columns:
            return {}

        # Filter for NA tests only
        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)
        na_mask = (desktop_status == "automation not applicable") | (mobile_status == "automation not applicable")
        na_tests = self._plan_df[na_mask]

        if len(na_tests) == 0:
            return {}

        # Count reasons - handle multiple reasons separated by newlines
        reasons_count: Dict[str, int] = {}
        for reason_raw in na_tests[self.NA_REASON_COL]:
            if pd.isna(reason_raw) or str(reason_raw).strip() == "":
                reason = "No reason specified"
                reasons_count[reason] = reasons_count.get(reason, 0) + 1
            else:
                # Split by newline and count each reason separately
                reasons = str(reason_raw).strip().split("\n")
                for r in reasons:
                    r = r.strip()
                    if r:
                        reasons_count[r] = reasons_count.get(r, 0) + 1

        # Sort by count descending
        return dict(sorted(reasons_count.items(), key=lambda x: x[1], reverse=True))

    def get_all_metrics(self) -> Optional[Dict]:
        """Calculate all metrics in one call."""
        if not self._load_data():
            return None

        return {
            "automated": self._calculate_automated(),
            "backlog": self._calculate_backlog(),
            "blocked": self._calculate_blocked(),
            "not_applicable": self._calculate_not_applicable(),
            "not_applicable_detailed": self._calculate_not_applicable_detailed(),
            "na_reasons": self._calculate_na_reasons()
        }
