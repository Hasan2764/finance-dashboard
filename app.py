import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# ---------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------
st.set_page_config(
    page_title="Profit & Loss Dashboard",
    layout="wide"
)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#4DB6FF;'>
    Usman Public School System
    </h1>
    <h3 style='text-align:center;'>
    Profit & Loss Dashboard
    </h3>
    """,
    unsafe_allow_html=True
)

st.divider()

# ---------------------------------------------------
# FILE UPLOADS
# ---------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    income_file = st.file_uploader(
        "Upload Income File",
        type="xlsx"
    )

with c2:
    expense_file = st.file_uploader(
        "Upload Expense File",
        type="xlsx"
    )

# ---------------------------------------------------
# PROCESS FILES
# ---------------------------------------------------
if income_file and expense_file:

    income_df = pd.read_excel(income_file)
    expense_df = pd.read_excel(expense_file)

    required_cols = [
        "Campus",
        "Month",
        "Account",
        "Amount"
    ]

    if (
        not all(col in income_df.columns for col in required_cols)
        or
        not all(col in expense_df.columns for col in required_cols)
    ):
        st.error(
            "Both files must contain "
            "Campus, Month, Account and Amount columns."
        )
        st.stop()

    # ---------------------------------------------------
    # FILTERS
    # ---------------------------------------------------
    f1, f2 = st.columns(2)

    campuses = sorted(
        income_df["Campus"].astype(str).unique()
    )

    months = sorted(
        income_df["Month"].astype(str).unique()
    )

    with f1:
        selected_campus = st.selectbox(
            "Campus",
            campuses
        )

    with f2:
        selected_month = st.selectbox(
            "Month",
            months
        )

    # ---------------------------------------------------
    # APPLY FILTERS
    # ---------------------------------------------------
    income_filtered = income_df[
        (income_df["Campus"].astype(str)
         == selected_campus)
        &
        (income_df["Month"].astype(str)
         == selected_month)
    ]

    expense_filtered = expense_df[
        (expense_df["Campus"].astype(str)
         == selected_campus)
        &
        (expense_df["Month"].astype(str)
         == selected_month)
    ]

    # ---------------------------------------------------
    # KPI CALCULATIONS
    # ---------------------------------------------------
    total_income = (
        income_filtered["Amount"].sum()
    )

    total_expense = (
        expense_filtered["Amount"].sum()
    )

    net_profit = (
        total_income
        -
        total_expense
    )

    st.divider()

    # ---------------------------------------------------
    # KPI CARDS
    # ---------------------------------------------------
    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Total Income",
        f"PKR {total_income:,.0f}"
    )

    k2.metric(
        "Total Expense",
        f"PKR {total_expense:,.0f}"
    )

    k3.metric(
        "Net Profit",
        f"PKR {net_profit:,.0f}"
    )

    st.divider()

    # ---------------------------------------------------
    # CHARTS
    # ---------------------------------------------------
    ch1, ch2 = st.columns(2)

    with ch1:

        pie_df = pd.DataFrame(
            {
                "Type": [
                    "Income",
                    "Expense"
                ],
                "Amount": [
                    total_income,
                    total_expense
                ]
            }
        )

        fig1 = px.pie(
            pie_df,
            names="Type",
            values="Amount",
            hole=0.5,
            title="Income vs Expense"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with ch2:

        expense_chart = (
            expense_filtered
            .groupby("Account")["Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Amount",
                ascending=False
            )
        )

        fig2 = px.bar(
            expense_chart,
            x="Account",
            y="Amount",
            title="Expense by Account"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # ---------------------------------------------------
    # TABLES
    # ---------------------------------------------------
    t1, t2 = st.columns(2)

    with t1:

        st.subheader(
            "Income Accounts"
        )

        income_summary = (
            income_filtered
            .groupby("Account")["Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Amount",
                ascending=False
            )
        )

        st.dataframe(
            income_summary,
            use_container_width=True
        )

    with t2:

        st.subheader(
            "Expense Accounts"
        )

        expense_summary = (
            expense_filtered
            .groupby("Account")["Amount"]
            .sum()
            .reset_index()
            .sort_values(
                "Amount",
                ascending=False
            )
        )

        st.dataframe(
            expense_summary,
            use_container_width=True
        )
# ---------------------------------------------------
    # DOWNLOAD EXCEL REPORT
    # ---------------------------------------------------
    
    excel_buffer = BytesIO()
    
    with pd.ExcelWriter(
            excel_buffer,
            engine="xlsxwriter"
    ) as writer:
    
        summary_df = pd.DataFrame({
            "Particular": [
                "Total Income",
                "Total Expense",
                "Net Profit"
            ],
            "Amount": [
                total_income,
                total_expense,
                net_profit
            ]
        })
    
        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )
    
        income_filtered.to_excel(
            writer,
            sheet_name="Income",
            index=False
        )
    
        expense_filtered.to_excel(
            writer,
            sheet_name="Expense",
            index=False
        )
    
    excel_data = excel_buffer.getvalue()
    
    st.download_button(
    label="📥 Download Excel Report",
    data=excel_data,
    file_name=(
        f"P&L_{selected_campus}_"
        f"{selected_month}.xlsx"
    ),
    # PDF REPORT
pdf_buffer = BytesIO()

doc = SimpleDocTemplate(pdf_buffer)
styles = getSampleStyleSheet()

elements = []

elements.append(
    Paragraph(
        "<b>Usman Public School System</b>",
        styles["Title"]
    )
)

elements.append(
    Paragraph(
        f"Campus: {selected_campus}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Month: {selected_month}",
        styles["Normal"]
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        f"Total Income: {total_income}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Total Expense: {total_expense}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Net Profit: {net_profit}",
        styles["Normal"]
    )
)

doc.build(elements)

pdf_data = pdf_buffer.getvalue()

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_data,
    file_name=(
        f"P&L_{selected_campus}_"
        f"{selected_month}.pdf"
    ),
    mime="application/pdf"
)mime=(
        "application/"
        "vnd.openxmlformats-"
        "officedocument."
        "spreadsheetml.sheet"
    )
)
else:
    st.info(
        "Upload both Income and Expense files."
    )
