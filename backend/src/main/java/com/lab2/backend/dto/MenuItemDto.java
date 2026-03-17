package com.lab2.backend.dto;

import com.lab2.backend.model.MenuItem;
import java.math.BigDecimal;

public class MenuItemDto {

    private Long id;
    private String itemName;
    private BigDecimal price;
    private String description;
    private Long restaurantId;

    public MenuItemDto() {}

    public static MenuItemDto fromEntity(MenuItem m) {
        if (m == null) return null;
        MenuItemDto dto = new MenuItemDto();
        dto.id = m.getId();
        dto.itemName = m.getItemName();
        dto.price = m.getPrice();
        dto.description = m.getDescription();
        dto.restaurantId = m.getRestaurant() != null ? m.getRestaurant().getId() : null;
        return dto;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getItemName() { return itemName; }
    public void setItemName(String itemName) { this.itemName = itemName; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Long getRestaurantId() { return restaurantId; }
    public void setRestaurantId(Long restaurantId) { this.restaurantId = restaurantId; }
}
