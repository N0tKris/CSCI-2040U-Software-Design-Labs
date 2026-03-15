package com.lab2.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.annotation.PostConstruct;
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Service
public class RestaurantService {
    private final RestaurantRepository repository;

    public RestaurantService(RestaurantRepository repository) {
        this.repository = repository;
    }

    @PostConstruct
    public void seedIfEmpty() {
        if (repository.count() > 0) {
            System.out.println("Restaurants already exist — skipping seed");
            return;
        }

        Path[] candidates = {
                Path.of("../restaurants_only.json"), // when running from backend/
                Path.of("restaurants_only.json")     // fallback
        };

        Path jsonPath = null;
        for (Path candidate : candidates) {
            if (Files.exists(candidate)) {
                jsonPath = candidate;
                break;
            }
        }

        if (jsonPath == null) {
            System.out.println("restaurants_only.json not found — skipping restaurant seed");
            return;
        }

        ObjectMapper mapper = new ObjectMapper();
        int inserted = 0;
        final int MAX_SEED = 300;

        try (BufferedReader reader = Files.newBufferedReader(jsonPath)) {
            String line;

            while ((line = reader.readLine()) != null) {
                if (inserted >= MAX_SEED) break;
                if (line.trim().isEmpty()) continue;

                JsonNode node = mapper.readTree(line);

                String name = text(node, "name");
                String categories = text(node, "categories");
                String address = text(node, "address");
                String city = text(node, "city");
                String state = text(node, "state");
                String postalCode = text(node, "postal_code");

                if (name == null || name.isBlank() || categories == null || categories.isBlank()) {
                    continue;
                }

                String cuisine = firstCategory(categories);
                String location = buildLocation(address, city, state, postalCode);

                if (location.isBlank()) {
                    continue;
                }

                if (repository.existsByNameAndLocation(name, location)) {
                    continue;
                }

                Restaurant r = new Restaurant();
                r.setName(name);
                r.setCuisine(cuisine);
                r.setLocation(location);
                r.setDescription("Imported from restaurants_only.json");
                r.setDietaryTags("");

                repository.save(r);
                inserted++;
            }

            System.out.println("Seeded " + inserted + " restaurants from " + jsonPath);
        } catch (IOException e) {
            System.out.println("Failed to seed restaurants: " + e.getMessage());
        }
    }

    private String text(JsonNode node, String fieldName) {
        JsonNode value = node.get(fieldName);
        if (value == null || value.isNull()) return "";
        return value.asText("").trim();
    }

    private String firstCategory(String categories) {
        if (categories == null || categories.isBlank()) {
            return "Restaurant";
        }

        String[] parts = categories.split(",");
        for (String part : parts) {
            String trimmed = part.trim();
            if (!trimmed.isEmpty() && !trimmed.equalsIgnoreCase("Restaurants") && !trimmed.equalsIgnoreCase("Food")) {
                return trimmed;
            }
        }

        return parts[0].trim().isEmpty() ? "Restaurant" : parts[0].trim();
    }

    private String buildLocation(String address, String city, String state, String postalCode) {
        StringBuilder sb = new StringBuilder();

        if (address != null && !address.isBlank()) sb.append(address.trim());
        if (city != null && !city.isBlank()) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(city.trim());
        }
        if (state != null && !state.isBlank()) {
            if (sb.length() > 0) sb.append(", ");
            sb.append(state.trim());
        }
        if (postalCode != null && !postalCode.isBlank()) {
            if (sb.length() > 0) sb.append(" ");
            sb.append(postalCode.trim());
        }

        return sb.toString().trim();
    }

    @Transactional(readOnly = true)
    public List<Restaurant> getAllRestaurants() {
        List<Restaurant> restaurants = repository.findAll();
        // Force initialization of lazy collections so DTOs can be built outside the session
        for (Restaurant r : restaurants) {
            r.getMenuItems().size();
            r.getReviews().size();
        }
        return restaurants.stream().sorted((a, b) -> Long.compare(a.getId(), b.getId())).toList();
    }

    @Transactional(readOnly = true)
    public Restaurant getRestaurantById(Long id) {
        Restaurant r = repository.findById(id).orElse(null);
        if (r != null) {
            r.getMenuItems().size();
            r.getReviews().size();
        }
        return r;
    }

    public Restaurant addRestaurant(Restaurant restaurant) {
        restaurant.setId(null);
        return repository.save(restaurant);
    }

    /**
     * Add a restaurant on behalf of an owner. Ensures the owner does not
     * already have a restaurant before creating a new one.
     *
     * @throws IllegalStateException if the owner already has a restaurant
     */
    public Restaurant addRestaurantByOwner(Long ownerId, Restaurant restaurant) {
        if (repository.existsByOwnerId(ownerId)) {
            throw new IllegalStateException("Owner already has a restaurant");
        }
        restaurant.setId(null);
        restaurant.setOwnerId(ownerId);
        return repository.save(restaurant);
    }

    /** Return the restaurant owned by the given user, or null if none. */
    @Transactional(readOnly = true)
    public Restaurant getRestaurantByOwner(Long ownerId) {
        Restaurant r = repository.findByOwnerId(ownerId).orElse(null);
        if (r != null) {
            r.getMenuItems().size();
            r.getReviews().size();
        }
        return r;
    }

    /** Return true if the given owner already has a restaurant. */
    public boolean ownerHasRestaurant(Long ownerId) {
        return repository.existsByOwnerId(ownerId);
    }

    @Transactional
    public Restaurant updateRestaurant(Long id, Restaurant updated) {
        return repository.findById(id).map(r -> {
            r.setName(updated.getName());
            r.setCuisine(updated.getCuisine());
            r.setLocation(updated.getLocation());
            r.setDescription(updated.getDescription());
            r.setDietaryTags(updated.getDietaryTags());
            if (updated.getOwnerId() != null) {
                r.setOwnerId(updated.getOwnerId());
            }
            return repository.save(r);
        }).orElse(null);
    }

    public boolean deleteRestaurant(Long id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
            return true;
        }
        return false;
    }

    /** Delete all restaurants (admin action). */
    public void deleteAll() {
        repository.deleteAll();
    }

    public boolean validateRestaurant(Restaurant r) {
        return r != null
                && hasText(r.getName())
                && hasText(r.getCuisine())
                && hasText(r.getLocation());
    }

    private boolean hasText(String value) {
        return value != null && !value.trim().isEmpty();
    }
}
