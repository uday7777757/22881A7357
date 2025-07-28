import os
from flask import request
from datetime import datetime

def log_request(response):
    log_dir = "Logging Middleware"
    log_file = "example_log_output.txt"
    os.makedirs(log_dir, exist_ok=True)  

    log_path = os.path.join(log_dir, log_file)
    with open(log_path, "a") as f:
        log = f"[{datetime.utcnow()}] {request.method} {request.path} {response.status_code} {request.remote_addr}\n"
        f.write(log)

    return response