#!/usr/bin/env python3
"""
Pod Manager Controller
A simple controller container that deploys and manages new containers.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional
import docker
from docker.errors import DockerException, NotFound, APIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PodManagerController:
    """Controller for managing container deployments."""
    
    def __init__(self):
        """Initialize the controller with Docker client."""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def deploy_container(self, config: Dict) -> Optional[str]:
        """
        Deploy a new container based on configuration.
        
        Args:
            config: Dictionary with container configuration
                - image: Docker image to deploy
                - name: Container name
                - environment: Optional environment variables
                - ports: Optional port mappings
                - command: Optional command to run
        
        Returns:
            Container ID if successful, None otherwise
        """
        try:
            image = config.get('image')
            name = config.get('name')
            
            if not image:
                logger.error("Image not specified in configuration")
                return None
            
            # Pull image if not present
            logger.info(f"Ensuring image {image} is available...")
            try:
                self.client.images.pull(image)
            except Exception as e:
                logger.warning(f"Could not pull image {image}: {e}")
            
            # Prepare container configuration
            container_config = {
                'image': image,
                'detach': True,
            }
            
            if name:
                container_config['name'] = name
            
            if 'environment' in config:
                container_config['environment'] = config['environment']
            
            if 'ports' in config:
                container_config['ports'] = config['ports']
            
            if 'command' in config:
                container_config['command'] = config['command']
            
            if 'volumes' in config:
                container_config['volumes'] = config['volumes']
            
            # Deploy the container
            logger.info(f"Deploying container with config: {container_config}")
            container = self.client.containers.run(**container_config)
            logger.info(f"Container deployed successfully: {container.id[:12]}")
            
            return container.id
            
        except APIError as e:
            logger.error(f"Docker API error while deploying container: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while deploying container: {e}")
            return None
    
    def list_containers(self, all_containers: bool = False) -> List[Dict]:
        """
        List all managed containers.
        
        Args:
            all_containers: If True, include stopped containers
        
        Returns:
            List of container information dictionaries
        """
        try:
            containers = self.client.containers.list(all=all_containers)
            container_info = []
            
            for container in containers:
                info = {
                    'id': container.id[:12],
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                    'status': container.status,
                }
                container_info.append(info)
            
            return container_info
            
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    def stop_container(self, container_id: str) -> bool:
        """
        Stop a running container.
        
        Args:
            container_id: Container ID or name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            logger.info(f"Container {container_id} stopped successfully")
            return True
        except NotFound:
            logger.error(f"Container {container_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            return False
    
    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """
        Remove a container.
        
        Args:
            container_id: Container ID or name
            force: Force removal of running container
        
        Returns:
            True if successful, False otherwise
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            logger.info(f"Container {container_id} removed successfully")
            return True
        except NotFound:
            logger.error(f"Container {container_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error removing container {container_id}: {e}")
            return False
    
    def get_container_logs(self, container_id: str, tail: int = 100) -> Optional[str]:
        """
        Get logs from a container.
        
        Args:
            container_id: Container ID or name
            tail: Number of lines to retrieve from the end
        
        Returns:
            Container logs as string, None if error
        """
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode('utf-8')
            return logs
        except NotFound:
            logger.error(f"Container {container_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting logs for container {container_id}: {e}")
            return None


def load_deployments_from_file(filepath: str) -> List[Dict]:
    """Load deployment configurations from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except FileNotFoundError:
        logger.warning(f"Deployment file {filepath} not found")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in deployment file: {e}")
        return []


def main():
    """Main entry point for the controller."""
    logger.info("Starting Pod Manager Controller...")
    
    try:
        controller = PodManagerController()
    except Exception as e:
        logger.error(f"Failed to initialize controller: {e}")
        sys.exit(1)
    
    # Check for deployment configuration file
    config_file = os.environ.get('DEPLOYMENT_CONFIG', '/config/deployments.json')
    
    if os.path.exists(config_file):
        logger.info(f"Loading deployments from {config_file}")
        deployments = load_deployments_from_file(config_file)
        
        for deployment in deployments:
            logger.info(f"Processing deployment: {deployment.get('name', 'unnamed')}")
            container_id = controller.deploy_container(deployment)
            if container_id:
                logger.info(f"Deployment successful: {container_id}")
            else:
                logger.error("Deployment failed")
    else:
        logger.info(f"No deployment configuration found at {config_file}")
        logger.info("Controller is running in monitoring mode")
    
    # List current containers
    logger.info("Current containers:")
    containers = controller.list_containers(all_containers=True)
    for container in containers:
        logger.info(f"  - {container['name']} ({container['id']}): {container['status']}")
    
    # Keep controller running (in a real scenario, this would monitor for changes)
    logger.info("Controller initialized. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Controller shutting down...")


if __name__ == '__main__':
    main()
