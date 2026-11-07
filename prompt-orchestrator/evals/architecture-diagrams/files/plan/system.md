# Fleetwatch: system notes for the report figure

The report needs one architecture figure for the "System overview" section. It prints in the body
of an A4 landscape page, 24 cm wide.

## Deliverables and code paths

| Block | Code path | Talks to |
|---|---|---|
| Web app (React, Vite) | `web/` | Backend over HTTPS REST and a WebSocket; map tiles from OpenStreetMap over HTTPS (tiles load in the browser) |
| Mobile app (Flutter) | `mobile/` | Backend over HTTPS REST |
| Backend (NestJS) | `backend/` | PostgreSQL through Prisma; a BullMQ job queue it owns, stored in Redis; MQTT broker; SePay payment API over HTTPS; Resend email API over HTTPS; receives SePay webhooks over HTTPS |
| MQTT broker (Mosquitto) | `infra/mosquitto/` | Backend and the LoRa gateways over MQTT/TLS |
| LoRa gateway firmware | `firmware/gateway/` | MQTT broker over MQTT/TLS; trackers over LoRa |
| Tracker firmware | `firmware/tracker/` | Gateways over LoRa |
| PostgreSQL 16 | `infra/postgres/` | Backend |
| Redis 7 | `infra/redis/` | Backend (queue storage) |

Hosting: web app on Vercel; backend, broker, PostgreSQL and Redis in one Docker Compose stack on a
VPS. Actors: operators use the web app; customers use the mobile app.

## Backend modules (for reference)

auth, users, organizations, devices, telemetry, incidents, contracts, invoices, payments,
notifications, audit, parameters, maps. Each module has a controller, a service and DTOs.
