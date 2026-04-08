package com.lab2.backend.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lab2.backend.model.Restaurant;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.MenuItemRepository;
import com.lab2.backend.repository.RestaurantRepository;
import com.lab2.backend.repository.UserRepository;
import com.lab2.backend.service.AuthService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;

import java.util.ArrayList;
import java.util.Map;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Integration tests for {@link MenuItemController}.
 * Uses H2 in-memory database (configured in test application.properties).
 */
@SpringBootTest
@AutoConfigureMockMvc
class MenuItemControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RestaurantRepository restaurantRepository;

    @Autowired
    private MenuItemRepository menuItemRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private AuthService authService;

    @Autowired
    private ObjectMapper objectMapper;

    private String adminToken;
    private String ownerToken;
    private String otherOwnerToken;
    private String userToken;
    private Long restaurantId;
    private Long otherRestaurantId;

    @BeforeEach
    void setUp() {
        menuItemRepository.deleteAll();
        restaurantRepository.deleteAll();
        userRepository.deleteAll();
        authService.clearTokens();

        // Create admin
        User admin = userRepository.save(
                new User("admin", passwordEncoder.encode("adminpass"), User.Role.ADMIN));

        // Create owner with a restaurant
        User owner = userRepository.save(
                new User("owner1", passwordEncoder.encode("ownerpass"), User.Role.OWNER));

        // Create another owner with a different restaurant
        User otherOwner = userRepository.save(
                new User("owner2", passwordEncoder.encode("ownerpass2"), User.Role.OWNER));

        // Create a regular user
        User user = userRepository.save(
                new User("user1", passwordEncoder.encode("userpass"), User.Role.USER));

        // Create restaurants
        Restaurant r1 = new Restaurant();
        r1.setName("Owner1 Bistro");
        r1.setCuisine("Italian");
        r1.setLocation("123 Main St");
        r1.setOwnerId(owner.getId());
        r1 = restaurantRepository.save(r1);
        restaurantId = r1.getId();

        Restaurant r2 = new Restaurant();
        r2.setName("Owner2 Diner");
        r2.setCuisine("American");
        r2.setLocation("456 Oak Ave");
        r2.setOwnerId(otherOwner.getId());
        r2 = restaurantRepository.save(r2);
        otherRestaurantId = r2.getId();

        // Log in each user to get tokens
        adminToken = authService.login(
                new com.lab2.backend.dto.LoginRequest("admin", "adminpass"))
                .map(lr -> lr.getToken()).orElseThrow();
        ownerToken = authService.login(
                new com.lab2.backend.dto.LoginRequest("owner1", "ownerpass"))
                .map(lr -> lr.getToken()).orElseThrow();
        otherOwnerToken = authService.login(
                new com.lab2.backend.dto.LoginRequest("owner2", "ownerpass2"))
                .map(lr -> lr.getToken()).orElseThrow();
        userToken = authService.login(
                new com.lab2.backend.dto.LoginRequest("user1", "userpass"))
                .map(lr -> lr.getToken()).orElseThrow();
    }

    @Test
    void adminCanAddMenuItemToAnyRestaurant() throws Exception {
        Map<String, Object> body = Map.of(
                "itemName", "Margherita Pizza",
                "price", "12.99",
                "description", "Classic tomato and mozzarella",
                "dietaryTags", "Vegan, Gluten-Free"
        );

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.itemName").value("Margherita Pizza"))
                .andExpect(jsonPath("$.price").value(12.99))
                .andExpect(jsonPath("$.description").value("Classic tomato and mozzarella"))
                .andExpect(jsonPath("$.dietaryTags").value("Vegan, Gluten-Free"))
                .andExpect(jsonPath("$.restaurantId").value(restaurantId));
    }

    @Test
    void adminCanAddMenuItemToOtherOwnersRestaurant() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Burger", "price", "9.99");

        mockMvc.perform(post("/api/restaurants/{id}/menu", otherRestaurantId)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.restaurantId").value(otherRestaurantId));
    }

    @Test
    void ownerCanAddMenuItemToOwnRestaurant() throws Exception {
        Map<String, Object> body = Map.of(
                "itemName", "Tiramisu",
                "price", "7.50"
        );

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.itemName").value("Tiramisu"))
                .andExpect(jsonPath("$.price").value(7.50))
                .andExpect(jsonPath("$.restaurantId").value(restaurantId));
    }

    @Test
    void ownerCannotAddMenuItemToOtherRestaurant() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Fries", "price", "3.99");

        mockMvc.perform(post("/api/restaurants/{id}/menu", otherRestaurantId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error").value("You can only add menu items to your own restaurant"));
    }

    @Test
    void regularUserCannotAddMenuItem() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Soup", "price", "5.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", userToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error").value("Admin or Owner privileges required"));
    }

    @Test
    void unauthenticatedUserCannotAddMenuItem() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Salad", "price", "6.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isForbidden());
    }

    @Test
    void addMenuItemFailsForNonExistentRestaurant() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Pasta", "price", "11.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", 99999L)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isNotFound());
    }

    @Test
    void addMenuItemFailsWithoutItemName() throws Exception {
        Map<String, Object> body = Map.of("price", "8.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("itemName is required"));
    }

    @Test
    void addMenuItemFailsWithoutPrice() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Dessert");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("price is required"));
    }

    @Test
    void addMenuItemFailsWithNegativePrice() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Dessert", "price", "-1.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("price must be non-negative"));
    }

    @Test
    void menuItemDescriptionIsOptional() throws Exception {
        Map<String, Object> body = Map.of("itemName", "Water", "price", "0.00");

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.itemName").value("Water"))
                .andExpect(jsonPath("$.price").value(0.00));
    }

    @Test
    void menuItemDietaryTagsAreNormalizedAndDeduplicated() throws Exception {
        ArrayList<Object> dietaryTags = new ArrayList<>();
        dietaryTags.add(" vegan ");
        dietaryTags.add("Gluten free");
        dietaryTags.add("VEGAN");
        dietaryTags.add("");
        dietaryTags.add(null);

        Map<String, Object> body = Map.of(
                "itemName", "Power Bowl",
                "price", "14.25",
                "dietaryTags", dietaryTags
        );

        mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.dietaryTags").value("Vegan, Gluten-Free"));
    }

    @Test
    void ownerCanUpdateMenuItemDietaryTags() throws Exception {
        Map<String, Object> createBody = Map.of(
                "itemName", "Taco",
                "price", "9.99"
        );

        String response = mockMvc.perform(post("/api/restaurants/{id}/menu", restaurantId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createBody)))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Long menuItemId = objectMapper.readTree(response).get("id").asLong();

        Map<String, Object> updateBody = Map.of(
                "dietaryTags", java.util.List.of("Halal", "Nut Free", "halal")
        );

        mockMvc.perform(put("/api/restaurants/{id}/menu/{menuId}", restaurantId, menuItemId)
                        .header("Authorization", ownerToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateBody)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.dietaryTags").value("Halal, Nut-Free"));
    }
}
