#!/bin/bash
# Sets up Prometheus, Grafana, and Loki

set -e

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}Setting up monitoring stack for Flask API...${NC}"

# Create namespace for monitoring
echo -e "\n${BOLD}Setting up monitoring namespace...${NC}"
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Add Helm repositories
echo -e "\n${BOLD}Adding Helm repositories...${NC}"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || echo -e "${YELLOW}prometheus-community repository already exists${NC}"
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || echo -e "${YELLOW}grafana repository already exists${NC}"
helm repo update

# Check if Prometheus is already installed
if helm status prometheus -n monitoring &>/dev/null; then
    echo -e "\n${YELLOW}Prometheus Stack already installed. Skipping installation.${NC}"
else
    # Install Prometheus Stack with Grafana
    echo -e "\n${BOLD}Installing Prometheus Stack (includes Grafana)...${NC}"
    helm install prometheus prometheus-community/kube-prometheus-stack \
      --namespace monitoring \
      --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
      --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
      --wait
fi

# Check if Loki is already installed
if helm status loki -n monitoring &>/dev/null; then
    echo -e "\n${YELLOW}Loki Stack already installed. Skipping installation.${NC}"
else
    # Install Loki Stack for log aggregation (without Grafana as it's already installed)
    echo -e "\n${BOLD}Installing Loki Stack for log aggregation...${NC}"
    helm install loki grafana/loki-stack \
      --namespace monitoring \
      --set grafana.enabled=false \
      --set promtail.enabled=true \
      --set loki.persistence.enabled=true \
      --set loki.persistence.size=10Gi \
      --wait
fi

# Check if ServiceMonitor for Flask API exists
echo -e "\n${BOLD}Checking ServiceMonitor for Flask API...${NC}"
if kubectl get servicemonitor -n monitoring flask-api &>/dev/null; then
    echo -e "${GREEN}ServiceMonitor for Flask API already exists.${NC}"
else
    echo -e "${YELLOW}ServiceMonitor not found. Make sure monitoring.enabled=true and monitoring.serviceMonitor.enabled=true in your Helm values.${NC}"
    echo -e "${YELLOW}If deploying outside of Helm, creating a ServiceMonitor now...${NC}"
    # Only create if not found
    cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: flask-api-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: flask-api
  namespaceSelector:
    matchNames:
      - flask-api
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
EOF
fi

# Configure Loki as a data source in Grafana
echo -e "\n${BOLD}Configuring Loki as a data source in Grafana...${NC}"

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
kubectl rollout status deployment/prometheus-grafana -n monitoring --timeout=120s || {
    echo -e "${YELLOW}Grafana deployment not fully ready, but we'll continue...${NC}"
}

# Get Grafana admin password
GRAFANA_PASSWORD=$(kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

# Check if we successfully got the password
if [ -z "$GRAFANA_PASSWORD" ]; then
    echo -e "${RED}Failed to retrieve Grafana password${NC}"
    GRAFANA_PASSWORD="<check-grafana-secret>"
fi

# Configure the datasource using kubectl exec
echo "Adding Loki data source to Grafana..."
kubectl exec -n monitoring deploy/prometheus-grafana -- curl -s -X POST -H "Content-Type: application/json" \
    -d '{"name":"Loki","type":"loki","url":"http://loki:3100","access":"proxy","basicAuth":false}' \
    -u admin:$GRAFANA_PASSWORD \
    http://localhost:3000/api/datasources &>/dev/null || echo -e "${YELLOW}Failed to add Loki data source automatically. You may need to add it manually.${NC}"

# Check if the Flask API ConfigMap dashboard exists
echo -e "\n${BOLD}Checking for existing Flask API dashboard...${NC}"
if kubectl get configmap -n monitoring -l grafana_dashboard=true,app.kubernetes.io/name=flask-api 2>/dev/null | grep -q flask-api; then
    echo -e "${GREEN}Found existing Flask API dashboard ConfigMap. Grafana should automatically detect it.${NC}"
else
    echo -e "${YELLOW}No existing Flask API dashboard ConfigMap found.${NC}"
    echo -e "${YELLOW}Make sure your Helm deployment has monitoring.enabled=true and monitoring.grafana.dashboards.enabled=true${NC}"
fi

echo -e "\n${GREEN}=============================================================${NC}"
echo -e "${GREEN}Monitoring setup completed!${NC}"
echo -e "${GREEN}=============================================================${NC}"
echo -e "\n${BOLD}To access Grafana:${NC}"
echo -e "  1. Run: ${YELLOW}kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80${NC}"
echo -e "  2. Open: ${YELLOW}http://localhost:3000${NC}"
echo -e "  3. Login with:"
echo -e "     - Username: ${YELLOW}admin${NC}"
echo -e "     - Password: ${YELLOW}$GRAFANA_PASSWORD${NC}"
echo -e "\n${BOLD}Finding your Flask API Dashboard:${NC}"
echo -e "  1. Navigate to Dashboards > Browse"
echo -e "  2. Look for 'Flask API Dashboard' (from your Helm chart configuration)"
echo -e "  3. If not visible, check if ConfigMap with the dashboard exists:"
echo -e "     ${YELLOW}kubectl get configmap -n monitoring -l grafana_dashboard=true${NC}"
echo -e "\n${BOLD}To view Flask API metrics in Grafana:${NC}"
echo -e "  1. Go to Explore (compass icon)"
echo -e "  2. Select Prometheus as the data source"
echo -e "  3. Try queries like: ${YELLOW}flask_http_requests_total${NC}"
echo -e "\n${BOLD}To view Flask API logs in Grafana:${NC}"
echo -e "  1. Go to Explore (compass icon)"
echo -e "  2. Select Loki as the data source"
echo -e "  3. Try queries like: ${YELLOW}{namespace=\"flask-api\"}${NC}"
echo -e "\n${BOLD}Useful Dashboard URLs:${NC}"
echo -e "  - Grafana: ${YELLOW}http://localhost:3000${NC} (after port-forward)"
echo -e "  - Prometheus: ${YELLOW}http://localhost:9090${NC} (after running: kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090)"
echo -e "${GREEN}=============================================================${NC}"

echo -e "\n${GREEN}Setup complete! You can now monitor your Flask API with Prometheus, Grafana, and Loki.${NC}"
