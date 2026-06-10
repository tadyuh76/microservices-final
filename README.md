# PeakPick

PeakPick là prototype **service-based + event-driven** cho luồng đặt hàng trước và nhận hàng tại ô pickup trong cửa hàng tiện lợi.

Ứng dụng demo:

```text
https://peakpick.tech
```

## Ý Tưởng

Trong giờ cao điểm, khách chỉ mua vài món nhỏ vẫn phải xếp hàng cùng toàn bộ khách tại quầy. PeakPick đổi luồng thành:

```text
Đặt món trước -> Chọn khung giờ nhận -> Thanh toán mock -> Hệ thống gán ô pickup -> Nhân viên chuẩn bị -> Khách xác nhận mã nhận hàng
```

Điểm chính của bài là **pickup slot**: một ô nhận hàng vật lý hoặc logic được giữ cho một đơn đã thanh toán trong một khung giờ cụ thể.

## Kiến Trúc

Project hiện dùng **service-based architecture** thay vì microservices tách repo. Lý do là scope của bài còn nhỏ, mỗi module nghiệp vụ chưa đủ lớn để tách thành một repo và database riêng.

Repo này giữ toàn bộ source trong một codebase, nhưng chia module theo business capability:

| Module | Trách nhiệm |
|---|---|
| API Gateway | Cổng REST duy nhất cho frontend, kiểm tra token và phân quyền cơ bản |
| Identity | Tài khoản demo, vai trò, token đăng nhập |
| Catalog | Danh mục sản phẩm, giá, trạng thái bán |
| Order | Giỏ hàng, checkout mock, trạng thái đơn hàng |
| Slot | Khung giờ nhận, sức chứa, gán và giải phóng ô pickup |
| Store Operations | Bảng xử lý của nhân viên, chuẩn bị đơn, xác nhận pickup |
| Inventory | Giữ hàng, trừ tồn, phát hiện thiếu hàng |
| Notification | Mô phỏng thông báo đơn sẵn sàng hoặc thiếu hàng |
| Analytics | Đếm sự kiện, thống kê vận hành |
| Frontend | Giao diện SolidJS cho khách và nhân viên |

## Event-Driven Flow

Các module backend giao tiếp workflow chính bằng RabbitMQ events:

```text
OrderPaid
-> PickupSlotReserved
-> InventoryReserved
-> OrderPreparing
-> OrderReady
-> NotificationRequested
-> OrderPickedUp
```

Order module không gọi trực tiếp toàn bộ module khác sau checkout. Nó publish `OrderPaid`; Slot, Inventory, Store Operations, Notification và Analytics tự consume event phù hợp. Cách này giữ coupling thấp nhưng vẫn vừa sức hơn microservices đầy đủ.

## Tech Stack

| Lớp | Công nghệ |
|---|---|
| Frontend | SolidJS, Vite, TypeScript |
| Backend | FastAPI, Python |
| Database | PostgreSQL một database chung |
| Message broker | RabbitMQ |
| API docs | Swagger / OpenAPI tại `/docs` |
| Container | Docker, Docker Compose |
| Test | Pytest, frontend build |

## Cấu Trúc Repo

```text
frontend/                  SolidJS UI
services/api_gateway/       REST gateway
services/identity_service/  identity/auth module
services/catalog_service/   catalog module
services/order_service/     order module
services/slot_service/      pickup slot module
services/store_ops_service/ staff operations module
services/inventory_service/ inventory module
services/notification_service/
services/analytics_service/
shared/                    event, auth, settings, logging utilities
db/init.sql                PostgreSQL schema and seed data
tests/                     unit and integration tests
```

## Chạy Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q

cd frontend
npm ci
npm run build
cd ..

docker compose up --build
```

Các port local:

| Thành phần | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API Gateway | http://localhost:8000 |
| RabbitMQ UI | http://localhost:15672 |
| Identity | http://localhost:8008/docs |
| Catalog | http://localhost:8001/docs |
| Order | http://localhost:8002/docs |
| Slot | http://localhost:8003/docs |
| Store Operations | http://localhost:8004/docs |
| Inventory | http://localhost:8005/docs |
| Notification | http://localhost:8006/docs |
| Analytics | http://localhost:8007/docs |

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

Bài nên trình bày PeakPick là prototype service-based có event-driven workflow:

```text
- Chia module theo business capability
- API Gateway làm điểm vào cho frontend
- RabbitMQ cho domain events
- PostgreSQL lưu dữ liệu demo trong một database chung
- Shared utilities chỉ có một bản trong repo
- Không claim production-ready
```
