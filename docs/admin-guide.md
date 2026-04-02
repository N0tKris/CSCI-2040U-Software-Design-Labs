# PlateRate – Admin Guide

This guide covers all administrative capabilities available to the admin role in PlateRate.

---

## Logging In

1. Open PlateRate in your browser (default: `http://127.0.0.1:5000`).
2. On the landing page, click **Admin View**.
3. Enter the admin credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
4. Click **Admin Login**.
5. You will be redirected to the Admin Dashboard.

---

## Admin Dashboard Overview

The Admin Dashboard provides two main management panels:

- **Users table** — lists all registered accounts with their role (USER, OWNER, ADMIN).
- **Restaurants table** — lists all restaurants with cuisine, location, dietary tags, and action buttons.
- **Reviews panel** — lists all submitted reviews with user, restaurant, rating, and comment.

---

## Managing Restaurants

### Adding a Restaurant Manually

1. In the Restaurants panel, click **+ Add Restaurant**.
2. Fill in the restaurant details (name, cuisine, location, dietary tags, description).
3. Submit the form.

### Editing a Restaurant

1. In the Restaurants table, find the restaurant you want to update.
2. Click **Edit**.
3. Modify the fields as needed and save.

### Deleting a Restaurant

1. In the Restaurants table, find the restaurant to remove.
2. Click **Delete**.
3. The restaurant and its associated data are removed from the database.

---

## Importing Restaurants from Yelp

The Yelp import feature populates the catalog with real restaurant data.

1. From the Admin Dashboard, navigate to the **Restaurants** panel.
2. Click **Import from Yelp**.
3. Enter the parameters:
   - **Location** — e.g., `Toronto`
   - **Max Results** — between 1 and 50
4. Click **Import**.

The backend fetches restaurant data from the Yelp API and stores it in the database. Duplicate entries (matched by `yelp_id`) are automatically skipped.

> **Note:** Yelp imposes daily API call limits. Use smaller batch sizes if you encounter quota errors. The system uses offset-based pagination and retry logic to handle rate limiting gracefully.

---

## Uploading Restaurant Images

1. In the Restaurants table, click **Edit** on the target restaurant.
2. Use the image upload field to select a file.
   - Accepted formats: JPG, PNG, GIF, WebP
   - Maximum file size: 5 MB
3. Save the form. The image will appear on the restaurant's public listing.

---

## Moderating Reviews

### Viewing Pending Reviews

Navigate to the pending reviews section of the Admin Dashboard to see reviews awaiting moderation.

### Approving a Review

Click **Approve** next to a pending review. It will become visible to all users on the restaurant page.

### Rejecting a Review

Click **Reject** next to a pending review. It will be hidden from public view.

---

## View As User (Admin Simulation Mode)

To simulate the user experience for review testing:

1. Click **View As User** in the Admin Dashboard.
2. The system impersonates the first USER account, allowing you to see the platform from a user's perspective.
3. Click **Exit User View** to return to the Admin Dashboard.

---

## Logging Out

Click **Logout** in the top-right corner of the Admin Dashboard to end your session.
