# PlateRate Filter Tests

Simple unit tests for the restaurant filtering functionality.

## Overview

The test suite covers the three main filtering functions:

- **`extractUniqueCuisines()`** - Extracts unique cuisine types from restaurants
- **`extractUniqueDietaryTags()`** - Extracts unique dietary tags from restaurants
- **`applyFilters()`** - Applies combined filters (search, cuisine, dietary tags)

## Test Categories

### 1. Extract Unique Cuisines (3 tests)
- Extract all unique cuisines
- Verify cuisines are sorted
- Handle empty restaurant array

### 2. Extract Unique Dietary Tags (3 tests)
- Extract all unique tags
- Trim whitespace from tags
- Handle empty dietary tags

### 3. Filter by Cuisine (3 tests)
- Filter by single cuisine
- Filter by different cuisines
- Return all when no cuisine selected

### 4. Filter by Dietary Tags (3 tests)
- Filter by single tag
- Filter by multiple tags (AND logic)
- Return empty when no matches

### 5. Filter by Search Query (4 tests)
- Search by restaurant name
- Search by cuisine type
- Search by location
- Case-insensitive search

### 6. Combined Filters (4 tests)
- Search + Cuisine
- Cuisine + Dietary Tags
- All three filters together
- Too restrictive filters

### 7. Edge Cases (3 tests)
- Empty restaurant array
- Undefined dietary tags
- No filters applied

**Total: 23 tests**

## Running Tests

### Install dependencies
```bash
cd frontend
npm install
```

### Run all tests
```bash
npm test
```

### Run tests in watch mode (auto-rerun on changes)
```bash
npm run test:watch
```

### Run with coverage report
```bash
npm run test:coverage
```

## Expected Output

All 23 tests should pass:
- ✓ 3 tests for extractUniqueCuisines
- ✓ 3 tests for extractUniqueDietaryTags
- ✓ 3 tests for cuisine filtering
- ✓ 3 tests for dietary tag filtering
- ✓ 4 tests for search filtering
- ✓ 4 tests for combined filtering
- ✓ 3 tests for edge cases

## Test Data

Tests use 4 mock restaurants:
1. **Italian Bistro** - Italian, vegan, gluten-free
2. **Sushi Palace** - Japanese, pescatarian
3. **Burger King** - American, vegan
4. **Taco Stand** - Mexican, vegan, gluten-free, halal

## Notes

These tests verify the core filtering logic in isolation. For integration testing, you would test these functions within the actual user_dashboard.html context with real API responses.

Tests follow the AAA pattern (Arrange, Act, Assert) for clarity and maintainability.
