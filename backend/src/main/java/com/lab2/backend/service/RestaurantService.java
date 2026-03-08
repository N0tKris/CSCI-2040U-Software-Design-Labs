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
