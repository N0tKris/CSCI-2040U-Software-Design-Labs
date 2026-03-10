package com.lab2.backend.controller;

import com.lab2.backend.service.YelpService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Admin endpoint for importing restaurants from the Yelp Fusion API.
 */
@RestController
@RequestMapping("/api/admin")
public class YelpController {

    private final YelpService yelpService;

    public YelpController(YelpService yelpService) {
        this.yelpService = yelpService;
    }

    /**
     * POST /api/admin/import-yelp-restaurants
     *
     * Optional query params:
     *   location  – search location (default: Toronto)
     *   limit     – max results 1-50  (default: 20)
     */
    @PostMapping("/import-yelp-restaurants")
    public ResponseEntity<?> importYelpRestaurants(
            @RequestParam(defaultValue = "Toronto") String location,
            @RequestParam(defaultValue = "20") int limit) {
        try {
            int imported = yelpService.importRestaurants(location, limit);
            return ResponseEntity.ok(Map.of(
                    "ok", true,
                    "imported", imported,
                    "message", imported + " restaurant(s) imported from Yelp"
            ));
        } catch (IllegalStateException e) {
            // missing API key
            return ResponseEntity.badRequest().body(Map.of(
                    "ok", false,
                    "error", e.getMessage()
            ));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "ok", false,
                    "error", "Yelp import failed: " + e.getMessage()
            ));
        }
    }
}
