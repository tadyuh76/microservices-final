# PeakPick Deployment

Production deploy dùng cơ chế pull-based:

```text
GitHub main branch
-> systemd timer trên server
-> scripts/deploy.sh
-> docker compose -f docker-compose.prod.yml up -d --build
```

Repo deploy theo hướng service-based: một codebase, nhiều FastAPI module, một PostgreSQL database chung và RabbitMQ cho event flow.

## Environment

File `.env.production` trên server:

```bash
PUBLIC_API_BASE_URL=https://peakpick.tech
CORS_ORIGINS=https://peakpick.tech,https://www.peakpick.tech
PEAKPICK_AUTH_SECRET=replace-with-a-long-random-secret
```

## Public Reverse Proxy

Docker Compose production bind app vào localhost:

```text
127.0.0.1:5173 -> frontend
127.0.0.1:8000 -> API Gateway
```

Nginx public HTTPS proxy:

```text
/health, /routes, /identity/*, /catalog/*, /orders/*, /slots/*,
/store/*, /inventory/*, /notifications/*, /analytics/*, /system/*
-> http://127.0.0.1:8000

/*
-> http://127.0.0.1:5173
```
