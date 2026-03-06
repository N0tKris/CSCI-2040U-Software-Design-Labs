package com.lab2.backend.controller;

import com.lab2.backend.model.Restaurant;
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
    public ResponseEntity<List<Restaurant>> getAllRestaurants() {
        return ResponseEntity.ok(restaurantService.getAllRestaurants());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Restaurant> getById(@PathVariable Long id) {
        Restaurant restaurant = restaurantService.getRestaurantById(id);
        if (restaurant == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(restaurant);
    }

    @PostMapping
    public ResponseEntity<?> create(@RequestHeader(value = "Authorization", required = false) String token,
                                    @RequestBody Restaurant restaurant) {
        // Only admin may create restaurants
        if (!authService.isAdmin(token)) {
            Map<String, String> err = new HashMap<>();
            err.put("error", "Admin privileges required");
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body(err);
        }

        if (!restaurantService.validateRestaurant(restaurant)) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "name, cuisine and location are required");
            return ResponseEntity.badRequest().body(error);
        }
        Restaurant created = restaurantService.addRestaurant(restaurant);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> update(@PathVariable Long id, @RequestBody Restaurant restaurant) {
        if (!restaurantService.validateRestaurant(restaurant)) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "name, cuisine and location are required");
            return ResponseEntity.badRequest().body(error);
        }
        Restaurant updated = restaurantService.updateRestaurant(id, restaurant);
        if (updated == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(updated);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable Long id) {
        boolean deleted = restaurantService.deleteRestaurant(id);
        if (!deleted) {
            return ResponseEntity.notFound().build();
        }
        Map<String, String> response = new HashMap<>();
        response.put("message", "Restaurant deleted successfully");
        return ResponseEntity.ok(response);
    }
}
