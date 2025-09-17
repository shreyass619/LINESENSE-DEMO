# app.py
import streamlit as st
import pandas as pd
import socket
import json
import threading
import time
import plotly.express as px
import subprocess
st.set_page_config(page_title="LT Line Break Detector", layout="wide")
st.title("⚡ LT Line Break Detector Dashboard")
all_data = pd.DataFrame()
def receive_data():
    global all_data
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 9999))
    buffer = ""
    while True:
        data = client_socket.recv(4096).decode()
        if not data:
            break
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            try:
                records = json.loads(line)
                new_df = pd.DataFrame(records)
                all_data = pd.concat([all_data, new_df], ignore_index=True)
            except json.JSONDecodeError:
                pass
    client_socket.close()
if st.button("▶ Start Simulation"):
    subprocess.Popen(["python", "simulator.py"])
    subprocess.Popen(["python", "detector.py"])
    threading.Thread(target=receive_data, daemon=True).start()
    st.success("Simulation started!")
placeholder = st.empty()
while True:
    if not all_data.empty:
        with placeholder.container():
            st.subheader("📊 Latest Feeder Status")
            latest = all_data.groupby("feeder").tail(1)
            st.dataframe(latest)

            st.subheader("📉 Feeder Status Over Time")
            fig = px.line(
                all_data,
                x="time",
                y="alive",
                color="feeder",
                markers=True,
                title="Feeder Alive/Break Timeline (1 = Alive, 0 = Break)"
            )
            st.plotly_chart(fig, use_container_width=True)

            alerts = []
            for feeder, group in latest.groupby("feeder"):
                if group["alive"].iloc[-1] == 0:
                    alerts.append(f"⚠️ ALERT: Line break in {feeder}")
            if alerts:
                st.error("\n".join(alerts))
    time.sleep(2)
