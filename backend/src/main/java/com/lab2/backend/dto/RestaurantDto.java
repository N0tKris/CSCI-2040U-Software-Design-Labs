package com.lab2.backend.dto;

import com.lab2.backend.model.MenuItem;
import com.lab2.backend.model.Restaurant;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class RestaurantDto {
    private static final Pattern YELP_RATING_PATTERN = Pattern.compile("^\\s*([0-5](?:\\.\\d+)?)\\s+stars\\b");

    private Long id;
    private String name;
    private String cuisine;
    private String location;
    private String dietaryTags;
    private String description;
    private Long ownerId;
    private double stars;
    private String imageUrl;
    private List<String> menuItemNames;
    private List<MenuItemDto> menuItems;

    public RestaurantDto() {}

    public static RestaurantDto fromEntity(Restaurant r) {
        if (r == null) return null;
        RestaurantDto dto = new RestaurantDto();
        dto.id = r.getId();
        dto.name = r.getName();
        dto.cuisine = r.getCuisine();
        dto.location = r.getLocation();
        dto.dietaryTags = r.getDietaryTags();
        dto.description = r.getDescription();
        dto.ownerId = r.getOwnerId();
        dto.imageUrl = r.getImageUrl();
        if (r.getReviews() != null && !r.getReviews().isEmpty()) {
            dto.stars = r.getReviews().stream()
                    .mapToDouble(review -> review.getRating())
                    .average()
                    .orElse(0.0);
        } else {
            // Fallback for Yelp-imported restaurants where rating is embedded in description,
            // e.g. "4.4 stars (978 reviews on Yelp)".
            dto.stars = parseYelpRating(r.getDescription());
        }
        if (r.getMenuItems() != null) {
            dto.menuItemNames = r.getMenuItems().stream()
                    .map(MenuItem::getItemName)
                    .collect(Collectors.toList());
            dto.menuItems = r.getMenuItems().stream()
                    .map(MenuItemDto::fromEntity)
                    .collect(Collectors.toList());
        }
        return dto;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCuisine() { return cuisine; }
    public void setCuisine(String cuisine) { this.cuisine = cuisine; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    public String getDietaryTags() { return dietaryTags; }
    public void setDietaryTags(String dietaryTags) { this.dietaryTags = dietaryTags; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Long getOwnerId() { return ownerId; }
    public void setOwnerId(Long ownerId) { this.ownerId = ownerId; }
    public double getStars() { return stars; }
    public void setStars(double stars) { this.stars = stars; }
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    public List<String> getMenuItemNames() { return menuItemNames; }
    public void setMenuItemNames(List<String> menuItemNames) { this.menuItemNames = menuItemNames; }
    public List<MenuItemDto> getMenuItems() { return menuItems; }
    public void setMenuItems(List<MenuItemDto> menuItems) { this.menuItems = menuItems; }

    private static double parseYelpRating(String description) {
        if (description == null || description.isBlank()) {
            return 0.0;
        }
        Matcher matcher = YELP_RATING_PATTERN.matcher(description);
        if (!matcher.find()) {
            return 0.0;
        }
        try {
            return Double.parseDouble(matcher.group(1));
        } catch (NumberFormatException ignored) {
            return 0.0;
        }
    }
}
