import json
import os
from datetime import datetime
from pathlib import Path


class HoneypotLogger:
    def __init__(self, log_dir="/var/log/multi_honeypot", honeypot_type="generic"):
        self.log_dir = Path(log_dir)
        self.honeypot_type = honeypot_type
        self.log_file = self.log_dir / f"{honeypot_type.lower()}.log"

        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, ip_address, port, event_type, event_data):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ip_address": ip_address,
            "port": port,
            "honeypot_type": self.honeypot_type,
            "event_type": event_type,
            "event_data": event_data
        }

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Error writing log: {e}")
