# Flask String API Installation Guide

This guide will help you install and run the Flask String API on a Kubernetes
cluster.

## Prerequisites

- Kubernetes cluster (KinD, Minikube, or other)
- kubectl
- Helm v3+
- Git

## Ingress Setup

### 1. Install an Ingress Controller

You can install an ingress controller using one of these methods:

**Option A: Using Kind with built-in ingress support**

If you're using Kind (Kubernetes in Docker), create a cluster with ingress support:

1. Create a file named `kind-config.yaml`:
   ```yaml
   kind: Cluster
   apiVersion: kind.x-k8s.io/v1alpha4
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
   ```

2. Create the cluster with this config:
   ```bash
   kind create cluster --config=kind-config.yaml
   ```

3. Install the NGINX ingress controller for Kind:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
   ```

4. Wait for the ingress controller to be ready:
   ```bash
   kubectl wait --namespace ingress-nginx \
     --for=condition=ready pod \
     --selector=app.kubernetes.io/component=controller \
     --timeout=90s
   ```

**Option B: Using Helm**

Install NGINX Ingress Controller using Helm:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace
```

### 2. Configure DNS for the Ingress

```bash
echo "127.0.0.1 flask-api.local" | sudo tee -a /etc/hosts
```

## Build the Docker Image

Run this command in the project root:

```bash
docker build -t flask-api:latest .
```

## Load image into KinD

```bash
kind load docker-image flask-api:latest
```

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

### 1. Set up secrets

If you're fine with using the pre-configured MySQL root
password[mysecretpassword], you can skip this step.

Run the setup script to create necessary Kubernetes secrets:

```bash
chmod +x setup-secrets.sh
./setup-secrets.sh
```

Follow the prompts to set up your MySQL credentials.

### 2. Deploy the app

Install the application using Helm:

```bash
helm install flask-api ./flask-api-chart -n flask-api
```

**Or use Skaffold for local development(Recommended):**

```bash
skaffold dev
```

### 3. Verify the installation

Check that all pods are running:

```bash
kubectl get pods -n flask-api
```

### 4. Test the API

The API will be available at:

- Save a string: POST to http://localhost:5000/api/v1/strings/save
- Get a random string: GET from http://localhost:5000/api/v1/strings/random
- API Documentation: http://localhost:5000/docs

For detailed usage refer to the [README.md](README.md) file.

