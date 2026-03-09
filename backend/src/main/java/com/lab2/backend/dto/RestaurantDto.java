package com.lab2.backend.dto;

import com.lab2.backend.model.MenuItem;
import com.lab2.backend.model.Restaurant;
import java.util.List;
import java.util.stream.Collectors;

public class RestaurantDto {
    private Long id;
    private String name;
    private String cuisine;
    private String location;
    private String dietaryTags;
    private String description;
    private Long ownerId;
    private List<String> menuItemNames;

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
        if (r.getMenuItems() != null) {
            dto.menuItemNames = r.getMenuItems().stream()
                    .map(MenuItem::getItemName)
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
    public List<String> getMenuItemNames() { return menuItemNames; }
    public void setMenuItemNames(List<String> menuItemNames) { this.menuItemNames = menuItemNames; }
}
