"""Watsons Turkey Automation Dashboard - Streamlit application."""
import streamlit as st
import tempfile
import os
from datetime import datetime
from data_processor import AutomationDataProcessor

st.set_page_config(
    page_title="Watsons Turkey Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.main { background-color: #ffffff; }
.main-header {
    font-size: 2.8rem; font-weight: 700; color: #1e3a8a;
    text-align: center; margin-bottom: 1rem; padding: 1.5rem 0;
}
[data-testid="stMetricValue"] { font-size: 3rem !important; font-weight: 800 !important; color: #1e293b !important; }
[data-testid="stMetricLabel"] { font-size: 1.1rem !important; font-weight: 600 !important; color: #475569 !important; }
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
.upload-section {
    background-color: #f8fafc; padding: 2rem; border-radius: 12px;
    border: 2px dashed #cbd5e1; margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


def load_metrics(baseline_file, plan_file):
    """Process uploaded CSV files and return metrics."""
    baseline_path = plan_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(baseline_file.getvalue())
            baseline_path = f.name

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(plan_file.getvalue())
            plan_path = f.name

        processor = AutomationDataProcessor(baseline_path, plan_path)
        return processor.get_all_metrics()
    except Exception:
        return None
    finally:
        for path in (baseline_path, plan_path):
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass


def render_metrics(metrics):
    """Render the main metrics cards."""
    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        auto = metrics["automated"]
        st.metric("✅ AUTOMATED", f"{auto['total']:,}", help="Total automated test cases")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {auto["desktop"]:,} | <b>Mobile:</b> {auto["mobile"]:,}</div>',
            unsafe_allow_html=True
        )

    with col2:
        backlog = metrics["backlog"]
        st.metric("📋 BACKLOG", f"{backlog['smart_total']:,}", help="Backlog with smart deduplication")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {backlog["desktop"]:,} | '
            f'<b>Mobile:</b> {backlog["mobile"]:,} | <b>Both:</b> {backlog["both"]:,}</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.metric("🚫 BLOCKED", f"{metrics['blocked']:,}", help="Currently blocked tests")

    with col4:
        na = metrics["not_applicable"]
        st.metric("➖ NOT APPLICABLE", f"{na['total']:,}", help="Tests not applicable for automation")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {na["desktop"]:,} | '
            f'<b>Mobile:</b> {na["mobile"]:,} | <b>Both:</b> {na["both"]:,}</div>',
            unsafe_allow_html=True
        )


def render_summary(metrics):
    """Render the summary section with coverage breakdown."""
    st.divider()
    st.markdown("### 📈 Summary")

    auto_total = metrics["automated"]["total"]
    backlog_total = metrics["backlog"]["smart_total"]
    blocked_total = metrics["blocked"]
    na_total = metrics["not_applicable"]["total"]
    total = auto_total + backlog_total + blocked_total + na_total

    if total == 0:
        return

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("#### Coverage Breakdown")
        st.markdown(f"**Total Test Cases:** {total:,}")

        for label, value in [
            ("✅ Automated", auto_total),
            ("📋 Backlog", backlog_total),
            ("🚫 Blocked", blocked_total),
            ("➖ Not Applicable", na_total)
        ]:
            if value > 0 or label in ("✅ Automated", "📋 Backlog"):
                pct = (value / total) * 100
                st.markdown(f"**{label}:** {pct:.1f}% ({value:,} tests)")
                st.progress(pct / 100)

    with col_right:
        st.markdown("#### Key Metrics")
        applicable = auto_total + backlog_total + blocked_total

        if applicable > 0:
            coverage = (auto_total / applicable) * 100
            st.markdown(f"""
            <div class="summary-metric">
                <div style="font-size: 0.9rem; color: #64748b;">Automation Coverage</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{coverage:.1f}%</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">{auto_total:,} of {applicable:,} applicable tests</div>
            </div>
            """, unsafe_allow_html=True)

        if auto_total > 0:
            ratio = (backlog_total / auto_total) * 100
            st.markdown(f"""
            <div class="summary-metric">
                <div style="font-size: 0.9rem; color: #64748b;">Backlog-to-Automated Ratio</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{ratio:.1f}%</div>
                <div style="font-size: 0.85rem; color: #94a3b8;">{backlog_total:,} backlog vs {auto_total:,} automated</div>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    st.markdown('<h1 class="main-header">📊 Watsons Turkey Automation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>"
        "Upload your baseline and plan CSV files to visualize automation metrics</p>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 📁 Baseline File")
        baseline = st.file_uploader("Upload baseline CSV", type=['csv'], key='baseline', label_visibility="collapsed")
        if baseline:
            st.success(f"✅ {baseline.name} ({baseline.size:,} bytes)")

    with col2:
        st.markdown("#### 📁 Plan File")
        plan = st.file_uploader("Upload plan CSV", type=['csv'], key='plan', label_visibility="collapsed")
        if plan:
            st.success(f"✅ {plan.name} ({plan.size:,} bytes)")

    st.markdown('</div>', unsafe_allow_html=True)

    if baseline and plan:
        st.divider()
        with st.spinner("🔄 Processing data..."):
            metrics = load_metrics(baseline, plan)
            if metrics is None:
                st.error("❌ Error processing files. Check CSV format.")
                st.stop()

            st.markdown(
                f"<p style='text-align: center; color: #64748b;'>"
                f"📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                unsafe_allow_html=True
            )
            st.divider()
            render_metrics(metrics)
            render_summary(metrics)
            st.divider()
            st.caption("🔄 Upload new files to refresh | 📊 Smart deduplication applied")
    else:
        st.info("👆 Upload both CSV files to view dashboard")
        with st.expander("ℹ️ Required File Format"):
            st.markdown("""
**Baseline CSV** columns: `Automation Status Testim Desktop`, `Automation Status Testim Mobile View`
- Values: "Automated UAT" or "Automated Prod"

**Plan CSV** columns: `Automation Status Testim Desktop`, `Automation Status Testim Mobile View`, `Device`
- Values: "In progress", "Ready to be automated", "Blocked", "Automation not applicable"
- Device: "Desktop", "Mobile", or "Both"
""")


if __name__ == "__main__":
    main()
