import requests
import sys

BACKEND_URL = "http://localhost:8080/api/catalog"

def print_menu():
    print("\n" + "="*50)
    print("CATALOG MANAGEMENT SYSTEM")
    print("="*50)
    print("1. View all items")
    print("2. View item details")
    print("3. Add new item")
    print("4. Edit item")
    print("5. Delete item")
    print("6. Exit")
    print("="*50)

def view_all_items():
    try:
        response = requests.get(BACKEND_URL)
        items = response.json()
        
        if not items:
            print("\nNo items in catalog.")
            return
        
        print("\n" + "="*70)
        print(f"{'ID':<5} {'Name':<25} {'Description':<40}")
        print("="*70)
        for item in items:
            print(f"{item['id']:<5} {item['name']:<25} {item['description']:<40}")
        print("="*70)
    except Exception as e:
        print(f"\nError fetching items: {e}")

def view_item_details():
    item_id = input("\nEnter item ID: ").strip()
    try:
        response = requests.get(f"{BACKEND_URL}/{item_id}")
        if response.status_code == 200:
            item = response.json()
            print("\n" + "="*50)
            print(f"ID: {item['id']}")
            print(f"Name: {item['name']}")
            print(f"Description: {item['description']}")
            print("="*50)
        else:
            print(f"\nItem not found.")
    except Exception as e:
        print(f"\nError: {e}")

def add_item():
    print("\n--- Add New Item ---")
    name = input("Enter name: ").strip()
    description = input("Enter description: ").strip()
    
    if not name or not description:
        print("\nError: Name and description cannot be empty!")
        return
    
    try:
        response = requests.post(BACKEND_URL, json={
            "name": name,
            "description": description
        })
        if response.status_code == 201:
            item = response.json()
            print(f"\nItem added successfully! (ID: {item['id']})")
        else:
            print(f"\nError adding item: {response.text}")
    except Exception as e:
        print(f"\nError: {e}")

def edit_item():
    item_id = input("\nEnter item ID to edit: ").strip()
    
    # First, get the current item
    try:
        response = requests.get(f"{BACKEND_URL}/{item_id}")
        if response.status_code != 200:
            print(f"\nItem not found.")
            return
        
        current_item = response.json()
        print(f"\nCurrent Name: {current_item['name']}")
        print(f"Current Description: {current_item['description']}")
        
        name = input("\nEnter new name (press Enter to keep current): ").strip()
        description = input("Enter new description (press Enter to keep current): ").strip()
        
        # Use current values if not provided
        if not name:
            name = current_item['name']
        if not description:
            description = current_item['description']
        
        response = requests.put(f"{BACKEND_URL}/{item_id}", json={
            "name": name,
            "description": description
        })
        
        if response.status_code == 200:
            print("\nItem updated successfully!")
        else:
            print(f"\nError updating item: {response.text}")
    except Exception as e:
        print(f"\nError: {e}")

def delete_item():
    item_id = input("\nEnter item ID to delete: ").strip()
    confirm = input(f"Are you sure you want to delete item {item_id}? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\nDeletion cancelled.")
        return
    
    try:
        response = requests.delete(f"{BACKEND_URL}/{item_id}")
        if response.status_code == 200:
            print("\nItem deleted successfully!")
        else:
            print(f"\nError deleting item.")
    except Exception as e:
        print(f"\nError: {e}")

def main():
    print("\nStarting Catalog Management System...")
    print("Checking backend connection...")
    
    try:
        requests.get(BACKEND_URL, timeout=2)
        print("Connected to backend at", BACKEND_URL)
    except:
        print("\nERROR: Cannot connect to backend. Please start the backend first:")
        print("   cd backend && ./mvnw spring-boot:run")
        sys.exit(1)
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            view_all_items()
        elif choice == '2':
            view_item_details()
        elif choice == '3':
            add_item()
        elif choice == '4':
            edit_item()
        elif choice == '5':
            delete_item()
        elif choice == '6':
            print("\nExiting Catalog Management System. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
