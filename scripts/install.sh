#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

CLUSTER_NAME="test---flask-api-cluster"
SETUP_MONITORING=true
LOCAL_MODE=true

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --skip-monitoring) SETUP_MONITORING=false ;;
        --help) 
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-monitoring  Skip setting up monitoring stack"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done


command_exists() {
    command -v "$1" >/dev/null 2>&1
}

progress() {
    echo -e "\n${BLUE}==>${NC} ${BOLD}$1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

progress "Starting Flask API complete setup"
echo -e "Cluster name: ${YELLOW}${CLUSTER_NAME}${NC}"
echo -e "Setup monitoring: ${YELLOW}${SETUP_MONITORING}${NC}"

progress "Checking for required tools"
for cmd in kind kubectl helm docker; do
    if ! command_exists $cmd; then
        error "$cmd is not installed. Please install it and try again."
    fi
    success "$cmd is installed"
done

progress "Creating Kind cluster configuration"
cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${CLUSTER_NAME}
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

progress "Checking if cluster already exists"
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${YELLOW}Cluster '${CLUSTER_NAME}' already exists.${NC}"
    read -p "Delete existing cluster and continue? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        progress "Deleting existing cluster"
        kind delete cluster --name "${CLUSTER_NAME}" || error "Failed to delete existing cluster"
    else
        error "Setup aborted. Please delete the cluster manually or use a different cluster name."
    fi
fi

progress "Creating Kind cluster"
kind create cluster --config=kind-config.yaml || error "Failed to create Kind cluster"

progress "Waiting for cluster to be ready"
kubectl cluster-info || error "Failed to connect to cluster"

progress "Installing NGINX Ingress Controller"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml || error "Failed to install NGINX Ingress Controller"

echo "Waiting for resources to be created..."
sleep 10

progress "Waiting for NGINX Ingress Controller to be ready"
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=180s || error "Timed out waiting for NGINX Ingress Controller"

progress "Creating flask-api namespace"
kubectl create namespace flask-api || error "Failed to create flask-api namespace"

progress "Setting up secrets"

JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)
MYSQL_ROOT_PASSWORD="mysecretpassword"
MYSQL_DATABASE="strings_db"

if [ "$LOCAL_MODE" = true ]; then
    echo -e "${YELLOW}Using local mode - creating regular Kubernetes secrets${NC}"
    
    # Create MySQL secret
    kubectl create secret generic mysql-credentials \
      -n flask-api \
      --from-literal=mysql-root-password=$MYSQL_ROOT_PASSWORD \
      --from-literal=mysql-password=$MYSQL_ROOT_PASSWORD \
      --from-literal=mysql-database=$MYSQL_DATABASE || error "Failed to create MySQL secrets"
    
    # Create JWT secrets
    kubectl create secret generic jwt-secrets \
      -n flask-api \
      --from-literal=jwt-secret-key=$JWT_SECRET \
      --from-literal=jwt-refresh-secret-key=$JWT_REFRESH_SECRET || error "Failed to create JWT secrets"
      
    success "Created regular Kubernetes secrets for local development"
fi

if [ "$SETUP_MONITORING" = true ]; then
    progress "Creating monitoring namespace"
    kubectl create namespace monitoring || echo "Namespace monitoring already exists"
fi

progress "Building Docker image"
docker build -t flask-api:latest . || error "Failed to build Docker image"

progress "Loading image into Kind cluster"
kind load docker-image flask-api:latest --name $CLUSTER_NAME || error "Failed to load image into Kind cluster"

progress "Installing Flask API using Helm"
helm install flask-api ./flask-api-chart -n flask-api || error "Failed to install Flask API"

progress "Waiting for Flask API deployment to be ready"
kubectl wait --for=condition=available --timeout=300s deployment/flask-api -n flask-api || echo -e "${YELLOW}Warning: Timed out waiting for Flask API deployment${NC}"

if [ "$SETUP_MONITORING" = true ]; then
    progress "Setting up monitoring stack"
    chmod +x ./scripts/setup_monitoring.sh
    ./scripts/setup_monitoring.sh || echo -e "${YELLOW}Warning: Monitoring setup may not have completed successfully${NC}"
fi


echo -e "\n${GREEN}=============================================================${NC}"
echo -e "${GREEN}Flask API setup completed!${NC}"
echo -e "${GREEN}=============================================================${NC}"
echo -e "\n${BOLD}Your Flask API is now available at:${NC}"
echo -e "  - http://flask-api.local/"
echo -e "  - API Documentation: http://flask-api.local/docs"
echo -e "\n${BOLD}To test API endpoints, try:${NC}"
echo -e "  - Register: curl -X POST http://flask-api.local/api/v1/auth/register -H \"Content-Type: application/json\" -d '{\"email\":\"test@example.com\",\"password\":\"securepassword123\"}'"
echo -e "  - Get random string: curl -X GET http://flask-api.local/api/v1/strings/random"
echo -e "\n${BOLD}To access Kubernetes resources:${NC}"
echo -e "  - kubectl get all -n flask-api"
echo -e "\n${BOLD}To delete the cluster:${NC}"
echo -e "  - kind delete cluster --name ${CLUSTER_NAME}"
echo -e "${GREEN}=============================================================${NC}"
