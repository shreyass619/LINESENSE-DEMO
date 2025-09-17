# detector.py
import socket
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
PORT = 9999
def popup_alert(alert_message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("⚠️ Line Break Detected", alert_message)
    root.destroy()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", PORT))
print("✅ Detector connected to simulator")
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
            feeders_down = {}
            for r in records:
                if r["alive"] == 0:
                    feeders_down[r["feeder"]] = r["time"]
            if feeders_down:
                feeders_list = [f"{feeder} (at {t})" for feeder, t in feeders_down.items()]
                alert_message = "⚠️ Multiple Feeders Outage:\n" + "\n".join(feeders_list)
                print(alert_message)
                popup_alert(alert_message)

        except json.JSONDecodeError:
            pass
client_socket.close()
