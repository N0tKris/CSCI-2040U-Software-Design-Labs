package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.annotation.PostConstruct;
import java.util.List;

@Service
public class RestaurantService {
    private final RestaurantRepository repository;

    public RestaurantService(RestaurantRepository repository) {
        this.repository = repository;
    }

    @PostConstruct
    public void seedIfEmpty() {
        // No-op: restaurant data is persisted in the database across restarts.
        // Do not delete existing restaurants on startup.
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
