# FastAPI API Monitoring Dashboard --- Demo Task

A self-contained monitoring and alerting demo for a FastAPI application
using Prometheus, Grafana, and Alertmanager.

## Stack

-   FastAPI
-   Prometheus
-   Grafana
-   Alertmanager
-   Docker Compose
-   Python 3.12+ (only needed for non-Docker local development)

## Prerequisites

Install:

1.  Git
2.  Docker Desktop
3.  Optional: Python 3.12+ for running the API outside Docker

Verify:

``` bash
git --version
docker --version
docker compose version
```

## Start Everything

From the project directory:

``` bash
docker compose up --build -d
```

Check containers:

``` bash
docker compose ps
```

Services:

-   FastAPI: http://localhost:8000
-   Swagger UI: http://localhost:8000/docs
-   Prometheus: http://localhost:9090
-   Grafana: http://localhost:3000
-   Alertmanager: http://localhost:9093

## Grafana Login

``` text
Username: admin
Password: Admin@12345
```

## Stop

``` bash
docker compose down
```

Remove volumes as well:

``` bash
docker compose down -v
```

> Removing volumes deletes persisted Prometheus, Grafana, and
> Alertmanager data.

## API Endpoints

  Endpoint                   Purpose
  -------------------------- -------------------------------------
  GET /health                Service health check
  GET /users                 Sample users
  GET /products              Sample products
  GET /protected             Authentication failure/success demo
  GET /simulate-error        HTTP 500 demo
  GET /simulate-timeout      \>3 second latency demo
  GET /simulate-rate-limit   HTTP 429 demo
  GET /metrics               Prometheus metrics

## Failure Demonstrations

### Authentication Failure

``` bash
curl -i http://localhost:8000/protected
```

Expected: `401 Unauthorized`

Valid token:

``` bash
curl -i -H "Authorization: Bearer demo-token" http://localhost:8000/protected
```

Expected: `200 OK`

### Timeout / High Latency

``` bash
curl -i http://localhost:8000/simulate-timeout
```

The endpoint intentionally waits approximately 5 seconds.

### Server Error

``` bash
curl -i http://localhost:8000/simulate-error
```

Expected: `500 Internal Server Error`

This endpoint is also used to demonstrate the HTTP 500 Alertmanager
notification.

### Rate Limit

``` bash
curl -i http://localhost:8000/simulate-rate-limit
```

Expected: `429 Too Many Requests`

## Generate Traffic

``` bash
curl http://localhost:8000/health
curl http://localhost:8000/users
curl http://localhost:8000/products
```

Generate HTTP 500 errors:

``` bash
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/simulate-error
done
```

## Prometheus

Open http://localhost:9090

Useful queries:

### Request Rate

``` promql
sum(rate(http_requests_total[5m]))
```

### Failed Requests

``` promql
sum(rate(http_requests_total{status=~"4..|5.."}[5m]))
```

### Error Percentage

``` promql
100 * sum(rate(http_requests_total{status=~"4..|5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Average Latency

``` promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

## Grafana

Open http://localhost:3000

Login:

``` text
Username: admin
Password: admin
```

The Prometheus datasource and monitoring dashboard are provisioned
automatically.

The dashboard provides visibility into:

-   API service status
-   Uptime
-   Total requests
-   Failed requests
-   Error rate
-   Request rate
-   Average response time
-   HTTP error trends
-   Endpoint traffic

## Alertmanager

Open http://localhost:9093

The demo includes alert rules for:

-   API downtime
-   High response time (\>3 seconds)
-   HTTP 500 errors
-   Increased failure rate
-   Health check failure
-   Authentication failures
-   Rate-limit failures

### Notification Channels

Slack and email notifications are configured through local environment
variables and secret files.

Sensitive credentials must never be committed to Git.

The project uses:

``` text
.env
alertmanager/secrets/slack_webhook
alertmanager/secrets/smtp_password
```

These files are excluded through `.gitignore`.

### Test an Alert

``` bash
curl -i http://localhost:8000/simulate-error
```

After the alert rule's evaluation period, the `HTTP500Errors` alert
should appear in Alertmanager and notifications should arrive in Slack
and email.

Check active alerts:

``` bash
curl -s http://localhost:9093/api/v2/alerts | python3 -m json.tool
```

## Alert Pipeline

``` text
FastAPI
   ↓
Prometheus
   ↓
Alert Rules
   ↓
Alertmanager
   ├── Slack
   └── Email
```

Grafana visualization:

``` text
FastAPI
   ↓
Prometheus
   ↓
Grafana
```

## Recommended Demo Order

1.  Show the project structure.
2.  Start the Docker Compose stack.
3.  Show `docker compose ps`.
4.  Open FastAPI Swagger UI.
5.  Show `/health`.
6.  Open Prometheus targets and show the FastAPI target as UP.
7.  Open the Grafana monitoring dashboard.
8.  Show request volume, failed requests, error rate and latency.
9.  Trigger `/simulate-error`.
10. Show the HTTP 500 alert in Prometheus/Alertmanager.
11. Show the Slack notification.
12. Show the email notification.
13. Trigger `/simulate-timeout` and demonstrate high latency.
14. Trigger authentication and rate-limit failures.
15. Show Alertmanager's active alerts.

## Troubleshooting

See `docs/troubleshooting.md`.

## Security

Never commit:

``` text
.env
alertmanager/secrets/
```

The repository `.gitignore` excludes both locations.

If credentials are exposed, rotate the affected credentials before using
the project again.

## Definition of Done

-   FastAPI runs successfully.
-   Prometheus collects FastAPI metrics.
-   Prometheus target remains healthy.
-   Grafana displays API health and performance metrics.
-   Alert rules load successfully.
-   HTTP 500 failures generate alerts.
-   Increased failure rate is detectable.
-   Alertmanager receives alerts.
-   Slack notifications work.
-   Email notifications work.
-   Docker Compose starts the complete monitoring stack.
-   Notification credentials are excluded from Git.
-   Documentation explains setup, monitoring, alerting and testing.
