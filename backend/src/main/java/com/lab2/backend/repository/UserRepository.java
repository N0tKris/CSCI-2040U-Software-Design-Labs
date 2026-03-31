package com.lab2.backend.repository;

import com.lab2.backend.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * JPA repository for {@link User} entities.
 * Provides CRUD operations and custom query methods for user lookup.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /** Find a user by their unique username. */
    Optional<User> findByUsername(String username);

    /** Check whether a user with the given username already exists. */
    boolean existsByUsername(String username);

    /** Find the first user account by role. */
    Optional<User> findFirstByRole(User.Role role);

}
