# Demo Script

## Part 1 — Normal operation

1. Open Swagger:
   http://localhost:8000/docs
2. Call `/health`.
3. Call `/users`.
4. Call `/products`.
5. Open Grafana:
   http://localhost:3000
6. Show service status, request count, response time and error rate.

## Part 2 — Authentication failure

```bash
curl -i http://localhost:8000/protected
```

Explain:

- HTTP 401
- Authentication failure
- Request ID
- Authentication alert

Then:

```bash
curl -i -H "Authorization: Bearer demo-token" http://localhost:8000/protected
```

Show successful recovery.

## Part 3 — HTTP 500

```bash
curl -i http://localhost:8000/simulate-error
```

Explain:

- HTTP 500 detected
- Prometheus records the failure
- Grafana shows the error trend
- Alertmanager receives the alert
- Logs provide the request ID and exception

## Part 4 — High latency

```bash
curl -i http://localhost:8000/simulate-timeout
```

Explain that the endpoint intentionally waits 5 seconds, exceeding the 3-second requirement.

## Part 5 — Rate limit

```bash
curl -i http://localhost:8000/simulate-rate-limit
```

Explain HTTP 429 and the rate-limit alert.

## Part 6 — Root cause

Open:

```bash
docker compose logs api
```

Find the request ID from the response/dashboard event and show the corresponding application log entry.

## Evidence to capture

- FastAPI Swagger
- Grafana dashboard in normal state
- Grafana dashboard during failures
- Prometheus targets
- Prometheus alerts
- Alertmanager alert
- Email/Slack notification
- Terminal/API response showing request ID
- Application logs showing root cause
