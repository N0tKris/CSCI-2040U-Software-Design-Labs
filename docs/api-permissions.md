# PlateRate – API Endpoints & Role Permissions

Base URL: `http://localhost:8080`

Roles: **Public** (no auth), **User**, **Owner**, **Admin**

Authorization is enforced manually in controllers using token checks via `AuthService`. The token is passed as a raw `Authorization` header value (no `Bearer` prefix).

---

## Authentication

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Returns UUID session token |
| POST | `/api/auth/logout` | Authenticated | Invalidates token (optional header accepted) |
| GET | `/api/auth/me` | Authenticated | Returns current user info |

Source: `AuthController.java`

---

## Users

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/users` | Admin only | List all users |
| POST | `/api/users/register` | Public | Self-registration; role must be USER or OWNER |

Source: `UserController.java`

---

## Restaurants

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/restaurants` | Public | List all restaurants |
| GET | `/api/restaurants/{id}` | Public | Get single restaurant |
| GET | `/api/restaurants/my` | Owner only | Get the owner's restaurant |
| POST | `/api/restaurants` | Admin or Owner | Create restaurant (Owner limited to one) |
| PUT | `/api/restaurants/{id}` | Admin only | Update restaurant (JSON body) |
| PUT | `/api/restaurants/{id}` (multipart) | Admin only | Update restaurant with image |
| DELETE | `/api/restaurants/{id}` | Admin only | Delete single restaurant |
| DELETE | `/api/restaurants/all` | Admin only | Delete all restaurants |
| POST | `/api/restaurants/{id}/upload-image` | Admin or Owner (own only) | Upload restaurant image |

Source: `RestaurantController.java`

---

## Menu Items

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/restaurants/{restaurantId}/menu` | Admin or Owner (own restaurant only) | Add menu item |

Source: `MenuItemController.java`

---

## Reviews

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/reviews` | Admin only | List all reviews |
| GET | `/api/reviews/restaurant/{restaurantId}` | Public | Get published reviews for a restaurant |
| POST | `/api/reviews` | User only | Submit a review |
| POST | `/api/reviews/admin/user-view` | Admin only | Impersonate first USER for admin review view |

Source: `ReviewController.java`

---

## Admin Review Moderation

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/admin/reviews/pending` | Admin only | List pending reviews |
| PUT | `/api/admin/reviews/{id}/approve` | Admin only | Approve a review |
| PUT | `/api/admin/reviews/{id}/reject` | Admin only | Reject a review |

Source: `AdminReviewController.java`

---

## Yelp Integration

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/admin/import-yelp-restaurants` | Admin (frontend-enforced) | Import restaurants from Yelp API |
| GET | `/api/yelp/reviews/restaurant/{restaurantId}` | Public | Get Yelp review snippets for a restaurant |
| GET | `/api/yelp/debug/yelp-reviews/{id}` | Public | Debug endpoint for Yelp review data |

> **Note:** The import endpoint does not perform backend-level auth checks — admin access is enforced by the Flask frontend session only.

Source: `YelpController.java`, `YelpPublicController.java`

---

## Legacy Catalog

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET/POST/PUT/DELETE | `/api/catalog` | Varies | CRUD on legacy catalog items (CSV-backed) |

Source: `CatalogController.java`

---

## Role Permission Matrix Summary

| Feature | Public | User | Owner | Admin |
|---|---|---|---|---|
| Browse restaurants | ✅ | ✅ | ✅ | ✅ |
| View restaurant details | ✅ | ✅ | ✅ | ✅ |
| View published reviews | ✅ | ✅ | ✅ | ✅ |
| Register account | ✅ | — | — | — |
| Submit review | ❌ | ✅ | ❌ | ❌ |
| Create restaurant | ❌ | ❌ | ✅ (1 only) | ✅ |
| Edit / delete restaurant | ❌ | ❌ | ❌ | ✅ |
| Upload restaurant image | ❌ | ❌ | ✅ (own only) | ✅ |
| Add menu items | ❌ | ❌ | ✅ (own only) | ✅ |
| Import from Yelp | ❌ | ❌ | ❌ | ✅ |
| Moderate reviews | ❌ | ❌ | ❌ | ✅ |
| View all users | ❌ | ❌ | ❌ | ✅ |
