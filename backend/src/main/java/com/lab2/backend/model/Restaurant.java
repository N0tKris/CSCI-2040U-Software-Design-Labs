package com.lab2.backend.model;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a restaurant.
 * Owns a collection of MenuItem and Review entities; both are cascade-deleted
 * when the restaurant is removed.
 */
@Entity
@Table(name = "restaurants")
public class Restaurant {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** The user ID of the owner who created this restaurant (null if created by admin). */
    @Column(name = "owner_id")
    private Long ownerId;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, length = 50)
    private String cuisine;

    /** Comma-separated dietary tags, e.g. "vegan,gluten-free". */
    @Column(name = "dietary_tags", length = 255)
    private String dietaryTags;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, length = 255)
    private String location;

    /** Menu items belonging to this restaurant. Removed when restaurant is deleted. */
    @OneToMany(mappedBy = "restaurant", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<MenuItem> menuItems = new ArrayList<>();

    /** Reviews for this restaurant. Removed when restaurant is deleted. */
    @OneToMany(mappedBy = "restaurant", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<Review> reviews = new ArrayList<>();

    /** URL path to the restaurant's uploaded image, e.g. "/uploads/restaurant-1.jpg". */
    @Column(name = "image_url", length = 512)
    private String imageUrl;

    public Restaurant() {}

    public Restaurant(String name, String cuisine, String dietaryTags,
                      String description, String location) {
        this.name = name;
        this.cuisine = cuisine;
        this.dietaryTags = dietaryTags;
        this.description = description;
        this.location = location;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getOwnerId() { return ownerId; }
    public void setOwnerId(Long ownerId) { this.ownerId = ownerId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCuisine() { return cuisine; }
    public void setCuisine(String cuisine) { this.cuisine = cuisine; }

    public String getDietaryTags() { return dietaryTags; }
    public void setDietaryTags(String dietaryTags) { this.dietaryTags = dietaryTags; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }

    public List<MenuItem> getMenuItems() { return menuItems; }
    public void setMenuItems(List<MenuItem> menuItems) { this.menuItems = menuItems; }

    public List<Review> getReviews() { return reviews; }
    public void setReviews(List<Review> reviews) { this.reviews = reviews; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
