import logging
import time

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class HealthCheck:
    def __init__(self):
        self.start_time = time.time()

    def setup_health_routes(self, app):
        """Setup health check endpoints"""
        health_bp = Blueprint("health", __name__)

        @health_bp.route("/health")
        def health():
            """Basic health check for load balancers"""
            return jsonify({"status": "healthy"})

        @health_bp.route("/health/detailed")
        def detailed_health():
            """Detailed health check with system & DB status"""
            health_data = {
                "status": "healthy",
                "uptime": time.time() - self.start_time,
                "version": app.config.get("VERSION", "unknown"),
                "components": {
                    "system": {"status": "healthy"},
                },
            }

            # Check database if available
            try:
                if hasattr(app, "extensions") and "sqlalchemy" in app.extensions:
                    from src.factory import db

                    # Test DB connection with a simple query
                    db.session.execute(text("SELECT 1")).fetchone()
                    health_data["components"]["database"] = {"status": "healthy"}

            except SQLAlchemyError as e:
                logger.error(f"Database health check failed: {str(e)}")
                health_data["status"] = "degraded"
                health_data["components"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                health_data["status"] = "degraded"

            return jsonify(health_data)

        @health_bp.route("/ready")
        def readiness():
            """Readiness check for Kubernetes"""
            # For simplicity, we consider the app ready if DB connection works
            try:
                if hasattr(app, "extensions") and "sqlalchemy" in app.extensions:
                    from src.factory import db

                    db.session.execute(text("SELECT 1")).fetchone()
                return jsonify({"status": "ready"})
            except Exception as e:
                logger.error(f"Readiness check failed: {str(e)}")
                return jsonify({"status": "not ready", "error": str(e)}), 503

        app.register_blueprint(health_bp)
