package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.repository.ReviewRepository;
import com.lab2.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

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
    public List<Review> getAllReviews() {
        return reviewRepository.findAll();
    }

    /** Return all reviews for a given restaurant. */
    public List<Review> getReviewsByRestaurant(Long restaurantId) {
        return reviewRepository.findByRestaurantId(restaurantId);
    }

    /**
     * Create a review for a restaurant by a user.
     *
     * @throws IllegalArgumentException if user, restaurant, or rating is invalid
     */
    public Review createReview(Long userId, Long restaurantId, int rating, String comment) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        Restaurant restaurant = restaurantRepository.findById(restaurantId)
                .orElseThrow(() -> new IllegalArgumentException("Restaurant not found"));
        if (rating < 1 || rating > 5) {
            throw new IllegalArgumentException("Rating must be between 1 and 5");
        }
        Review review = new Review(user, restaurant, rating, comment);
        return reviewRepository.save(review);
    }
}
