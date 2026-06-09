# PeakPick Deployment

Thư mục này giữ ghi chú deploy cũ của repo tổng hợp. Bản đang chạy public hiện dùng repo riêng:

```text
peakpick-deployment
```

Trong bản microservice hiện tại:

```text
GitHub repos tách riêng
-> /opt/peakpick-split trên VPS
-> docker compose trong peakpick-deployment
-> Nginx public HTTPS
-> API Gateway và Frontend bind localhost
```

Domain đang live:

```text
https://peakpick-103-90-225-235.sslip.io
```

## Cấu Hình Chính

File env production trên server:

```text
/opt/peakpick-split/peakpick-deployment/.env.production
```

Các biến cần có:

```bash
PEAKPICK_AUTH_SECRET=replace-with-a-long-random-secret
PUBLIC_DOMAIN=peakpick-103-90-225-235.sslip.io
PUBLIC_API_BASE_URL=https://peakpick-103-90-225-235.sslip.io
CORS_ORIGINS=https://peakpick-103-90-225-235.sslip.io
```

## Chạy Lại Stack

```bash
cd /opt/peakpick-split/peakpick-deployment
docker compose --env-file .env.production up -d --build
```

Không bật Caddy trên server hiện tại vì Nginx đã dùng port `80` và `443`.

## Tài Khoản Demo

```text
admin@peakpick.local / admin123
manager.ueh@peakpick.local / manager123
manager.d1@peakpick.local / manager123
```
