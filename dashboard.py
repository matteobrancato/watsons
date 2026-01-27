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
        st.metric("✅ Automated", f"{auto['total']:,}", help="Total automated test cases")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {auto["desktop"]:,} | <b>Mobile:</b> {auto["mobile"]:,}</div>',
            unsafe_allow_html=True
        )

    with col2:
        backlog = metrics["backlog"]
        st.metric("📋 Backlog", f"{backlog['smart_total']:,}", help="Backlog with smart deduplication")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {backlog["desktop"]:,} | '
            f'<b>Mobile:</b> {backlog["mobile"]:,} | <b>Both:</b> {backlog["both"]:,}</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.metric("🚫 Blocked", f"{metrics['blocked']:,}", help="Currently blocked tests")

    with col4:
        na = metrics["not_applicable"]
        na_detailed = metrics["not_applicable_detailed"]
        armonic = na_detailed["armonic"]
        st.metric("➖ Automation Not Applicable", f"{na['total']:,}", help="Tests not applicable for automation")
        st.markdown(
            f'<div class="breakdown-text"><b>Desktop:</b> {na["desktop"]:,} | '
            f'<b>Mobile:</b> {na["mobile"]:,} | <b>Both:</b> {na["both"]:,}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="breakdown-text" style="margin-top: 0.5rem; font-size: 0.85rem;">'
            f'<b>Armonic Not Applicable sum:</b> {armonic["total"]:,}<br>'
            f'<span style="font-size: 0.8rem; color: #94a3b8;">'
            f'D: {armonic["desktop"]} | M: {armonic["mobile"]} | B: {armonic["both"]}</span></div>',
            unsafe_allow_html=True
        )


def render_na_threshold(metrics):
    """Render the Not Applicable Threshold section with gauge chart."""
    st.divider()
    st.markdown("### 🎯 Not Applicable Threshold")

    auto_total = metrics["automated"]["total"]
    armonic_na = metrics["not_applicable_detailed"]["armonic"]["total"]
    threshold = 15.0  # 15% threshold

    # Calculate the ratio: NA / (Automated + NA)
    total_completed = auto_total + armonic_na
    if total_completed > 0:
        na_ratio = (armonic_na / total_completed) * 100
    else:
        na_ratio = 0

    # Determine status color
    if na_ratio <= threshold:
        status_color = "#22c55e"  # Green
        status_text = "Within threshold"
        status_icon = "✅"
    elif na_ratio <= threshold * 1.2:  # Up to 20% over threshold (18%)
        status_color = "#f59e0b"  # Amber
        status_text = "Near threshold"
        status_icon = "⚠️"
    else:
        status_color = "#ef4444"  # Red
        status_text = "Exceeds threshold"
        status_icon = "🚨"

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        # Create a simple gauge-like visualization using progress bars
        st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 2px solid #e2e8f0;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 3rem; font-weight: 800; color: {status_color};">{na_ratio:.1f}%</span>
                <span style="font-size: 1.5rem; color: #64748b;"> / {threshold:.0f}%</span>
            </div>
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 1.2rem; color: {status_color};">{status_icon} {status_text}</span>
            </div>
            <div style="background-color: #e2e8f0; border-radius: 10px; height: 20px; overflow: hidden; position: relative;">
                <div style="background-color: {status_color}; height: 100%; width: {min(na_ratio, 100)}%; transition: width 0.3s;"></div>
                <div style="position: absolute; left: {threshold}%; top: 0; bottom: 0; width: 3px; background-color: #1e293b;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.8rem; color: #94a3b8;">
                <span>0%</span>
                <span style="position: relative; left: {threshold - 50}%;">Threshold ({threshold:.0f}%)</span>
                <span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
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
        """, unsafe_allow_html=True)


def render_na_reasons(metrics):
    """Render the Not Applicable Reasons breakdown section."""
    na_reasons = metrics.get("na_reasons", {})

    if not na_reasons:
        return

    st.divider()
    st.markdown("### 📋 Not Applicable Reasons Analysis")

    total_reasons = sum(na_reasons.values())

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        # Bar chart visualization - build HTML as single block
        colors = ["#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#6366f1", "#ef4444", "#14b8a6", "#f97316", "#84cc16", "#06b6d4", "#a855f7"]

        bars_html = ""
        for i, (reason, count) in enumerate(na_reasons.items()):
            pct = (count / total_reasons) * 100
            color = colors[i % len(colors)]
            bars_html += f"""
            <div style="margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-size: 0.9rem; font-weight: 500; color: #1e293b;">{reason}</span>
                    <span style="font-size: 0.9rem; font-weight: 600; color: #64748b;">{count} ({pct:.1f}%)</span>
                </div>
                <div style="background-color: #e2e8f0; border-radius: 6px; height: 12px; overflow: hidden;">
                    <div style="background-color: {color}; height: 100%; width: {pct}%; transition: width 0.3s;"></div>
                </div>
            </div>
            """

        st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 2px solid #e2e8f0;">
            {bars_html}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Summary stats
        st.markdown(f"""
        <div style="background-color: #f8fafc; padding: 1.5rem; border-radius: 12px; border: 2px solid #e2e8f0; height: 100%;">
            <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem;">Summary</div>
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; color: #64748b;">Total Reasons Recorded</div>
                <div style="font-size: 2rem; font-weight: 800; color: #1e293b;">{total_reasons}</div>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; color: #64748b;">Unique Reasons</div>
                <div style="font-size: 2rem; font-weight: 800; color: #1e293b;">{len(na_reasons)}</div>
            </div>
            <hr style="border-color: #e2e8f0; margin: 1rem 0;">
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;"><b>Top 3 Reasons</b></div>
        """, unsafe_allow_html=True)

        top_3 = list(na_reasons.items())[:3]
        for i, (reason, count) in enumerate(top_3):
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.3rem;">
                {medal} {reason}: <b>{count}</b>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


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
            render_na_threshold(metrics)
            render_na_reasons(metrics)
            render_summary(metrics)
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
