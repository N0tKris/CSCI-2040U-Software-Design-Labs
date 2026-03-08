package com.lab2.backend;

import com.lab2.backend.model.User;
import com.lab2.backend.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Seeds the database with a default admin account on application startup
 * if one does not already exist. The default admin password is encoded
 * using the application's PasswordEncoder so it can be authenticated
 * by the AuthService which compares hashed passwords.
 */
@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        final String defaultAdmin = "admin";
        final String defaultPassword = "admin123";

        if (!userRepository.existsByUsername(defaultAdmin)) {
            User admin = new User();
            admin.setUsername(defaultAdmin);
            admin.setPassword(passwordEncoder.encode(defaultPassword));
            admin.setRole(User.Role.ADMIN);
            userRepository.save(admin);
            System.out.println("Default admin account created (username: admin)");
            return;
        }

        // Admin exists — ensure the stored password is encoded. Some
        // development runs may have previously stored a plain-text admin
        // password; update it to an encoded hash if necessary.
        userRepository.findByUsername(defaultAdmin).ifPresent(u -> {
            String stored = u.getPassword();
            // BCrypt hashes typically start with $2a$ or $2b$; if not,
            // assume it's not encoded and replace it with an encoded value.
            if (stored == null || !(stored.startsWith("$2a$") || stored.startsWith("$2b$") || stored.startsWith("$2y$"))) {
                u.setPassword(passwordEncoder.encode(defaultPassword));
                userRepository.save(u);
                System.out.println("Existing admin password was updated to a hashed value");
            } else {
                System.out.println("Admin account exists with encoded password — no change");
            }
        });
    }
}
