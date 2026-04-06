package com.lab2.backend.service;

import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Fetches restaurant data from the Yelp Fusion API and imports it into the
 * local database.  Duplicates (same name + location) are skipped.
 */
@Service
public class YelpService {

    private static final Pattern YELP_BIZ_ALIAS_PATTERN = Pattern.compile("/biz/([^/?#]+)");

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

    /**
     * Fetches Yelp review text for a restaurant previously imported from Yelp.
     * The restaurant's Yelp business alias is inferred from its yelpUrl field.
     */
    public List<Map<String, Object>> getReviewsForRestaurant(Long restaurantId) {
        if (yelpApiKey == null || yelpApiKey.isBlank()) {
            throw new IllegalStateException("YELP_API_KEY is not configured");
        }

        Restaurant restaurant = restaurantRepository.findById(restaurantId)
                .orElseThrow(() -> new IllegalArgumentException("Restaurant not found"));

        // Only call Yelp reviews API when a valid Yelp business ID exists.
        if (restaurant.getYelpId() == null || restaurant.getYelpId().isBlank()) {
            return Collections.emptyList();
        }

        String yelpId = restaurant.getYelpId().trim();
        System.out.println("Using Yelp ID: " + yelpId);
        System.out.println("Yelp ID: " + yelpId);

        List<Map<String, Object>> reviews = getReviews(yelpId);
        System.out.println("Number of reviews fetched: " + reviews.size());
        return reviews;
    }

    public List<Map<String, Object>> getReviews(String yelpId) {
        if (yelpId == null || yelpId.isBlank()) {
            return Collections.emptyList();
        }
        try {
            return fetchReviewsByBusinessRef(yelpId.trim());
        } catch (HttpClientErrorException.NotFound e) {
            System.out.println("Yelp reviews not found for ID: " + yelpId);
            return Collections.emptyList();
        }
    }

    // ── Internal helpers ────────────────────────────────────────────

    private int parseAndSave(String json) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode businesses = root.path("businesses");
            if (!businesses.isArray()) return 0;

            List<Restaurant> toSave = new ArrayList<>();
            int upsertedCount = 0;

            for (JsonNode biz : businesses) {
                Restaurant r = mapToRestaurant(biz);
                if (r == null) continue;                         // invalid entry
                Optional<Restaurant> existing = Optional.empty();
                if (hasText(r.getYelpId())) {
                    existing = restaurantRepository.findByYelpId(r.getYelpId());
                }
                if (existing.isEmpty()) {
                    existing = restaurantRepository.findByNameAndLocation(r.getName(), r.getLocation());
                }
                if (existing.isPresent()) {
                    mergeImportedRestaurant(existing.get(), r);
                    toSave.add(existing.get());
                } else {
                    toSave.add(r);
                }
                upsertedCount++;
            }

            if (!toSave.isEmpty()) {
                restaurantRepository.saveAll(toSave);            // batch insert
            }
            return upsertedCount;

        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Yelp response: " + e.getMessage(), e);
        }
    }

    private List<Map<String, Object>> parseReviews(String json) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode reviews = root.path("reviews");
            if (!reviews.isArray()) {
                return List.of();
            }

            List<Map<String, Object>> out = new ArrayList<>();
            for (JsonNode review : reviews) {
                Map<String, Object> mapped = new HashMap<>();
                mapped.put("source", "yelp");
                mapped.put("username", review.path("user").path("name").asText("Yelp User"));
                mapped.put("rating", review.path("rating").asDouble(0.0));
                mapped.put("comment", textOrNull(review, "text"));
                mapped.put("createdAt", textOrNull(review, "time_created"));
                mapped.put("url", textOrNull(review, "url"));
                out.add(mapped);
            }
            return out;
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Yelp reviews response: " + e.getMessage(), e);
        }
    }

    private static String extractBusinessAlias(String yelpUrl) {
        if (yelpUrl == null || yelpUrl.isBlank()) {
            return null;
        }

        String raw = yelpUrl.trim();
        Matcher matcher = YELP_BIZ_ALIAS_PATTERN.matcher(raw);
        if (matcher.find()) {
            String encodedAlias = matcher.group(1);
            if (encodedAlias != null && !encodedAlias.isBlank()) {
                try {
                    String decoded = URLDecoder.decode(encodedAlias, StandardCharsets.UTF_8);
                    return decoded.isBlank() ? null : decoded;
                } catch (Exception ignored) {
                    return encodedAlias;
                }
            }
        }

        try {
            URI uri = URI.create(raw);
            String path = uri.getPath();
            if (path == null) {
                return null;
            }
            int bizIndex = path.indexOf("/biz/");
            if (bizIndex < 0) {
                return null;
            }
            String aliasPath = path.substring(bizIndex + 5);
            int slashIndex = aliasPath.indexOf('/');
            String alias = (slashIndex >= 0) ? aliasPath.substring(0, slashIndex) : aliasPath;
            return alias.isBlank() ? null : alias;
        } catch (Exception ignored) {
            return null;
        }
    }

    private List<Map<String, Object>> fetchReviewsByBusinessRef(String businessRef) {
        String url = UriComponentsBuilder.fromHttpUrl(yelpBaseUrl + "/businesses/{ref}/reviews")
                .buildAndExpand(Map.of("ref", businessRef))
                .toUriString();

        System.out.println("Using Yelp ID: " + businessRef);
        System.out.println("Fetching Yelp reviews for ID: " + businessRef);
        System.out.println("Request URL: " + url);

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(yelpApiKey);
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));

        ResponseEntity<String> response;
        try {
            response = restTemplate.exchange(
                    url, HttpMethod.GET, new HttpEntity<>(headers), String.class);
        } catch (HttpClientErrorException.NotFound e) {
            System.out.println("Response status: 404");
            System.out.println("Response body: " + e.getResponseBodyAsString());
            throw e;
        }

        System.out.println("Response status: " + response.getStatusCode().value());
        System.out.println("Response body: " + response.getBody());
        System.out.println("Response: " + response.getBody());

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new RuntimeException("Yelp reviews API returned status " + response.getStatusCode());
        }
        return parseReviews(response.getBody());
    }

    private Optional<String> resolveBusinessIdBySearch(Restaurant restaurant) {
        String name = restaurant.getName();
        String location = restaurant.getLocation();
        if (name == null || name.isBlank()) {
            return Optional.empty();
        }

        List<String> locationCandidates = new ArrayList<>();
        if (location != null && !location.isBlank()) {
            locationCandidates.add(location);
            String maybeCity = extractCityFromLocation(location);
            if (maybeCity != null && !maybeCity.isBlank()) {
                locationCandidates.add(maybeCity);
            }
        }
        if (locationCandidates.isEmpty()) {
            return Optional.empty();
        }

        for (String candidateLocation : locationCandidates) {
            Optional<String> found = resolveBusinessIdBySearch(name, candidateLocation);
            if (found.isPresent()) {
                return found;
            }
        }
        return Optional.empty();
    }

    private Optional<String> resolveBusinessIdBySearch(String name, String location) {
        String url = UriComponentsBuilder.fromHttpUrl(yelpBaseUrl + "/businesses/search")
                .queryParam("term", name)
                .queryParam("location", location)
                .queryParam("categories", "restaurants")
                .queryParam("limit", 5)
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(yelpApiKey);
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.GET, new HttpEntity<>(headers), String.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                return Optional.empty();
            }

            JsonNode root = objectMapper.readTree(response.getBody());
            JsonNode businesses = root.path("businesses");
            if (!businesses.isArray() || businesses.isEmpty()) {
                return Optional.empty();
            }

            String targetName = normalize(name);
            for (JsonNode biz : businesses) {
                String candidateName = normalize(biz.path("name").asText(""));
                String id = textOrNull(biz, "id");
                if (Objects.equals(candidateName, targetName) && id != null && !id.isBlank()) {
                    return Optional.of(id);
                }
            }

            String firstId = textOrNull(businesses.get(0), "id");
            return (firstId == null || firstId.isBlank()) ? Optional.empty() : Optional.of(firstId);
        } catch (Exception ignored) {
            return Optional.empty();
        }
    }

    private Optional<String> resolveBusinessIdByPhone(String yelpPhone) {
        String phone = normalizePhone(yelpPhone);
        if (phone == null || phone.isBlank()) {
            return Optional.empty();
        }

        String url = UriComponentsBuilder.fromHttpUrl(yelpBaseUrl + "/businesses/search/phone")
                .queryParam("phone", phone)
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(yelpApiKey);
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url, HttpMethod.GET, new HttpEntity<>(headers), String.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                return Optional.empty();
            }

            JsonNode root = objectMapper.readTree(response.getBody());
            JsonNode businesses = root.path("businesses");
            if (!businesses.isArray() || businesses.isEmpty()) {
                return Optional.empty();
            }

            String id = textOrNull(businesses.get(0), "id");
            return (id == null || id.isBlank()) ? Optional.empty() : Optional.of(id);
        } catch (Exception ignored) {
            return Optional.empty();
        }
    }

    private static String normalize(String value) {
        if (value == null) {
            return "";
        }
        return value.toLowerCase()
                .replace("&", "and")
                .replaceAll("[^a-z0-9]+", "")
                .trim();
    }

    private static String normalizePhone(String rawPhone) {
        if (rawPhone == null || rawPhone.isBlank()) {
            return null;
        }
        String digits = rawPhone.replaceAll("[^0-9+]", "");
        if (digits.isBlank()) {
            return null;
        }

        // Yelp search/phone expects E.164 (e.g., +17038138181)
        if (digits.startsWith("+")) {
            return digits;
        }
        if (digits.length() == 11 && digits.startsWith("1")) {
            return "+" + digits;
        }
        if (digits.length() == 10) {
            return "+1" + digits;
        }
        return "+" + digits;
    }

    private static String extractCityFromLocation(String location) {
        if (location == null || location.isBlank()) {
            return null;
        }
        List<String> parts = Arrays.stream(location.split(","))
                .map(String::trim)
                .filter(part -> !part.isBlank())
                .toList();
        if (parts.isEmpty()) {
            return null;
        }
        return parts.get(parts.size() - 1);
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
        String address = buildFormattedAddress(loc);
        String location = hasText(address) ? address : buildFallbackLocation(loc);
        if (location == null || location.isBlank()) return null;

        JsonNode coordinates = biz.path("coordinates");
        Double latitude = doubleOrNull(coordinates, "latitude");
        Double longitude = doubleOrNull(coordinates, "longitude");

        // Rating → stored in description for now (the entity has no rating column)
        JsonNode ratingNode = biz.path("rating");
        JsonNode reviewCountNode = biz.path("review_count");
        double rating = ratingNode.asDouble(0);
        int reviewCount = reviewCountNode.asInt(0);

        // Build a quick description from Yelp data
        String description = String.format("%.1f stars (%d reviews on Yelp)", rating, reviewCount);

        Restaurant r = new Restaurant();
        r.setName(name.length() > 100 ? name.substring(0, 100) : name);
        r.setCuisine(cuisine.length() > 50 ? cuisine.substring(0, 50) : cuisine);
        r.setLocation(location.length() > 255 ? location.substring(0, 255) : location);
        r.setAddress(address != null && address.length() > 255 ? address.substring(0, 255) : address);
        r.setDescription(description);
        r.setYelpImageUrl(truncate(textOrNull(biz, "image_url"), 512));
        r.setYelpUrl(truncate(textOrNull(biz, "url"), 512));
        r.setYelpId(truncate(textOrNull(biz, "id"), 128));
        r.setYelpPhone(truncate(firstNonBlank(
                textOrNull(biz, "display_phone"),
                textOrNull(biz, "phone")
        ), 64));
        r.setYelpPrice(truncate(textOrNull(biz, "price"), 16));
        r.setYelpRating(isPresentValueNode(ratingNode) ? rating : null);
        r.setYelpReviewCount(isPresentValueNode(reviewCountNode) ? reviewCount : null);
        r.setYelpIsClosed(parseBooleanOrNull(biz.path("is_closed")));
        r.setLatitude(latitude);
        r.setLongitude(longitude);
        return r;
    }

    private void mergeImportedRestaurant(Restaurant existing, Restaurant incoming) {
        if (!hasText(existing.getAddress()) && hasText(incoming.getAddress())) {
            existing.setAddress(incoming.getAddress());
        }
        if (existing.getLatitude() == null && incoming.getLatitude() != null) {
            existing.setLatitude(incoming.getLatitude());
        }
        if (existing.getLongitude() == null && incoming.getLongitude() != null) {
            existing.setLongitude(incoming.getLongitude());
        }
        if (!hasText(existing.getYelpImageUrl()) && hasText(incoming.getYelpImageUrl())) {
            existing.setYelpImageUrl(incoming.getYelpImageUrl());
        }
        if (!hasText(existing.getYelpUrl()) && hasText(incoming.getYelpUrl())) {
            existing.setYelpUrl(incoming.getYelpUrl());
        }
        if (!hasText(existing.getYelpId()) && hasText(incoming.getYelpId())) {
            existing.setYelpId(incoming.getYelpId());
        }
        if (!hasText(existing.getYelpPhone()) && hasText(incoming.getYelpPhone())) {
            existing.setYelpPhone(incoming.getYelpPhone());
        }
        if (!hasText(existing.getYelpPrice()) && hasText(incoming.getYelpPrice())) {
            existing.setYelpPrice(incoming.getYelpPrice());
        }
        if (existing.getYelpRating() == null && incoming.getYelpRating() != null) {
            existing.setYelpRating(incoming.getYelpRating());
        }
        if (existing.getYelpReviewCount() == null && incoming.getYelpReviewCount() != null) {
            existing.setYelpReviewCount(incoming.getYelpReviewCount());
        }
        if (existing.getYelpIsClosed() == null && incoming.getYelpIsClosed() != null) {
            existing.setYelpIsClosed(incoming.getYelpIsClosed());
        }
        if (!hasText(existing.getDescription()) && hasText(incoming.getDescription())) {
            existing.setDescription(incoming.getDescription());
        }
    }

    private static String textOrNull(JsonNode node, String field) {
        JsonNode child = node.path(field);
        if (child.isMissingNode() || child.isNull()) return null;
        String text = child.asText("").trim();
        return text.isEmpty() ? null : text;
    }

    private static String buildFallbackLocation(JsonNode locationNode) {
        String address = textOrNull(locationNode, "address1");
        String city = textOrNull(locationNode, "city");
        String state = textOrNull(locationNode, "state");
        String postalCode = textOrNull(locationNode, "zip_code");
        StringBuilder builder = new StringBuilder();
        if (address != null) builder.append(address);
        if (city != null) {
            if (builder.length() > 0) builder.append(", ");
            builder.append(city);
        }
        if (state != null) {
            if (builder.length() > 0) builder.append(", ");
            builder.append(state);
        }
        if (postalCode != null) {
            if (builder.length() > 0) builder.append(" ");
            builder.append(postalCode);
        }
        return builder.toString().trim();
    }

    private static String buildFormattedAddress(JsonNode locationNode) {
        JsonNode displayAddress = locationNode.path("display_address");
        if (displayAddress.isArray() && !displayAddress.isEmpty()) {
            List<String> parts = new ArrayList<>();
            for (JsonNode part : displayAddress) {
                String value = part.asText("").trim();
                if (!value.isBlank()) {
                    parts.add(value);
                }
            }
            if (!parts.isEmpty()) {
                return String.join(", ", parts);
            }
        }
        if (displayAddress.isTextual()) {
            String text = displayAddress.asText("").trim();
            if (!text.isBlank()) {
                return text;
            }
        }
        return null;
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private static String truncate(String value, int maxLength) {
        if (value == null) return null;
        return value.length() > maxLength ? value.substring(0, maxLength) : value;
    }

    private static Boolean parseBooleanOrNull(JsonNode node) {
        if (node == null || node.isMissingNode() || node.isNull()) {
            return null;
        }
        return node.asBoolean();
    }

    private static Double doubleOrNull(JsonNode node, String field) {
        if (node == null || node.isMissingNode() || node.isNull()) {
            return null;
        }
        JsonNode child = node.path(field);
        if (child.isMissingNode() || child.isNull()) {
            return null;
        }
        if (child.isNumber()) {
            return child.asDouble();
        }
        String text = child.asText("").trim();
        if (text.isBlank()) {
            return null;
        }
        try {
            return Double.parseDouble(text);
        } catch (NumberFormatException ignored) {
            return null;
        }
    }

    private static boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private static boolean isPresentValueNode(JsonNode node) {
        return node != null && !node.isMissingNode() && !node.isNull();
    }
}
