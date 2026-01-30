package com.lab2.backend.controller;

import com.lab2.backend.model.CatalogItem;
import com.lab2.backend.service.CatalogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/catalog")
@CrossOrigin(origins = "*")
public class CatalogController {

    @Autowired
    private CatalogService catalogService;

    @GetMapping
    public ResponseEntity<List<CatalogItem>> getAllItems() {
        return ResponseEntity.ok(catalogService.getAllItems());
    }

    @GetMapping("/{id}")
    public ResponseEntity<CatalogItem> getItemById(@PathVariable int id) {
        CatalogItem item = catalogService.getItemById(id);
        if (item != null) {
            return ResponseEntity.ok(item);
        }
        return ResponseEntity.notFound().build();
    }

    @PostMapping
    public ResponseEntity<?> addItem(@RequestBody CatalogItem item) {
        if (!catalogService.validateItem(item)) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Name and description cannot be empty");
            return ResponseEntity.badRequest().body(error);
        }
        CatalogItem created = catalogService.addItem(item);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateItem(@PathVariable int id, @RequestBody CatalogItem item) {
        if (!catalogService.validateItem(item)) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Name and description cannot be empty");
            return ResponseEntity.badRequest().body(error);
        }
        CatalogItem updated = catalogService.updateItem(id, item);
        if (updated != null) {
            return ResponseEntity.ok(updated);
        }
        return ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteItem(@PathVariable int id) {
        boolean deleted = catalogService.deleteItem(id);
        if (deleted) {
            Map<String, String> response = new HashMap<>();
            response.put("message", "Item deleted successfully");
            return ResponseEntity.ok(response);
        }
        return ResponseEntity.notFound().build();
    }
}
