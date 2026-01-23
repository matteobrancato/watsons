"""
Watsons Turkey Automation Dashboard
Professional Streamlit dashboard for test automation metrics visualization
"""
import streamlit as st
from data_processor import AutomationDataProcessor
import tempfile
import os


st.set_page_config(
    page_title="Watsons Turkey Automation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1.5rem 0;
    }
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .breakdown-text {
        font-size: 0.95rem;
        font-weight: 500;
        color: #64748b;
        margin-top: 0.75rem;
        padding: 0.5rem;
        background-color: #f8fafc;
        border-radius: 6px;
        text-align: center;
    }
    .summary-metric {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .stProgress > div > div {
        background-color: #3b82f6;
    }
    hr {
        margin: 2rem 0;
        border-color: #e2e8f0;
    }
    h3 {
        color: #1e293b;
        font-weight: 700;
    }
    .stCaptionContainer {
        color: #64748b;
    }
    .upload-section {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #cbd5e1;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def load_metrics_from_files(baseline_file, plan_file):
    """Process uploaded CSV files and calculate metrics"""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_baseline:
        tmp_baseline.write(baseline_file.getvalue())
        baseline_path = tmp_baseline.name

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_plan:
        tmp_plan.write(plan_file.getvalue())
        plan_path = tmp_plan.name

    try:
        processor = AutomationDataProcessor(baseline_path=baseline_path, plan_path=plan_path)
        return processor.get_all_metrics()
    finally:
        try:
            os.unlink(baseline_path)
            os.unlink(plan_path)
        except:
            pass


def render_dashboard(metrics):
    """Render dashboard with calculated metrics"""
    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        automated = metrics["automated"]
        st.metric(
            label="✅ AUTOMATED",
            value=f"{automated['total']:,}",
            help="Total automated test cases (UAT + Prod)"
        )
        st.markdown(
            f'<div class="breakdown-text"><strong>Desktop:</strong> {automated["desktop"]:,} | '
            f'<strong>Mobile:</strong> {automated["mobile"]:,}</div>',
            unsafe_allow_html=True
        )

    with col2:
        backlog = metrics["backlog"]
        st.metric(
            label="📋 BACKLOG",
            value=f"{backlog['smart_total']:,}",
            help="In Progress + Ready to be automated (with smart deduplication)"
        )
        st.markdown(
            f'<div class="breakdown-text"><strong>Desktop:</strong> {backlog["desktop"]:,} | '
            f'<strong>Mobile:</strong> {backlog["mobile"]:,} | <strong>Both:</strong> {backlog["both"]:,}</div>',
            unsafe_allow_html=True
        )

    with col3:
        blocked = metrics["blocked"]
        st.metric(
            label="🚫 BLOCKED",
            value=f"{blocked:,}",
            help="Test cases currently blocked"
        )

    with col4:
        not_applicable = metrics["not_applicable"]
        st.metric(
            label="➖ NOT APPLICABLE",
            value=f"{not_applicable['total']:,}",
            help="Tests not applicable for automation (by device)"
        )
        st.markdown(
            f'<div class="breakdown-text"><strong>Desktop:</strong> {not_applicable["desktop"]:,} | '
            f'<strong>Mobile:</strong> {not_applicable["mobile"]:,} | <strong>Both:</strong> {not_applicable["both"]:,}</div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown("### 📈 Summary")
    st.write("")

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("#### Coverage Breakdown")

        automated_total = metrics["automated"]["total"]
        backlog_total = metrics["backlog"]["smart_total"]
        blocked_total = metrics["blocked"]
        na_total = metrics["not_applicable"]["total"]
        total_tests = automated_total + backlog_total + blocked_total + na_total

        if total_tests > 0:
            automated_pct = (automated_total / total_tests) * 100
            backlog_pct = (backlog_total / total_tests) * 100
            blocked_pct = (blocked_total / total_tests) * 100
            na_pct = (na_total / total_tests) * 100

            st.markdown(f"**Total Test Cases:** {total_tests:,}")
            st.write("")
            st.markdown(f"**✅ Automated:** {automated_pct:.1f}% ({automated_total:,} tests)")
            st.progress(automated_pct / 100)
            st.write("")
            st.markdown(f"**📋 Backlog:** {backlog_pct:.1f}% ({backlog_total:,} tests)")
            st.progress(backlog_pct / 100)
            st.write("")

            if blocked_total > 0:
                st.markdown(f"**🚫 Blocked:** {blocked_pct:.1f}% ({blocked_total:,} tests)")
                st.progress(blocked_pct / 100)
                st.write("")

            st.markdown(f"**➖ Not Applicable:** {na_pct:.1f}% ({na_total:,} tests)")
            st.progress(na_pct / 100)

    with col_right:
        st.markdown("#### Key Metrics")
        st.write("")

        applicable_tests = automated_total + backlog_total + blocked_total
        if applicable_tests > 0:
            automation_coverage = (automated_total / applicable_tests) * 100
            st.markdown(f"""
            <div class="summary-metric">
                <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.25rem;">Automation Coverage</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{automation_coverage:.1f}%</div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem;">
                    {automated_total:,} automated out of {applicable_tests:,} applicable tests
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")

        if automated_total > 0:
            backlog_ratio = (backlog_total / automated_total) * 100
            st.markdown(f"""
            <div class="summary-metric">
                <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.25rem;">Backlog-to-Automated Ratio</div>
                <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b;">{backlog_ratio:.1f}%</div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem;">
                    {backlog_total:,} backlog items vs {automated_total:,} automated
                </div>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    st.markdown('<h1 class="main-header">📊 Watsons Turkey Automation Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #64748b; font-size: 0.95rem; margin-bottom: 2rem;'>"
        "Upload your baseline and plan CSV files to visualize automation metrics</p>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 📁 Baseline File")
        baseline_file = st.file_uploader(
            "Upload baseline CSV",
            type=['csv'],
            key='baseline',
            help="CSV file with automated test cases (Desktop/Mobile columns)",
            label_visibility="collapsed"
        )
        if baseline_file:
            st.success(f"✅ {baseline_file.name} ({baseline_file.size:,} bytes)")

    with col2:
        st.markdown("#### 📁 Plan File")
        plan_file = st.file_uploader(
            "Upload plan CSV",
            type=['csv'],
            key='plan',
            help="CSV file with backlog, blocked, and test status",
            label_visibility="collapsed"
        )
        if plan_file:
            st.success(f"✅ {plan_file.name} ({plan_file.size:,} bytes)")

    st.markdown('</div>', unsafe_allow_html=True)

    if baseline_file and plan_file:
        st.divider()
        with st.spinner("🔄 Processing data..."):
            try:
                metrics = load_metrics_from_files(baseline_file, plan_file)
                if metrics is None:
                    st.error("❌ Error processing files. Check CSV format.")
                    st.stop()

                from datetime import datetime
                st.markdown(
                    f"<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>"
                    f"📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                    unsafe_allow_html=True
                )
                st.divider()
                render_dashboard(metrics)
                st.divider()
                st.caption("🔄 Upload new files to refresh | 📊 Smart deduplication applied")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Ensure CSV files have correct format and structure")
    else:
        st.info("👆 Upload both CSV files to view dashboard")
        with st.expander("ℹ️ Required File Format"):
            st.markdown("""
            **Baseline CSV** must contain:
            - `Automation Status Testim Desktop` column
            - `Automation Status Testim Mobile View` column
            - Values: "Automated UAT" or "Automated Prod"

            **Plan CSV** must contain:
            - `Automation Status Testim Desktop` column
            - `Automation Status Testim Mobile View` column
            - `Device` column (Desktop/Mobile/Both)
            - Values: "In progress", "Ready to be automated", "Blocked", "Automation not applicable"

            **Smart features:**
            - ✅ Automated tests calculated from baseline
            - 📋 Smart deduplication for Desktop/Mobile overlap
            - 🚫 Blocked tests counted
            - ➖ Not applicable categorized by device
            """)


if __name__ == "__main__":
    main()
