import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.title("Timestamp Analysis Tool")

# 1) File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
if not uploaded_file:
    st.stop()

# 2) Read CSV
df = pd.read_csv(uploaded_file)

# 3) Extract timestamps & their row indices
timestamps = df['timestamp'].dropna().reset_index(drop=True)
valid_indices = df.index[df['timestamp'].notna()].tolist()

# 4) Compute abnormal timestamp jumps (diff ≠ 1)
diffs = timestamps.diff().dropna()
mask = diffs != 1
ab_ts = timestamps[mask.index[mask]]
ab_diffs = diffs[mask]
ab_utc = ab_ts.apply(lambda x: datetime.utcfromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))
abnormal_df = pd.DataFrame({
    "timestamp": ab_ts.astype(int),
    "difference": ab_diffs.astype(int),
    "UTC Time": ab_utc
})

# 5) Compute sampling-rate anomalies (sample_count ≠ 25)
samples = []
for i in range(len(valid_indices) - 1):
    cnt = valid_indices[i+1] - valid_indices[i]
    if cnt != 25:
        ts = timestamps.iloc[i]
        samples.append({
            "timestamp": int(ts),
            "sample_count": cnt,
            "UTC Time": datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        })
samples_df = pd.DataFrame(samples)

# 6) Plot timestamp progression
st.subheader("📈 Timestamp Progression Over Time")
fig, ax = plt.subplots()
ax.plot(timestamps, marker='o', linestyle='-')
ax.set_xlabel("Index")
ax.set_ylabel("Timestamp")
st.pyplot(fig)

# 7) Show & download abnormal-timestamp table
st.subheader("⚠️ Abnormal Timestamp Jumps (difference ≠ 1)")
st.dataframe(abnormal_df)

csv1 = abnormal_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Abnormal Timestamps CSV",
    data=csv1,
    file_name="abnormal_timestamps.csv",
    mime="text/csv"
)

# 8) Show & download sampling-rate anomalies
st.subheader("⚠️ Sampling-Rate Anomalies (sample_count ≠ 25)")
st.dataframe(samples_df)

csv2 = samples_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Sampling Anomalies CSV",
    data=csv2,
    file_name="sampling_anomalies.csv",
    mime="text/csv"
)
