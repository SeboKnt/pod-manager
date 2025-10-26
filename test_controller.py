#!/usr/bin/env python3
"""
Unit tests for Pod Manager Controller
"""

import unittest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch, call
from controller import PodManagerController, load_deployments_from_file


class TestPodManagerController(unittest.TestCase):
    """Test cases for PodManagerController"""
    
    @patch('controller.docker')
    def setUp(self, mock_docker):
        """Set up test fixtures"""
        self.mock_client = MagicMock()
        mock_docker.from_env.return_value = self.mock_client
        self.controller = PodManagerController()
    
    def test_controller_initialization(self):
        """Test controller initializes with Docker client"""
        self.assertIsNotNone(self.controller.client)
    
    @patch('controller.docker')
    def test_deploy_container_success(self, mock_docker):
        """Test successful container deployment"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        mock_container = MagicMock()
        mock_container.id = "abc123def456"
        mock_client.containers.run.return_value = mock_container
        
        controller = PodManagerController()
        
        config = {
            'image': 'nginx:alpine',
            'name': 'test-nginx'
        }
        
        container_id = controller.deploy_container(config)
        
        self.assertEqual(container_id, "abc123def456")
        mock_client.containers.run.assert_called_once()
    
    @patch('controller.docker')
    def test_deploy_container_missing_image(self, mock_docker):
        """Test deployment fails when image is missing"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        controller = PodManagerController()
        
        config = {
            'name': 'test-container'
        }
        
        container_id = controller.deploy_container(config)
        
        self.assertIsNone(container_id)
        mock_client.containers.run.assert_not_called()
    
    @patch('controller.docker')
    def test_list_containers(self, mock_docker):
        """Test listing containers"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        mock_container1 = MagicMock()
        mock_container1.id = "container1"
        mock_container1.name = "nginx"
        mock_container1.status = "running"
        mock_container1.image.tags = ["nginx:alpine"]
        
        mock_container2 = MagicMock()
        mock_container2.id = "container2"
        mock_container2.name = "redis"
        mock_container2.status = "running"
        mock_container2.image.tags = ["redis:alpine"]
        
        mock_client.containers.list.return_value = [mock_container1, mock_container2]
        
        controller = PodManagerController()
        containers = controller.list_containers()
        
        self.assertEqual(len(containers), 2)
        self.assertEqual(containers[0]['name'], 'nginx')
        self.assertEqual(containers[1]['name'], 'redis')
    
    @patch('controller.docker')
    def test_stop_container_success(self, mock_docker):
        """Test stopping a container successfully"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        controller = PodManagerController()
        result = controller.stop_container("test123")
        
        self.assertTrue(result)
        mock_container.stop.assert_called_once()
    
    @patch('controller.docker')
    def test_remove_container_success(self, mock_docker):
        """Test removing a container successfully"""
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        
        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        controller = PodManagerController()
        result = controller.remove_container("test123")
        
        self.assertTrue(result)
        mock_container.remove.assert_called_once_with(force=False)


class TestConfigurationLoading(unittest.TestCase):
    """Test cases for configuration loading"""
    
    def test_load_single_deployment(self):
        """Test loading a single deployment configuration"""
        config_data = {
            'name': 'test-app',
            'image': 'nginx:alpine'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            deployments = load_deployments_from_file(temp_file)
            self.assertEqual(len(deployments), 1)
            self.assertEqual(deployments[0]['name'], 'test-app')
        finally:
            os.unlink(temp_file)
    
    def test_load_multiple_deployments(self):
        """Test loading multiple deployment configurations"""
        config_data = [
            {'name': 'app1', 'image': 'nginx:alpine'},
            {'name': 'app2', 'image': 'redis:alpine'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            deployments = load_deployments_from_file(temp_file)
            self.assertEqual(len(deployments), 2)
            self.assertEqual(deployments[0]['name'], 'app1')
            self.assertEqual(deployments[1]['name'], 'app2')
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """Test loading from a nonexistent file"""
        deployments = load_deployments_from_file('/nonexistent/file.json')
        self.assertEqual(len(deployments), 0)
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = f.name
        
        try:
            deployments = load_deployments_from_file(temp_file)
            self.assertEqual(len(deployments), 0)
        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
