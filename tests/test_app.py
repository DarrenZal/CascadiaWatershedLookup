"""
Unit tests for the Flask web application.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def mock_watershed_service():
    """Mock watershed service for testing."""
    mock_service = Mock()
    return mock_service


class TestFlaskApp:
    """Test cases for the Flask web application."""
    
    def test_index_route(self, client):
        """Test the main index route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Cascadia Watershed Lookup' in response.data
    
    def test_health_check_route(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data
    
    @patch('app.watershed_service')
    def test_lookup_api_success(self, mock_service, client):
        """Test successful watershed lookup via API."""
        # Mock successful lookup result
        mock_result = {
            'input_address': 'Seattle, WA',
            'coordinates': {'latitude': 47.6062, 'longitude': -122.3321},
            'watershed_info': {
                'immediate_watershed': {
                    'name': 'Test Watershed',
                    'country': 'USA',
                    'area_sqkm': 100.0
                }
            }
        }
        mock_service.lookup_watershed.return_value = mock_result
        app.watershed_service = mock_service
        
        response = client.post('/api/lookup', 
                             data=json.dumps({'address': 'Seattle, WA'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['input_address'] == 'Seattle, WA'
    
    @patch('app.watershed_service')
    def test_lookup_api_not_found(self, mock_service, client):
        """Test watershed lookup with no results."""
        mock_service.lookup_watershed.return_value = None
        app.watershed_service = mock_service
        
        response = client.post('/api/lookup',
                             data=json.dumps({'address': 'Invalid Address'}),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Watershed not found'
    
    def test_lookup_api_missing_address(self, client):
        """Test API call without address parameter."""
        response = client.post('/api/lookup',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid request'
    
    def test_lookup_api_empty_address(self, client):
        """Test API call with empty address."""
        response = client.post('/api/lookup',
                             data=json.dumps({'address': '   '}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Empty address'
    
    def test_lookup_api_service_unavailable(self, client):
        """Test API call when watershed service is unavailable."""
        # Temporarily set service to None
        original_service = app.watershed_service
        app.watershed_service = None
        
        try:
            response = client.post('/api/lookup',
                                 data=json.dumps({'address': 'Seattle, WA'}),
                                 content_type='application/json')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['error'] == 'Watershed service unavailable'
        finally:
            # Restore original service
            app.watershed_service = original_service
    
    @patch('app.watershed_service')
    def test_lookup_api_exception_handling(self, mock_service, client):
        """Test API exception handling."""
        mock_service.lookup_watershed.side_effect = Exception('Test error')
        app.watershed_service = mock_service
        
        response = client.post('/api/lookup',
                             data=json.dumps({'address': 'Seattle, WA'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'Internal server error'
    
    def test_invalid_json_request(self, client):
        """Test API call with invalid JSON."""
        response = client.post('/api/lookup',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_404_error_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Not found'
    
    def test_favicon_route(self, client):
        """Test favicon route."""
        response = client.get('/favicon.ico')
        # Should either serve the favicon or return 404, both are acceptable
        assert response.status_code in [200, 404]


if __name__ == '__main__':
    pytest.main([__file__])