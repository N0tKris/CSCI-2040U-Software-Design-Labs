package com.lab2.backend.controller;

import com.lab2.backend.dto.MenuItemDto;
import com.lab2.backend.model.MenuItem;
import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.MenuItemRepository;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

/**
 * REST controller for menu item endpoints.
 * Allows admins and restaurant owners to add menu items.
 */
@RestController
@RequestMapping("/api/restaurants/{restaurantId}/menu")
@CrossOrigin(origins = "*")
public class MenuItemController {

    private final RestaurantRepository restaurantRepository;
    private final MenuItemRepository menuItemRepository;
    private final AuthService authService;

    public MenuItemController(RestaurantRepository restaurantRepository,
                              MenuItemRepository menuItemRepository,
                              AuthService authService) {
        this.restaurantRepository = restaurantRepository;
        this.menuItemRepository = menuItemRepository;
        this.authService = authService;
    }

    /**
     * Add a menu item to a restaurant.
     * POST /api/restaurants/{restaurantId}/menu
     * <ul>
     *   <li>Admin can add items to any restaurant.</li>
     *   <li>Owner can add items only to their own restaurant.</li>
     * </ul>
     * Body: { itemName, price, description (optional) }
     */
    @PostMapping
    public ResponseEntity<?> addMenuItem(
            @RequestHeader(value = "Authorization", required = false) String token,
            @PathVariable Long restaurantId,
            @RequestBody Map<String, Object> body) {

        boolean isAdmin = authService.isAdmin(token);
        boolean isOwner = authService.isOwner(token);

        if (!isAdmin && !isOwner) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin or Owner privileges required"));
        }

        // Validate required fields
        Object itemNameObj = body.get("itemName");
        Object priceObj = body.get("price");
        if (itemNameObj == null || itemNameObj.toString().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "itemName is required"));
        }
        if (priceObj == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "price is required"));
        }

        String itemName = itemNameObj.toString().trim();
        BigDecimal price;
        try {
            price = new BigDecimal(priceObj.toString());
            if (price.compareTo(BigDecimal.ZERO) < 0) {
                return ResponseEntity.badRequest().body(Map.of("error", "price must be non-negative"));
            }
        } catch (NumberFormatException e) {
            return ResponseEntity.badRequest().body(Map.of("error", "price must be a valid number"));
        }

        String description = body.containsKey("description") && body.get("description") != null
                ? body.get("description").toString()
                : null;

        // Look up the restaurant
        Restaurant restaurant = restaurantRepository.findById(restaurantId).orElse(null);
        if (restaurant == null) {
            return ResponseEntity.notFound().build();
        }

        // Owner must own this restaurant
        if (isOwner && !isAdmin) {
            Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
            if (ownerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid token"));
            }
            if (!ownerId.equals(restaurant.getOwnerId())) {
                Map<String, String> err = new HashMap<>();
                err.put("error", "You can only add menu items to your own restaurant");
                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(err);
            }
        }

        MenuItem menuItem = new MenuItem(restaurant, itemName, price, description);
        MenuItem saved = menuItemRepository.save(menuItem);
        return ResponseEntity.status(HttpStatus.CREATED).body(MenuItemDto.fromEntity(saved));
    }
}
