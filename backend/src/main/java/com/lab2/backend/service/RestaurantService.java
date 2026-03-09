package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import org.springframework.stereotype.Service;

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
        // Clear all restaurants at startup so the admin dashboard shows an
        // empty list. This intentionally removes any demo data that may
        // have been present from previous runs.
        repository.deleteAll();
    }

    public List<Restaurant> getAllRestaurants() {
        return repository.findAll().stream().sorted((a, b) -> Long.compare(a.getId(), b.getId())).toList();
    }

    public Restaurant getRestaurantById(Long id) {
        return repository.findById(id).orElse(null);
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
    public Restaurant getRestaurantByOwner(Long ownerId) {
        return repository.findByOwnerId(ownerId).orElse(null);
    }

    /** Return true if the given owner already has a restaurant. */
    public boolean ownerHasRestaurant(Long ownerId) {
        return repository.existsByOwnerId(ownerId);
    }

    public Restaurant updateRestaurant(Long id, Restaurant updated) {
        return repository.findById(id).map(r -> {
            updated.setId(id);
            return repository.save(updated);
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
