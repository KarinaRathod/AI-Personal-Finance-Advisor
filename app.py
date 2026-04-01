import os
import json
import numpy as np
from dotenv import load_dotenv
import streamlit as st
import matplotlib.pyplot as plt

from crewai import Agent, Task, Crew, LLM

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

# -----------------------------
# LLM SETUP
# -----------------------------
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# -----------------------------
# STORAGE FILE
# -----------------------------
DATA_FILE = "finance_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="AI Finance Advisor PRO", layout="wide")
st.title("💰 AI Personal Finance Advisor PRO")
st.caption("Smart budgeting, saving & investing powered by AI")

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("📥 Enter Financial Details")

income = st.sidebar.number_input("Monthly Income", min_value=0, value=0)

rent = st.sidebar.number_input("Rent", min_value=0, value=0)
food = st.sidebar.number_input("Food", min_value=0, value=0)
transport = st.sidebar.number_input("Transport", min_value=0, value=0)
entertainment = st.sidebar.number_input("Entertainment", min_value=0, value=0)
other = st.sidebar.number_input("Other Expenses", min_value=0, value=0)

savings_goal = st.sidebar.number_input("Savings Goal", min_value=0, value=0)

# -----------------------------
# CALCULATIONS
# -----------------------------
total_expenses = rent + food + transport + entertainment + other
savings = income - total_expenses

# Save safely
data.update({
    "income": income,
    "expenses": total_expenses,
    "savings": savings
})
save_data(data)

# -----------------------------
# SUMMARY METRICS
# -----------------------------
st.subheader("📊 Financial Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Income", f"₹{income}")
col2.metric("Expenses", f"₹{total_expenses}")
col3.metric("Savings", f"₹{savings}")

# -----------------------------
# EXPENSE CHART (FIXED)
# -----------------------------
st.subheader("📉 Expense Breakdown")

labels = ["Rent", "Food", "Transport", "Entertainment", "Other"]
values = [rent, food, transport, entertainment, other]

# Fix NaN
values = [0 if (v is None or np.isnan(v)) else v for v in values]

if sum(values) == 0:
    st.warning("⚠️ Add some expenses to view chart")
else:
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title("Expense Distribution")
    st.pyplot(fig)

# -----------------------------
# AI FINANCIAL ADVISOR
# -----------------------------
st.subheader("🧠 AI Financial Advisor")

if st.button("Get Advice"):

    advisor = Agent(
        role="Financial Advisor",
        goal="Give smart budgeting and investment advice",
        backstory="Expert financial planner",
        llm=llm
    )

    task = Task(
        description=f"""
        Analyze financial situation:

        Income: {income}
        Expenses: {total_expenses}
        Savings: {savings}
        Goal: {savings_goal}

        Provide:
        - Budget improvements
        - Saving strategies
        - Investment ideas
        - Risk level
        """,
        expected_output="Structured financial advice",
        agent=advisor
    )

    crew = Crew(agents=[advisor], tasks=[task])
    result = crew.kickoff()

    st.success("✅ Advice Generated")
    st.write(result.raw)

# -----------------------------
# SAVINGS TRACKER
# -----------------------------
st.subheader("🎯 Savings Goal Tracker")

if savings_goal > 0:
    progress = max(0, min(savings / savings_goal, 1))
    st.progress(progress)
    st.write(f"{int(progress * 100)}% of goal achieved")

# -----------------------------
# ANALYTICS CHART
# -----------------------------
st.subheader("📊 Financial Health")

fig2, ax2 = plt.subplots()

categories = ["Income", "Expenses", "Savings"]
values2 = [income, total_expenses, max(savings, 0)]

ax2.bar(categories, values2)
ax2.set_title("Financial Overview")

st.pyplot(fig2)

# -----------------------------
# DOWNLOAD REPORT
# -----------------------------
st.subheader("📥 Export Data")

st.download_button(
    "Download Report",
    data=json.dumps(data, indent=2),
    file_name="finance_report.json",
    mime="application/json"
)