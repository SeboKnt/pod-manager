# Dockerfile for Pod Manager Controller
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy controller script
COPY controller.py .

# Make controller executable
RUN chmod +x controller.py

# Create config directory
RUN mkdir -p /config

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the controller
CMD ["python", "controller.py"]
