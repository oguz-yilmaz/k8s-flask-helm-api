from time import time

from flask import Blueprint, Response, request
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "flask_http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP Request Latency",
    ["method", "endpoint"],
)

STRINGS_SAVED = Counter("flask_strings_saved_total", "Number of strings saved")

STRINGS_RETRIEVED = Counter(
    "flask_strings_retrieved_total", "Number of strings retrieved"
)

AUTH_SUCCESS = Counter(
    "flask_auth_success_total",
    "Authentication success count",
    ["type"],
)

AUTH_FAILURE = Counter(
    "flask_auth_failure_total",
    "Authentication failure count",
    ["type"],
)


def setup_metrics(app):
    """Setup Prometheus metrics collection for Flask app"""
    metrics_blueprint = Blueprint("metrics", __name__)

    @metrics_blueprint.route("/metrics")
    def metrics():
        """Endpoint that returns Prometheus metrics"""
        return Response(generate_latest(), mimetype="text/plain")

    app.register_blueprint(metrics_blueprint)

    @app.before_request
    def before_request():
        request.start_time = time()

    @app.after_request
    def after_request(response):
        # Skip metrics endpoint itself to avoid recursion
        if request.path != "/metrics":
            endpoint = request.endpoint or "unknown"

            REQUEST_COUNT.labels(
                method=request.method, endpoint=endpoint, status=response.status_code
            ).inc()

            if hasattr(request, "start_time"):
                REQUEST_LATENCY.labels(
                    method=request.method, endpoint=endpoint
                ).observe(time() - request.start_time)

        return response

    return app
