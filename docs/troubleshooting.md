# PlateRate – Troubleshooting Guide

## Backend Not Reachable

**Symptom:** Frontend shows connection errors; API calls fail.

**Checks:**
1. Confirm the Spring Boot backend is running: `curl http://localhost:8080/api/catalog`
2. Ensure port 8080 is free — no other process should be using it.
3. Check the terminal running the backend for startup errors.
4. Verify `application.properties` has the correct DB URL if using PostgreSQL.

---

## Sessions Reset After Backend Restart

**Symptom:** Users are suddenly logged out; tokens return 401 after a backend restart.

**Cause:** The token store is an in-memory `Map<token, user>` in `AuthService.java`. It does not persist across restarts. This is by design for the MVP.

**Fix:** All users must log in again after the backend restarts. Preserving the database across restarts (do not drop/recreate tables on every startup) prevents data loss while only requiring re-login.

---

## Token / Authorization Errors

**Symptom:** Requests return 401 or 403 unexpectedly.

**Cause:** The backend expects the raw token string in the `Authorization` header — there is no `Bearer ` prefix. Some HTTP clients or frontend modifications may accidentally add one.

**Fix:** Confirm the `Authorization` header value is exactly the UUID token returned at login, with no prefix.

---

## OWNER Role Constraint Error

**Symptom:** Registering or updating a user with the OWNER role fails with a database constraint violation.

**Cause:** The database was created before the OWNER role was added to the check constraint.

**Fix:** Run the following SQL against your PostgreSQL database:

```sql
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));
```

---

## Owner Cannot Create a Second Restaurant

**Symptom:** An owner account receives an error when trying to register a second restaurant.

**Cause:** By design, each owner account is limited to one restaurant. This constraint is enforced in `RestaurantController.java`.

**Fix:** This is expected behavior. To manage multiple restaurants, create separate owner accounts.

---

## Admin View as Owner: Restaurant Looks Unsaved

**Symptom:** In admin owner simulation mode, registering a restaurant appears to fail or disappear.

**Cause:** Owner simulation uses admin credentials and tracked simulation state. If simulation state is stale (for example after manual session edits or abrupt tab/session changes), the dashboard may not show the expected restaurant.

**Fix:**
1. Exit owner simulation using **Back to Admin**.
2. Re-enter via **View as Owner** from the Admin Dashboard.
3. Retry restaurant registration.
4. If needed, log out admin and log back in to reset session state.

The current frontend stores a simulation restaurant id in session to keep owner-view data visible after creation.

---

## Yelp Import Not Working

**Symptom:** Import from Yelp returns an error or imports nothing.

**Checks:**
1. Confirm `YELP_API_KEY` is set correctly in `.env`.
2. Verify the `.env` file is loaded by the application at startup (`YelpService.java` reads it).
3. Check that you have not exceeded the Yelp API daily call quota. The import uses offset-based pagination and backoff/retry logic to handle quota limits gracefully, but it cannot exceed the daily cap.
4. Try a smaller import limit (e.g., 5–10) to verify the key is valid.

---

## Yelp Reviews Not Displaying

**Symptom:** Restaurant detail pages show no Yelp review snippets.

**Checks:**
1. Verify the restaurant has a `yelp_id` set (only imported restaurants do).
2. Confirm `YELP_API_KEY` is valid and has not expired.
3. Check the debug endpoint: `GET /api/yelp/debug/yelp-reviews/{id}` returns raw Yelp data for a given restaurant ID.

---

## Review Submitted but Not Visible to Users

**Symptom:** A newly submitted review is not shown on public restaurant pages.

**Cause:** Reviews start in `PENDING` status and are hidden until approved.

**Fix:**
1. Log in as admin.
2. Open pending reviews.
3. Approve the review to set status to `PUBLISHED`.

---

## Image Upload Failures

**Symptom:** Uploading a restaurant image returns an error.

**Checks:**
1. Confirm the file type is one of: JPG, PNG, GIF, WebP. Other formats are rejected.
2. Confirm the file is under 5 MB. Larger files are rejected by `RestaurantService.java`.
3. Check Spring multipart limits in `application.properties` if uploads consistently fail near the size limit.
4. Verify the uploads directory exists and is writable by the backend process.

---

## Missing PostgreSQL Locally

**Symptom:** Backend fails to start with a database connection error.

**Fix:** Switch to the H2 dev profile to run without PostgreSQL:

```bash
# Linux/Mac
export SPRING_PROFILES_ACTIVE=dev && ./mvnw spring-boot:run

# Windows
$env:SPRING_PROFILES_ACTIVE="dev"; .\mvnw.cmd spring-boot:run
```

---

## Python / Frontend Errors

**Symptom:** Frontend fails to start or throws import errors.

**Fix:**
1. Make sure the virtual environment is activated before running `app.py`.
2. Reinstall dependencies: `pip install -r frontend/requirements.txt`.
3. Confirm you are running from the `frontend/` directory or that relative paths in `app.py` resolve correctly.

---

## Admin Endpoint Returns Forbidden

**Symptom:** Admin API calls return 403.

**Checks:**
1. Confirm you are logged in as the `admin` account (not a USER or OWNER).
2. Check that the `Authorization` header is being sent with every request (raw token, no `Bearer` prefix).
3. Note: The Yelp import endpoint (`/api/admin/import-yelp-restaurants`) does not enforce backend auth — it relies on the Flask session to restrict access to admins.
