package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.repository.ReviewRepository;
import com.lab2.backend.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ReviewService {

    private final ReviewRepository reviewRepository;
    private final RestaurantRepository restaurantRepository;
    private final UserRepository userRepository;

    public ReviewService(ReviewRepository reviewRepository,
                         RestaurantRepository restaurantRepository,
                         UserRepository userRepository) {
        this.reviewRepository = reviewRepository;
        this.restaurantRepository = restaurantRepository;
        this.userRepository = userRepository;
    }

    /** Return all reviews. */
    @Transactional(readOnly = true)
    public List<Review> getAllReviews() {
        List<Review> reviews = reviewRepository.findAll();
        for (Review r : reviews) {
            if (r.getUser() != null) r.getUser().getUsername();
            if (r.getRestaurant() != null) r.getRestaurant().getId();
        }
        return reviews;
    }

    /** Return all reviews for a given restaurant. */
    @Transactional(readOnly = true)
    public List<Review> getReviewsByRestaurant(Long restaurantId) {
        List<Review> reviews = reviewRepository.findByRestaurantId(restaurantId);
        for (Review r : reviews) {
            if (r.getUser() != null) r.getUser().getUsername();
            if (r.getRestaurant() != null) r.getRestaurant().getId();
        }
        return reviews;
    }

    /**
     * Create a review for a restaurant by a user.
     *
     * @throws IllegalArgumentException if user, restaurant, or rating is invalid
     */
    public Review createReview(Long userId, Long restaurantId, double rating, String comment) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        Restaurant restaurant = restaurantRepository.findById(restaurantId)
                .orElseThrow(() -> new IllegalArgumentException("Restaurant not found"));
        if (rating < 1 || rating > 5) {
            throw new IllegalArgumentException("Rating must be between 1 and 5");
        }
        // Only allow half-step increments: 1.0, 1.5, 2.0, ... 5.0
        if (Math.abs((rating * 2) - Math.round(rating * 2)) > 1e-9) {
            throw new IllegalArgumentException("Rating must be in 0.5 increments");
        }
        Review review = new Review(user, restaurant, rating, comment);
        return reviewRepository.save(review);
    }
}
