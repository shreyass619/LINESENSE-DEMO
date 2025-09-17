# simulator.py
import csv
import random
import time
import socket
import json
from datetime import datetime
NUM_FEEDERS = 10
METERS_PER_FEEDER = 150
PORT = 9999
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", PORT))
server_socket.listen(1)
print("✅ Simulator running... Waiting for connection...")
client_socket, _ = server_socket.accept()
print("✅ Detector/App connected!")
with open("meter_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "feeder", "meter", "alive"])
outages = {}  
while True:
    records = []
    now = datetime.now().strftime("%H:%M:%S")
    for feeder in range(1, NUM_FEEDERS + 1):
        if feeder not in outages and random.random() < 0.01: 
            outage_duration = random.randint(10, 40)
            outages[feeder] = outage_duration
            print(f"⚠️ Outage started in Feeder-{feeder} at {now} for {outage_duration}s")
        if feeder in outages:
            outages[feeder] -= 1
            alive = 0 if outages[feeder] > 0 else 1
            if outages[feeder] <= 0:
                del outages[feeder]
        else:
            alive = 1
        for meter in range(1, METERS_PER_FEEDER + 1):
            record = {
                "time": now,
                "feeder": f"Feeder-{feeder}",
                "meter": f"Meter-{meter}",
                "alive": alive
            }
            records.append(record)
    client_socket.sendall((json.dumps(records) + "\n").encode())
    with open("meter_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        for r in records:
            writer.writerow([r["time"], r["feeder"], r["meter"], r["alive"]])

    time.sleep(1)
