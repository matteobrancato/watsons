"""Watsons Turkey Automation Dashboard - Streamlit application."""

import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

from data_processor import AutomationDataProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Watsons Turkey Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS styles
CUSTOM_CSS = """
<style>
.main { background-color: #ffffff; }
.main-header {
    font-size: 2.8rem; font-weight: 700; color: #1e3a8a;
    text-align: center; margin-bottom: 1rem; padding: 1.5rem 0;
}
[data-testid="stMetricValue"] {
    font-size: 3rem !important; font-weight: 800 !important; color: #1e293b !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1.1rem !important; font-weight: 600 !important; color: #475569 !important;
}
[data-testid="stMetric"] {
    background-color: #ffffff; padding: 1.5rem; border-radius: 12px;
    border: 2px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.breakdown-text {
    font-size: 0.95rem; font-weight: 500; color: #64748b;
    margin-top: 0.75rem; padding: 0.5rem; background-color: #f8fafc;
    border-radius: 6px; text-align: center;
}
.summary-metric {
    background-color: #f8fafc; padding: 1rem; border-radius: 8px;
    border: 1px solid #e2e8f0; margin-bottom: 0.5rem;
}
.stProgress > div > div { background-color: #3b82f6; }
hr { margin: 2rem 0; border-color: #e2e8f0; }
h3 { color: #1e293b; font-weight: 700; }
</style>
"""

# Color palette for charts
CHART_COLORS = [
    "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#6366f1",
    "#ef4444", "#14b8a6", "#f97316", "#84cc16", "#06b6d4", "#a855f7",
]


def load_metrics(baseline_file: Any, plan_file: Any) -> Optional[Dict]:
    """Process uploaded CSV files and return metrics."""
    baseline_path: Optional[str] = None
    plan_path: Optional[str] = None

    try:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(baseline_file.getvalue())
            baseline_path = f.name

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            f.write(plan_file.getvalue())
            plan_path = f.name

        processor = AutomationDataProcessor(baseline_path, plan_path)
        return processor.get_all_metrics()

    except Exception as e:
        logger.error("Error processing files: %s", e)
        return None

    finally:
        for path in (baseline_path, plan_path):
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass


def render_metrics(metrics: Dict) -> None:
    """Render the main metrics cards."""
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")

    with col1:
        auto = metrics["automated"]
        st.metric("✅ Automated", f"{auto['total']:,}", help="Total automated test cases")
        st.markdown(
            f'<div class="breakdown-text">'
            f'<b>D:</b> {auto["desktop"]:,} | <b>M:</b> {auto["mobile"]:,}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col2:
        backlog = metrics["backlog"]
        st.metric("📋 Backlog", f"{backlog['smart_total']:,}", help="Backlog with smart deduplication")
        st.markdown(
            f'<div class="breakdown-text">'
            f'<b>D:</b> {backlog["desktop"]:,} | '
            f'<b>M:</b> {backlog["mobile"]:,} | <b>B:</b> {backlog["both"]:,}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col3:
        in_review = metrics["in_review"]
        st.metric("🔍 In Review", f"{in_review['total']:,}", help="Tests with 'Passed with issue' status")
        st.markdown(
            f'<div class="breakdown-text">'
            f'<b>D:</b> {in_review["desktop"]:,} | <b>M:</b> {in_review["mobile"]:,}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col4:
        st.metric("🚫 Blocked", f"{metrics['blocked']:,}", help="Currently blocked tests")

    with col5:
        na = metrics["not_applicable"]
        armonic = metrics["not_applicable_detailed"]["armonic"]
        st.metric("➖ Not Applicable", f"{na['total']:,}", help="Tests not applicable for automation")
        st.markdown(
            f'<div class="breakdown-text">'
            f'<b>D:</b> {na["desktop"]:,} | '
            f'<b>M:</b> {na["mobile"]:,} | <b>B:</b> {na["both"]:,}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="breakdown-text" style="margin-top: 0.5rem; font-size: 0.85rem;">'
            f'<b>Armonic:</b> {armonic["total"]:,}'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_na_threshold(metrics: Dict) -> None:
    """Render the Not Applicable Threshold section."""
    st.divider()
    st.markdown("### 🎯 Not Applicable Threshold")

    auto_total = metrics["automated"]["total"]
    armonic_na = metrics["not_applicable_detailed"]["armonic"]["total"]
    threshold = 15.0

    total_completed = auto_total + armonic_na
    na_ratio = (armonic_na / total_completed * 100) if total_completed > 0 else 0

    if na_ratio <= threshold:
        status_color, status_text, status_icon = "#22c55e", "Within threshold", "✅"
    elif na_ratio <= threshold * 1.2:
        status_color, status_text, status_icon = "#f59e0b", "Near threshold", "⚠️"
    else:
        status_color, status_text, status_icon = "#ef4444", "Exceeds threshold", "🚨"

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 2px solid #e2e8f0;">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <span style="font-size: 3rem; font-weight: 800; color: {status_color};">{na_ratio:.1f}%</span>
                    <span style="font-size: 1.5rem; color: #64748b;"> / {threshold:.0f}%</span>
                </div>
                <div style="text-align: center; margin-bottom: 1rem;">
                    <span style="font-size: 1.2rem; color: {status_color};">{status_icon} {status_text}</span>
                </div>
                <div style="background-color: #e2e8f0; border-radius: 10px; height: 20px; overflow: hidden; position: relative;">
                    <div style="background-color: {status_color}; height: 100%; width: {min(na_ratio, 100)}%;"></div>
                    <div style="position: absolute; left: {threshold}%; top: 0; bottom: 0; width: 3px; background-color: #1e293b;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">
                    <span>0%</span>
                    <span>Threshold ({threshold:.0f}%)</span>
                    <span>100%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; height: 100%;">
                <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;"><b>Calculation</b></div>
                <div style="font-size: 0.85rem; color: #475569;">
                    <div style="margin-bottom: 0.3rem;">Armonic NA: <b>{armonic_na:,}</b></div>
                    <div style="margin-bottom: 0.3rem;">Automated: <b>{auto_total:,}</b></div>
                    <div style="margin-bottom: 0.3rem;">Total: <b>{total_completed:,}</b></div>
                    <hr style="margin: 0.5rem 0; border-color: #e2e8f0;">
                    <div>Ratio: {armonic_na:,} / {total_completed:,} = <b>{na_ratio:.1f}%</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _build_reasons_bars(reasons: Dict[str, int], total: int) -> str:
    """Build HTML bars for NA reasons."""
    if not reasons or total == 0:
        return '<div style="color: #94a3b8; text-align: center; padding: 1rem;">No data</div>'

    bars = []
    for i, (reason, count) in enumerate(reasons.items()):
        pct = (count / total) * 100
        color = CHART_COLORS[i % len(CHART_COLORS)]
        bar = (
            '<div style="margin-bottom: 0.6rem;">'
            '<div style="display: flex; justify-content: space-between; margin-bottom: 0.2rem;">'
            f'<span style="font-size: 0.85rem; font-weight: 500; color: #1e293b;">{reason}</span>'
            f'<span style="font-size: 0.85rem; font-weight: 600; color: #64748b;">{count} ({pct:.1f}%)</span>'
            '</div>'
            '<div style="background-color: #e2e8f0; border-radius: 4px; height: 10px; overflow: hidden;">'
            f'<div style="background-color: {color}; height: 100%; width: {pct}%;"></div>'
            '</div>'
            '</div>'
        )
        bars.append(bar)
    return ''.join(bars)


def render_na_reasons(metrics: Dict) -> None:
    """Render the Not Applicable Reasons breakdown section for Desktop and Mobile."""
    na_reasons = metrics.get("na_reasons", {})
    desktop_reasons = na_reasons.get("desktop", {})
    mobile_reasons = na_reasons.get("mobile", {})

    if not desktop_reasons and not mobile_reasons:
        return

    st.divider()
    st.markdown("### 📋 Not Applicable Reasons Analysis")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 🖥️ Desktop")
        total_desktop = sum(desktop_reasons.values()) if desktop_reasons else 0
        bars_html = _build_reasons_bars(desktop_reasons, total_desktop)
        html = (
            '<div style="background-color: #f8fafc; padding: 1rem; border-radius: 12px; border: 2px solid #e2e8f0;">'
            f'<div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.8rem;"><b>Total:</b> {total_desktop}</div>'
            f'{bars_html}'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📱 Mobile")
        total_mobile = sum(mobile_reasons.values()) if mobile_reasons else 0
        bars_html = _build_reasons_bars(mobile_reasons, total_mobile)
        html = (
            '<div style="background-color: #f8fafc; padding: 1rem; border-radius: 12px; border: 2px solid #e2e8f0;">'
            f'<div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.8rem;"><b>Total:</b> {total_mobile}</div>'
            f'{bars_html}'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


def render_summary(metrics: Dict) -> None:
    """Render the summary section with coverage breakdown."""
    st.divider()
    st.markdown("### 📈 Summary")

    auto_total = metrics["automated"]["total"]
    backlog_total = metrics["backlog"]["smart_total"]
    in_review_total = metrics["in_review"]["total"]
    blocked_total = metrics["blocked"]
    na_total = metrics["not_applicable"]["total"]
    total = auto_total + backlog_total + in_review_total + blocked_total + na_total

    if total == 0:
        st.warning("No test cases found.")
        return

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("#### Coverage Breakdown")
        st.markdown(f"**Total Test Cases:** {total:,}")

        breakdown_items = [
            ("✅ Automated", auto_total),
            ("📋 Backlog", backlog_total),
            ("🔍 In Review", in_review_total),
            ("🚫 Blocked", blocked_total),
            ("➖ Not Applicable", na_total),
        ]

        for label, value in breakdown_items:
            if value > 0 or label in ("✅ Automated", "📋 Backlog"):
                pct = (value / total) * 100
                st.markdown(f"**{label}:** {pct:.1f}% ({value:,} tests)")
                st.progress(pct / 100)

    with col_right:
        st.markdown("#### Key Metrics")
        applicable = auto_total + backlog_total + in_review_total + blocked_total

        if applicable > 0:
            coverage = (auto_total / applicable) * 100
            st.markdown(
                f"""
                <div class="summary-metric">
                    <div style="font-size: 0.9rem; color: #64748b;">Automation Coverage</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{coverage:.1f}%</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">{auto_total:,} of {applicable:,} applicable tests</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if auto_total > 0:
            ratio = (backlog_total / auto_total) * 100
            st.markdown(
                f"""
                <div class="summary-metric">
                    <div style="font-size: 0.9rem; color: #64748b;">Backlog-to-Automated Ratio</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{ratio:.1f}%</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">{backlog_total:,} backlog vs {auto_total:,} automated</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    """Main application entry point."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">📊 Watsons Turkey Automation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>"
        "Upload your baseline and plan CSV files to visualize automation metrics</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 📁 Baseline File")
        st.caption("[TestRail Baseline Suite](https://elabaswatson.testrail.io/index.php?/suites/view/7544)")
        baseline = st.file_uploader("Upload baseline CSV", type=["csv"], key="baseline", label_visibility="collapsed")
        if baseline:
            st.success(f"✅ {baseline.name} ({baseline.size:,} bytes)")

    with col2:
        st.markdown("#### 📁 Plan File")
        st.caption("[TestRail Plan](https://elabaswatson.testrail.io/index.php?/plans/view/61979)")
        plan = st.file_uploader("Upload plan CSV", type=["csv"], key="plan", label_visibility="collapsed")
        if plan:
            st.success(f"✅ {plan.name} ({plan.size:,} bytes)")

    if baseline and plan:
        st.divider()

        with st.spinner("🔄 Processing data..."):
            metrics = load_metrics(baseline, plan)

        if metrics is None:
            st.error("❌ Error processing files. Please check CSV format and try again.")
            st.stop()

        st.markdown(
            f"<p id='metrics-section' style='text-align: center; color: #64748b;'>"
            f"📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            unsafe_allow_html=True,
        )

        st.divider()
        render_metrics(metrics)
        render_na_threshold(metrics)
        render_na_reasons(metrics)
        render_summary(metrics)

    else:
        st.info("👆 Upload both CSV files to view dashboard")
        with st.expander("ℹ️ Required File Format"):
            st.markdown(
                """
**Baseline CSV** columns: `Automation Status Testim Desktop`, `Automation Status Testim Mobile View`
- Values: "Automated UAT" or "Automated Prod"

**Plan CSV** columns: `Automation Status Testim Desktop`, `Automation Status Testim Mobile View`, `Device`
- Values: "In progress", "Ready to be automated", "Blocked", "Automation not applicable"
- Device: "Desktop", "Mobile", or "Both"
"""
            )


if __name__ == "__main__":
    main()
