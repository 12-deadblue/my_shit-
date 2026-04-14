import pytest
from flask_jwt_extended import decode_token

def test_auth_happy_path(client, mocker, mock_redis):
    """Test successful Google token exchange for JWT pair."""
    # Mock the google identity verifier to bypass real network requests
    mocker.patch('services.google_auth.verify_google_token', return_value={
        'sub': '987654321',  # Google ID
        'email': 'newuser@google.com',
        'name': 'New Tester',
        'picture': 'https://example.com/pic.png'
    })
    
    response = client.post('/api/auth/google', json={
        'access_token': 'dummy_google_token'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['success'] is True
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['email'] == 'newuser@google.com'
    
    # Verify the JWT claims match
    decoded = decode_token(data['access_token'])
    assert 'sub' in decoded

def test_auth_missing_payload(client):
    """Test the endpoint behaves safely if missing JSON body."""
    response = client.post('/api/auth/google')
    assert response.status_code == 415  # Unsuppported media type (no JSON)
    
    response2 = client.post('/api/auth/google', json={})
    assert response2.status_code == 400
    assert 'Token missing' in response2.get_json().get('error', '')

def test_auth_invalid_token(client, mocker):
    """Test simulation of Google rejecting a fraudulent token."""
    mocker.patch('services.google_auth.verify_google_token', return_value=None)
    
    response = client.post('/api/auth/google', json={
        'access_token': 'fraudulent_token_123'
    })
    
    assert response.status_code == 401
    assert 'Invalid token' in response.get_json().get('error', '')
