package com.lab2.backend.dto;

import com.lab2.backend.model.Restaurant;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

class RestaurantDtoTest {

    @Test
    void fromEntity_prefersLocalImageOverYelpImage() {
        Restaurant restaurant = new Restaurant();
        restaurant.setImageUrl("/uploads/local.jpg");
        restaurant.setYelpImageUrl("https://images.yelpcdn.com/photo.jpg");
        restaurant.setAddress("123 King St, Toronto, ON");

        RestaurantDto dto = RestaurantDto.fromEntity(restaurant);

        assertEquals("/uploads/local.jpg", dto.getImageUrl());
        assertEquals("https://images.yelpcdn.com/photo.jpg", dto.getYelpImageUrl());
        assertEquals("123 King St, Toronto, ON", dto.getAddress());
    }

    @Test
    void fromEntity_fallsBackToYelpImageWhenLocalImageMissing() {
        Restaurant restaurant = new Restaurant();
        restaurant.setImageUrl("   ");
        restaurant.setYelpImageUrl("https://images.yelpcdn.com/photo.jpg");
        restaurant.setAddress(null);

        RestaurantDto dto = RestaurantDto.fromEntity(restaurant);

        assertEquals("https://images.yelpcdn.com/photo.jpg", dto.getImageUrl());
        assertNull(dto.getAddress());
    }

    @Test
    void fromEntity_usesYelpRatingWhenNoReviews() {
        Restaurant restaurant = new Restaurant();
        restaurant.setYelpRating(4.3);
        restaurant.setDescription("3.0 stars (2 reviews on Yelp)");

        RestaurantDto dto = RestaurantDto.fromEntity(restaurant);

        assertEquals(4.3, dto.getStars());
    }

    @Test
    void fromEntity_keepsImageUrlNullWhenNoLocalOrYelpImage() {
        Restaurant restaurant = new Restaurant();
        restaurant.setImageUrl(null);
        restaurant.setYelpImageUrl(null);
        restaurant.setAddress(null);

        RestaurantDto dto = RestaurantDto.fromEntity(restaurant);

        assertNull(dto.getImageUrl());
    }

    @Test
    void fromEntity_usesLocationAsFallbackAddress() {
        Restaurant restaurant = new Restaurant();
        restaurant.setLocation("88 Bloor St W, Toronto, ON");

        RestaurantDto dto = RestaurantDto.fromEntity(restaurant);

        assertEquals("88 Bloor St W, Toronto, ON", dto.getAddress());
    }
}
