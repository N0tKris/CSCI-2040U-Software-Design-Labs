package com.lab2.backend.dto;

import com.lab2.backend.model.User;

/**
 * Minimal user DTO to avoid exposing sensitive fields.
 */
public class UserDto {
    private Long id;
    private String username;
    private String role;

    public UserDto() {}

    public UserDto(Long id, String username, String role) {
        this.id = id;
        this.username = username;
        this.role = role;
    }

    public static UserDto fromEntity(User u) {
        if (u == null) return null;
        return new UserDto(u.getId(), u.getUsername(), u.getRole() != null ? u.getRole().name() : null);
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}
