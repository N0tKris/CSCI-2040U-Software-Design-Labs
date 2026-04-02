package com.lab2.backend.dto;

import com.lab2.backend.model.Review;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class ReviewDto {
    private Long id;
    private Long userId;
    private String username;
    private String comment;
    private double rating;
    private Long restaurantId;
    private String restaurantName;
    private LocalDateTime createdAt;
    private String status;
    private List<String> imageUrls = new ArrayList<>();

    public ReviewDto() {}

    public static ReviewDto fromEntity(Review r) {
        if (r == null) return null;
        ReviewDto dto = new ReviewDto();
        dto.id = r.getId();
        dto.comment = r.getComment();
        dto.rating = r.getRating();
        dto.restaurantId = r.getRestaurant() != null ? r.getRestaurant().getId() : null;
        dto.restaurantName = r.getRestaurant() != null ? r.getRestaurant().getName() : null;
        if (r.getUser() != null) {
            dto.userId = r.getUser().getId();
            dto.username = r.getUser().getUsername();
        }
        dto.createdAt = r.getTimestamp();
        dto.status = r.getStatus();
        dto.imageUrls = r.getImageUrls() != null ? new ArrayList<>(r.getImageUrls()) : new ArrayList<>();
        return dto;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getComment() { return comment; }
    public void setComment(String comment) { this.comment = comment; }
    public double getRating() { return rating; }
    public void setRating(double rating) { this.rating = rating; }
    public Long getRestaurantId() { return restaurantId; }
    public void setRestaurantId(Long restaurantId) { this.restaurantId = restaurantId; }
    public String getRestaurantName() { return restaurantName; }
    public void setRestaurantName(String restaurantName) { this.restaurantName = restaurantName; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public List<String> getImageUrls() { return imageUrls; }
    public void setImageUrls(List<String> imageUrls) { this.imageUrls = imageUrls != null ? imageUrls : new ArrayList<>(); }
}
