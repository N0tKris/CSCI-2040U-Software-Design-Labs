package com.lab2.backend.controller;

import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.service.AuthService;
import com.lab2.backend.service.ReviewService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * REST controller for review endpoints.
 */
@RestController
@RequestMapping("/api/reviews")
@CrossOrigin(origins = "*")
public class ReviewController {

    private final ReviewService reviewService;
    private final AuthService authService;

    public ReviewController(ReviewService reviewService, AuthService authService) {
        this.reviewService = reviewService;
        this.authService = authService;
    }

    /**
     * List all reviews. Admin-only.
     * GET /api/reviews
     */
    @GetMapping
    public ResponseEntity<?> listAll(
            @RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin privileges required"));
        }
        List<Review> reviews = reviewService.getAllReviews();
        List<Map<String, Object>> out = reviews.stream().map(this::toMap).toList();
        return ResponseEntity.ok(out);
    }

    /**
     * List reviews for a specific restaurant.
     * GET /api/reviews/restaurant/{restaurantId}
     * Accessible by admin or by the owner of that restaurant.
     */
    @GetMapping("/restaurant/{restaurantId}")
    public ResponseEntity<?> listByRestaurant(
            @PathVariable Long restaurantId,
            @RequestHeader(value = "Authorization", required = false) String token) {
        // Allow admin or owner (frontend enforces owner-only-their-restaurant)
        if (token == null || (!authService.isAdmin(token) && !authService.isOwner(token))) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Insufficient privileges"));
        }
        List<Review> reviews = reviewService.getReviewsByRestaurant(restaurantId);
        List<Map<String, Object>> out = reviews.stream().map(this::toMap).toList();
        return ResponseEntity.ok(out);
    }

    /**
     * Create a review.
     * POST /api/reviews
     * Body: { restaurantId, rating, comment }
     * Requires a valid user token (USER role).
     */
    @PostMapping
    public ResponseEntity<?> create(
            @RequestHeader(value = "Authorization", required = false) String token,
            @RequestBody Map<String, Object> body) {
        if (token == null || token.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Authentication required"));
        }
        User user = authService.getUserByToken(token).orElse(null);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid token"));
        }
        // Only regular users may leave reviews
        if (user.getRole() != User.Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Only users may leave reviews"));
        }

        Long restaurantId;
        int rating;
        try {
            Object ridObj = body.get("restaurantId");
            Object ratingObj = body.get("rating");
            if (ridObj == null || ratingObj == null) {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "restaurantId and rating are required"));
            }
            restaurantId = Long.valueOf(ridObj.toString());
            rating = Integer.parseInt(ratingObj.toString());
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "restaurantId and rating must be valid numbers"));
        }
        String comment = body.containsKey("comment") ? String.valueOf(body.get("comment")) : null;

        try {
            Review review = reviewService.createReview(user.getId(), restaurantId, rating, comment);
            return ResponseEntity.status(HttpStatus.CREATED).body(toMap(review));
        } catch (IllegalArgumentException e) {
            Map<String, String> err = new HashMap<>();
            err.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(err);
        }
    }

    private Map<String, Object> toMap(Review r) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", r.getId());
        m.put("userId", r.getUser() != null ? r.getUser().getId() : null);
        m.put("username", r.getUser() != null ? r.getUser().getUsername() : null);
        m.put("restaurantId", r.getRestaurant() != null ? r.getRestaurant().getId() : null);
        m.put("rating", r.getRating());
        m.put("comment", r.getComment());
        m.put("timestamp", r.getTimestamp() != null ? r.getTimestamp().toString() : null);
        return m;
    }
}
