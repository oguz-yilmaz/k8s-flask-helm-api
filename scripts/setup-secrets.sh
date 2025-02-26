#!/bin/bash

echo "Setting up required secrets for the Flask API project"
echo "======================================================"

# Prompt for MySQL credentials
read -p "Enter MySQL root password [mysecretpassword]: " root_password
root_password=${root_password:-mysecretpassword}

read -p "Enter MySQL database name [strings_db]: " db_name
db_name=${db_name:-strings_db}

# Create namespace if it doesn't exist
kubectl create namespace flask-api 2>/dev/null || true

# Check if secret exists and delete it if it does
if kubectl get secret mysql-credentials -n flask-api &>/dev/null; then
    echo "Deleting existing mysql-credentials secret..."
    kubectl delete secret mysql-credentials -n flask-api
fi

# Check if sealed secret exists and delete it if it does
if kubectl get sealedsecret mysql-credentials -n flask-api &>/dev/null; then
    echo "Deleting existing mysql-credentials sealed secret..."
    kubectl delete sealedsecret mysql-credentials -n flask-api
fi

# Create the MySQL secrets with all required keys
echo "Creating new mysql-credentials secret..."
kubectl create secret generic mysql-credentials \
  -n flask-api \
  --from-literal=mysql-root-password=$root_password \
  --from-literal=mysql-password=$root_password \
  --from-literal=mysql-database=$db_name

echo "Secrets created successfully!"
echo "Now run: \`skaffold dev\` or \`helm install flask-api . -n flask-api\`"
