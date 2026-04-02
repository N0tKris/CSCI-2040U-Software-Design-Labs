# PlateRate – Architecture Overview

## System Summary

PlateRate is a three-tier web application for restaurant discovery and review. It supports three roles — **User**, **Owner**, and **Admin** — each with distinct capabilities enforced through manual controller-level authorization.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Java 17, Spring Boot 3.2, Spring Web, Spring Data JPA, Spring Security, Validation |
| Frontend | Python 3.8+, Flask (server-rendered), Jinja2 templates, JavaScript |
| Database | PostgreSQL (production), H2 in-memory (dev/test profile) |
| External API | Yelp Fusion API (restaurant import and review snippets) |
| Build Tools | Maven (backend), pip (frontend) |

---

## Layered Backend Architecture

The backend follows a standard layered architecture:

```
HTTP Request
    ↓
Controller Layer       (handles routing, input validation, auth token checks)
    ↓
Service Layer          (business logic, data transformation)
    ↓
Repository Layer       (Spring Data JPA interfaces)
    ↓
PostgreSQL / H2
```

### Package Structure

```
backend/src/main/java/com/lab2/backend/
├── controller/        AuthController, UserController, RestaurantController,
│                      MenuItemController, ReviewController, AdminReviewController,
│                      YelpController, YelpPublicController, CatalogController
├── service/           AuthService, RestaurantService, ReviewService, YelpService
├── repository/        RestaurantRepository, UserRepository, ReviewRepository
├── model/             User, Restaurant, MenuItem, Review
└── config/            SecurityConfig, WebMvcConfig, DataInitializer
```

---

## Authentication & Session Model

- Login via `POST /api/auth/login` returns a **UUID token** stored in an **in-memory map** (`token → user`) inside `AuthService`.
- Tokens are passed as raw `Authorization` header values — no `Bearer` prefix is used.
- Spring Security is configured to **allow all requests globally**; authorization is enforced manually in each controller by calling `AuthService` token checks.
- **Important:** Because the token store is in-memory, all sessions are invalidated on backend restart.

---

## Frontend Architecture

The Flask frontend acts as a server-rendered UI layer that proxies API requests to the Spring Boot backend.

```
Browser
  ↓
Flask (app.py)         Role-oriented routes: /user/*, /owner/*, /admin/*
  ↓
Jinja2 Templates       landing.html, user_dashboard.html, owner_dashboard.html, etc.
  ↓
Backend REST API       http://localhost:8080
```

Flask sessions track the logged-in role independently of backend tokens.

---

## Database Schema

Core tables:

| Table | Key Fields |
|---|---|
| `users` | id, username, password, role (USER / OWNER / ADMIN) |
| `restaurants` | id, name, cuisine, location, dietary_tags, description, image, rating, yelp_id |
| `menus` | id, restaurant_id, item_name, price, description |
| `reviews` | id, user_id, restaurant_id, rating, comment, status |

- The `yelp_id` field on `restaurants` prevents duplicate imports.
- The `rating` field stores Yelp-sourced ratings for imported restaurants.

---

## Static File Serving

Uploaded restaurant images are served from the filesystem via a `/uploads/**` mapping configured in `WebMvcConfig.java`. Allowed upload types are JPG, PNG, GIF, and WebP with a 5 MB size limit.

---

## Data Bootstrapping

- A default admin account (`admin` / `admin123`) is seeded on first run via `DataInitializer.java`.
- Restaurants are seeded from `restaurants_only.json` if the database is empty, handled in `RestaurantService.java`.

---

## Profiles

| Profile | Database | Usage |
|---|---|---|
| default | PostgreSQL | Production / local with Docker |
| dev | H2 in-memory | Development and testing without Docker |

Activate dev profile: set `SPRING_PROFILES_ACTIVE=dev` before starting the backend.
