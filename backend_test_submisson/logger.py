from flask import request
from datetime import datetime

def log_request(response):
    with open("Logging Middleware/example_log_output.txt", "a") as f:
        log = f"[{datetime.utcnow()}] {request.method} {request.path} {response.status_code} {request.remote_addr}\n"
        f.write(log)
    return response