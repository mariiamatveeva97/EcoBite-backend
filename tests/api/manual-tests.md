# Handmatige API-tests via de gateway (APIM)

Gateway-basis: https://ecobite-lktyc37ky6ppu-apim.azure-api.net/ecobite
Gedaan met curl op 2026-10-15. Rate limit op de gateway: 3 aanroepen per 60 seconden per client-IP.
Let op: Set-Cookie headers (ARRAffinity) zijn weggelaten, die zijn niet relevant.

| # | Scenario | Commando | Verwacht | Gekregen |
|---|----------|----------|----------|----------|
| 1 | Health check | `curl -s -i $BASE/health` | 200 en `{"status":"ok"}` | 200, `{"status":"ok"}`, header `Server: uvicorn` (backend antwoordde) |
| 2 | Bestaat niet | `curl -s -i $BASE/bestaat-niet` | 404 | 404 `{ "statusCode": 404, "message": "Resource not found" }`. Dit antwoord komt van de gateway (APIM), niet van de backend: geen `Server: uvicorn`, en FastAPI zou `{"detail":"Not Found"}` geven |
| 3 | /ingredients zonder sessie | `curl -s -i $BASE/ingredients` | 401 of 403, geen data | Eerst 500 (zie bevinding), na de fix 401 `{"detail":"Not authenticated"}`. Geen gebruikersdata in het antwoord |
| 4 | Rate limit | 5 keer `/health` achter elkaar | 429 na de 3e aanroep | 13:42:32 200, 200, 200; 13:42:33 429; 13:42:34 429. Header `Retry-After: 58`, bericht "Rate limit is exceeded. Try again in 58 seconds." |
| 5 | Na het venster | 65 seconden wachten, dan `/health` | 200 | 13:43:39 200 |

## Bevinding bij scenario 3

Eerste resultaat was 500 Internal Server Error in plaats van 401.
Oorzaak (uit AppServiceConsoleLogs in Log Analytics): `AttributeError: '_IncludedRouter' object has no attribute 'path'`
in de automatische Application Insights-agent (opentelemetry fastapi-instrumentatie). De agent kan routes die via
`include_router` zijn toegevoegd niet verwerken. `/health` staat direct op de app en werkte daarom wel.
Tijdelijke oplossing: app setting `ApplicationInsightsAgent_EXTENSION_VERSION=disabled` en de app herstarten. Daarna 401.
Blijvende oplossing (nog te doen): een FastAPI-versie vastzetten die compatibel is met de agent.

## Waar zie je dit in de logs

- 429 en 404 van de gateway staan in `ApiManagementGatewayLogs` (BackendResponseCode leeg, TotalTime 0) en niet in `AppServiceHTTPLogs`, omdat ze de backend nooit bereiken.
