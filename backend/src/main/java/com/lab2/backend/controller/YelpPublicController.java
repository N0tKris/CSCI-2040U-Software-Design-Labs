package com.lab2.backend.controller;

import com.lab2.backend.service.YelpService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * Public endpoints for retrieving Yelp data associated with local restaurants.
 */
@RestController
@RequestMapping("/api/yelp")
@CrossOrigin(origins = "*")
public class YelpPublicController {

    private final YelpService yelpService;

    public YelpPublicController(YelpService yelpService) {
        this.yelpService = yelpService;
    }

    /**
     * GET /api/yelp/reviews/restaurant/{restaurantId}
     *
     * Fetch Yelp review text for a restaurant that has a Yelp URL.
     */
    @GetMapping("/reviews/restaurant/{restaurantId}")
    public ResponseEntity<?> getYelpReviewsForRestaurant(@PathVariable Long restaurantId) {
        try {
            List<Map<String, Object>> reviews = yelpService.getReviewsForRestaurant(restaurantId);
            return ResponseEntity.ok(reviews);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", "Failed to fetch Yelp reviews: " + e.getMessage()));
        }
    }

    /**
     * Temporary debug endpoint for validating Yelp reviews by explicit Yelp business ID.
     * GET /api/yelp/debug/yelp-reviews/{id}
     */
    @GetMapping("/debug/yelp-reviews/{id}")
    public Object debugReviews(@PathVariable String id) {
        return yelpService.getReviews(id);
    }
}
