#!/bin/bash
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

kubectl config use-context $ENVIRONMENT
kubectl apply -f infrastructure/kubernetes/$ENVIRONMENT/
kubectl set image deployment/fraud-api fraud-api=registry.fraud.com/api:$VERSION