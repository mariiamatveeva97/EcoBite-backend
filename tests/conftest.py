import os

# Veilige testwaarden. Ze moeten gezet zijn VOORDAT app.core.config wordt geimporteerd,
# want daar wordt `settings = Settings()` direct bij het importeren aangemaakt.
os.environ["DATABASE_URL"] = "postgresql+psycopg2://test:test@localhost:5432/test"
os.environ["ENV"] = "test"
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_PUBL_KEY"] = "test.test.test"
os.environ["SUPABASE_SECRET_KEY"] = "test.test.test"
os.environ["GROQ_API_KEY"] = "test"
os.environ["SPOONACULAR_API_KEY"] = "test"

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.database import get_db
from app.main import app


@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = uuid4()
    return user


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def client(fake_db):
    # De database wordt altijd vervangen: geen enkele test raakt een echte database.
    app.dependency_overrides[get_db] = lambda: fake_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def authed_client(client, fake_user):
    # Ingelogde gebruiker nagebootst: Supabase wordt niet aangeroepen.
    app.dependency_overrides[get_current_user] = lambda: fake_user
    return client
