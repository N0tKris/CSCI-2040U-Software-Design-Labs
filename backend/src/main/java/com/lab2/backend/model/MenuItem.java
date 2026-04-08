package com.lab2.backend.model;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.validation.constraints.DecimalMin;
import java.math.BigDecimal;

/**
 * Represents a single item on a restaurant's menu.
 * Belongs to exactly one Restaurant; deleted when that restaurant is deleted.
 */
@Entity
@Table(name = "menus")
public class MenuItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** The restaurant this menu item belongs to. */
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "restaurant_id", nullable = false)
    @JsonBackReference
    private Restaurant restaurant;

    @Column(name = "item_name", nullable = false, length = 100)
    private String itemName;

    @DecimalMin(value = "0.0", message = "Price must be non-negative")
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(columnDefinition = "TEXT")
    private String description;

    /** Comma-separated dietary tags, e.g. "Vegan, Gluten-Free". */
    @Column(name = "dietary_tags", length = 255)
    private String dietaryTags;

    /** URL path to the menu item's uploaded image, e.g. "/uploads/menu-item-1.jpg". */
    @Column(name = "image_url", length = 512)
    private String imageUrl;

    public MenuItem() {}

    public MenuItem(Restaurant restaurant, String itemName, BigDecimal price, String description) {
        this.restaurant = restaurant;
        this.itemName = itemName;
        this.price = price;
        this.description = description;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Restaurant getRestaurant() { return restaurant; }
    public void setRestaurant(Restaurant restaurant) { this.restaurant = restaurant; }

    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getDietaryTags() { return dietaryTags; }
    public void setDietaryTags(String dietaryTags) { this.dietaryTags = dietaryTags; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
}
