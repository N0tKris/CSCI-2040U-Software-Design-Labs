package com.lab2.backend.repository;

import com.lab2.backend.model.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    /** Find all reviews for a given restaurant. */
    List<Review> findByRestaurantId(Long restaurantId);

    /** Find reviews by moderation status. */
    List<Review> findByStatus(String status);

    /** Find reviews for a given restaurant with a specific status. */
    List<Review> findByRestaurantIdAndStatus(Long restaurantId, String status);
}
