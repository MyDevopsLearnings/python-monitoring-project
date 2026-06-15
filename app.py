from flask import Flask, jsonify, render_template, request
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

import psutil
import socket
import platform
import time
import os
import logging

app = Flask(__name__)

# ---------------------------------------------------
# Logging
# ---------------------------------------------------

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------------------------------------------
# Application Start Time
# ---------------------------------------------------

APP_START_TIME = time.time()

# ---------------------------------------------------
# Prometheus Metrics
# ---------------------------------------------------

cpu_usage = Gauge(
    "system_cpu_usage_percent",
    "Current CPU Usage Percentage"
)

memory_usage = Gauge(
    "system_memory_usage_percent",
    "Current Memory Usage Percentage"
)

disk_usage = Gauge(
    "system_disk_usage_percent",
    "Current Disk Usage Percentage"
)

uptime_metric = Gauge(
    "application_uptime_seconds",
    "Application Uptime"
)

request_counter = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint"]
)

response_time = Histogram(
    "http_response_time_seconds",
    "HTTP Response Time",
    ["endpoint"]
)

# ---------------------------------------------------
# Request Tracking
# ---------------------------------------------------

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):

    request_counter.labels(
        method=request.method,
        endpoint=request.path
    ).inc()

    duration = time.time() - request.start_time

    response_time.labels(
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------------------------------------------
# Home
# ---------------------------------------------------

@app.route("/")
def home():

    return jsonify({
        "application": "Python Monitoring Tool",
        "version": "2.0",
        "status": "Running"
    })

# ---------------------------------------------------
# Health Check
# ---------------------------------------------------

@app.route("/health")
def health():

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    status = "UP"

    if cpu > 90 or memory > 90:
        status = "WARNING"

    logging.info("Health API Called")

    return jsonify({
        "status": status,
        "cpu_percent": cpu,
        "memory_percent": memory
    })

# ---------------------------------------------------
# System Information
# ---------------------------------------------------

@app.route("/system-info")
def system_info():

    return jsonify({
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(),
        "python_version": platform.python_version(),
        "boot_time": psutil.boot_time()
    })

# ---------------------------------------------------
# Resource Usage
# ---------------------------------------------------

@app.route("/resource-usage")
def resource_usage():

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=1),

        "memory_percent": memory.percent,

        "memory_used_gb":
            round(memory.used / (1024 ** 3), 2),

        "memory_total_gb":
            round(memory.total / (1024 ** 3), 2),

        "disk_percent":
            disk.percent,

        "disk_used_gb":
            round(disk.used / (1024 ** 3), 2),

        "disk_total_gb":
            round(disk.total / (1024 ** 3), 2)
    })

# ---------------------------------------------------
# Network Statistics
# ---------------------------------------------------

@app.route("/network-stats")
def network_stats():

    net = psutil.net_io_counters()

    return jsonify({
        "bytes_sent": net.bytes_sent,
        "bytes_received": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_received": net.packets_recv
    })

# ---------------------------------------------------
# Top Processes
# ---------------------------------------------------

@app.route("/process-info")
def process_info():

    processes = []

    for proc in psutil.process_iter(
            ['pid', 'name', 'cpu_percent']):

        try:
            processes.append(proc.info)

        except Exception:
            continue

    top_processes = sorted(
        processes,
        key=lambda p: p['cpu_percent'],
        reverse=True
    )[:10]

    return jsonify(top_processes)

# ---------------------------------------------------
# Uptime
# ---------------------------------------------------

@app.route("/uptime")
def uptime():

    uptime_seconds = time.time() - APP_START_TIME

    return jsonify({
        "uptime_seconds":
            round(uptime_seconds, 2),

        "uptime_minutes":
            round(uptime_seconds / 60, 2),

        "uptime_hours":
            round(uptime_seconds / 3600, 2)
    })

# ---------------------------------------------------
# SLA
# ---------------------------------------------------

@app.route("/sla")
def sla():

    uptime_seconds = time.time() - APP_START_TIME

    return jsonify({
        "uptime_percentage": 99.99,
        "uptime_seconds": round(
            uptime_seconds, 2
        )
    })

# ---------------------------------------------------
# Request Count
# ---------------------------------------------------

@app.route("/request-count")
def request_count():

    total_requests = 0

    for metric in request_counter.collect():

        for sample in metric.samples:

            if sample.name.endswith("_total"):
                total_requests += sample.value

    return jsonify({
        "total_requests": int(total_requests)
    })

# ---------------------------------------------------
# App Statistics
# ---------------------------------------------------

@app.route("/app-stats")
def app_stats():

    return jsonify({
        "environment":
            os.getenv("ENVIRONMENT", "DEV"),

        "hostname":
            socket.gethostname(),

        "uptime_seconds":
            round(
                time.time() - APP_START_TIME,
                2
            )
    })

# ---------------------------------------------------
# Metrics Endpoint
# ---------------------------------------------------

@app.route("/metrics")
def metrics():

    cpu_usage.set(
        psutil.cpu_percent()
    )

    memory_usage.set(
        psutil.virtual_memory().percent
    )

    disk_usage.set(
        psutil.disk_usage("/").percent
    )

    uptime_metric.set(
        time.time() - APP_START_TIME
    )

    return (
        generate_latest(),
        200,
        {
            "Content-Type":
            CONTENT_TYPE_LATEST
        }
    )

# ---------------------------------------------------
# Error Handlers
# ---------------------------------------------------

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error":
            "Resource Not Found"
    }), 404

@app.errorhandler(500)
def server_error(error):

    return jsonify({
        "error":
            "Internal Server Error"
    }), 500

# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
