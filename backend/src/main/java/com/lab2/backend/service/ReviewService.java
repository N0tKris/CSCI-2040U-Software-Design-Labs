package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.model.Review;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.repository.ReviewRepository;
import com.lab2.backend.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;

@Service
public class ReviewService {

    private static final int MAX_REVIEW_IMAGES = 3;
    private static final long MAX_IMAGE_SIZE = 5L * 1024L * 1024L;
    private static final Set<String> ALLOWED_IMAGE_TYPES = Set.of(
            "image/jpeg", "image/jpg", "image/png", "image/webp"
    );

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

    /** Return all reviews with PENDING status. */
    @Transactional(readOnly = true)
    public List<Review> getPendingReviews() {
        List<Review> reviews = reviewRepository.findByStatus(Review.STATUS_PENDING);
        for (Review r : reviews) {
            if (r.getUser() != null) r.getUser().getUsername();
            if (r.getRestaurant() != null) r.getRestaurant().getId();
        }
        return reviews;
    }

    /** Return only PUBLISHED reviews for a given restaurant. */
    @Transactional(readOnly = true)
    public List<Review> getReviewsByRestaurant(Long restaurantId) {
        List<Review> reviews = reviewRepository.findByRestaurantIdAndStatus(restaurantId, Review.STATUS_PUBLISHED);
        for (Review r : reviews) {
            if (r.getUser() != null) r.getUser().getUsername();
            if (r.getRestaurant() != null) r.getRestaurant().getId();
        }
        return reviews;
    }

    /**
     * Approve a pending review (set status to PUBLISHED).
     *
     * @throws IllegalArgumentException if review not found or already processed
     */
    @Transactional
    public Review approveReview(Long reviewId) {
        Review review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new IllegalArgumentException("Review not found"));
        if (!Review.STATUS_PENDING.equals(review.getStatus())) {
            throw new IllegalArgumentException(
                    "Review cannot be approved because its current status is " + review.getStatus() + ", expected PENDING");
        }
        review.setStatus(Review.STATUS_PUBLISHED);
        return reviewRepository.save(review);
    }

    /**
     * Reject a pending review (set status to REJECTED).
     *
     * @throws IllegalArgumentException if review not found or already processed
     */
    @Transactional
    public Review rejectReview(Long reviewId) {
        Review review = reviewRepository.findById(reviewId)
                .orElseThrow(() -> new IllegalArgumentException("Review not found"));
        if (!Review.STATUS_PENDING.equals(review.getStatus())) {
            throw new IllegalArgumentException(
                    "Review cannot be rejected because its current status is " + review.getStatus() + ", expected PENDING");
        }
        review.setStatus(Review.STATUS_REJECTED);
        return reviewRepository.save(review);
    }

    /**
     * Create a review for a restaurant by a user.
     *
     * @throws IllegalArgumentException if user, restaurant, or rating is invalid
     */
    public Review createReview(Long userId, Long restaurantId, double rating, String comment) {
        return createReview(userId, restaurantId, rating, comment, null, null);
    }

    /**
     * Create a review for a restaurant and optionally persist up to 3 uploaded images.
     */
    @Transactional
    public Review createReview(Long userId,
                               Long restaurantId,
                               double rating,
                               String comment,
                               List<MultipartFile> images,
                               Path reviewUploadsRoot) {
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

        List<MultipartFile> sanitizedImages = images == null
                ? List.of()
                : images.stream().filter(f -> f != null && !f.isEmpty()).toList();

        if (sanitizedImages.size() > MAX_REVIEW_IMAGES) {
            throw new IllegalArgumentException("A maximum of 3 images is allowed per review");
        }

        for (MultipartFile file : sanitizedImages) {
            String contentType = file.getContentType() == null
                    ? ""
                    : file.getContentType().toLowerCase(Locale.ROOT);
            if (!ALLOWED_IMAGE_TYPES.contains(contentType)) {
                throw new IllegalArgumentException("Only JPG, JPEG, PNG, and WEBP images are allowed");
            }
            if (file.getSize() > MAX_IMAGE_SIZE) {
                throw new IllegalArgumentException("Each image must be 5MB or smaller");
            }
        }

        Review review = new Review(user, restaurant, rating, comment);
        Review saved = reviewRepository.save(review);

        if (!sanitizedImages.isEmpty()) {
            if (reviewUploadsRoot == null) {
                throw new IllegalArgumentException("Upload path is not configured");
            }

            List<String> urls = storeReviewImages(saved.getId(), sanitizedImages, reviewUploadsRoot);
            saved.setImageUrls(urls);
            saved = reviewRepository.save(saved);
        }

        return saved;
    }

    private List<String> storeReviewImages(Long reviewId,
                                           List<MultipartFile> images,
                                           Path reviewUploadsRoot) {
        Path reviewDir = reviewUploadsRoot.resolve(String.valueOf(reviewId));
        try {
            Files.createDirectories(reviewDir);
        } catch (IOException e) {
            throw new IllegalArgumentException("Failed to prepare review image directory");
        }

        List<String> urls = new ArrayList<>();
        for (int index = 0; index < images.size(); index++) {
            MultipartFile file = images.get(index);
            String ext = inferExtension(file.getContentType(), file.getOriginalFilename());
            String fileName = "img-" + (index + 1) + "-" + System.currentTimeMillis() + ext;
            Path target = reviewDir.resolve(fileName);
            try {
                Files.copy(file.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException e) {
                throw new IllegalArgumentException("Failed to store review image");
            }
            urls.add("/uploads/reviews/" + reviewId + "/" + fileName);
        }

        return urls;
    }

    private String inferExtension(String contentType, String originalName) {
        if (contentType != null) {
            String lowerType = contentType.toLowerCase(Locale.ROOT);
            if ("image/png".equals(lowerType)) return ".png";
            if ("image/webp".equals(lowerType)) return ".webp";
            return ".jpg";
        }
        if (originalName != null) {
            String lower = originalName.toLowerCase(Locale.ROOT);
            if (lower.endsWith(".png")) return ".png";
            if (lower.endsWith(".webp")) return ".webp";
        }
        return ".jpg";
    }
}
