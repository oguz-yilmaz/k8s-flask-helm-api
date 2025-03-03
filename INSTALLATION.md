# Flask String API Installation Guide

### 1. Configure DNS for the Ingress

```bash
echo "127.0.0.1 flask-api.local" | sudo tee -a /etc/hosts
```

### 2. Run the installation script

```bash
chmod +x ./scripts/install.sh
./scripts/install.sh
```

if you want to skip observability stack installation, you can run the following command:

```bash
./scripts/install.sh --skip-monitoring
```

### 3. Verify the installation

Check that all pods are running:

```bash
kubectl get pods -n flask-api
```

### 4. Monitoring and Logs

If you installed the observability stack, you can access the Grafana dashboard
with the following command:

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Prometheus

Access the metrics dashboard at `http://localhost:3000/d/flask-api/flask-api-dashboard`.

### Loki

Access the logs dashboard at `http://localhost:3000/d/flask-api-logs/flask-api-logs-dashboard`.

### 4. Quick test

After the installation is complete, you can test the API with the following commands:

- Get a random string: GET from `http://flask-api.local/api/v1/strings/random`

It should return "No strings found.", you can register a user and save a string
to get a random string.

For detailed usage refer to the [README.md](README.md) file.


### Troubleshooting

If you get `Bind for 0.0.0.0:80 failed: port is already allocated.` error, you may
want to check your existing cluster services and stop them if necessary and try again.
