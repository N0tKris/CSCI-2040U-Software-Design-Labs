package com.lab2.backend.service;

import com.lab2.backend.dto.LoginRequest;
import com.lab2.backend.dto.LoginResponse;
import com.lab2.backend.model.User;
import com.lab2.backend.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service that handles user authentication.
 * <p>
 * Tokens are stored in an in-memory map.  This is sufficient for
 * a development / lab project; a production application would use
 * JWTs or a persistent session store.
 */
@Service
public class AuthService {

    private final UserRepository userRepository;

    private final PasswordEncoder passwordEncoder;

    /** Maps token → authenticated User. */
    private final Map<String, User> tokenStore = new ConcurrentHashMap<>();

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    /**
     * Authenticate a user with the supplied credentials.
     *
     * @return a {@link LoginResponse} on success, or empty if credentials are invalid
     */
    public Optional<LoginResponse> login(LoginRequest request) {
        Optional<User> userOpt = userRepository.findByUsername(request.getUsername());

        if (userOpt.isEmpty()) {
            return Optional.empty();
        }

        User user = userOpt.get();

        // Verify password using the configured PasswordEncoder. Passwords
        // are hashed on registration (see UserService), so we must compare
        // the provided plain password against the stored hash.
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return Optional.empty();
        }

        String token = UUID.randomUUID().toString();
        tokenStore.put(token, user);

        return Optional.of(new LoginResponse(
                token,
                user.getUsername(),
                user.getRole().name()
        ));
    }

    /**
     * Look up the user associated with a session token.
     *
     * @return the authenticated {@link User}, or empty if the token is invalid
     */
    public Optional<User> getUserByToken(String token) {
        if (token == null || token.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(tokenStore.get(token));
    }

    /**
     * Check whether the given token belongs to an admin user.
     */
    public boolean isAdmin(String token) {
        return getUserByToken(token)
                .map(u -> u.getRole() == User.Role.ADMIN)
                .orElse(false);
    }

    /**
     * Check whether the given token belongs to an owner user.
     */
    public boolean isOwner(String token) {
        return getUserByToken(token)
                .map(u -> u.getRole() == User.Role.OWNER)
                .orElse(false);
    }

    /**
     * Invalidate (log out) the given token.
     */
    public void logout(String token) {
        tokenStore.remove(token);
    }

    /**
     * Clear all active tokens. Intended for use in tests only.
     */
    public void clearTokens() {
        tokenStore.clear();
    }
}
