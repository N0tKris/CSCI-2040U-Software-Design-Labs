package com.lab2.backend.repository;

import com.lab2.backend.model.MenuItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MenuItemRepository extends JpaRepository<MenuItem, Long> {

    /** Find all menu items belonging to the given restaurant. */
    List<MenuItem> findByRestaurantId(Long restaurantId);
}
