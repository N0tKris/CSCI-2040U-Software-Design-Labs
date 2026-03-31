package com.lab2.backend.controller;

import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.dto.ReviewDto;
import com.lab2.backend.repository.UserRepository;
import java.util.stream.Collectors;
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
    private final UserRepository userRepository;

    public ReviewController(ReviewService reviewService, AuthService authService, UserRepository userRepository) {
        this.reviewService = reviewService;
        this.authService = authService;
        this.userRepository = userRepository;
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
        List<ReviewDto> out = reviews.stream().map(ReviewDto::fromEntity).collect(Collectors.toList());
        return ResponseEntity.ok(out);
    }

    /**
     * List reviews for a specific restaurant.
     * GET /api/reviews/restaurant/{restaurantId}
     * Public endpoint so guests and signed-in users can browse restaurant reviews.
     */
    @GetMapping("/restaurant/{restaurantId}")
    public ResponseEntity<?> listByRestaurant(
            @PathVariable Long restaurantId,
            @RequestHeader(value = "Authorization", required = false) String token) {
        List<Review> reviews = reviewService.getReviewsByRestaurant(restaurantId);
        List<ReviewDto> out = reviews.stream().map(ReviewDto::fromEntity).collect(Collectors.toList());
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
        double rating;
        try {
            Object ridObj = body.get("restaurantId");
            Object ratingObj = body.get("rating");
            if (ridObj == null || ratingObj == null) {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "restaurantId and rating are required"));
            }
            restaurantId = Long.valueOf(ridObj.toString());
            rating = Double.parseDouble(ratingObj.toString());
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "restaurantId and rating must be valid numbers"));
        }
        String comment = body.containsKey("comment") ? String.valueOf(body.get("comment")) : null;

        try {
            Review review = reviewService.createReview(user.getId(), restaurantId, rating, comment);
            return ResponseEntity.status(HttpStatus.CREATED).body(ReviewDto.fromEntity(review));
        } catch (IllegalArgumentException e) {
            Map<String, String> err = new HashMap<>();
            err.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(err);
        }
    }

    /**
     * Create a review from admin "view as user" mode.
     * POST /api/reviews/admin/user-view
     * Body: { restaurantId, rating, comment }
     *
     * This endpoint allows admins to simulate user review submission without
     * reusing an admin token as a normal USER token.
     */
    @PostMapping("/admin/user-view")
    public ResponseEntity<?> createFromAdminUserView(
            @RequestHeader(value = "Authorization", required = false) String token,
            @RequestBody Map<String, Object> body) {
        if (token == null || token.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Authentication required"));
        }

        User adminUser = authService.getUserByToken(token).orElse(null);
        if (adminUser == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid token"));
        }
        if (adminUser.getRole() != User.Role.ADMIN) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin privileges required"));
        }

        User actingUser = userRepository.findFirstByRole(User.Role.USER).orElse(null);
        if (actingUser == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("error", "No regular USER account exists for admin view-as-user mode"));
        }

        Long restaurantId;
        double rating;
        try {
            Object ridObj = body.get("restaurantId");
            Object ratingObj = body.get("rating");
            if (ridObj == null || ratingObj == null) {
                return ResponseEntity.badRequest()
                        .body(Map.of("error", "restaurantId and rating are required"));
            }
            restaurantId = Long.valueOf(ridObj.toString());
            rating = Double.parseDouble(ratingObj.toString());
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "restaurantId and rating must be valid numbers"));
        }
        String comment = body.containsKey("comment") ? String.valueOf(body.get("comment")) : null;

        try {
            Review review = reviewService.createReview(actingUser.getId(), restaurantId, rating, comment);
            Map<String, Object> out = new HashMap<>();
            out.put("review", ReviewDto.fromEntity(review));
            out.put("mode", "ADMIN_USER_VIEW");
            out.put("actingUser", actingUser.getUsername());
            out.put("impersonatedBy", adminUser.getUsername());
            return ResponseEntity.status(HttpStatus.CREATED).body(out);
        } catch (IllegalArgumentException e) {
            Map<String, String> err = new HashMap<>();
            err.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(err);
        }
    }

}
