-- ============================================================
-- Restaurant Review System - PostgreSQL Database Schema
-- ============================================================
-- Tables: users, restaurants, menus, reviews
-- ============================================================

-- Drop tables in reverse dependency order if they exist
DROP TABLE IF EXISTS review_images CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS menus CASCADE;
DROP TABLE IF EXISTS restaurants CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- USERS TABLE
-- role is stored as VARCHAR(10) so Hibernate's @Enumerated(EnumType.STRING)
-- works correctly and new roles (OWNER, etc.) can be added without DDL changes.
-- ============================================================
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        VARCHAR(10)  NOT NULL DEFAULT 'USER'
        CONSTRAINT chk_users_role CHECK (role IN ('ADMIN', 'USER', 'OWNER'))
);

-- Index for fast username lookups (e.g. login)
CREATE INDEX idx_users_username ON users (username);

-- ============================================================
-- RESTAURANTS TABLE
-- ============================================================
CREATE TABLE restaurants (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    cuisine       VARCHAR(50)  NOT NULL,
    dietary_tags  VARCHAR(255),          -- comma-separated tags, e.g. 'vegan,gluten-free'
    description   TEXT,
    location      VARCHAR(255) NOT NULL
);

-- Index for cuisine-based filtering
CREATE INDEX idx_restaurants_cuisine ON restaurants (cuisine);

-- ============================================================
-- MENUS TABLE
-- Each row represents one menu item belonging to a restaurant.
-- Cascade delete removes all menu items when a restaurant is deleted.
-- ============================================================
CREATE TABLE menus (
    id            SERIAL PRIMARY KEY,
    restaurant_id INT            NOT NULL,
    item_name     VARCHAR(100)   NOT NULL,
    price         NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    description   TEXT,
    image_url     VARCHAR(512),

    CONSTRAINT fk_menus_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants (id)
        ON DELETE CASCADE
);

-- Index to quickly retrieve the menu for a given restaurant
CREATE INDEX idx_menus_restaurant_id ON menus (restaurant_id);

-- ============================================================
-- REVIEWS TABLE
-- Each row is a review written by a user for a restaurant.
-- Cascade delete removes reviews when the user or restaurant is deleted.
-- ============================================================
CREATE TABLE reviews (
    id            SERIAL PRIMARY KEY,
    user_id       INT       NOT NULL,
    restaurant_id INT       NOT NULL,
    rating        SMALLINT  NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment       TEXT,
    timestamp     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reviews_restaurant
        FOREIGN KEY (restaurant_id)
        REFERENCES restaurants (id)
        ON DELETE CASCADE
);

-- Indexes for common query patterns
CREATE INDEX idx_reviews_restaurant_id ON reviews (restaurant_id);
CREATE INDEX idx_reviews_user_id       ON reviews (user_id);

-- ============================================================
-- REVIEW IMAGES TABLE
-- Stores up to 3 image URLs per review.
-- ============================================================
CREATE TABLE review_images (
    review_id    INT          NOT NULL,
    image_url    VARCHAR(512) NOT NULL,

    CONSTRAINT fk_review_images_review
        FOREIGN KEY (review_id)
        REFERENCES reviews (id)
        ON DELETE CASCADE
);

CREATE INDEX idx_review_images_review_id ON review_images (review_id);
