import pytest
from flask_jwt_extended import create_access_token
from db.models import SavedPage, db

@pytest.fixture
def auth_headers(app, test_user):
    """Generates valid JWT headers for the test user."""
    with app.app_context():
        token = create_access_token(identity=str(test_user.id))
        return {'Authorization': f'Bearer {token}'}

def test_save_page_unauthorized(client):
    """Ensure anonymous users cannot save pages."""
    response = client.post('/api/data/pages', json={
        "url": "https://example.com"
    })
    assert response.status_code == 401
    assert 'Missing Authorization Header' in response.get_json().get('msg', '')

def test_save_page_validation_error(client, auth_headers):
    """Ensure missing url payload throws 400."""
    response = client.post('/api/data/pages', headers=auth_headers, json={
        "title": "A page with no URL"
    })
    
    assert response.status_code == 400
    assert 'url is required' in response.get_json().get('error', '')

def test_save_page_happy_path(client, auth_headers, test_user, app, mock_redis):
    """Test authenticated user successfully saving a page."""
    
    response = client.post('/api/data/pages', headers=auth_headers, json={
        "url": "https://example.com/test",
        "title": "Test Page"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['page']['url'] == "https://example.com/test"
    assert data['page']['title'] == "Test Page"
    
    # Assert it was actually saved in the in-memory SQLite database
    with app.app_context():
        # verify row exists
        saved = SavedPage.query.filter_by(user_id=test_user.id).first()
        assert saved is not None
        assert saved.url == "https://example.com/test"

def test_free_tier_limit(client, auth_headers, test_user, app, mock_redis, mocker):
    """Ensure free tier users get blocked at FREE_MAX_SAVED_PAGES."""
    # Force Mock Redis to return that we already have 50 pages saved
    mocker.patch.object(mock_redis, 'get_cached_page_count', return_value=50) # Assuming 50 is max
    app.config["FREE_MAX_SAVED_PAGES"] = 50
    
    response = client.post('/api/data/pages', headers=auth_headers, json={
        "url": "https://example.com/too-many"
    })
    
    assert response.status_code == 403
    assert 'limit reached' in response.get_json().get('error', '').lower()
