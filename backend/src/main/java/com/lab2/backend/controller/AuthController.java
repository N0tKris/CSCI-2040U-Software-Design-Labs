package com.lab2.backend.controller;

import com.lab2.backend.dto.LoginRequest;
import com.lab2.backend.dto.LoginResponse;
import com.lab2.backend.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST controller for authentication endpoints.
 */
@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * Authenticate a user.
     * <p>
     * <b>POST /api/auth/login</b>
     *
     * @param request JSON body with {@code username} and {@code password}
     * @return 200 with token + role on success, 401 on failure
     */
    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request)
                .<ResponseEntity<?>>map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.status(401)
                        .body(Map.of("error", "Invalid username or password")));
    }

    /**
     * Log out (invalidate a session token).
     * <p>
     * <b>POST /api/auth/logout</b>
     */
    @PostMapping("/logout")
    public ResponseEntity<?> logout(@RequestHeader(value = "Authorization", required = false) String token) {
        if (token != null && !token.isBlank()) {
            authService.logout(token);
        }
        return ResponseEntity.ok(Map.of("message", "Logged out successfully"));
    }
}
