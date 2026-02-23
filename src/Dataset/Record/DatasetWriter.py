import csv
import os
from dataclasses import asdict

class DatasetWriter:
    def __init__(self, flow_path: str, host_path: str):
        self.flow_path = flow_path
        self.host_path = host_path

        self.flow_file = open(flow_path, "a", newline="", encoding="utf-8")
        self.host_file = open(host_path, "a", newline="", encoding="utf-8")

        self.flow_writer = None
        self.host_writer = None

    # ---------------- FLOW ----------------
    def write_flow(self, feature):
        data = asdict(feature)

        # flatten FlowKey object
        fk = data.pop("flow_key")
        data["src_ip"] = fk.src_ip
        data["dst_ip"] = fk.dst_ip
        data["dst_port"] = fk.dst_port
        data["protocol"] = fk.protocol.name
        data["direction"] = fk.direction.name

        if self.flow_writer is None:
            self.flow_writer = csv.DictWriter(self.flow_file, fieldnames=data.keys())
            if os.stat(self.flow_path).st_size == 0:
                self.flow_writer.writeheader()

        self.flow_writer.writerow(data)
        self.flow_file.flush()

    # ---------------- HOST ----------------
    def write_host(self, feature):
        data = asdict(feature)

        if self.host_writer is None:
            self.host_writer = csv.DictWriter(self.host_file, fieldnames=data.keys())
            if os.stat(self.host_path).st_size == 0:
                self.host_writer.writeheader()

        self.host_writer.writerow(data)
        self.host_file.flush()

    def close(self):
        self.flow_file.close()
        self.host_file.close()
