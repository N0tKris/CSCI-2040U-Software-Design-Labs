# PlateRate – Step-by-Step Workflows

---

## Workflow 1: First-Time Setup and First Login

**Goal:** Get the system running and access each role for the first time.

1. Start PostgreSQL (Docker or local instance).
2. Start the backend: `./mvnw spring-boot:run` from the `backend/` directory.
3. Start the frontend: `python3 frontend/app.py` from the `frontend/` directory.
4. Open `http://127.0.0.1:5000` in your browser.
5. Click **Admin View** → log in with `admin` / `admin123`.
6. Verify the Admin Dashboard loads and the user/restaurant tables are visible.
7. Log out, then register a User account and an Owner account to confirm all three role flows work.

---

## Workflow 2: User Submits a Review and Admin Publishes It

**Goal:** Walk through the full review lifecycle from submission to visibility.

1. Log in as a **User** account.
2. Browse the restaurant catalog on the User Dashboard.
3. Click **Leave Review** on any restaurant card.
4. Select a star rating and type a comment in the modal.
5. Click **Submit Review** — the review is saved immediately.
6. Log out, then log in as **Admin**.
7. Navigate to the Reviews panel to confirm the review appears.
8. *(Optional for future iteration)* Use **Approve** or **Reject** to moderate the review.

---

## Workflow 3: Owner Onboarding — Account → Restaurant → Menu → Image

**Goal:** Set up a complete owner listing from scratch.

1. From the landing page, click **Owner View** → **Owner Sign Up**.
2. Create an owner account with a username and password.
3. After logging in, fill in the **Register Your Restaurant** form with name, cuisine, location, and description.
4. Click **Register Restaurant** — the listing now appears in the public catalog.
5. From the Owner Dashboard, click **Add Menu Item** and add at least one item with a name, price, and description.
6. Click **Upload Image**, select a JPG or PNG file under 5 MB, and submit.
7. Log out and log in as a User to verify the restaurant, menu, and image are visible in the catalog.

---

## Workflow 4: Admin Data Management Lifecycle

**Goal:** Import, manage, and clean restaurant data as an admin.

1. Log in as **Admin**.
2. Click **Import from Yelp**, set Location to `Toronto` and Max Results to `10`, then click **Import**.
3. Verify imported restaurants appear in the Restaurants table with cuisine and location fields populated.
4. Click **Edit** on one restaurant to update its description or dietary tags. Save.
5. Click **Delete** on a test/placeholder restaurant to remove it from the catalog.
6. Navigate to the **Reviews** panel and review any submitted user reviews. Approve or reject as appropriate.
7. Use **View As User** to confirm the catalog looks correct from a user perspective, then exit user view.

---

## Workflow 5: Running Tests

**Goal:** Validate the backend and frontend test suites pass.

1. Start the backend with the dev (H2) profile so no PostgreSQL instance is required:
   ```bash
   export SPRING_PROFILES_ACTIVE=dev
   ./mvnw test
   ```
2. Confirm all backend tests pass (Auth, User, MenuItemController, RestaurantService, ReviewService).
3. In the `frontend/` directory:
   ```bash
   npm install
   npm test
   ```
4. Confirm `filters.test.js` passes.
