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
```

