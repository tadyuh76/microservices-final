# PeakPick Server Deployment

Production deployment uses a pull-based sync:

```text
GitHub main branch
-> systemd timer on the server
-> scripts/deploy.sh
-> docker compose -f docker-compose.prod.yml up -d --build
```

Only these ports are public by default:

```text
5173 frontend
8000 API Gateway
```

PostgreSQL, RabbitMQ, and internal FastAPI services stay inside Docker.

Server environment file:

```bash
PUBLIC_API_BASE_URL=http://SERVER_IP:8000
CORS_ORIGINS=http://SERVER_IP:5173
PEAKPICK_AUTH_SECRET=replace-with-a-long-random-secret
```

On `cop-fe`, place that file at:

```text
/opt/peakpick/.env.production
```

The deployment script expects 12 running containers: PostgreSQL, RabbitMQ,
frontend, API Gateway, Identity, Catalog, Order, Slot, Store Operations,
Inventory, Notification, and Analytics.

Demo accounts seeded by `db/init.sql`:

```text
admin@peakpick.local / admin123
manager.ueh@peakpick.local / manager123
manager.d1@peakpick.local / manager123
```
