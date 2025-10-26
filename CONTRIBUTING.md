# Contributing to Pod Manager

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/SeboKnt/pod-manager.git
cd pod-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
python -m unittest test_controller.py -v
```

## Testing

### Unit Tests

Run the test suite:
```bash
python -m unittest test_controller.py
```

### Verification Script

Run the complete verification:
```bash
./verify.sh
```

This will:
- Build the Docker image
- Validate JSON configurations
- Run all unit tests
- Check Python syntax

## Building the Docker Image

```bash
docker build -t pod-manager:latest .
```

## Running Locally

### Option 1: With Docker Compose
```bash
docker-compose up
```

### Option 2: With the run script
```bash
./run.sh
```

### Option 3: Manual Docker run
```bash
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/examples:/config \
  -e DEPLOYMENT_CONFIG=/config/deployments.json \
  pod-manager:latest
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Adding New Features

1. Create a new branch
2. Implement your feature with tests
3. Ensure all tests pass
4. Update documentation
5. Submit a pull request

## Security

When adding new features:
- Never commit secrets or credentials
- Validate all user inputs
- Use the least privilege principle
- Keep dependencies up to date
