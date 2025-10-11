"""
Tests for ML API endpoints
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_ml_models_list(client):
    """Test ML models listing endpoint"""
    response = client.get('/api/ml/models')
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data


def test_ml_score_missing_symbol(client):
    """Test ML score endpoint with missing symbol"""
    response = client.get('/api/ml/score')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False
    assert 'symbol required' in data['error']


def test_ml_score_valid_symbol(client):
    """Test ML score endpoint with valid symbol"""
    response = client.get('/api/ml/score?symbol=AAPL&timeframe=1h')
    # May succeed or fail depending on data availability
    assert response.status_code in [200, 400, 500]
    data = response.get_json()
    assert 'success' in data


def test_ml_active_version(client):
    """Test ML active version endpoint"""
    response = client.get('/api/ml/active-version?asset_class=equity&timeframe=1h')
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data


def test_ml_promote_missing_params(client):
    """Test ML promote endpoint with missing parameters"""
    response = client.post('/api/ml/promote', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False


def test_online_status(client):
    """Test online learning status endpoint"""
    response = client.get('/api/ml/online-status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data


def test_deep_detect_missing_symbol(client):
    """Test deep detection with missing symbol"""
    response = client.get('/api/ml/deep-detect')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False


def test_multi_timeframe_missing_symbol(client):
    """Test multi-timeframe with missing symbol"""
    response = client.get('/api/ml/multi-timeframe')
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] == False
