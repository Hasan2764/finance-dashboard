import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE ----------------
st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.markdown("<h1 style='text-align:center; color:#4DB6FF;'>Usman Public School System</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Profit & Loss Dashboard</h3>", unsafe_allow_html=True)

st.write("---")

# ---------------- UPLOAD ----------------
col1, col2 = st.columns(2)

with col1:
    income_file = st.file_uploader("Upload Income File", type=["xlsx"])

with col2:
    expense_file = st.file_uploader("Upload Expense File", type=["xlsx"])

# ---------------- PROCESS ----------------
if income_file and expense_file:

    income_df = pd.read_excel(income_file)
    expense_df = pd.read_excel(expense_file)

    # Safety check
    required_cols = ["Account", "Amount"]

    if not all(col in income_df.columns for col in required_cols) or not all(col in expense_df.columns for col in required_cols):
        st.error("Both files must have 'Account' and 'Amount' columns")
    else:

        # ---------------- TOTALS ----------------
        total_income = income_df["Amount"].sum()
        total_expense = expense_df["Amount"].sum()
        net_profit = total_income - total_expense

        # ---------------- KPIs ----------------
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Income", f"{total_income:,.0f}")
        c2.metric("Total Expense", f"{total_expense:,.0f}")
        c3.metric("Net Profit", f"{net_profit:,.0f}")

        st.write("---")

        # ---------------- PIE CHART ----------------
        fig1 = px.pie(
            names=["Income", "Expense"],
            values=[total_income, total_expense],
            title="Income vs Expense"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ---------------- ACCOUNT WISE BREAKDOWN ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Income Breakdown (Account Wise)")
            income_chart = income_df.groupby("Account")["Amount"].sum().reset_index()
            fig2 = px.bar(income_chart, x="Account", y="Amount", title="Income by Account")
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(income_chart)

        with col2:
            st.subheader("Expense Breakdown (Account Wise)")
            expense_chart = expense_df.groupby("Account")["Amount"].sum().reset_index()
            fig3 = px.bar(expense_chart, x="Account", y="Amount", title="Expense by Account")
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(expense_chart)

else:
    st.info("Please upload BOTH Income and Expense Excel files")
