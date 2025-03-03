# Monitoring and Logs

First you need to install the monitoring and logs stack. Run the following command:

```bash
chmod +x ./scripts/setup_monitoring.sh
./scripts/setup_monitoring.sh
```

This will install Prometheus, Grafana, and Loki. And it will also
give you the credentials to access the dashboards.

Then forwards the ports to access the dashboards:

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Prometheus

Access the metrics dashboard at `http://localhost:3000/d/flask-api/flask-api-dashboard`.

### Loki

Access the logs dashboard at `http://localhost:3000/d/flask-api-logs/flask-api-logs-dashboard`.

