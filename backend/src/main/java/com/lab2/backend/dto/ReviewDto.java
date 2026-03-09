package com.lab2.backend.dto;

import com.lab2.backend.model.Review;
import java.time.LocalDateTime;

public class ReviewDto {
    private Long id;
    private Long userId;
    private String username;
    private String comment;
    private int rating;
    private Long restaurantId;
    private LocalDateTime createdAt;

    public ReviewDto() {}

    public static ReviewDto fromEntity(Review r) {
        if (r == null) return null;
        ReviewDto dto = new ReviewDto();
        dto.id = r.getId();
        dto.comment = r.getComment();
        dto.rating = r.getRating();
        dto.restaurantId = r.getRestaurant() != null ? r.getRestaurant().getId() : null;
        if (r.getUser() != null) {
            dto.userId = r.getUser().getId();
            dto.username = r.getUser().getUsername();
        }
        dto.createdAt = r.getTimestamp();
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
    public int getRating() { return rating; }
    public void setRating(int rating) { this.rating = rating; }
    public Long getRestaurantId() { return restaurantId; }
    public void setRestaurantId(Long restaurantId) { this.restaurantId = restaurantId; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
