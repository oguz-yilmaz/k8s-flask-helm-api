#!/bin/bash

echo "Setting up required secrets for the Flask API project"
echo "======================================================"

# Determine path to templates directory from project root
PROJECT_ROOT=$(pwd)
TEMPLATES_DIR="${PROJECT_ROOT}/flask-api-chart/templates"

# Make sure the templates directory exists
if [ ! -d "$TEMPLATES_DIR" ]; then
    echo "Error: Templates directory not found at $TEMPLATES_DIR"
    echo "Make sure you're running this script from the project root directory"
    exit 1
fi

# Sealed Secrets Controller Configuration
read -p "Enter sealed-secrets controller namespace [kube-system]: " CONTROLLER_NAMESPACE
CONTROLLER_NAMESPACE=${CONTROLLER_NAMESPACE:-kube-system}

read -p "Enter sealed-secrets controller name [sealed-secrets]: " CONTROLLER_NAME
CONTROLLER_NAME=${CONTROLLER_NAME:-sealed-secrets}

# Check if the sealed-secrets controller exists
if ! kubectl get service "$CONTROLLER_NAME" -n "$CONTROLLER_NAMESPACE" &>/dev/null; then
    echo "Warning: Sealed Secrets controller service '$CONTROLLER_NAME' not found in namespace '$CONTROLLER_NAMESPACE'"
    echo "You may need to install the Sealed Secrets controller or use different values."
    
    # Ask user if they want to continue anyway
    read -p "Continue anyway? (y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        echo "Exiting script."
        exit 1
    fi
fi

# Prompt for MySQL credentials
read -p "Enter MySQL root password [mysecretpassword]: " root_password
root_password=${root_password:-mysecretpassword}

read -p "Enter MySQL database name [strings_db]: " db_name
db_name=${db_name:-strings_db}

# Generate secure random JWT secrets if not provided
read -p "Enter JWT secret key (leave empty to generate): " jwt_secret
if [ -z "$jwt_secret" ]; then
    jwt_secret=$(openssl rand -base64 32)
    echo "Generated JWT secret key"
fi

read -p "Enter JWT refresh secret key (leave empty to generate): " jwt_refresh_secret
if [ -z "$jwt_refresh_secret" ]; then
    jwt_refresh_secret=$(openssl rand -base64 32)
    echo "Generated JWT refresh secret key"
fi

# Create namespace if it doesn't exist
kubectl create namespace flask-api 2>/dev/null || true

# Handle MySQL credentials
if kubectl get secret mysql-credentials -n flask-api &>/dev/null; then
    echo "Deleting existing mysql-credentials secret..."
    kubectl delete secret mysql-credentials -n flask-api
fi

# Create the MySQL secrets with all required keys
echo "Creating new mysql-credentials secret..."
kubectl create secret generic mysql-credentials \
  -n flask-api \
  --from-literal=mysql-root-password=$root_password \
  --from-literal=mysql-password=$root_password \
  --from-literal=mysql-database=$db_name

# Verify MySQL secret was created
if ! kubectl get secret mysql-credentials -n flask-api &>/dev/null; then
    echo "Error: Failed to create MySQL secret"
    exit 1
fi

# Handle JWT secrets
if kubectl get secret jwt-secrets -n flask-api &>/dev/null; then
    echo "Deleting existing jwt-secrets secret..."
    kubectl delete secret jwt-secrets -n flask-api
fi

# Create JWT secrets
echo "Creating new jwt-secrets secret..."
kubectl create secret generic jwt-secrets \
  -n flask-api \
  --from-literal=jwt-secret-key=$jwt_secret \
  --from-literal=jwt-refresh-secret-key=$jwt_refresh_secret

# Verify JWT secret was created
if ! kubectl get secret jwt-secrets -n flask-api &>/dev/null; then
    echo "Error: Failed to create JWT secret"
    exit 1
fi

# Check for kubeseal
if ! command -v kubeseal &> /dev/null; then
    echo "Error: kubeseal not found. Please install kubeseal to create sealed secrets."
    exit 1
fi

# Create a temporary directory for intermediate files
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Create or update sealed MySQL secrets
MYSQL_SEALED_SECRET_FILE="$TEMPLATES_DIR/sealed-mysql-secret.yaml"
MYSQL_TEMP_FILE="$TEMP_DIR/mysql-secret.yaml"

echo "Exporting MySQL secret to temporary file..."
kubectl get secret mysql-credentials -n flask-api -o yaml > "$MYSQL_TEMP_FILE"

# Check if the file contains actual content
if [ ! -s "$MYSQL_TEMP_FILE" ]; then
    echo "Error: Export of MySQL secret failed - temporary file is empty"
    exit 1
fi

echo "Sealing MySQL secrets with kubeseal..."
# Use explicit controller name and namespace
kubeseal --format yaml \
         --controller-namespace="$CONTROLLER_NAMESPACE" \
         --controller-name="$CONTROLLER_NAME" \
         < "$MYSQL_TEMP_FILE" > "$MYSQL_SEALED_SECRET_FILE" 2>/dev/null || {
    echo "Failed to seal MySQL secret using controller service."
    echo "Trying alternative method: using kubeseal's cert directly..."
    
    # Try to fetch the controller's certificate
    CERT_FILE="$TEMP_DIR/sealed-secrets-cert.pem"
    if kubectl get secret -n "$CONTROLLER_NAMESPACE" sealed-secrets-key -o yaml | \
       grep -q "tls.crt"; then
        echo "Fetching certificate from sealed-secrets-key..."
        kubectl get secret -n "$CONTROLLER_NAMESPACE" sealed-secrets-key -o jsonpath='{.data.tls\.crt}' | \
        base64 --decode > "$CERT_FILE"
        
        # Use the certificate directly
        kubeseal --format yaml --cert "$CERT_FILE" < "$MYSQL_TEMP_FILE" > "$MYSQL_SEALED_SECRET_FILE"
    else
        echo "Failed to find sealed-secrets certificate."
        echo "Creating raw secrets instead (these will need to be sealed manually)."
        cp "$MYSQL_TEMP_FILE" "$MYSQL_SEALED_SECRET_FILE"
    fi
}

# Check if the sealed file contains actual content
if [ ! -s "$MYSQL_SEALED_SECRET_FILE" ]; then
    echo "Error: Sealing of MySQL secret failed - output file is empty"
    echo "Creating a dummy sealed secret template that you will need to update manually"
    
    cat > "$MYSQL_SEALED_SECRET_FILE" << EOF
# Source: flask-api-chart/templates/sealed-mysql-secret.yaml
---
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysql-credentials
  namespace: flask-api
spec:
  encryptedData:
    # These need to be replaced with real sealed values
    mysql-database: PLACEHOLDER
    mysql-root-password: PLACEHOLDER
  template:
    metadata:
      name: mysql-credentials
      namespace: flask-api
    type: Opaque
EOF
    echo "Created placeholder sealed secret template for MySQL"
fi

# Create or update sealed JWT secrets
JWT_SEALED_SECRET_FILE="$TEMPLATES_DIR/sealed-jwt-secret.yaml"
JWT_TEMP_FILE="$TEMP_DIR/jwt-secret.yaml"

echo "Exporting JWT secret to temporary file..."
kubectl get secret jwt-secrets -n flask-api -o yaml > "$JWT_TEMP_FILE"

# Check if the file contains actual content
if [ ! -s "$JWT_TEMP_FILE" ]; then
    echo "Error: Export of JWT secret failed - temporary file is empty"
    exit 1
fi

echo "Sealing JWT secrets with kubeseal..."
# Use explicit controller name and namespace
kubeseal --format yaml \
         --controller-namespace="$CONTROLLER_NAMESPACE" \
         --controller-name="$CONTROLLER_NAME" \
         < "$JWT_TEMP_FILE" > "$JWT_SEALED_SECRET_FILE" 2>/dev/null || {
    echo "Failed to seal JWT secret using controller service."
    echo "Trying alternative method: using kubeseal's cert directly..."
    
    # Try to fetch the controller's certificate (if we haven't already)
    CERT_FILE="$TEMP_DIR/sealed-secrets-cert.pem"
    if [ ! -f "$CERT_FILE" ] && kubectl get secret -n "$CONTROLLER_NAMESPACE" sealed-secrets-key -o yaml | \
       grep -q "tls.crt"; then
        echo "Fetching certificate from sealed-secrets-key..."
        kubectl get secret -n "$CONTROLLER_NAMESPACE" sealed-secrets-key -o jsonpath='{.data.tls\.crt}' | \
        base64 --decode > "$CERT_FILE"
    fi
    
    # Use the certificate directly if we have it
    if [ -f "$CERT_FILE" ]; then
        kubeseal --format yaml --cert "$CERT_FILE" < "$JWT_TEMP_FILE" > "$JWT_SEALED_SECRET_FILE"
    else
        echo "Failed to find sealed-secrets certificate."
        echo "Creating raw secrets instead (these will need to be sealed manually)."
        cp "$JWT_TEMP_FILE" "$JWT_SEALED_SECRET_FILE"
    fi
}

# Check if the sealed file contains actual content
if [ ! -s "$JWT_SEALED_SECRET_FILE" ]; then
    echo "Error: Sealing of JWT secret failed - output file is empty"
    echo "Creating a dummy sealed secret template that you will need to update manually"
    
    cat > "$JWT_SEALED_SECRET_FILE" << EOF
# Source: flask-api-chart/templates/sealed-jwt-secret.yaml
---
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: jwt-secrets
  namespace: flask-api
spec:
  encryptedData:
    # These need to be replaced with real sealed values
    jwt-secret-key: PLACEHOLDER
    jwt-refresh-secret-key: PLACEHOLDER
  template:
    metadata:
      name: jwt-secrets
      namespace: flask-api
    type: Opaque
EOF
    echo "Created placeholder sealed secret template for JWT"
fi

if grep -q "PLACEHOLDER" "$MYSQL_SEALED_SECRET_FILE" || grep -q "PLACEHOLDER" "$JWT_SEALED_SECRET_FILE"; then
    echo "WARNING: Some secrets were not properly sealed and contain placeholder values."
    echo "You will need to manually seal these secrets using kubeseal before deploying to production."
    echo "For development purposes, you can modify the script to use regular Kubernetes secrets instead."
else
    echo "Secrets created and sealed successfully!"
fi

echo "Secret files have been placed in the Helm templates directory:"
echo "- $MYSQL_SEALED_SECRET_FILE"
echo "- $JWT_SEALED_SECRET_FILE"
echo "You can now deploy your application with: helm install flask-api ./flask-api-chart -n flask-api"
