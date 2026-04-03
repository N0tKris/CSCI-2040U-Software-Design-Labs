package com.lab2.backend.controller;

import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.dto.ReviewDto;
import com.lab2.backend.repository.UserRepository;
import org.springframework.http.MediaType;
import java.util.stream.Collectors;
import com.lab2.backend.service.AuthService;
import com.lab2.backend.service.ReviewService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.nio.file.Paths;
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
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
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

        ParsedReviewInput parsed = parseReviewInput(body.get("restaurantId"), body.get("rating"), body.get("comment"));
        if (parsed.error != null) {
            return ResponseEntity.badRequest().body(Map.of("error", parsed.error));
        }

        try {
            Review review = reviewService.createReview(user.getId(), parsed.restaurantId, parsed.rating, parsed.comment);
            return ResponseEntity.status(HttpStatus.CREATED).body(ReviewDto.fromEntity(review));
        } catch (IllegalArgumentException e) {
            Map<String, String> err = new HashMap<>();
            err.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(err);
        }
    }

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> createMultipart(
            @RequestHeader(value = "Authorization", required = false) String token,
            @RequestParam("restaurantId") String restaurantId,
            @RequestParam("rating") String rating,
            @RequestParam(value = "comment", required = false) String comment,
            @RequestParam(value = "images", required = false) List<MultipartFile> images) {
        if (token == null || token.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Authentication required"));
        }
        User user = authService.getUserByToken(token).orElse(null);
        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Invalid token"));
        }
        if (user.getRole() != User.Role.USER) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Only users may leave reviews"));
        }

        ParsedReviewInput parsed = parseReviewInput(restaurantId, rating, comment);
        if (parsed.error != null) {
            return ResponseEntity.badRequest().body(Map.of("error", parsed.error));
        }

        try {
            Path uploadRoot = Paths.get(System.getProperty("user.dir"), "uploads", "reviews");
            Review review = reviewService.createReview(
                    user.getId(),
                    parsed.restaurantId,
                    parsed.rating,
                    parsed.comment,
                    images,
                    uploadRoot
            );
            return ResponseEntity.status(HttpStatus.CREATED).body(ReviewDto.fromEntity(review));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
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
    @PostMapping(value = "/admin/user-view", consumes = MediaType.APPLICATION_JSON_VALUE)
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

        User actingUser = resolveActingUserForAdminView(adminUser);

        ParsedReviewInput parsed = parseReviewInput(body.get("restaurantId"), body.get("rating"), body.get("comment"));
        if (parsed.error != null) {
            return ResponseEntity.badRequest().body(Map.of("error", parsed.error));
        }

        try {
            Review review = reviewService.createReview(actingUser.getId(), parsed.restaurantId, parsed.rating, parsed.comment);
            Map<String, Object> out = new HashMap<>();
            out.put("review", ReviewDto.fromEntity(review));
            out.put("mode", "ADMIN_USER_VIEW");
            out.put("actingUser", actingUser.getUsername());
            out.put("actingRole", actingUser.getRole().name());
            out.put("impersonatedBy", adminUser.getUsername());
            return ResponseEntity.status(HttpStatus.CREATED).body(out);
        } catch (IllegalArgumentException e) {
            Map<String, String> err = new HashMap<>();
            err.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(err);
        }
    }

    @PostMapping(value = "/admin/user-view", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> createFromAdminUserViewMultipart(
            @RequestHeader(value = "Authorization", required = false) String token,
            @RequestParam("restaurantId") String restaurantId,
            @RequestParam("rating") String rating,
            @RequestParam(value = "comment", required = false) String comment,
            @RequestParam(value = "images", required = false) List<MultipartFile> images) {
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

        User actingUser = resolveActingUserForAdminView(adminUser);

        ParsedReviewInput parsed = parseReviewInput(restaurantId, rating, comment);
        if (parsed.error != null) {
            return ResponseEntity.badRequest().body(Map.of("error", parsed.error));
        }

        try {
            Path uploadRoot = Paths.get(System.getProperty("user.dir"), "uploads", "reviews");
            Review review = reviewService.createReview(
                    actingUser.getId(),
                    parsed.restaurantId,
                    parsed.rating,
                    parsed.comment,
                    images,
                    uploadRoot
            );

            Map<String, Object> out = new HashMap<>();
            out.put("review", ReviewDto.fromEntity(review));
            out.put("mode", "ADMIN_USER_VIEW");
            out.put("actingUser", actingUser.getUsername());
            out.put("actingRole", actingUser.getRole().name());
            out.put("impersonatedBy", adminUser.getUsername());
            return ResponseEntity.status(HttpStatus.CREATED).body(out);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    private User resolveActingUserForAdminView(User adminUser) {
        return userRepository.findFirstByRole(User.Role.USER).orElse(adminUser);
    }

    private ParsedReviewInput parseReviewInput(Object restaurantIdRaw, Object ratingRaw, Object commentRaw) {
        if (restaurantIdRaw == null || ratingRaw == null) {
            return ParsedReviewInput.error("restaurantId and rating are required");
        }

        try {
            Long restaurantId = Long.valueOf(restaurantIdRaw.toString());
            double rating = Double.parseDouble(ratingRaw.toString());
            String comment = commentRaw != null ? String.valueOf(commentRaw) : null;
            return ParsedReviewInput.ok(restaurantId, rating, comment);
        } catch (NumberFormatException e) {
            return ParsedReviewInput.error("restaurantId and rating must be valid numbers");
        }
    }

    private static class ParsedReviewInput {
        private final Long restaurantId;
        private final double rating;
        private final String comment;
        private final String error;

        private ParsedReviewInput(Long restaurantId, double rating, String comment, String error) {
            this.restaurantId = restaurantId;
            this.rating = rating;
            this.comment = comment;
            this.error = error;
        }

        private static ParsedReviewInput ok(Long restaurantId, double rating, String comment) {
            return new ParsedReviewInput(restaurantId, rating, comment, null);
        }

        private static ParsedReviewInput error(String error) {
            return new ParsedReviewInput(null, 0, null, error);
        }
    }

}
