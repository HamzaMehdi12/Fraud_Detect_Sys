#!/bin/bash
# Performs zero-downtime deployment
DEPLOYMENT="fraud-api"
IMAGE_TAG=$1

kubectl set image deployment/$DEPLOYMENT $DEPLOYMENT=registry.fraud.com/api:$IMAGE_TAG
kubectl rollout status deployment/$DEPLOYMENT --timeout=300s