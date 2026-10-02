# Monitoring Architecture

```text
                         ┌─────────────────┐
                         │     FastAPI     │
                         │   REST service  │
                         └────────┬────────┘
                                  │
                           /metrics
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Prometheus    │
                         │ Metrics + Rules │
                         └───────┬─────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  ▼                             ▼
           ┌─────────────┐              ┌─────────────┐
           │   Grafana   │              │ Alertmanager│
           │  Dashboard  │              │   Alerts    │
           └─────────────┘              └──────┬──────┘
                                               │
                                      Email / Slack
```

## Observed signals

- API availability
- Request volume
- Response latency
- HTTP status codes
- Failed request count
- Error percentage
- Health endpoint failures
- Authentication failures
- Rate-limit failures

## Root-cause path

Each application response includes `X-Request-ID`. Application logs include the same request ID. This allows a failed dashboard event to be connected to an individual request and its application log entry.
