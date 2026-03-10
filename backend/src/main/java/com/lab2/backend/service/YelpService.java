package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.ArrayList;
import java.util.List;

/**
 * Fetches restaurant data from the Yelp Fusion API and imports it into the
 * local database.  Duplicates (same name + location) are skipped.
 */
@Service
public class YelpService {

    private final RestTemplate restTemplate;
    private final RestaurantRepository restaurantRepository;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${yelp.api.key:}")
    private String yelpApiKey;

    @Value("${yelp.api.base-url:https://api.yelp.com/v3}")
    private String yelpBaseUrl;

    public YelpService(RestTemplate restTemplate, RestaurantRepository restaurantRepository) {
        this.restTemplate = restTemplate;
        this.restaurantRepository = restaurantRepository;
    }

    /**
     * Calls the Yelp Business Search endpoint, maps each result to a
     * {@link Restaurant} entity, and batch-inserts any that don't already exist.
     *
     * @return the number of new restaurants imported
     */
    public int importRestaurants(String location, int limit) {
        if (yelpApiKey == null || yelpApiKey.isBlank()) {
            throw new IllegalStateException("YELP_API_KEY is not configured");
        }

        String url = UriComponentsBuilder.fromHttpUrl(yelpBaseUrl + "/businesses/search")
                .queryParam("location", location)
                .queryParam("categories", "restaurants")
                .queryParam("limit", Math.min(limit, 50))   // Yelp max is 50
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(yelpApiKey);
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));

        ResponseEntity<String> response = restTemplate.exchange(
                url, HttpMethod.GET, new HttpEntity<>(headers), String.class);

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new RuntimeException("Yelp API returned status " + response.getStatusCode());
        }

        return parseAndSave(response.getBody());
    }

    // ── Internal helpers ────────────────────────────────────────────

    private int parseAndSave(String json) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode businesses = root.path("businesses");
            if (!businesses.isArray()) return 0;

            List<Restaurant> toSave = new ArrayList<>();

            for (JsonNode biz : businesses) {
                Restaurant r = mapToRestaurant(biz);
                if (r == null) continue;                         // invalid entry
                if (isDuplicate(r)) continue;                    // already in DB
                toSave.add(r);
            }

            if (!toSave.isEmpty()) {
                restaurantRepository.saveAll(toSave);            // batch insert
            }
            return toSave.size();

        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Yelp response: " + e.getMessage(), e);
        }
    }

    private Restaurant mapToRestaurant(JsonNode biz) {
        String name = textOrNull(biz, "name");
        if (name == null || name.isBlank()) return null;

        // Cuisine: first category title, default to "Restaurant"
        String cuisine = "Restaurant";
        JsonNode cats = biz.path("categories");
        if (cats.isArray() && !cats.isEmpty()) {
            String title = cats.get(0).path("title").asText("");
            if (!title.isBlank()) cuisine = title;
        }

        // Location
        JsonNode loc = biz.path("location");
        String address = textOrNull(loc, "address1");
        String city = textOrNull(loc, "city");
        String location = buildLocation(address, city);
        if (location == null || location.isBlank()) return null;

        // Rating → stored in description for now (the entity has no rating column)
        double rating = biz.path("rating").asDouble(0);
        int reviewCount = biz.path("review_count").asInt(0);

        // Build a quick description from Yelp data
        String description = String.format("%.1f stars (%d reviews on Yelp)", rating, reviewCount);

        Restaurant r = new Restaurant();
        r.setName(name.length() > 100 ? name.substring(0, 100) : name);
        r.setCuisine(cuisine.length() > 50 ? cuisine.substring(0, 50) : cuisine);
        r.setLocation(location.length() > 255 ? location.substring(0, 255) : location);
        r.setDescription(description);
        return r;
    }

    private boolean isDuplicate(Restaurant r) {
        return restaurantRepository.existsByNameAndLocation(r.getName(), r.getLocation());
    }

    private static String textOrNull(JsonNode node, String field) {
        JsonNode child = node.path(field);
        if (child.isMissingNode() || child.isNull()) return null;
        String text = child.asText("").trim();
        return text.isEmpty() ? null : text;
    }

    private static String buildLocation(String address, String city) {
        if (address != null && city != null) return address + ", " + city;
        if (city != null) return city;
        return address;       // may be null → caller checks
    }
}
