# Flask String API Installation Guide

This guide will help you install and run the Flask String API on a Kubernetes
cluster.

## Prerequisites

- Kubernetes cluster (KinD, Minikube, or other)
- kubectl
- Helm v3+
- Git

## Sealed Secrets Setup

This project uses Bitnami Sealed Secrets for secure credential management.

1. Install the Sealed Secrets controller:
   ```bash
   helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
   helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

2. Install the kubeseal CLI tool:

For MacOS
```bash
brew install kubeseal
```

For Linux
```bash
KUBESEAL_VERSION=0.24.5
wget "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz"
tar -xvzf kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
```

For Windows
```bash
Download from https://github.com/bitnami-labs/sealed-secrets/releases
```

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/flask-string-api.git
cd flask-string-api
```

### 2. Set up secrets

Run the setup script to create necessary Kubernetes secrets:

```bash
chmod +x setup-secrets.sh
./setup-secrets.sh
```

Follow the prompts to set up your MySQL credentials.

### 3. Deploy with Helm

Install the application using Helm:

```bash
helm install flask-api ./flask-api-chart -n flask-api
```

Or use Skaffold for development:

```bash
skaffold dev
```

### 4. Verify the installation

Check that all pods are running:

```bash
kubectl get pods -n flask-api
```

### 5. Test the API

The API will be available at:

- Save a string: POST to http://localhost:5000/api/v1/strings/save
- Get a random string: GET from http://localhost:5000/api/v1/strings/random
- API Documentation: http://localhost:5000/docs

Example using curl:

```bash
# Save a string
curl -X POST http://localhost:5000/api/v1/strings/save \
  -H "Content-Type: application/json" \
  -d '{"string": "Hello, World!"}'

# Get a random string
curl http://localhost:5000/api/v1/strings/random
```

## Troubleshooting

If you encounter issues:

1. Check pod status:
   ```bash
   kubectl get pods -n flask-api
   ```

2. Check pod logs:
   ```bash
   kubectl logs -n flask-api <pod-name>
   ```

3. Ensure migrations have run:
   ```bash
   kubectl logs -n flask-api flask-api-migrations-xxxxx
   ```
