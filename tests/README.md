# Tests voor de EcoBite API

## Wat wordt getest
De tests gebruiken FastAPI `TestClient`. Er worden geen echte externe diensten aangeroepen
(geen Supabase, Groq, Spoonacular, SOAP of echte database). Authenticatie en database zijn vervangen
met `app.dependency_overrides` en mocks (zie `conftest.py`).

| Test | Wat het controleert |
|------|---------------------|
| test_health_returns_ok | GET /health geeft 200 en precies `{"status": "ok"}` |
| test_recipes_without_login_returns_401 | GET /recipes zonder cookie geeft 401 "Not authenticated" |
| test_recipe_with_invalid_uuid_returns_422 | GET /recipes/<geen uuid> geeft een validatiefout (422) |
| test_get_recipes_success_with_mocked_service | Succespad met nagebootste gebruiker en service: 200 en lege lijst |
| test_delete_unknown_recipe_returns_404 | DELETE van een onbekend recept geeft 404 "Recept niet gevonden" |
| test_delete_existing_recipe_returns_204 | DELETE van een bestaand recept geeft 204 en doet delete + commit |

## Veilige testomgeving
`conftest.py` zet nep-waarden voor DATABASE_URL en de API-sleutels voordat `app` wordt geimporteerd.
Omgevingsvariabelen gaan vóór het lokale `.env` bestand, dus echte sleutels worden niet gebruikt.

## Lokaal draaien
    pip install -r requirements-dev.txt
    python -m pytest -v

## Test dat echt kan falen
Ik heb in `test_health_returns_ok` bewust `{"status": "oke"}` verwacht. Resultaat:
    FAILED tests/test_api.py::test_health_returns_ok - AssertionError: assert {'status': 'ok'} == {'status': 'oke'}
Na het herstellen: 6 passed.
