# Troubleshooting

## Containers are not starting

Run:

```bash
docker compose ps
docker compose logs api
docker compose logs prometheus
docker compose logs grafana
docker compose logs alertmanager
```

## Grafana has no data

1. Confirm API is running:
   `curl http://localhost:8000/health`
2. Confirm metrics:
   `curl http://localhost:8000/metrics`
3. Open Prometheus:
   http://localhost:9090
4. Check `Status -> Targets`.
5. The `fastapi` target should be `UP`.

## Dashboard is empty

Generate traffic:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/users
curl http://localhost:8000/products
```

Wait a few seconds for Prometheus scraping.

## Alerts are not firing

Prometheus evaluates rules every 5 seconds. Some alerts also require a `for` period.

Open:

http://localhost:9090/alerts

Then open:

http://localhost:9093

## Port already in use

Check the process using ports 8000, 9090, 3000, or 9093.

Alternatively change the left side of the Docker Compose port mapping, e.g.:

```yaml
ports:
  - "8001:8000"
```

## Reset everything

```bash
docker compose down -v
docker compose up --build -d
```

This removes Grafana/Prometheus/Alertmanager persisted data.
