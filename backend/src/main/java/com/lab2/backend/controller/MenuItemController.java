package com.lab2.backend.controller;

import com.lab2.backend.dto.MenuItemDto;
import com.lab2.backend.model.MenuItem;
import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.MenuItemRepository;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

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

    /**
     * Update a menu item.
     * PUT /api/restaurants/{restaurantId}/menu/{menuItemId}
     */
    @PutMapping("/{menuItemId}")
    public ResponseEntity<?> updateMenuItem(
            @RequestHeader(value = "Authorization", required = false) String token,
            @PathVariable Long restaurantId,
            @PathVariable Long menuItemId,
            @RequestBody Map<String, Object> body) {

        boolean isAdmin = authService.isAdmin(token);
        boolean isOwner = authService.isOwner(token);

        if (!isAdmin && !isOwner) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin or Owner privileges required"));
        }

        MenuItem menuItem = menuItemRepository.findById(menuItemId).orElse(null);
        if (menuItem == null) {
            return ResponseEntity.notFound().build();
        }

        // Verify restaurant ownership
        if (menuItem.getRestaurant().getId().longValue() != restaurantId) {
            return ResponseEntity.badRequest().body(Map.of("error", "Menu item does not belong to this restaurant"));
        }

        // Owner authorization check
        if (isOwner && !isAdmin) {
            Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
            if (ownerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid token"));
            }
            if (!ownerId.equals(menuItem.getRestaurant().getOwnerId())) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("error", "You can only update menu items for your own restaurant"));
            }
        }

        // Update fields if provided
        if (body.containsKey("itemName") && body.get("itemName") != null) {
            String itemName = body.get("itemName").toString().trim();
            if (!itemName.isBlank()) {
                menuItem.setItemName(itemName);
            }
        }
        if (body.containsKey("price") && body.get("price") != null) {
            try {
                BigDecimal price = new BigDecimal(body.get("price").toString());
                if (price.compareTo(BigDecimal.ZERO) >= 0) {
                    menuItem.setPrice(price);
                }
            } catch (NumberFormatException e) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid price"));
            }
        }
        if (body.containsKey("description")) {
            menuItem.setDescription(body.get("description") != null ? body.get("description").toString() : null);
        }

        MenuItem updated = menuItemRepository.save(menuItem);
        return ResponseEntity.ok(MenuItemDto.fromEntity(updated));
    }

    /**
     * Upload an image for a menu item.
     * POST /api/restaurants/{restaurantId}/menu/{menuItemId}/upload-image
     */
    @PostMapping(value = "/{menuItemId}/upload-image", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> uploadMenuItemImage(
            @RequestHeader(value = "Authorization", required = false) String token,
            @PathVariable Long restaurantId,
            @PathVariable Long menuItemId,
            @RequestParam("file") MultipartFile file) {

        boolean isAdmin = authService.isAdmin(token);
        boolean isOwner = authService.isOwner(token);

        if (!isAdmin && !isOwner) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin or Owner privileges required"));
        }

        MenuItem menuItem = menuItemRepository.findById(menuItemId).orElse(null);
        if (menuItem == null) {
            return ResponseEntity.notFound().build();
        }

        if (menuItem.getRestaurant().getId().longValue() != restaurantId) {
            return ResponseEntity.badRequest().body(Map.of("error", "Menu item does not belong to this restaurant"));
        }

        // Owner authorization check
        if (isOwner && !isAdmin) {
            Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
            if (ownerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid token"));
            }
            if (!ownerId.equals(menuItem.getRestaurant().getOwnerId())) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("error", "You can only upload images for menu items in your own restaurant"));
            }
        }

        if (file == null || file.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "No file provided"));
        }

        Set<String> ALLOWED_IMAGE_TYPES = Set.of("image/jpeg", "image/png", "image/gif", "image/webp");
        final long MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 MB

        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_IMAGE_TYPES.contains(contentType.toLowerCase(Locale.ROOT))) {
            return ResponseEntity.badRequest().body(Map.of("error", "Invalid file type. Only JPG, PNG, GIF and WebP images are allowed."));
        }
        if (file.getSize() > MAX_IMAGE_SIZE) {
            return ResponseEntity.badRequest().body(Map.of("error", "File too large. Maximum size is 5 MB."));
        }

        try {
            Path uploadDir = Paths.get(System.getProperty("user.dir"), "uploads");
            Files.createDirectories(uploadDir);

            String originalFilename = file.getOriginalFilename();
            String extension = (originalFilename != null && originalFilename.contains("."))
                    ? originalFilename.substring(originalFilename.lastIndexOf('.'))
                    : ".jpg";
            if (!Set.of(".jpg", ".jpeg", ".png", ".gif", ".webp").contains(extension.toLowerCase(Locale.ROOT))) {
                extension = ".jpg";
            }
            String filename = "menu-item-" + menuItemId + "-" + System.currentTimeMillis() + extension;
            Path dest = uploadDir.resolve(filename);
            file.transferTo(dest);

            menuItem.setImageUrl("/uploads/" + filename);
            MenuItem updated = menuItemRepository.save(menuItem);
            return ResponseEntity.ok(MenuItemDto.fromEntity(updated));
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to upload image: " + e.getMessage()));
        }
    }

    /**
     * Delete a menu item.
     * DELETE /api/restaurants/{restaurantId}/menu/{menuItemId}
     */
    @DeleteMapping("/{menuItemId}")
    public ResponseEntity<?> deleteMenuItem(
            @RequestHeader(value = "Authorization", required = false) String token,
            @PathVariable Long restaurantId,
            @PathVariable Long menuItemId) {

        boolean isAdmin = authService.isAdmin(token);
        boolean isOwner = authService.isOwner(token);

        if (!isAdmin && !isOwner) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Admin or Owner privileges required"));
        }

        MenuItem menuItem = menuItemRepository.findById(menuItemId).orElse(null);
        if (menuItem == null) {
            return ResponseEntity.notFound().build();
        }

        if (menuItem.getRestaurant().getId().longValue() != restaurantId) {
            return ResponseEntity.badRequest().body(Map.of("error", "Menu item does not belong to this restaurant"));
        }

        // Owner authorization check
        if (isOwner && !isAdmin) {
            Long ownerId = authService.getUserByToken(token).map(u -> u.getId()).orElse(null);
            if (ownerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Invalid token"));
            }
            if (!ownerId.equals(menuItem.getRestaurant().getOwnerId())) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                        .body(Map.of("error", "You can only delete menu items from your own restaurant"));
            }
        }

        menuItemRepository.deleteById(menuItemId);
        return ResponseEntity.ok(Map.of("message", "Menu item deleted successfully"));
    }
}
