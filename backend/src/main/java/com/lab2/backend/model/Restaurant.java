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

    /** Formatted street address from Yelp display_address or the app's canonical address string. */
    @Column(name = "address", length = 255)
    private String address;

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

    /** Yelp-provided primary image URL (remote), retained as fallback when no local image is uploaded. */
    @Column(name = "yelp_image_url", length = 512)
    private String yelpImageUrl;

    @Column(name = "yelp_url", length = 512)
    private String yelpUrl;

    /** Yelp business ID from Yelp API response (business.id). */
    @Column(name = "yelp_id", length = 128)
    private String yelpId;

    @Column(name = "yelp_phone", length = 64)
    private String yelpPhone;

    @Column(name = "yelp_price", length = 16)
    private String yelpPrice;

    @Column(name = "yelp_rating")
    private Double yelpRating;

    @Column(name = "yelp_review_count")
    private Integer yelpReviewCount;

    @Column(name = "yelp_is_closed")
    private Boolean yelpIsClosed;

    /** Geographic latitude of the restaurant location (decimal degrees). */
    @Column(name = "latitude")
    private Double latitude;

    /** Geographic longitude of the restaurant location (decimal degrees). */
    @Column(name = "longitude")
    private Double longitude;

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

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public List<MenuItem> getMenuItems() { return menuItems; }
    public void setMenuItems(List<MenuItem> menuItems) { this.menuItems = menuItems; }

    public List<Review> getReviews() { return reviews; }
    public void setReviews(List<Review> reviews) { this.reviews = reviews; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public String getYelpImageUrl() { return yelpImageUrl; }
    public void setYelpImageUrl(String yelpImageUrl) { this.yelpImageUrl = yelpImageUrl; }

    public String getYelpUrl() { return yelpUrl; }
    public void setYelpUrl(String yelpUrl) { this.yelpUrl = yelpUrl; }

    public String getYelpId() { return yelpId; }
    public void setYelpId(String yelpId) { this.yelpId = yelpId; }

    public String getYelpPhone() { return yelpPhone; }
    public void setYelpPhone(String yelpPhone) { this.yelpPhone = yelpPhone; }

    public String getYelpPrice() { return yelpPrice; }
    public void setYelpPrice(String yelpPrice) { this.yelpPrice = yelpPrice; }

    public Double getYelpRating() { return yelpRating; }
    public void setYelpRating(Double yelpRating) { this.yelpRating = yelpRating; }

    public Integer getYelpReviewCount() { return yelpReviewCount; }
    public void setYelpReviewCount(Integer yelpReviewCount) { this.yelpReviewCount = yelpReviewCount; }

    public Boolean getYelpIsClosed() { return yelpIsClosed; }
    public void setYelpIsClosed(Boolean yelpIsClosed) { this.yelpIsClosed = yelpIsClosed; }

    public Double getLatitude() { return latitude; }
    public void setLatitude(Double latitude) { this.latitude = latitude; }

    public Double getLongitude() { return longitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
}
