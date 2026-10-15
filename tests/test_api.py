from uuid import uuid4

from app.services import recipe_service


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "oke"}


def test_recipes_without_login_returns_401(client):
    response = client.get("/recipes")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_recipe_with_invalid_uuid_returns_422(authed_client):
    response = authed_client.get("/recipes/dit-is-geen-uuid")
    assert response.status_code == 422


def test_get_recipes_success_with_mocked_service(authed_client, fake_user, monkeypatch):
    calls = {}

    def fake_get_recipes(db, user):
        calls["user"] = user
        return []

    monkeypatch.setattr(recipe_service, "get_recipes_for_user", fake_get_recipes)

    response = authed_client.get("/recipes")

    assert response.status_code == 200
    assert response.json() == []
    assert calls["user"] is fake_user


def test_delete_unknown_recipe_returns_404(authed_client, fake_db):
    fake_db.query.return_value.filter.return_value.first.return_value = None

    response = authed_client.delete(f"/recipes/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Recept niet gevonden"}
    fake_db.delete.assert_not_called()


def test_delete_existing_recipe_returns_204(authed_client, fake_db):
    fake_db.query.return_value.filter.return_value.first.return_value = object()

    response = authed_client.delete(f"/recipes/{uuid4()}")

    assert response.status_code == 204
    fake_db.delete.assert_called_once()
    fake_db.commit.assert_called_once()
