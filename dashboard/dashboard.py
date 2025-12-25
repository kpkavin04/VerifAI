import json
import pandas as pd
import streamlit as st
from pathlib import Path

LOG_FILE = Path("logs/requests.jsonl")

st.set_page_config(
    page_title="VerifAI Dashboard",
    layout="wide"
)

st.title("VerifAI — RAG Monitoring Dashboard")

# Load logs
if not LOG_FILE.exists():
    st.error("No logs found. Run queries first.")
    st.stop()

rows = []
with open(LOG_FILE, "r") as f:
    for line in f:
        rows.append(json.loads(line))

df = pd.json_normalize(rows)

# Derived fields
df["is_refusal"] = df["outcome"].str.startswith("REFUSED")
df["has_error"] = df["outcome"].str.contains("ERROR", na=False)

# High-level metrics
total_requests = len(df)
refusal_rate = df["is_refusal"].mean()
error_rate = df["has_error"].mean()
avg_latency = df["latency_ms.total"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Requests", total_requests)
col2.metric("Refusal Rate", f"{refusal_rate:.2%}")
col3.metric("Error Rate", f"{error_rate:.2%}")
col4.metric("Avg Latency (ms)", f"{avg_latency:.0f}")

st.divider()

# Latency breakdown
st.subheader("Latency Distribution")

latency_df = df[[
    "latency_ms.retrieval",
    "latency_ms.generation",
    "latency_ms.total"
]]

st.bar_chart(latency_df)

# Confidence vs Outcome
st.subheader("Confidence vs Outcome")

confidence_df = df[~df["is_refusal"]][
    ["confidence", "outcome"]
]

if not confidence_df.empty:
    st.scatter_chart(confidence_df, x="confidence", y="confidence")
else:
    st.info("No answered queries yet.")

# Refusal reasons
st.subheader("Refusal Reasons")

refusals = df[df["is_refusal"]]

if not refusals.empty:
    refusal_counts = (
        refusals["generation.refusal_reason"]
        .value_counts()
        .rename_axis("reason")
        .reset_index(name="count")
    )
    st.table(refusal_counts)
else:
    st.info("No refusals logged.")

# Cost tracking
st.subheader("Cost")

st.metric(
    "Total Cost",
    f"${df['cost'].sum():.2f}"
)

# Raw logs for debugging
with st.expander("View Raw Logs"):
    st.dataframe(df)
