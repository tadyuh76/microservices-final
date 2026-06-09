# PeakPick

PeakPick là hệ thống đặt hàng trước và nhận hàng theo ô pickup cho cửa hàng tiện lợi trong giờ cao điểm. Dự án hiện được tổ chức theo **Microservices Architecture + Event-Driven Architecture**.

Ứng dụng đang chạy tại:

```text
https://peakpick-103-90-225-235.sslip.io
```

## Ý tưởng

Thay vì khách phải xếp hàng, quét từng món, thanh toán rồi chờ xác nhận tại quầy, PeakPick đổi luồng thành:

```text
Đặt món trước -> Chọn khung giờ nhận -> Hệ thống gán ô pickup -> Nhân viên chuẩn bị -> Khách xác nhận mã nhận hàng
```

Điểm chính của bài là **pickup slot**: một ô nhận hàng vật lý hoặc logic được giữ cho một đơn đã thanh toán trong một khung giờ cụ thể.

## Kiến Trúc

PeakPick dùng microservices vì các nghiệp vụ có ranh giới rõ:

| Microservice | Trách nhiệm |
|---|---|
| API Gateway | Cổng REST duy nhất cho frontend, kiểm tra token và phân quyền cơ bản |
| Identity Service | Tài khoản demo, vai trò, token đăng nhập |
| Catalog Service | Danh mục sản phẩm, giá, trạng thái bán |
| Order Service | Giỏ hàng, checkout mock, trạng thái đơn hàng |
| Slot Service | Khung giờ nhận, sức chứa, gán và giải phóng ô pickup |
| Store Operations Service | Bảng xử lý của nhân viên, chuẩn bị đơn, xác nhận pickup |
| Inventory Service | Giữ hàng, trừ tồn, phát hiện thiếu hàng |
| Notification Service | Mô phỏng thông báo đơn sẵn sàng hoặc thiếu hàng |
| Analytics Service | Đếm sự kiện, thống kê vận hành |
| Frontend | Giao diện SolidJS cho khách và nhân viên |

Microservices trong bản tách repo có:

```text
- Repo riêng cho từng service
- Dockerfile riêng
- PostgreSQL database riêng cho từng service có dữ liệu
- RabbitMQ dùng chung để truyền domain events
- API Gateway làm điểm vào duy nhất cho client
```

## Event-Driven Flow

Luồng demo chính đi qua RabbitMQ:

```text
OrderPaid
-> PickupSlotReserved
-> InventoryReserved
-> OrderPreparing
-> OrderReady
-> NotificationRequested
-> OrderPickedUp
```

Các service không gọi trực tiếp tất cả service khác. Ví dụ, sau checkout, Order Service chỉ publish `OrderPaid`; Slot, Inventory, Store Operations và Analytics tự consume event phù hợp. Cách này giảm coupling và thể hiện rõ eventual consistency.

## Tech Stack

| Lớp | Công nghệ |
|---|---|
| Frontend | SolidJS, Vite, TypeScript |
| Backend | FastAPI, Python |
| Database | PostgreSQL, database riêng theo service |
| Message broker | RabbitMQ |
| API docs | Swagger / OpenAPI tại `/docs` của từng service |
| Container | Docker, Docker Compose |
| Reverse proxy | Nginx trên VPS, Caddy là option local/free-domain |
| Test | Pytest, frontend build |

## Repo Tách Microservice

Các repo chính đã được tách và push lên GitHub:

```text
peakpick-api-gateway
peakpick-identity-service
peakpick-catalog-service
peakpick-order-service
peakpick-slot-service
peakpick-store-ops-service
peakpick-inventory-service
peakpick-notification-service
peakpick-analytics-service
peakpick-frontend
peakpick-deployment
```

Repo `peakpick-deployment` là nơi chạy toàn bộ hệ thống bằng Docker Compose. Repo hiện tại giữ bản tổng hợp ban đầu, yêu cầu môn học và tài liệu dự án.

## Chạy Local Từ Repo Tổng Hợp

```bash
uv venv
uv pip install -r requirements.txt
uv run pytest -q
cd frontend && npm install && npm run build && cd ..
docker compose up --build
```

Các port local:

| Thành phần | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Gateway | http://localhost:8000 |
| RabbitMQ UI | http://localhost:15672 |
| Identity Service | http://localhost:8008/docs |
| Catalog Service | http://localhost:8001/docs |
| Order Service | http://localhost:8002/docs |
| Slot Service | http://localhost:8003/docs |
| Store Operations Service | http://localhost:8004/docs |
| Inventory Service | http://localhost:8005/docs |
| Notification Service | http://localhost:8006/docs |
| Analytics Service | http://localhost:8007/docs |

## Chạy Bản Microservice Tách Repo

Đặt các repo `peakpick-*` cùng cấp thư mục, sau đó:

```bash
cd peakpick-deployment
docker compose up --build
```

Khi deploy public:

```bash
PEAKPICK_AUTH_SECRET=replace-with-long-secret
PUBLIC_DOMAIN=peakpick-103-90-225-235.sslip.io
PUBLIC_API_BASE_URL=https://peakpick-103-90-225-235.sslip.io
CORS_ORIGINS=https://peakpick-103-90-225-235.sslip.io
docker compose --env-file .env.production up -d --build
```

Trên server hiện tại, Nginx reverse proxy public HTTPS vào `127.0.0.1:5173` và `127.0.0.1:8000`. Các service nội bộ chỉ bind localhost.

## Tài Khoản Demo

```text
admin@peakpick.local / admin123
manager.ueh@peakpick.local / manager123
manager.d1@peakpick.local / manager123
```

## Demo API Nhanh

```bash
TOKEN=$(
  curl -s -X POST http://localhost:8000/identity/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"manager.ueh@peakpick.local","password":"manager123"}' \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
)

curl http://localhost:8000/catalog/products

curl -X POST http://localhost:8000/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{"store_id":"store-ueh","customer_name":"Huy","pickup_window":"12:00-12:15","items":[{"sku":"coffee","quantity":2}]}'

curl http://localhost:8000/store/board \
  -H "Authorization: Bearer $TOKEN"
```

## Phạm Vi Báo Cáo

Bài nên trình bày PeakPick là một prototype microservices vừa đủ cho môn Kiến trúc phần mềm:

```text
- Microservices tách theo business capability
- API Gateway làm điểm vào
- RabbitMQ cho event-driven communication
- Database riêng theo service trong bản deployment tách repo
- Trade-off: giảm coupling nhưng phải chấp nhận eventual consistency và debug khó hơn
- Không claim production-ready
```
