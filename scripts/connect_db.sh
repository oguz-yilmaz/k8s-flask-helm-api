#!/bin/bash

kubectl port-forward -n flask-api svc/flask-api-mysql 3306:3306
