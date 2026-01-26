"""Data processor for Watsons Turkey Automation Dashboard."""
import pandas as pd
from typing import Dict, Optional


class AutomationDataProcessor:
    """Processes automation test data from baseline and plan CSV files."""

    DESKTOP_COL = "Automation Status Testim Desktop"
    MOBILE_COL = "Automation Status Testim Mobile View"
    DEVICE_COL = "Device"
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

    def _calculate_not_applicable(self) -> Dict[str, int]:
        """Calculate not applicable tests with smart device breakdown."""
        if self._plan_df is None:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": 0}

        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)

        desktop_mask = desktop_status == "automation not applicable"
        mobile_mask = mobile_status == "automation not applicable"

        return self._count_by_device(self._plan_df, desktop_mask, mobile_mask)

    def get_all_metrics(self) -> Optional[Dict]:
        """Calculate all metrics in one call."""
        if not self._load_data():
            return None

        return {
            "automated": self._calculate_automated(),
            "backlog": self._calculate_backlog(),
            "blocked": self._calculate_blocked(),
            "not_applicable": self._calculate_not_applicable()
        }
