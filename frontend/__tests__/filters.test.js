// __tests__/filters.test.js
// Simple Jest tests for restaurant filtering functions

/**
 * Mock restaurant data for testing
 */
const mockRestaurants = [
  {
    id: 1,
    name: 'Italian Bistro',
    cuisine: 'Italian',
    location: 'Downtown',
    dietaryTags: 'vegan,gluten-free',
    menuItems: [
      { itemName: 'Pasta Primavera', dietaryTags: 'Vegetarian' },
      { itemName: 'Garden Salad', dietaryTags: 'Vegan, Gluten-Free' }
    ],
    stars: 4.5
  },
  {
    id: 2,
    name: 'Sushi Palace',
    cuisine: 'Japanese',
    location: 'Midtown',
    dietaryTags: 'pescatarian',
    stars: 4.2
  },
  {
    id: 3,
    name: 'Burger King',
    cuisine: 'American',
    location: 'Downtown',
    dietaryTags: 'vegan',
    menuItems: [
      { itemName: 'Impossible Burger', dietaryTags: 'Vegan' }
    ],
    stars: 3.8
  },
  {
    id: 4,
    name: 'Taco Stand',
    cuisine: 'Mexican',
    location: 'Uptown',
    dietaryTags: 'vegan,gluten-free,halal',
    stars: 4.0
  }
];

/**
 * Extract unique cuisines from restaurants
 */
function extractUniqueCuisines(restaurants) {
  const cuisines = new Set();
  restaurants.forEach(r => {
    if (r.cuisine) cuisines.add(r.cuisine);
  });
  return Array.from(cuisines).sort();
}

/**
 * Extract unique dietary tags from restaurants
 */
function extractUniqueDietaryTags(restaurants) {
  const tags = new Set();
  restaurants.forEach(r => {
    const tagString = r.dietaryTags || r.dietary_tags || '';
    if (tagString) {
      tagString.split(',').forEach(tag => {
        const trimmed = tag.trim();
        if (trimmed) tags.add(trimmed);
      });
    }
  });
  return Array.from(tags).sort();
}

function getCanonicalDietaryTagsForMenuItem(menuItem) {
  const tagString = menuItem.dietaryTags || menuItem.dietary_tags || '';
  if (!tagString) return [];
  return tagString
    .split(',')
    .map(tag => tag.trim().toLowerCase())
    .filter(Boolean);
}

function restaurantMatchesDietaryTags(restaurant, selectedDietaryTags) {
  if (selectedDietaryTags.length === 0) return true;

  const restaurantTags = (restaurant.dietaryTags || restaurant.dietary_tags || '')
    .toLowerCase().split(',').map(t => t.trim()).filter(Boolean);
  const restaurantMatches = selectedDietaryTags.every(tag =>
    restaurantTags.includes(tag.toLowerCase())
  );
  if (restaurantMatches) return true;

  const menuItems = restaurant.menuItems || restaurant.menu_items || [];
  return menuItems.some(item => {
    const itemTags = getCanonicalDietaryTagsForMenuItem(item);
    return selectedDietaryTags.every(tag => itemTags.includes(tag.toLowerCase()));
  });
}

/**
 * Apply filters to restaurants
 */
function applyFilters(restaurants, searchQuery, selectedCuisine, selectedDietaryTags) {
  return restaurants.filter(r => {
    // Filter by cuisine (exact match)
    if (selectedCuisine && (r.cuisine || '').toLowerCase() !== selectedCuisine.toLowerCase()) {
      return false;
    }

    // Filter by dietary tags (all selected tags must be present)
    if (selectedDietaryTags.length > 0) {
      if (!restaurantMatchesDietaryTags(r, selectedDietaryTags)) return false;
    }

    // Filter by search query
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matches = (r.name || '').toLowerCase().includes(q) ||
        (r.cuisine || '').toLowerCase().includes(q) ||
        (r.location || '').toLowerCase().includes(q) ||
        (r.dietaryTags || r.dietary_tags || '').toLowerCase().includes(q);
      if (!matches) return false;
    }

    return true;
  });
}

function resolveImageUrl(rawUrl, backendUrl) {
  if (!rawUrl) return '';
  const value = String(rawUrl).trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  const base = String(backendUrl || '').replace(/\/$/, '');
  return value.startsWith('/') ? (base + value) : (base + '/' + value);
}

// ──────────────────────────────────────────────────────────────
// TESTS
// ──────────────────────────────────────────────────────────────

describe('Restaurant Filters', () => {

  // ── Extract Unique Cuisines Tests ──
  describe('extractUniqueCuisines', () => {
    test('should extract all unique cuisines', () => {
      const cuisines = extractUniqueCuisines(mockRestaurants);
      expect(cuisines).toEqual(['American', 'Italian', 'Japanese', 'Mexican']);
    });

    test('should return sorted cuisines', () => {
      const cuisines = extractUniqueCuisines(mockRestaurants);
      const sorted = cuisines.slice().sort();
      expect(cuisines).toEqual(sorted);
    });

    test('should handle empty restaurants array', () => {
      const cuisines = extractUniqueCuisines([]);
      expect(cuisines).toEqual([]);
    });
  });

  // ── Extract Unique Dietary Tags Tests ──
  describe('extractUniqueDietaryTags', () => {
    test('should extract all unique dietary tags', () => {
      const tags = extractUniqueDietaryTags(mockRestaurants);
      expect(tags).toEqual(['gluten-free', 'halal', 'pescatarian', 'vegan']);
    });

    test('should trim whitespace from tags', () => {
      const restaurants = [
        { dietaryTags: 'vegan, gluten-free , halal' }
      ];
      const tags = extractUniqueDietaryTags(restaurants);
      expect(tags).toEqual(['gluten-free', 'halal', 'vegan']);
    });

    test('should handle empty dietary tags', () => {
      const restaurants = [{ dietaryTags: '' }];
      const tags = extractUniqueDietaryTags(restaurants);
      expect(tags).toEqual([]);
    });
  });

  // ── Filter by Cuisine Tests ──
  describe('applyFilters - Cuisine Filter', () => {
    test('should filter by single cuisine', () => {
      const filtered = applyFilters(mockRestaurants, '', 'Italian', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Italian Bistro');
    });

    test('should filter by different cuisine', () => {
      const filtered = applyFilters(mockRestaurants, '', 'Japanese', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Sushi Palace');
    });

    test('should return all restaurants when no cuisine selected', () => {
      const filtered = applyFilters(mockRestaurants, '', '', []);
      expect(filtered.length).toBe(4);
    });
  });

  // ── Filter by Dietary Tags Tests ──
  describe('applyFilters - Dietary Tags Filter', () => {
    test('should filter by single dietary tag', () => {
      const filtered = applyFilters(mockRestaurants, '', '', ['vegan']);
      expect(filtered.length).toBe(3);
      expect(filtered.map(r => r.name)).toEqual(
        expect.arrayContaining(['Italian Bistro', 'Burger King', 'Taco Stand'])
      );
    });

    test('should match menu item dietary tags', () => {
      const filtered = applyFilters(mockRestaurants, '', '', ['gluten-free']);
      expect(filtered.map(r => r.name)).toEqual(
        expect.arrayContaining(['Italian Bistro', 'Taco Stand'])
      );
    });

    test('should filter by multiple tags (AND logic)', () => {
      const filtered = applyFilters(mockRestaurants, '', '', ['vegan', 'gluten-free']);
      expect(filtered.length).toBe(2);
      expect(filtered.map(r => r.name)).toEqual(
        expect.arrayContaining(['Italian Bistro', 'Taco Stand'])
      );
    });

    test('should return empty when no restaurants match all tags', () => {
      const filtered = applyFilters(mockRestaurants, '', '', ['vegan', 'pescatarian']);
      expect(filtered.length).toBe(0);
    });
  });

  // ── Filter by Search Query Tests ──
  describe('applyFilters - Search Query Filter', () => {
    test('should search by restaurant name', () => {
      const filtered = applyFilters(mockRestaurants, 'sushi', '', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Sushi Palace');
    });

    test('should search by cuisine', () => {
      const filtered = applyFilters(mockRestaurants, 'italian', '', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].cuisine).toBe('Italian');
    });

    test('should search by location', () => {
      const filtered = applyFilters(mockRestaurants, 'downtown', '', []);
      expect(filtered.length).toBe(2);
    });

    test('should be case-insensitive', () => {
      const filtered = applyFilters(mockRestaurants, 'BURGER', '', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Burger King');
    });
  });

  // ── Combined Filters Tests ──
  describe('applyFilters - Combined Filters', () => {
    test('should filter by search + cuisine', () => {
      const filtered = applyFilters(mockRestaurants, 'vegan', 'Italian', []);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Italian Bistro');
    });

    test('should filter by cuisine + dietary tags', () => {
      const filtered = applyFilters(mockRestaurants, '', 'Mexican', ['vegan', 'gluten-free']);
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Taco Stand');
    });

    test('should filter by all three: search + cuisine + tags', () => {
      const filtered = applyFilters(
        mockRestaurants,
        'taco',
        'Mexican',
        ['vegan']
      );
      expect(filtered.length).toBe(1);
      expect(filtered[0].name).toBe('Taco Stand');
    });

    test('should return empty when filters are too restrictive', () => {
      const filtered = applyFilters(
        mockRestaurants,
        'sushi',
        'Italian',
        ['vegan']
      );
      expect(filtered.length).toBe(0);
    });
  });

  // ── Edge Cases Tests ──
  describe('applyFilters - Edge Cases', () => {
    test('should handle empty restaurants array', () => {
      const filtered = applyFilters([], '', 'Italian', []);
      expect(filtered).toEqual([]);
    });

    test('should handle undefined dietary tags', () => {
      const restaurants = [
        { id: 1, name: 'Test', cuisine: 'Test', location: 'Test' }
      ];
      const filtered = applyFilters(restaurants, '', '', ['vegan']);
      expect(filtered.length).toBe(0);
    });

    test('should return all restaurants when no filters applied', () => {
      const filtered = applyFilters(mockRestaurants, '', '', []);
      expect(filtered.length).toBe(4);
    });
  });

  describe('resolveImageUrl', () => {
    test('should keep absolute yelp image urls unchanged', () => {
      const result = resolveImageUrl('https://images.yelpcdn.com/photo.jpg', 'http://localhost:8080');
      expect(result).toBe('https://images.yelpcdn.com/photo.jpg');
    });

    test('should prefix backend url for local upload paths', () => {
      const result = resolveImageUrl('/uploads/restaurant-1.jpg', 'http://localhost:8080/');
      expect(result).toBe('http://localhost:8080/uploads/restaurant-1.jpg');
    });
  });

});
