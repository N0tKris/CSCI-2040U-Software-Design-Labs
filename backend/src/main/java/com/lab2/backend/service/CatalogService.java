package com.lab2.backend.service;

import com.lab2.backend.model.CatalogItem;
import org.springframework.stereotype.Service;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

@Service
public class CatalogService {
    // Path to CSV file (relative to where the backend runs - the project root)
    private static final String CSV_FILE = "../catalog.csv";
    private static final String CSV_DELIMITER = ",";

    /**
     * Milestone 1: Read all items from CSV file and parse into list of objects
     */
    public List<CatalogItem> getAllItems() {
        List<CatalogItem> items = new ArrayList<>();
        File file = new File(CSV_FILE);
        
        System.out.println("Reading CSV from: " + file.getAbsolutePath());
        
        if (!file.exists()) {
            System.out.println("CSV file not found, creating with sample data...");
            createSampleData();
        }
        
        try (BufferedReader br = new BufferedReader(new FileReader(CSV_FILE))) {
            String line;
            boolean isHeader = true;
            while ((line = br.readLine()) != null) {
                if (isHeader) {
                    isHeader = false;
                    continue; // Skip header row
                }
                String[] values = line.split(CSV_DELIMITER, -1);
                if (values.length >= 3) {
                    int id = Integer.parseInt(values[0].trim());
                    String name = values[1].trim();
                    String description = values[2].trim();
                    items.add(new CatalogItem(id, name, description));
                }
            }
            System.out.println("Loaded " + items.size() + " items from CSV");
        } catch (IOException e) {
            System.err.println("Error reading CSV: " + e.getMessage());
            e.printStackTrace();
        }
        return items;
    }

    /**
     * Get a single item by ID
     */
    public CatalogItem getItemById(int id) {
        return getAllItems().stream()
                .filter(item -> item.getId() == id)
                .findFirst()
                .orElse(null);
    }

    /**
     * Milestone 3: Add a new item with auto-generated ID
     */
    public CatalogItem addItem(CatalogItem newItem) {
        List<CatalogItem> items = getAllItems();
        
        // Generate new ID (max + 1)
        int maxId = items.stream()
                .mapToInt(CatalogItem::getId)
                .max()
                .orElse(0);
        newItem.setId(maxId + 1);
        
        items.add(newItem);
        saveAllItems(items);
        System.out.println("Added new item with ID: " + newItem.getId());
        return newItem;
    }

    /**
     * Milestone 3: Update an existing item
     */
    public CatalogItem updateItem(int id, CatalogItem updatedItem) {
        List<CatalogItem> items = getAllItems();
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).getId() == id) {
                updatedItem.setId(id);
                items.set(i, updatedItem);
                saveAllItems(items);
                System.out.println("Updated item ID: " + id);
                return updatedItem;
            }
        }
        return null;
    }

    /**
     * Delete an item by ID
     */
    public boolean deleteItem(int id) {
        List<CatalogItem> items = getAllItems();
        boolean removed = items.removeIf(item -> item.getId() == id);
        if (removed) {
            saveAllItems(items);
            System.out.println("Deleted item ID: " + id);
        }
        return removed;
    }

    /**
     * Milestone 4: Save all items back to CSV file
     */
    private void saveAllItems(List<CatalogItem> items) {
        try (PrintWriter pw = new PrintWriter(new FileWriter(CSV_FILE))) {
            pw.println("ID,Name,Description");
            for (CatalogItem item : items) {
                pw.println(item.getId() + CSV_DELIMITER + 
                          item.getName() + CSV_DELIMITER + 
                          item.getDescription());
            }
            System.out.println("Saved " + items.size() + " items to CSV");
        } catch (IOException e) {
            System.err.println("Error saving CSV: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Milestone 3: Validate item input (non-empty fields)
     */
    public boolean validateItem(CatalogItem item) {
        return item.getName() != null && !item.getName().trim().isEmpty() &&
               item.getDescription() != null && !item.getDescription().trim().isEmpty();
    }

    /**
     * Create sample data if CSV doesn't exist
     */
    private void createSampleData() {
        try (PrintWriter pw = new PrintWriter(new FileWriter(CSV_FILE))) {
            pw.println("ID,Name,Description");
            pw.println("1,Laptop,Dell XPS 15 - High performance laptop");
            pw.println("2,Mouse,Logitech MX Master 3 - Wireless mouse");
            pw.println("3,Keyboard,Mechanical keyboard with RGB lighting");
            pw.println("4,Monitor,27-inch 4K display");
            pw.println("5,Headphones,Sony WH-1000XM4 - Noise cancelling");
            System.out.println("Created sample CSV data");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
