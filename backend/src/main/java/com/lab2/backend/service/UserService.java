package com.lab2.backend.service;

import com.lab2.backend.model.User;
import com.lab2.backend.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    /**
     * Register a new user with the given username and password.
     * The password is hashed before storage, and the default role is USER.
     *
     * @throws IllegalArgumentException if the username is already taken or input is invalid
     */
    public User register(String username, String password) {
        return register(username, password, User.Role.USER);
    }

    /**
     * Register a new user with the given username, password, and role.
     * The password is hashed before storage.
     *
     * @throws IllegalArgumentException if the username is already taken or input is invalid
     */
    public User register(String username, String password, User.Role role) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username cannot be empty");
        }
        if (password == null || password.trim().isEmpty()) {
            throw new IllegalArgumentException("Password cannot be empty");
        }

        if (userRepository.existsByUsername(username)) {
            throw new IllegalArgumentException("Username already exists");
        }

        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setRole(role != null ? role : User.Role.USER);

        return userRepository.save(user);
    }

    /**
     * Return all users. Admin controllers may call this to show user lists.
     */
    public java.util.List<User> listAllUsers() {
        return userRepository.findAll();
    }
}
