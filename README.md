# Pod Manager

A simple controller container that demonstrates how easy it is to build a container that deploys and manages new containers.

## Overview

Pod Manager is a lightweight controller container built with Python that can deploy, monitor, and manage Docker containers. It demonstrates the fundamental concepts of container orchestration in a simple, easy-to-understand implementation.

## Features

- **Deploy Containers**: Automatically deploy containers from JSON configuration files
- **Container Management**: List, stop, and remove containers
- **Log Access**: Retrieve logs from managed containers
- **Configuration-Driven**: Use simple JSON files to define deployments
- **Docker API Integration**: Direct integration with Docker daemon

## Quick Start

### Prerequisites

- Docker installed and running
- Docker Compose (optional, for easier deployment)

### Option 1: Using Docker Compose (Recommended)

```bash
# Start the controller with example deployments
docker-compose up
```

### Option 2: Using the Run Script

```bash
# Build and run the controller
./run.sh
```

### Option 3: Manual Docker Commands

```bash
# Build the controller image
docker build -t pod-manager:latest .

# Run the controller
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/examples:/config \
  -e DEPLOYMENT_CONFIG=/config/deployments.json \
  pod-manager:latest
```

## Configuration

The controller reads deployment configurations from a JSON file. By default, it looks for `/config/deployments.json` inside the container.

### Deployment Configuration Format

#### Single Container
```json
{
    "name": "my-app",
    "image": "nginx:alpine",
    "ports": {
        "80/tcp": 8080
    },
    "environment": {
        "ENV_VAR": "value"
    }
}
```

#### Multiple Containers
```json
[
    {
        "name": "web-server",
        "image": "nginx:alpine",
        "ports": {
            "80/tcp": 8080
        }
    },
    {
        "name": "cache",
        "image": "redis:alpine",
        "ports": {
            "6379/tcp": 6379
        }
    }
]
```

### Configuration Options

- **name**: Container name (optional)
- **image**: Docker image to deploy (required)
- **ports**: Port mappings in format `{"container_port/protocol": host_port}`
- **environment**: Environment variables as key-value pairs
- **command**: Command to run in the container
- **volumes**: Volume mappings

## Examples

The `examples/` directory contains sample deployment configurations:

- `deployments.json`: Multiple container deployment (nginx + redis)
- `simple-deployment.json`: Single container deployment (hello-world)

To use a different configuration:

```bash
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/examples:/config \
  -e DEPLOYMENT_CONFIG=/config/simple-deployment.json \
  pod-manager:latest
```

## Architecture

The Pod Manager controller consists of:

1. **Controller Core** (`controller.py`): Main application logic
   - Docker client initialization
   - Container deployment logic
   - Container lifecycle management

2. **Configuration Loader**: Reads and validates JSON deployment configs

3. **Docker API Integration**: Uses the official Docker SDK for Python

## How It Works

1. The controller starts and initializes a connection to the Docker daemon
2. It reads the deployment configuration file (if specified)
3. For each deployment configuration:
   - Pulls the required Docker image (if not present)
   - Creates and starts the container with specified settings
   - Logs the deployment status
4. Lists all managed containers
5. Continues running in monitoring mode

## Development

### Project Structure

```
pod-manager/
├── controller.py          # Main controller implementation
├── Dockerfile            # Container image definition
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker Compose configuration
├── run.sh               # Quick start script
├── examples/            # Example deployment configs
│   ├── deployments.json
│   └── simple-deployment.json
└── README.md            # This file
```

### Testing Locally

You can test the controller locally with Python:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the controller
DEPLOYMENT_CONFIG=examples/deployments.json python controller.py
```

**Note**: The controller needs access to Docker socket, so ensure Docker is running.

## Security Considerations

⚠️ **Important**: This controller requires access to the Docker socket (`/var/run/docker.sock`), which gives it full control over the Docker daemon. In production:

- Use appropriate access controls
- Consider using Docker API over TCP with TLS
- Implement authentication and authorization
- Run with minimal required privileges
- Use security scanning on deployed images

## Use Cases

This project demonstrates how to build a controller container for:

- **Development Environments**: Quickly spin up development stacks
- **Testing**: Automate container deployment for integration tests
- **Learning**: Understand container orchestration concepts
- **Prototyping**: Build custom orchestration solutions

## License

This is a test repository for demonstrating container controller concepts.

## Contributing

This is a demonstration project, but suggestions and improvements are welcome!
