"""Data processor for Watsons Turkey Automation Dashboard.

Version: 2.1 - In Review returns Dict with desktop/mobile/total breakdown.
"""

import logging
import pandas as pd
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AutomationDataProcessor:
    """Processes automation test data from baseline and plan CSV files."""

    DESKTOP_COL = "Automation Status Testim Desktop"
    MOBILE_COL = "Automation Status Testim Mobile View"
    DEVICE_COL = "Device"
    NA_REASON_COL = "Automation Not Applicable Reason"
    ID_COL = "ID"

    STATUS_COL = "Status"

    AUTOMATED_STATUSES = frozenset({"automated uat", "automated prod"})
    BACKLOG_STATUSES = frozenset({"in progress", "ready to be automated"})
    NA_STATUS = "automation not applicable"
    BLOCKED_STATUS = "blocked"
    IN_REVIEW_STATUS = "passed with issue"

    def __init__(self, baseline_path: str, plan_path: str) -> None:
        """Initialize processor with file paths."""
        self._baseline_path = baseline_path
        self._plan_path = plan_path
        self._baseline_df: Optional[pd.DataFrame] = None
        self._plan_df: Optional[pd.DataFrame] = None

    def _load_data(self) -> bool:
        """Load CSV files into dataframes."""
        try:
            self._baseline_df = pd.read_csv(self._baseline_path)
            self._plan_df = pd.read_csv(self._plan_path)
            return True
        except FileNotFoundError as e:
            logger.error("File not found: %s", e.filename)
            return False
        except pd.errors.EmptyDataError:
            logger.error("One or more CSV files are empty")
            return False
        except pd.errors.ParserError as e:
            logger.error("CSV parsing error: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error loading data: %s", e)
            return False

    def _normalize_column(self, df: pd.DataFrame, col: str) -> pd.Series:
        """Normalize column values: lowercase, stripped, NaN as empty string."""
        if col not in df.columns:
            return pd.Series([""] * len(df), index=df.index)
        return df[col].fillna("").astype(str).str.strip().str.lower()

    def _get_device_value(self, df: pd.DataFrame, idx: int) -> str:
        """Safely get device value at index."""
        if self.DEVICE_COL not in df.columns:
            return ""
        raw_value = df[self.DEVICE_COL].iloc[idx]
        return str(raw_value).strip() if pd.notna(raw_value) else ""

    def _count_by_device_smart(
        self, df: pd.DataFrame, desktop_mask: pd.Series, mobile_mask: pd.Series
    ) -> Dict[str, int]:
        """Count with smart deduplication based on device type."""
        desktop_count = mobile_count = both_count = 0

        for i in range(len(df)):
            device = self._get_device_value(df, i)
            d_match = desktop_mask.iloc[i]
            m_match = mobile_mask.iloc[i]

            if device == "Both":
                if d_match and m_match:
                    both_count += 1
                elif d_match:
                    desktop_count += 1
                elif m_match:
                    mobile_count += 1
            elif device == "Desktop" and d_match:
                desktop_count += 1
            elif device == "Mobile" and m_match:
                mobile_count += 1
            elif d_match and m_match:
                both_count += 1
            elif d_match:
                desktop_count += 1
            elif m_match:
                mobile_count += 1

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "both": both_count,
            "total": desktop_count + mobile_count + both_count,
        }

    def _count_by_device_simple(self, df: pd.DataFrame, mask: pd.Series) -> Dict[str, int]:
        """Simple pivot-style count by device (no cross-column deduplication)."""
        if self.DEVICE_COL not in df.columns:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": int(mask.sum())}

        desktop_count = mobile_count = both_count = 0

        for i in range(len(df)):
            if not mask.iloc[i]:
                continue

            device = self._get_device_value(df, i)
            if device == "Both":
                both_count += 1
            elif device == "Desktop":
                desktop_count += 1
            elif device == "Mobile":
                mobile_count += 1
            else:
                both_count += 1

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "both": both_count,
            "total": desktop_count + mobile_count + both_count,
        }

    def _calculate_automated(self) -> Dict[str, int]:
        """Calculate automated test cases from baseline."""
        if self._baseline_df is None:
            return {"desktop": 0, "mobile": 0, "total": 0}

        desktop_status = self._normalize_column(self._baseline_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._baseline_df, self.MOBILE_COL)

        desktop_count = int(desktop_status.isin(self.AUTOMATED_STATUSES).sum())
        mobile_count = int(mobile_status.isin(self.AUTOMATED_STATUSES).sum())

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "total": desktop_count + mobile_count,
        }

    def _calculate_backlog(self) -> Dict[str, int]:
        """Calculate backlog with smart deduplication."""
        if self._plan_df is None:
            return {"desktop": 0, "mobile": 0, "both": 0, "smart_total": 0}

        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)

        desktop_mask = desktop_status.isin(self.BACKLOG_STATUSES)
        mobile_mask = mobile_status.isin(self.BACKLOG_STATUSES)

        result = self._count_by_device_smart(self._plan_df, desktop_mask, mobile_mask)
        return {
            "desktop": result["desktop"],
            "mobile": result["mobile"],
            "both": result["both"],
            "smart_total": result["total"],
        }

    def _calculate_blocked(self) -> int:
        """Calculate blocked test cases from plan."""
        if self._plan_df is None:
            return 0

        desktop_status = self._normalize_column(self._plan_df, self.DESKTOP_COL)
        mobile_status = self._normalize_column(self._plan_df, self.MOBILE_COL)

        blocked_mask = (desktop_status == self.BLOCKED_STATUS) | (mobile_status == self.BLOCKED_STATUS)
        return int(blocked_mask.sum())

    def _calculate_in_review(self) -> Dict[str, int]:
        """Calculate tests in review (Status = 'Passed with issue') from plan."""
        if self._plan_df is None or self.STATUS_COL not in self._plan_df.columns:
            return {"desktop": 0, "mobile": 0, "total": 0}

        plan_desktop, plan_mobile = self._split_plan_by_empty_row()

        desktop_count = 0
        if plan_desktop is not None and len(plan_desktop) > 0 and self.STATUS_COL in plan_desktop.columns:
            status = self._normalize_column(plan_desktop, self.STATUS_COL)
            desktop_count = int((status == self.IN_REVIEW_STATUS).sum())

        mobile_count = 0
        if plan_mobile is not None and len(plan_mobile) > 0 and self.STATUS_COL in plan_mobile.columns:
            status = self._normalize_column(plan_mobile, self.STATUS_COL)
            mobile_count = int((status == self.IN_REVIEW_STATUS).sum())

        return {
            "desktop": desktop_count,
            "mobile": mobile_count,
            "total": max(desktop_count, mobile_count),
        }

    def _split_plan_by_empty_row(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Split plan dataframe into Desktop and Mobile sections by empty row."""
        if self._plan_df is None:
            return None, None

        if self.ID_COL not in self._plan_df.columns:
            return self._plan_df, pd.DataFrame()

        empty_rows = self._plan_df[self._plan_df[self.ID_COL].isna()].index
        if len(empty_rows) == 0:
            return self._plan_df, pd.DataFrame()

        split_idx = empty_rows[0]
        plan_desktop = self._plan_df.iloc[:split_idx].copy()
        plan_mobile = self._plan_df.iloc[split_idx + 1 :].copy().reset_index(drop=True)

        return plan_desktop, plan_mobile

    def _calculate_not_applicable_for_df(
        self, df: Optional[pd.DataFrame], status_col: str
    ) -> Dict[str, int]:
        """Calculate not applicable for a specific dataframe and status column."""
        if df is None or len(df) == 0:
            return {"desktop": 0, "mobile": 0, "both": 0, "total": 0}

        status = self._normalize_column(df, status_col)
        mask = status == self.NA_STATUS
        return self._count_by_device_simple(df, mask)

    def _calculate_not_applicable_detailed(self) -> Dict:
        """Calculate not applicable with Plan Desktop and Plan Mobile breakdown."""
        plan_desktop, plan_mobile = self._split_plan_by_empty_row()

        na_plan_desktop = self._calculate_not_applicable_for_df(plan_desktop, self.DESKTOP_COL)
        na_plan_mobile = self._calculate_not_applicable_for_df(plan_mobile, self.MOBILE_COL)

        armonic = {
            "desktop": max(na_plan_desktop["desktop"], na_plan_mobile["desktop"]),
            "mobile": max(na_plan_desktop["mobile"], na_plan_mobile["mobile"]),
            "both": max(na_plan_desktop["both"], na_plan_mobile["both"]),
        }
        armonic["total"] = armonic["desktop"] + armonic["mobile"] + armonic["both"]

        return {
            "plan_desktop": na_plan_desktop,
            "plan_mobile": na_plan_mobile,
            "armonic": armonic,
        }

    def _calculate_not_applicable(self) -> Dict[str, int]:
        """Calculate not applicable tests (returns armonic totals)."""
        detailed = self._calculate_not_applicable_detailed()
        return detailed["armonic"].copy()

    def _count_reasons_for_df(self, df: Optional[pd.DataFrame], status_col: str) -> Dict[str, int]:
        """Count NA reasons for a specific dataframe."""
        if df is None or len(df) == 0 or self.NA_REASON_COL not in df.columns:
            return {}

        status = self._normalize_column(df, status_col)
        na_mask = status == self.NA_STATUS
        na_tests = df[na_mask]

        if len(na_tests) == 0:
            return {}

        reasons_count: Dict[str, int] = {}
        for reason_raw in na_tests[self.NA_REASON_COL]:
            if pd.isna(reason_raw) or str(reason_raw).strip() == "":
                reasons_count["No reason specified"] = reasons_count.get("No reason specified", 0) + 1
            else:
                for reason in str(reason_raw).strip().split("\n"):
                    reason = reason.strip()
                    if reason:
                        reasons_count[reason] = reasons_count.get(reason, 0) + 1

        return dict(sorted(reasons_count.items(), key=lambda x: x[1], reverse=True))

    def _calculate_na_reasons(self) -> Dict:
        """Calculate breakdown of Not Applicable reasons for Desktop and Mobile."""
        plan_desktop, plan_mobile = self._split_plan_by_empty_row()

        return {
            "desktop": self._count_reasons_for_df(plan_desktop, self.DESKTOP_COL),
            "mobile": self._count_reasons_for_df(plan_mobile, self.MOBILE_COL),
        }

    def get_all_metrics(self) -> Optional[Dict]:
        """Calculate all metrics in one call."""
        if not self._load_data():
            return None

        return {
            "automated": self._calculate_automated(),
            "backlog": self._calculate_backlog(),
            "blocked": self._calculate_blocked(),
            "in_review": self._calculate_in_review(),
            "not_applicable": self._calculate_not_applicable(),
            "not_applicable_detailed": self._calculate_not_applicable_detailed(),
            "na_reasons": self._calculate_na_reasons(),
        }
