#!/bin/bash
# Quick verification script to test the pod-manager controller

set -e

echo "=== Pod Manager Controller Quick Test ==="
echo ""

# Build the image if needed
echo "1. Building pod-manager image..."
docker build -t pod-manager:latest . -q

# Verify the image exists
echo "✓ Image built successfully"
echo ""

# Validate configuration files
echo "2. Validating configuration files..."
python3 -c "import json; json.load(open('examples/deployments.json'))" && echo "✓ examples/deployments.json is valid"
python3 -c "import json; json.load(open('examples/simple-deployment.json'))" && echo "✓ examples/simple-deployment.json is valid"
echo ""

# Run unit tests
echo "3. Running unit tests..."
python3 -m unittest test_controller.py -q
echo "✓ All unit tests passed"
echo ""

# Test Python syntax
echo "4. Validating Python syntax..."
python3 -m py_compile controller.py
echo "✓ controller.py syntax is valid"
echo ""

echo "=== All checks passed! ==="
echo ""
echo "To run the controller with example deployments:"
echo "  ./run.sh"
echo ""
echo "Or with docker-compose:"
echo "  docker-compose up"
echo ""
