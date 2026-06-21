import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ---------------------------------------------------
# PDF GENERATOR (FIXED)
# ---------------------------------------------------
def generate_pdf(campus, month, total_income, total_expense, net_profit, income_df, expense_df):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Usman Public School System", styles["Title"]))
    elements.append(Paragraph("Profit & Loss Report", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # Summary Table
    summary_data = [
        ["Particular", "Amount"],
        ["Campus", campus],
        ["Month", month],
        ["Total Income", f"{total_income:,.0f}"],
        ["Total Expense", f"{total_expense:,.0f}"],
        ["Net Profit", f"{net_profit:,.0f}"],
    ]

    table = Table(summary_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Income Table
    elements.append(Paragraph("Income Summary", styles["Heading3"]))
    income_table = [income_df.columns.tolist()] + income_df.values.tolist()
    elements.append(Table(income_table))
    elements.append(Spacer(1, 20))

    # Expense Table
    elements.append(Paragraph("Expense Summary", styles["Heading3"]))
    expense_table = [expense_df.columns.tolist()] + expense_df.values.tolist()
    elements.append(Table(expense_table))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------
st.set_page_config(
    page_title="Profit & Loss Dashboard",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    h1, h2, h3 {
        letter-spacing: 0.5px;
    }

    div[data-testid="metric-container"] {
        background: #0e1628;
        border: 1px solid #1f2a44;
        padding: 15px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown("""
<h1 style='text-align:center; color:#4DB6FF;'>
Usman Public School System
</h1>
<h3 style='text-align:center;'>
Profit & Loss Dashboard
</h3>
""", unsafe_allow_html=True)

st.divider()


# ---------------------------------------------------
# FILE UPLOADS
# ---------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    income_file = st.file_uploader("Upload Income File", type="xlsx")

with c2:
    expense_file = st.file_uploader("Upload Expense File", type="xlsx")


# ---------------------------------------------------
# PROCESS FILES
# ---------------------------------------------------
if income_file and expense_file:

    income_df = pd.read_excel(income_file)
    expense_df = pd.read_excel(expense_file)

    required_cols = ["Campus", "Month", "Account", "Amount"]

    if (
        not all(col in income_df.columns for col in required_cols)
        or
        not all(col in expense_df.columns for col in required_cols)
    ):
        st.error("Both files must contain Campus, Month, Account and Amount columns.")
        st.stop()


    # ---------------------------------------------------
    # FILTERS
    # ---------------------------------------------------
    f1, f2 = st.columns(2)

    campuses = sorted(income_df["Campus"].astype(str).unique())
    months = sorted(income_df["Month"].astype(str).unique())

    with f1:
        selected_campus = st.selectbox("Campus", campuses)

    with f2:
        selected_month = st.selectbox("Month", months)


    # ---------------------------------------------------
    # APPLY FILTERS
    # ---------------------------------------------------
    income_filtered = income_df[
        (income_df["Campus"].astype(str) == selected_campus)
        &
        (income_df["Month"].astype(str) == selected_month)
    ]

    expense_filtered = expense_df[
        (expense_df["Campus"].astype(str) == selected_campus)
        &
        (expense_df["Month"].astype(str) == selected_month)
    ]


    # ---------------------------------------------------
    # KPI CALCULATIONS
    # ---------------------------------------------------
    total_income = income_filtered["Amount"].sum()
    total_expense = expense_filtered["Amount"].sum()
    net_profit = total_income - total_expense


    st.divider()

    k1, k2, k3 = st.columns(3)

    k1.metric("Total Income", f"PKR {total_income:,.0f}")
    k2.metric("Total Expense", f"PKR {total_expense:,.0f}")
    k3.metric("Net Profit", f"PKR {net_profit:,.0f}")


    st.divider()

    # ---------------------------------------------------
    # TABLES (CREATE BEFORE PDF USE)
    # ---------------------------------------------------
    income_summary = (
        income_filtered.groupby("Account")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )

    expense_summary = (
        expense_filtered.groupby("Account")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )


    # ---------------------------------------------------
    # DOWNLOAD PDF REPORT (FIXED)
    # ---------------------------------------------------
    pdf_buffer = generate_pdf(
        selected_campus,
        selected_month,
        total_income,
        total_expense,
        net_profit,
        income_summary,
        expense_summary
    )

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer,
        file_name=f"P&L_{selected_campus}_{selected_month}.pdf",
        mime="application/pdf"
    )


else:
    st.info("Upload both Income and Expense files.")
