# PlateRate – FAQs & Common Issues

---

## General

**Q: Why does my login stop working after the server restarts?**

PlateRate uses an in-memory session token store. When the backend restarts, all active tokens are cleared. This is a known MVP limitation — simply log in again to get a new token.

---

**Q: I registered but can't log in. What's wrong?**

Check that you are selecting the correct role view on the landing page. User, Owner, and Admin each have separate login pages. Logging in through the wrong role view will fail even with valid credentials.

---

**Q: Can I browse restaurants without an account?**

Yes. The restaurant catalog and individual restaurant details are publicly visible. You only need an account to leave a review.

---

## Users

**Q: Why can't I post a review?**

Only accounts with the **User** role can submit reviews. If you are logged in as an Owner or Admin, the review submission option will not be available. Register or log in as a User account to leave reviews.

---

**Q: My review was submitted — why isn't it showing up?**

Reviews are published immediately upon submission in the current MVP. If your review is not visible, try refreshing the page. If the issue persists, contact your platform administrator to check the review status.

---

## Owners

**Q: Why can't I create a second restaurant?**

Each Owner account is limited to one restaurant listing. This is an intentional design constraint. To manage a second restaurant, create a new Owner account.

---

**Q: I uploaded an image but it's not showing. What happened?**

Check that your file meets the requirements: formats accepted are JPG, PNG, GIF, and WebP, with a maximum size of 5 MB. Files outside these constraints are silently rejected. Try re-uploading with a smaller or differently-formatted file.

---

## Admins

**Q: Why aren't Yelp reviews showing on a restaurant page?**

Yelp review snippets only appear for restaurants that were imported via the Yelp API (they have a `yelp_id` stored in the database). Manually created restaurants do not have Yelp data. Also verify that your `YELP_API_KEY` is valid and set in `.env`.

---

**Q: The Yelp import returned an error or imported nothing. What should I check?**

1. Confirm `YELP_API_KEY` is correctly set in `.env`.
2. Check that you have not exceeded the Yelp API daily call quota.
3. Try a smaller import limit (5–10 results) to isolate whether the issue is quota-related.

---

**Q: Why does an admin API endpoint return Forbidden (403)?**

The backend expects the raw session token in the `Authorization` header with no `Bearer` prefix. If you are calling the API directly (e.g., via curl or Postman), make sure the header value is exactly the UUID token returned at login.

---

**Q: I deleted some restaurants and now the database looks out of sync.**

There is a `DELETE /api/restaurants/all` endpoint that removes all restaurants at once — use this carefully. If data appears inconsistent, the safest fix is to re-import from Yelp or manually re-add restaurants through the Admin Dashboard.

---

## Developer / Setup

**Q: The backend fails to start with a database error.**

If you do not have PostgreSQL running, switch to the H2 dev profile: set `SPRING_PROFILES_ACTIVE=dev` before starting the backend. This uses an in-memory database with no external dependencies.

**Q: I get a role constraint error when creating an Owner account.**

Your database was created before the OWNER role was added. Run this SQL fix:

```sql
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('USER','ADMIN','OWNER'));
```
