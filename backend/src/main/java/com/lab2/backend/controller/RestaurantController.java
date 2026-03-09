package com.lab2.backend.controller;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.dto.RestaurantDto;
import java.util.stream.Collectors;
import com.lab2.backend.service.AuthService;
import com.lab2.backend.service.RestaurantService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/restaurants")
@CrossOrigin(origins = "*")
public class RestaurantController {

    private final RestaurantService restaurantService;
    private final AuthService authService;

    public RestaurantController(RestaurantService restaurantService, AuthService authService) {
        this.restaurantService = restaurantService;
        this.authService = authService;
    }

    @GetMapping
    public ResponseEntity<List<RestaurantDto>> getAllRestaurants() {
        List<RestaurantDto> out = restaurantService.getAllRestaurants()
                .stream().map(RestaurantDto::fromEntity).collect(Collectors.toList());
        return ResponseEntity.ok(out);
    }

    @GetMapping("/my")
    public ResponseEntity<?> getMyRestaurant(@RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isOwner(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Owner privileges required"));
        }
        Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
        if (ownerId == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid token"));
        }
        Restaurant restaurant = restaurantService.getRestaurantByOwner(ownerId);
        if (restaurant == null) {
            return ResponseEntity.ok(Map.of("restaurant", (Object) null, "hasRestaurant", false));
        }
        return ResponseEntity.ok(Map.of("restaurant", RestaurantDto.fromEntity(restaurant), "hasRestaurant", true));
    }

    @GetMapping("/{id}")
    public ResponseEntity<RestaurantDto> getById(@PathVariable Long id) {
        Restaurant restaurant = restaurantService.getRestaurantById(id);
        if (restaurant == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(RestaurantDto.fromEntity(restaurant));
    }

    @PostMapping
    public ResponseEntity<?> create(@RequestHeader(value = "Authorization", required = false) String token,
                                    @RequestBody Restaurant restaurant) {
        // Admin may always create restaurants
        if (authService.isAdmin(token)) {
            if (!restaurantService.validateRestaurant(restaurant)) {
                Map<String, String> error = new HashMap<>();
                error.put("error", "name, cuisine and location are required");
                return ResponseEntity.badRequest().body(error);
            }
            Restaurant created = restaurantService.addRestaurant(restaurant);
            return ResponseEntity.status(HttpStatus.CREATED).body(RestaurantDto.fromEntity(created));
        }

        // Owner may create exactly one restaurant linked to their account
        if (authService.isOwner(token)) {
            if (!restaurantService.validateRestaurant(restaurant)) {
                Map<String, String> error = new HashMap<>();
                error.put("error", "name, cuisine and location are required");
                return ResponseEntity.badRequest().body(error);
            }
            Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
            if (ownerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Invalid token"));
            }
            try {
                Restaurant created = restaurantService.addRestaurantByOwner(ownerId, restaurant);
                return ResponseEntity.status(HttpStatus.CREATED).body(RestaurantDto.fromEntity(created));
            } catch (IllegalStateException e) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
            }
        }

        Map<String, String> err = new HashMap<>();
        err.put("error", "Admin or Owner privileges required");
        return ResponseEntity.status(HttpStatus.FORBIDDEN).body(err);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> update(@RequestHeader(value = "Authorization", required = false) String token,
                                    @PathVariable Long id, @RequestBody Restaurant restaurant) {
        // Only admin may update restaurants
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Admin privileges required"));
        }

        if (!restaurantService.validateRestaurant(restaurant)) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "name, cuisine and location are required");
            return ResponseEntity.badRequest().body(error);
        }
        Restaurant updated = restaurantService.updateRestaurant(id, restaurant);
        if (updated == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(RestaurantDto.fromEntity(updated));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@RequestHeader(value = "Authorization", required = false) String token,
                                    @PathVariable Long id) {
        // Only admin may delete restaurants
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Admin privileges required"));
        }

        boolean deleted = restaurantService.deleteRestaurant(id);
        if (!deleted) {
            return ResponseEntity.notFound().build();
        }
        Map<String, String> response = new HashMap<>();
        response.put("message", "Restaurant deleted successfully");
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/all")
    public ResponseEntity<?> deleteAll(@RequestHeader(value = "Authorization", required = false) String token) {
        if (!authService.isAdmin(token)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(Map.of("error", "Admin privileges required"));
        }
        try {
            restaurantService.deleteAll();
            return ResponseEntity.ok(Map.of("message", "All restaurants deleted"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", "Failed to delete restaurants"));
        }
    }
}
