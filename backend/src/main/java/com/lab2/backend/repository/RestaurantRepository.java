package com.lab2.backend.repository;

import com.lab2.backend.model.Restaurant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface RestaurantRepository extends JpaRepository<Restaurant, Long> {

    /** Find a restaurant owned by the given user ID. */
    Optional<Restaurant> findByOwnerId(Long ownerId);

    /** Check whether a restaurant owned by the given user ID exists. */
    boolean existsByOwnerId(Long ownerId);

    /** Used by Yelp import to prevent duplicate entries. */
    boolean existsByNameAndLocation(String name, String location);

    /** Used by Yelp import to refresh an existing restaurant entry when syncing data. */
    Optional<Restaurant> findByNameAndLocation(String name, String location);

    /** Stable key for Yelp-imported restaurants. */
    Optional<Restaurant> findByYelpId(String yelpId);
}
