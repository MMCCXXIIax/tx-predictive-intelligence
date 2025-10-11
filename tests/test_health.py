"""
Tests for health check endpoints
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_basic_health_check(client):
    """Test basic health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'TX Trade Whisperer Backend'
    assert 'timestamp' in data


def test_index_health_check(client):
    """Test index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_detailed_health_check(client):
    """Test detailed health endpoint"""
    response = client.get('/health/detailed')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'components' in data
    assert 'database' in data['components']
    assert 'ml_models' in data['components']
    assert 'system' in data['components']
    assert 'workers' in data['components']


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'tx_http_requests_total' in response.data
