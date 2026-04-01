package com.lab2.backend.controller;

import com.lab2.backend.dto.ReviewDto;
import com.lab2.backend.model.Review;
import com.lab2.backend.service.AuthService;
import com.lab2.backend.service.ReviewService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Admin-only REST controller for review moderation.
 * Provides endpoints to list pending reviews and approve/reject them.
 */
@RestController
@RequestMapping("/api/admin/reviews")
@CrossOrigin(origins = "*")
public class AdminReviewController {

    private final ReviewService reviewService;
    private final AuthService authService;

    public AdminReviewController(ReviewService reviewService, AuthService authService) {
        this.reviewService = reviewService;
        this.authService = authService;
    }

    /**
     * List all pending reviews. Admin-only.
     * GET /api/admin/reviews/pending
     */
    @GetMapping("/pending")
    public ResponseEntity<?> listPending(
            @RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin privileges required"));
        }
        List<Review> reviews = reviewService.getPendingReviews();
        List<ReviewDto> out = reviews.stream().map(ReviewDto::fromEntity).collect(Collectors.toList());
        return ResponseEntity.ok(out);
    }

    /**
     * Approve a pending review (set status to PUBLISHED). Admin-only.
     * PUT /api/admin/reviews/{id}/approve
     */
    @PutMapping("/{id}/approve")
    public ResponseEntity<?> approve(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin privileges required"));
        }
        try {
            Review review = reviewService.approveReview(id);
            return ResponseEntity.ok(ReviewDto.fromEntity(review));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Reject a pending review (set status to REJECTED). Admin-only.
     * PUT /api/admin/reviews/{id}/reject
     */
    @PutMapping("/{id}/reject")
    public ResponseEntity<?> reject(
            @PathVariable Long id,
            @RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin privileges required"));
        }
        try {
            Review review = reviewService.rejectReview(id);
            return ResponseEntity.ok(ReviewDto.fromEntity(review));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
