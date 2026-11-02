import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="HIL Failure Intelligence Platform",
    page_icon="🚗",
    layout="wide"
)

# ==================================================
# STYLING
# ==================================================

st.markdown("""
<style>

.main {
    background-color:#0f172a;
}

.metric-container{
    padding:15px;
    border-radius:15px;
    text-align:center;
    color:white;
}

.pass-card{
    background:#16a34a;
}

.fail-card{
    background:#dc2626;
}

.report-card{
    background:#2563eb;
}

.hil-card{
    background:#9333ea;
}

.passrate-card{
    background:#0891b2;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect("hil_intelligence.db")

df = pd.read_sql(
    "SELECT * FROM report_summary",
    conn
)

# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.title("🔍 Filters")

selected_hil = st.sidebar.multiselect(
    "HIL",
    sorted(df["hil_name"].unique()),
    default=sorted(df["hil_name"].unique())
)

selected_test = st.sidebar.multiselect(
    "Test Script",
    sorted(df["test_script"].unique()),
    default=sorted(df["test_script"].unique())
)

pass_filter = st.sidebar.slider(
    "Pass Rate %",
    0,
    100,
    (0, 100)
)

df = df[
    (df["hil_name"].isin(selected_hil)) &
    (df["test_script"].isin(selected_test)) &
    (df["pass_rate"] >= pass_filter[0]) &
    (df["pass_rate"] <= pass_filter[1])
]

# ==================================================
# KPIS
# ==================================================

total_reports = len(df)

total_tests = int(df["total_tests"].sum())

total_pass = int(df["passed"].sum())

total_fail = int(df["failed"].sum())

total_na = int(df["na_count"].sum())

overall_passrate = round(
    (total_pass / total_tests) * 100,
    2
) if total_tests > 0 else 0

total_hils = df["hil_name"].nunique()

# ==================================================
# HEADER
# ==================================================

st.title("🚗 HIL Failure Intelligence Platform")

st.write(
    "Automotive Validation Analytics Dashboard"
)

st.markdown("---")

# ==================================================
# KPI ROW
# ==================================================

c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.metric("📄 Reports", total_reports)

with c2:
    st.metric("🧪 Total Tests", total_tests)

with c3:
    st.metric("✅ Passed", total_pass)

with c4:
    st.metric("❌ Failed", total_fail)

with c5:
    st.metric("📊 Pass Rate", f"{overall_passrate}%")

with c6:
    st.metric("🏭 HILs", total_hils)

st.markdown("---")

# ==================================================
# EXECUTIVE INSIGHTS
# ==================================================

if len(df):

    best = df.sort_values(
        "pass_rate",
        ascending=False
    ).iloc[0]

    worst = df.sort_values(
        "pass_rate"
    ).iloc[0]

    st.info(
        f"""
        🏆 Best Performing Test: {best['test_script']} ({best['pass_rate']}%)

        ⚠️ Worst Performing Test: {worst['test_script']} ({worst['pass_rate']}%)

        📊 Overall Quality Health: {overall_passrate}%
        """
    )

# ==================================================
# CHARTS ROW 1
# ==================================================

col1,col2 = st.columns(2)

with col1:

    pass_fail_df = pd.DataFrame({
        "Result":["Passed","Failed","NA"],
        "Count":[total_pass,total_fail,total_na]
    })

    fig = px.pie(
        pass_fail_df,
        names="Result",
        values="Count",
        hole=0.55,
        color="Result",
        color_discrete_map={
            "Passed":"green",
            "Failed":"red",
            "NA":"orange"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_passrate,
        title={"text":"Overall Quality Health"},
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":"green"},
            "steps":[
                {"range":[0,60],"color":"red"},
                {"range":[60,85],"color":"orange"},
                {"range":[85,100],"color":"green"}
            ]
        }
    ))

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# CHARTS ROW 2
# ==================================================

left,right = st.columns(2)

with left:

    fig = px.bar(
        df.sort_values("pass_rate"),
        x="test_script",
        y="pass_rate",
        color="pass_rate",
        title="Pass Rate By Test Script"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    hil_df = (
        df.groupby("hil_name")[["passed","failed"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        hil_df,
        x="hil_name",
        y=["passed","failed"],
        barmode="group",
        title="HIL Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# BEST / WORST TESTS
# ==================================================

c1,c2 = st.columns(2)

with c1:

    st.subheader("🏆 Best Performing Tests")

    st.dataframe(
        df.sort_values(
            "pass_rate",
            ascending=False
        )[
            [
                "test_script",
                "hil_name",
                "pass_rate",
                "passed",
                "failed"
            ]
        ].head(10),
        use_container_width=True
    )

with c2:

    st.subheader("⚠️ Worst Performing Tests")

    st.dataframe(
        df.sort_values(
            "pass_rate"
        )[
            [
                "test_script",
                "hil_name",
                "pass_rate",
                "passed",
                "failed"
            ]
        ].head(10),
        use_container_width=True
    )

# ==================================================
# REPORT EXPLORER
# ==================================================

st.subheader("🔎 Report Explorer")

selected_report = st.selectbox(
    "Select Report",
    sorted(df["report_name"].unique())
)

st.dataframe(
    df[
        df["report_name"] == selected_report
    ],
    use_container_width=True
)