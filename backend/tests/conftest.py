import pytest
from app import create_app
from db.models import db, User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    # Configure an in-memory SQLite database for blazing fast, isolated tests
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "JWT_SECRET_KEY": "super-secret-test-key",
        "REDIS_URL": "redis://localhost:6379/15"  # Use distinct DB for tests if real Redis exists
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """Mock the Redis caching layer so tests never rely on an actual network layer."""
    # We use mocker from pytest-mock (requires `pip install pytest-mock`)
    mock_redis = mocker.patch('services.cache.redis_client')
    # Because we added @require_redis which checks `redis_client.available`,
    # let's mock it to True to bypass the decorator aborts if we want to trace them.
    mock_redis.available = True
    return mock_redis

@pytest.fixture
def test_user(app):
    """Creates a default test user and returns it."""
    with app.app_context():
        user = User(
            google_id="123456789",
            email="testuser@example.com",
            name="Testing User",
            picture="https://example.com/avatar.png"
        )
        db.session.add(user)
        db.session.commit()
        
        # Detach it from the session to safely return
        db.session.refresh(user)
        return user
