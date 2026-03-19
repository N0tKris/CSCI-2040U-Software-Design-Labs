package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.repository.ReviewRepository;
import com.lab2.backend.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ReviewServiceTest {

    @Mock
    private ReviewRepository reviewRepository;

    @Mock
    private RestaurantRepository restaurantRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private ReviewService reviewService;

    private User testUser;
    private Restaurant testRestaurant;
    private Review testReview;

    @BeforeEach
    void setUp() {
        testUser = new User();
        testUser.setId(1L);
        testUser.setUsername("testuser");

        testRestaurant = new Restaurant();
        testRestaurant.setId(1L);
        testRestaurant.setName("Test Restaurant");

        testReview = new Review();
        testReview.setId(1L);
        testReview.setUser(testUser);
        testReview.setRestaurant(testRestaurant);
        testReview.setRating(4.5);
        testReview.setComment("Great food!");
    }

    // ============ getAllReviews() Tests ============

    @Test
    void testGetAllReviewsSuccess() {
        // Arrange
        List<Review> reviews = new ArrayList<>();
        reviews.add(testReview);
        Review review2 = new Review();
        review2.setId(2L);
        reviews.add(review2);
        when(reviewRepository.findAll()).thenReturn(reviews);

        // Act
        List<Review> result = reviewService.getAllReviews();

        // Assert
        assertEquals(2, result.size());
        verify(reviewRepository, times(1)).findAll();
    }

    @Test
    void testGetAllReviewsEmpty() {
        // Arrange
        when(reviewRepository.findAll()).thenReturn(new ArrayList<>());

        // Act
        List<Review> result = reviewService.getAllReviews();

        // Assert
        assertTrue(result.isEmpty());
        verify(reviewRepository, times(1)).findAll();
    }

    @Test
    void testGetAllReviewsInitializesLazyCollections() {
        // Arrange
        testReview.setUser(testUser);
        testReview.setRestaurant(testRestaurant);
        List<Review> reviews = new ArrayList<>();
        reviews.add(testReview);
        when(reviewRepository.findAll()).thenReturn(reviews);

        // Act
        List<Review> result = reviewService.getAllReviews();

        // Assert
        assertNotNull(result.get(0).getUser());
        assertNotNull(result.get(0).getRestaurant());
        verify(reviewRepository, times(1)).findAll();
    }

    // ============ getReviewsByRestaurant() Tests ============

    @Test
    void testGetReviewsByRestaurantSuccess() {
        // Arrange
        Long restaurantId = 1L;
        List<Review> reviews = new ArrayList<>();
        reviews.add(testReview);
        when(reviewRepository.findByRestaurantId(restaurantId)).thenReturn(reviews);

        // Act
        List<Review> result = reviewService.getReviewsByRestaurant(restaurantId);

        // Assert
        assertEquals(1, result.size());
        assertEquals(testReview.getId(), result.get(0).getId());
        verify(reviewRepository, times(1)).findByRestaurantId(restaurantId);
    }

    @Test
    void testGetReviewsByRestaurantEmpty() {
        // Arrange
        Long restaurantId = 99L;
        when(reviewRepository.findByRestaurantId(restaurantId)).thenReturn(new ArrayList<>());

        // Act
        List<Review> result = reviewService.getReviewsByRestaurant(restaurantId);

        // Assert
        assertTrue(result.isEmpty());
        verify(reviewRepository, times(1)).findByRestaurantId(restaurantId);
    }

    @Test
    void testGetReviewsByRestaurantMultipleReviews() {
        // Arrange
        Long restaurantId = 1L;
        Review review2 = new Review();
        review2.setId(2L);
        review2.setRestaurant(testRestaurant);
        review2.setUser(testUser);
        List<Review> reviews = new ArrayList<>();
        reviews.add(testReview);
        reviews.add(review2);
        when(reviewRepository.findByRestaurantId(restaurantId)).thenReturn(reviews);

        // Act
        List<Review> result = reviewService.getReviewsByRestaurant(restaurantId);

        // Assert
        assertEquals(2, result.size());
        verify(reviewRepository, times(1)).findByRestaurantId(restaurantId);
    }

    // ============ createReview() Tests - Success Cases ============

    @Test
    void testCreateReviewSuccess() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        double rating = 4.5;
        String comment = "Excellent service!";

        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(reviewRepository.save(any(Review.class))).thenReturn(testReview);

        // Act
        Review result = reviewService.createReview(userId, restaurantId, rating, comment);

        // Assert
        assertNotNull(result);
        assertEquals(testUser.getId(), result.getUser().getId());
        assertEquals(testRestaurant.getId(), result.getRestaurant().getId());
        verify(userRepository, times(1)).findById(userId);
        verify(restaurantRepository, times(1)).findById(restaurantId);
        verify(reviewRepository, times(1)).save(any(Review.class));
    }

    @Test
    void testCreateReviewWithMinimumRating() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        double rating = 1.0;

        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(reviewRepository.save(any(Review.class))).thenReturn(testReview);

        // Act
        Review result = reviewService.createReview(userId, restaurantId, rating, "Bad");

        // Assert
        assertNotNull(result);
        verify(reviewRepository, times(1)).save(any(Review.class));
    }

    @Test
    void testCreateReviewWithMaximumRating() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        double rating = 5.0;

        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(reviewRepository.save(any(Review.class))).thenReturn(testReview);

        // Act
        Review result = reviewService.createReview(userId, restaurantId, rating, "Excellent");

        // Assert
        assertNotNull(result);
        verify(reviewRepository, times(1)).save(any(Review.class));
    }

    @Test
    void testCreateReviewWithHalfIncrementRating() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        double rating = 3.5;

        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(reviewRepository.save(any(Review.class))).thenReturn(testReview);

        // Act
        Review result = reviewService.createReview(userId, restaurantId, rating, "Good");

        // Assert
        assertNotNull(result);
        verify(reviewRepository, times(1)).save(any(Review.class));
    }

    // ============ createReview() Tests - User Not Found ============

    @Test
    void testCreateReviewUserNotFound() {
        // Arrange
        Long userId = 99L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 4.0, "comment")
        );
        assertEquals("User not found", exception.getMessage());
        verify(userRepository, times(1)).findById(userId);
        verify(restaurantRepository, times(0)).findById(anyLong());
    }

    // ============ createReview() Tests - Restaurant Not Found ============

    @Test
    void testCreateReviewRestaurantNotFound() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 99L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.empty());

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 4.0, "comment")
        );
        assertEquals("Restaurant not found", exception.getMessage());
        verify(userRepository, times(1)).findById(userId);
        verify(restaurantRepository, times(1)).findById(restaurantId);
    }

    // ============ createReview() Tests - Invalid Rating (Out of Range) ============

    @Test
    void testCreateReviewRatingTooLow() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 0.5, "comment")
        );
        assertEquals("Rating must be between 1 and 5", exception.getMessage());
    }

    @Test
    void testCreateReviewRatingTooHigh() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 5.5, "comment")
        );
        assertEquals("Rating must be between 1 and 5", exception.getMessage());
    }

    @Test
    void testCreateReviewRatingZero() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 0.0, "comment")
        );
        assertEquals("Rating must be between 1 and 5", exception.getMessage());
    }

    // ============ createReview() Tests - Invalid Rating (Not 0.5 Increments) ============

    @Test
    void testCreateReviewRatingNotHalfIncrement() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 3.3, "comment")
        );
        assertEquals("Rating must be in 0.5 increments", exception.getMessage());
    }

    @Test
    void testCreateReviewRatingWithDecimal() {
        // Arrange
        Long userId = 1L;
        Long restaurantId = 1L;
        when(userRepository.findById(userId)).thenReturn(Optional.of(testUser));
        when(restaurantRepository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                reviewService.createReview(userId, restaurantId, 2.7, "comment")
        );
        assertEquals("Rating must be in 0.5 increments", exception.getMessage());
    }
}
