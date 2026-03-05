package com.lab2.backend;

import com.lab2.backend.model.User;
import com.lab2.backend.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * Seeds the database with a default admin account on application startup
 * if one does not already exist.
 */
@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;

    public DataInitializer(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Override
    public void run(String... args) {
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User("admin", "admin123", User.Role.ADMIN);
            userRepository.save(admin);
            System.out.println("Default admin account created (username: admin)");
        } else {
            System.out.println("Admin account already exists – skipping seed");
        }
    }
}
