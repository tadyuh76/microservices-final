# PeakPick

PeakPick is a service-based, event-driven pickup slot system for convenience stores during peak hours.

The idea is simple: instead of waiting in a cashier line, a customer orders small items before arriving, chooses a pickup window, pays through a mock checkout flow, and receives an assigned pickup slot. Store staff prepares the cart, places it in the assigned slot, then verifies the customer's pickup token or QR code.

## Problem

Convenience stores can become crowded during short peak periods such as class breaks, lunch time, or commute hours. Customers who only want one drink or snack still wait behind everyone else because all customers follow the same flow:

```text
Pick items -> Wait in line -> Cashier scans items -> Pay -> Wait for confirmation -> Leave
```

PeakPick changes the flow to:

```text
Order before arrival -> Choose pickup window -> Store prepares cart -> Assigned pickup slot -> Verify pickup
```

The main domain concept is the pickup slot. A pickup slot is a physical or logical store location reserved for one paid order during a specific pickup window.

## Architecture Plan

PeakPick uses:

```text
Service-Based Architecture + Event-Driven Architecture
```

Service-based architecture is selected because the system has clear business domains, but a pure microservices approach would be too complex for a small course project. Event-driven architecture is used to coordinate important lifecycle changes between services without forcing the Order Service to directly call every other service.

Main services:

| Service | Responsibility |
|---|---|
| API Gateway | Single entry point for frontend clients |
| Catalog Service | Products, categories, prices, and availability |
| Order Service | Cart, checkout, mock payment, and order lifecycle |
| Slot Service | Pickup windows, slot capacity, and slot assignment |
| Store Operations Service | Staff board, preparation status, and pickup verification |
| Inventory Service | Stock reservation, deduction, and shortage checks |
| Notification Service | Simulated ready, delay, and pickup notifications |
| Analytics Service | Event counters, slot utilization, and peak-hour demand |

## Main Demo Flow

The MVP focuses on one complete vertical journey:

```text
1. Customer browses items.
2. Customer creates cart and completes mock checkout.
3. Order Service publishes OrderPaid.
4. Slot Service assigns a pickup window and slot.
5. Store Operations dashboard shows the assigned slot.
6. Staff marks the order as Preparing and Ready.
7. Customer receives a pickup token or QR code.
8. Staff verifies pickup.
9. Order becomes PickedUp.
10. Slot becomes Available again.
```

## Core Events

```text
CartCreated
OrderPaid
PickupSlotReserved
InventoryReserved
InventoryShortageDetected
OrderPreparing
OrderReady
OrderPickedUp
OrderExpired
NotificationRequested
AnalyticsUpdated
```

## Lifecycle

Order lifecycle:

```text
CartCreated -> PaymentPending -> Paid -> SlotAssigned -> Preparing -> ReadyForPickup -> Completed
```

Slot lifecycle:

```text
Available -> Reserved -> Preparing -> Ready -> PickedUp -> Available
```

Extra states such as `Cancelled`, `Expired`, and `Delayed` can be added after the main flow works.

## Technology Plan

| Layer | Planned Technology |
|---|---|
| Frontend | SolidJS + Vite + TypeScript |
| Backend | FastAPI services |
| Database | PostgreSQL |
| Message Broker | RabbitMQ |
| API Docs | Swagger / OpenAPI |
| Deployment | Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Health endpoints and structured logs |

## Data Consistency Strategy

Use stronger consistency for decisions that must be correct:

```text
Payment status
Slot reservation
Inventory reservation
```

Use eventual consistency for supporting workflows where a short delay is acceptable:

```text
Notifications
Analytics
Dashboard summaries
Low-stock alerts
```

This is the main architecture trade-off: stronger consistency protects the critical order and slot flow, while event-driven updates reduce coupling for supporting services.

## Implementation Scope

Required MVP:

```text
Customer ordering page
Catalog browsing
Cart and mock checkout
Pickup time selection
Automatic slot assignment
Pickup token or QR code
Staff dashboard
Slot status updates
Inventory deduction
Notification simulation
Analytics event counter
RabbitMQ event flow
Docker Compose setup
Swagger API documentation
```

Stretch features, only if the MVP is already stable:

```text
Realtime staff board
Order expiration
Low-stock alerts
Peak-hour demand forecasting
Cloud deployment
Prometheus/Grafana monitoring
```

## Implemented Prototype

This repository now includes Huy's platform and eventing foundation:

```text
FastAPI services
RabbitMQ topic exchange
PostgreSQL event_log table
Shared event envelope and event types
API Gateway route skeleton
Health endpoints
Structured JSON logs
Docker Compose
GitHub Actions test workflow
Integration tests for the event flow
```

Service ports:

| Service | URL |
|---|---|
| API Gateway | http://localhost:8000 |
| Catalog Service | http://localhost:8001 |
| Order Service | http://localhost:8002 |
| Slot Service | http://localhost:8003 |
| Store Operations Service | http://localhost:8004 |
| Inventory Service | http://localhost:8005 |
| Notification Service | http://localhost:8006 |
| Analytics Service | http://localhost:8007 |
| Frontend | http://localhost:5173 |
| RabbitMQ UI | http://localhost:15672 |

Each FastAPI service exposes Swagger at `/docs` and a health check at `/health`.

Run locally:

```bash
uv venv
uv pip install -r requirements.txt
uv run pytest -q
cd frontend && npm install && npm run build && cd ..
docker compose up --build
```

Frontend foundation:

```text
frontend/src/App.tsx
frontend/src/services/api.ts
frontend/src/services/types.ts
```

The UI calls the API Gateway through `VITE_API_BASE_URL` and gives teammates a starting point for customer checkout, staff board actions, notifications, and analytics.

Quick demo path through the API Gateway:

```bash
curl http://localhost:8000/catalog/products

curl -X POST http://localhost:8000/orders/checkout \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Huy","pickup_window":"12:00-12:15","items":[{"sku":"coffee","quantity":2}]}'

curl http://localhost:8000/store/board
curl -X POST http://localhost:8000/store/orders/{order_id}/preparing
curl -X POST http://localhost:8000/store/orders/{order_id}/ready
curl -X POST http://localhost:8000/store/orders/{order_id}/pickup \
  -H "Content-Type: application/json" \
  -d '{"token":"PK-XXXXXX"}'

curl http://localhost:8000/analytics/events
```

RabbitMQ carries the main events:

```text
OrderPaid -> PickupSlotReserved -> OrderPreparing -> OrderPlacedInSlot
-> OrderReady -> NotificationRequested -> OrderPickedUp
```

## Team Split

| Role | Main Ownership |
|---|---|
| Platform and Eventing Lead | Repo structure, Docker Compose, RabbitMQ, PostgreSQL, shared event contracts, API Gateway, health checks, CI/CD |
| Ordering and Slot Lead | Order Service, Slot Service, checkout flow, slot assignment, `OrderPaid -> PickupSlotReserved` event flow |
| Store Operations and Inventory Lead | Catalog/Inventory Service, staff dashboard, status updates, inventory deduction, pickup verification |

## Two-Week Plan

Week 1:

```text
Set up project structure
Create Docker Compose skeleton
Start PostgreSQL and RabbitMQ
Implement base FastAPI services
Create catalog and order APIs
Publish OrderPaid event
Consume OrderPaid in Slot Service
Publish PickupSlotReserved event
Show assigned slot in staff board
```

Week 2:

```text
Add pickup token or QR code
Implement Preparing, Ready, and PickedUp actions
Add event logs and correlation IDs
Add notification and analytics simulation
Write integration tests for the main journey
Prepare Swagger screenshots and demo evidence
Finalize report sections and trade-off analysis
```

## Report Plan

The report should follow the required course outline:

1. Introduction
2. System Requirements
3. Architecture Selection
4. Architecture Design
5. Technical Design
6. Implementation
7. Evaluation
8. Conclusion

Important concepts to explain:

```text
Architectural characteristics
Modularity
Coupling and cohesion
Domain partitioning
Distributed system trade-offs
Data consistency strategy
Evolution from service-based architecture to fuller microservices
```

## Scope Control

If time is tight, keep the system focused on the main order-to-pickup journey:

```text
Keep Order Service, Slot Service, and Store Operations Service.
Merge Catalog and Inventory if needed.
Simulate Notification and Analytics with logs.
Keep payment as mock payment only.
Use a generated pickup token instead of real scanner integration.
```

PeakPick should be presented as a practical course prototype, not a production-ready system. The strongest point of the project is showing how service boundaries and events help coordinate orders, slots, inventory, staff operations, notifications, and analytics during peak-hour pickup.

## Server Deployment

Production-style deployment uses the dedicated compose file:

```bash
PUBLIC_API_BASE_URL=http://SERVER_IP:8000 \
CORS_ORIGINS=http://SERVER_IP:5173 \
docker compose -f docker-compose.prod.yml up -d --build
```

For the `cop-fe` server, GitHub auto-sync is handled by `scripts/deploy.sh` plus the systemd timer templates in `deployment/`. The timer pulls `main` from GitHub and redeploys only when the commit changes.
