package com.lab2.backend.service;

import com.lab2.backend.model.MenuItem;
import com.lab2.backend.model.Restaurant;
import com.lab2.backend.repository.RestaurantRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.nio.file.Path;
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
class RestaurantServiceTest {

    @Mock
    private RestaurantRepository repository;

    @InjectMocks
    private RestaurantService restaurantService;

    private Restaurant testRestaurant;
    private Restaurant testRestaurant2;

    @BeforeEach
    void setUp() {
        testRestaurant = new Restaurant();
        testRestaurant.setId(1L);
        testRestaurant.setName("Test Restaurant");
        testRestaurant.setCuisine("Italian");
        testRestaurant.setLocation("123 Main St");
        testRestaurant.setDescription("Great Italian food");

        testRestaurant2 = new Restaurant();
        testRestaurant2.setId(2L);
        testRestaurant2.setName("Another Restaurant");
        testRestaurant2.setCuisine("Japanese");
        testRestaurant2.setLocation("456 Oak Ave");
    }

    // ============ getAllRestaurants() Tests ============

    @Test
    void testGetAllRestaurantsSuccess() {
        // Arrange
        List<Restaurant> restaurants = new ArrayList<>();
        restaurants.add(testRestaurant);
        restaurants.add(testRestaurant2);
        when(repository.findAll()).thenReturn(restaurants);

        // Act
        List<Restaurant> result = restaurantService.getAllRestaurants();

        // Assert
        assertEquals(2, result.size());
        verify(repository, times(1)).findAll();
    }

    @Test
    void testGetAllRestaurantsEmpty() {
        // Arrange
        when(repository.findAll()).thenReturn(new ArrayList<>());

        // Act
        List<Restaurant> result = restaurantService.getAllRestaurants();

        // Assert
        assertTrue(result.isEmpty());
        verify(repository, times(1)).findAll();
    }

    @Test
    void testGetAllRestaurantsInitializesLazyCollections() {
        // Arrange
        testRestaurant.setMenuItems(new ArrayList<>());
        testRestaurant.setReviews(new ArrayList<>());
        List<Restaurant> restaurants = new ArrayList<>();
        restaurants.add(testRestaurant);
        when(repository.findAll()).thenReturn(restaurants);

        // Act
        List<Restaurant> result = restaurantService.getAllRestaurants();

        // Assert
        assertNotNull(result.get(0).getMenuItems());
        assertNotNull(result.get(0).getReviews());
        verify(repository, times(1)).findAll();
    }

    // ============ getRestaurantById() Tests ============

    @Test
    void testGetRestaurantByIdSuccess() {
        // Arrange
        Long restaurantId = 1L;
        when(repository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act
        Restaurant result = restaurantService.getRestaurantById(restaurantId);

        // Assert
        assertNotNull(result);
        assertEquals(testRestaurant.getId(), result.getId());
        assertEquals("Test Restaurant", result.getName());
        verify(repository, times(1)).findById(restaurantId);
    }

    @Test
    void testGetRestaurantByIdNotFound() {
        // Arrange
        Long restaurantId = 99L;
        when(repository.findById(restaurantId)).thenReturn(Optional.empty());

        // Act
        Restaurant result = restaurantService.getRestaurantById(restaurantId);

        // Assert
        assertNull(result);
        verify(repository, times(1)).findById(restaurantId);
    }

    @Test
    void testGetRestaurantByIdInitializesCollections() {
        // Arrange
        Long restaurantId = 1L;
        testRestaurant.setMenuItems(new ArrayList<>());
        testRestaurant.setReviews(new ArrayList<>());
        when(repository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));

        // Act
        Restaurant result = restaurantService.getRestaurantById(restaurantId);

        // Assert
        assertNotNull(result.getMenuItems());
        assertNotNull(result.getReviews());
        verify(repository, times(1)).findById(restaurantId);
    }

    // ============ addRestaurant() Tests ============

    @Test
    void testAddRestaurantSuccess() {
        // Arrange
        Restaurant newRestaurant = new Restaurant();
        newRestaurant.setId(5L); // Should be set to null
        newRestaurant.setName("New Restaurant");
        newRestaurant.setCuisine("Mexican");
        newRestaurant.setLocation("789 Elm St");

        Restaurant savedRestaurant = new Restaurant();
        savedRestaurant.setId(10L);
        savedRestaurant.setName("New Restaurant");
        when(repository.save(any(Restaurant.class))).thenReturn(savedRestaurant);

        // Act
        Restaurant result = restaurantService.addRestaurant(newRestaurant);

        // Assert
        assertNotNull(result);
        assertEquals(10L, result.getId());
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    @Test
    void testAddRestaurantSetsIdToNull() {
        // Arrange
        Restaurant newRestaurant = new Restaurant();
        newRestaurant.setId(999L);
        newRestaurant.setName("Test");
        newRestaurant.setCuisine("Italian");
        newRestaurant.setLocation("Test Location");

        when(repository.save(any(Restaurant.class))).thenAnswer(invocation -> {
            Restaurant arg = invocation.getArgument(0);
            assertNull(arg.getId(), "ID should be set to null before saving");
            return arg;
        });

        // Act
        restaurantService.addRestaurant(newRestaurant);

        // Assert
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    // ============ addRestaurantByOwner() Tests ============

    @Test
    void testAddRestaurantByOwnerSuccess() {
        // Arrange
        Long ownerId = 5L;
        Restaurant newRestaurant = new Restaurant();
        newRestaurant.setName("Owner's Restaurant");
        newRestaurant.setCuisine("French");
        newRestaurant.setLocation("100 Park St");

        Restaurant savedRestaurant = new Restaurant();
        savedRestaurant.setId(20L);
        savedRestaurant.setOwnerId(ownerId);
        savedRestaurant.setName("Owner's Restaurant");

        when(repository.existsByOwnerId(ownerId)).thenReturn(false);
        when(repository.save(any(Restaurant.class))).thenReturn(savedRestaurant);

        // Act
        Restaurant result = restaurantService.addRestaurantByOwner(ownerId, newRestaurant);

        // Assert
        assertNotNull(result);
        assertEquals(ownerId, result.getOwnerId());
        verify(repository, times(1)).existsByOwnerId(ownerId);
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    @Test
    void testAddRestaurantByOwnerOwnerAlreadyHasRestaurant() {
        // Arrange
        Long ownerId = 5L;
        Restaurant newRestaurant = new Restaurant();
        newRestaurant.setName("Another Restaurant");

        when(repository.existsByOwnerId(ownerId)).thenReturn(true);

        // Act & Assert
        IllegalStateException exception = assertThrows(IllegalStateException.class, () ->
                restaurantService.addRestaurantByOwner(ownerId, newRestaurant)
        );
        assertEquals("Owner already has a restaurant", exception.getMessage());
        verify(repository, times(1)).existsByOwnerId(ownerId);
        verify(repository, times(0)).save(any(Restaurant.class));
    }

    @Test
    void testAddRestaurantByOwnerSetsOwnerIdCorrectly() {
        // Arrange
        Long ownerId = 7L;
        Restaurant newRestaurant = new Restaurant();
        newRestaurant.setName("Test");

        when(repository.existsByOwnerId(ownerId)).thenReturn(false);
        when(repository.save(any(Restaurant.class))).thenAnswer(invocation -> {
            Restaurant arg = invocation.getArgument(0);
            assertEquals(ownerId, arg.getOwnerId(), "OwnerId should be set correctly");
            assertNull(arg.getId(), "ID should be null");
            return arg;
        });

        // Act
        restaurantService.addRestaurantByOwner(ownerId, newRestaurant);

        // Assert
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    // ============ getRestaurantByOwner() Tests ============

    @Test
    void testGetRestaurantByOwnerSuccess() {
        // Arrange
        Long ownerId = 5L;
        testRestaurant.setOwnerId(ownerId);
        when(repository.findByOwnerId(ownerId)).thenReturn(Optional.of(testRestaurant));

        // Act
        Restaurant result = restaurantService.getRestaurantByOwner(ownerId);

        // Assert
        assertNotNull(result);
        assertEquals(ownerId, result.getOwnerId());
        verify(repository, times(1)).findByOwnerId(ownerId);
    }

    @Test
    void testGetRestaurantByOwnerNotFound() {
        // Arrange
        Long ownerId = 99L;
        when(repository.findByOwnerId(ownerId)).thenReturn(Optional.empty());

        // Act
        Restaurant result = restaurantService.getRestaurantByOwner(ownerId);

        // Assert
        assertNull(result);
        verify(repository, times(1)).findByOwnerId(ownerId);
    }

    @Test
    void testGetRestaurantByOwnerInitializesCollections() {
        // Arrange
        Long ownerId = 5L;
        testRestaurant.setOwnerId(ownerId);
        testRestaurant.setMenuItems(new ArrayList<>());
        testRestaurant.setReviews(new ArrayList<>());
        when(repository.findByOwnerId(ownerId)).thenReturn(Optional.of(testRestaurant));

        // Act
        Restaurant result = restaurantService.getRestaurantByOwner(ownerId);

        // Assert
        assertNotNull(result.getMenuItems());
        assertNotNull(result.getReviews());
        verify(repository, times(1)).findByOwnerId(ownerId);
    }

    // ============ ownerHasRestaurant() Tests ============

    @Test
    void testOwnerHasRestaurantTrue() {
        // Arrange
        Long ownerId = 5L;
        when(repository.existsByOwnerId(ownerId)).thenReturn(true);

        // Act
        boolean result = restaurantService.ownerHasRestaurant(ownerId);

        // Assert
        assertTrue(result);
        verify(repository, times(1)).existsByOwnerId(ownerId);
    }

    @Test
    void testOwnerHasRestaurantFalse() {
        // Arrange
        Long ownerId = 99L;
        when(repository.existsByOwnerId(ownerId)).thenReturn(false);

        // Act
        boolean result = restaurantService.ownerHasRestaurant(ownerId);

        // Assert
        assertFalse(result);
        verify(repository, times(1)).existsByOwnerId(ownerId);
    }

    // ============ updateRestaurant() Tests ============

    @Test
    void testUpdateRestaurantSuccess() {
        // Arrange
        Long restaurantId = 1L;
        Restaurant updated = new Restaurant();
        updated.setName("Updated Name");
        updated.setCuisine("Updated Cuisine");
        updated.setLocation("Updated Location");
        updated.setDescription("Updated Description");

        Restaurant existing = new Restaurant();
        existing.setId(restaurantId);
        existing.setName("Old Name");

        when(repository.findById(restaurantId)).thenReturn(Optional.of(existing));
        when(repository.save(any(Restaurant.class))).thenReturn(existing);

        // Act
        Restaurant result = restaurantService.updateRestaurant(restaurantId, updated);

        // Assert
        assertNotNull(result);
        verify(repository, times(1)).findById(restaurantId);
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    @Test
    void testUpdateRestaurantNotFound() {
        // Arrange
        Long restaurantId = 99L;
        Restaurant updated = new Restaurant();

        when(repository.findById(restaurantId)).thenReturn(Optional.empty());

        // Act
        Restaurant result = restaurantService.updateRestaurant(restaurantId, updated);

        // Assert
        assertNull(result);
        verify(repository, times(1)).findById(restaurantId);
        verify(repository, times(0)).save(any(Restaurant.class));
    }

    @Test
    void testUpdateRestaurantWithOwnerId() {
        // Arrange
        Long restaurantId = 1L;
        Long newOwnerId = 10L;
        Restaurant updated = new Restaurant();
        updated.setName("Updated");
        updated.setOwnerId(newOwnerId);

        Restaurant existing = new Restaurant();
        existing.setId(restaurantId);
        existing.setOwnerId(5L);

        when(repository.findById(restaurantId)).thenReturn(Optional.of(existing));
        when(repository.save(any(Restaurant.class))).thenAnswer(invocation -> {
            Restaurant arg = invocation.getArgument(0);
            assertEquals(newOwnerId, arg.getOwnerId(), "OwnerId should be updated");
            return arg;
        });

        // Act
        restaurantService.updateRestaurant(restaurantId, updated);

        // Assert
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    // ============ deleteRestaurant() Tests ============

    @Test
    void testDeleteRestaurantSuccess() {
        // Arrange
        Long restaurantId = 1L;
        when(repository.existsById(restaurantId)).thenReturn(true);

        // Act
        boolean result = restaurantService.deleteRestaurant(restaurantId);

        // Assert
        assertTrue(result);
        verify(repository, times(1)).existsById(restaurantId);
        verify(repository, times(1)).deleteById(restaurantId);
    }

    @Test
    void testDeleteRestaurantNotFound() {
        // Arrange
        Long restaurantId = 99L;
        when(repository.existsById(restaurantId)).thenReturn(false);

        // Act
        boolean result = restaurantService.deleteRestaurant(restaurantId);

        // Assert
        assertFalse(result);
        verify(repository, times(1)).existsById(restaurantId);
        verify(repository, times(0)).deleteById(restaurantId);
    }

    // ============ deleteAll() Tests ============

    @Test
    void testDeleteAllSuccess() {
        // Act
        restaurantService.deleteAll();

        // Assert
        verify(repository, times(1)).deleteAll();
    }

    // ============ validateRestaurant() Tests ============

    @Test
    void testValidateRestaurantSuccess() {
        // Arrange
        Restaurant valid = new Restaurant();
        valid.setName("Valid Restaurant");
        valid.setCuisine("Italian");
        valid.setLocation("123 Main St");

        // Act
        boolean result = restaurantService.validateRestaurant(valid);

        // Assert
        assertTrue(result);
    }

    @Test
    void testValidateRestaurantNull() {
        // Act
        boolean result = restaurantService.validateRestaurant(null);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantNullName() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setCuisine("Italian");
        invalid.setLocation("123 Main St");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantEmptyName() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setName("   ");
        invalid.setCuisine("Italian");
        invalid.setLocation("123 Main St");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantNullCuisine() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setName("Restaurant");
        invalid.setLocation("123 Main St");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantEmptyCuisine() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setName("Restaurant");
        invalid.setCuisine("");
        invalid.setLocation("123 Main St");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantNullLocation() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setName("Restaurant");
        invalid.setCuisine("Italian");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    @Test
    void testValidateRestaurantEmptyLocation() {
        // Arrange
        Restaurant invalid = new Restaurant();
        invalid.setName("Restaurant");
        invalid.setCuisine("Italian");
        invalid.setLocation("   ");

        // Act
        boolean result = restaurantService.validateRestaurant(invalid);

        // Assert
        assertFalse(result);
    }

    // ============ uploadImage() Tests ============

    @Test
    void testUploadImageSuccess(@TempDir Path tempDir) throws IOException {
        // Arrange
        Long restaurantId = 1L;
        when(repository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(repository.save(any(Restaurant.class))).thenAnswer(invocation -> invocation.getArgument(0));

        MockMultipartFile file = new MockMultipartFile(
                "file", "photo.jpg", "image/jpeg", "fake-image-content".getBytes()
        );

        // Act
        Restaurant result = restaurantService.uploadImage(restaurantId, file, tempDir);

        // Assert
        assertNotNull(result);
        assertNotNull(result.getImageUrl());
        assertTrue(result.getImageUrl().startsWith("/uploads/"));
        assertTrue(result.getImageUrl().endsWith(".jpg"));
        verify(repository, times(1)).save(any(Restaurant.class));
    }

    @Test
    void testUploadImageRestaurantNotFound(@TempDir Path tempDir) throws IOException {
        // Arrange
        Long restaurantId = 99L;
        when(repository.findById(restaurantId)).thenReturn(Optional.empty());

        MockMultipartFile file = new MockMultipartFile(
                "file", "photo.jpg", "image/jpeg", "fake-image-content".getBytes()
        );

        // Act
        Restaurant result = restaurantService.uploadImage(restaurantId, file, tempDir);

        // Assert
        assertNull(result);
        verify(repository, times(0)).save(any(Restaurant.class));
    }

    @Test
    void testUploadImageInvalidFileType(@TempDir Path tempDir) {
        // Arrange
        MockMultipartFile file = new MockMultipartFile(
                "file", "document.pdf", "application/pdf", "pdf-content".getBytes()
        );

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                restaurantService.uploadImage(1L, file, tempDir)
        );
        assertTrue(exception.getMessage().contains("Invalid file type"));
    }

    @Test
    void testUploadImageEmptyFile(@TempDir Path tempDir) {
        // Arrange
        MockMultipartFile file = new MockMultipartFile(
                "file", "empty.jpg", "image/jpeg", new byte[0]
        );

        // Act & Assert
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () ->
                restaurantService.uploadImage(1L, file, tempDir)
        );
        assertTrue(exception.getMessage().contains("No file provided"));
    }

    @Test
    void testUploadImagePngExtension(@TempDir Path tempDir) throws IOException {
        // Arrange
        Long restaurantId = 1L;
        when(repository.findById(restaurantId)).thenReturn(Optional.of(testRestaurant));
        when(repository.save(any(Restaurant.class))).thenAnswer(invocation -> invocation.getArgument(0));

        MockMultipartFile file = new MockMultipartFile(
                "file", "photo.png", "image/png", "fake-png-content".getBytes()
        );

        // Act
        Restaurant result = restaurantService.uploadImage(restaurantId, file, tempDir);

        // Assert
        assertNotNull(result);
        assertTrue(result.getImageUrl().endsWith(".png"));
    }
}
