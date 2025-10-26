#!/bin/bash
# Build and run the pod manager controller

echo "Building Pod Manager Controller..."
docker build -t pod-manager:latest .

echo ""
echo "Running Pod Manager Controller..."
docker run -it --rm \
  --name pod-manager-controller \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/examples:/config \
  -e DEPLOYMENT_CONFIG=/config/deployments.json \
  pod-manager:latest
