"""Command-line entry point for Mini Store."""

from models.cart import Cart
from models.cartitem import CartItem
from models.user import Admin, Customer
from services.user_manager import UserManager
from store import Store


def _show_categories(store: Store) -> None:
    categories = store.list_categories()
    if not categories:
        print("No categories available.")
        return
    print("Available categories:")
    for category in categories:
        print(f"- {category}")


def _show_by_category(store: Store) -> None:
    _show_categories(store)
    category = input("Category name: ").strip()
    if category:
        store.list_products_by_category(category)


def _change_password(user_manager: UserManager) -> None:
    old_password = input("Current password: ")
    new_password = input("New password: ")
    user_manager.change_password(old_password, new_password)


def admin_menu(store: Store, user_manager: UserManager) -> None:
    while True:
        print("\n====== ADMIN MENU ======")
        print("1. Show products")
        print("2. Show products by category")
        print("3. Add product")
        print("4. Update stock")
        print("5. Remove product")
        print("6. Change password")
        print("7. Logout")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            store.list_products()
        elif choice == "2":
            _show_by_category(store)
        elif choice == "3":
            name = input("Product name: ").strip()
            category = input("Category (press Enter for General): ").strip() or "General"
            try:
                price = float(input("Price: "))
                stock = int(input("Stock: "))
                store.add_product(name, price, stock, category)
            except ValueError as error:
                print(f"Invalid product details: {error}")
        elif choice == "4":
            name = input("Product name: ").strip()
            try:
                new_stock = int(input("New stock: "))
                store.update_stock(name, new_stock)
            except ValueError:
                print("Stock must be a whole number.")
        elif choice == "5":
            store.remove_product(input("Product name: ").strip())
        elif choice == "6":
            _change_password(user_manager)
        elif choice == "7":
            user_manager.logout()
            return
        else:
            print("Invalid choice!")


def customer_menu(customer: Customer, store: Store, user_manager: UserManager) -> None:
    cart = Cart(store)
    try:
        while True:
            print("\n====== CUSTOMER MENU ======")
            print("1. Show products")
            print("2. Browse products by category")
            print("3. Add product to cart")
            print("4. Show cart")
            print("5. Update cart quantity")
            print("6. Remove product from cart")
            print("7. Checkout")
            print("8. Purchase history")
            print("9. Change password")
            print("10. Logout")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                store.list_products()
            elif choice == "2":
                _show_by_category(store)
            elif choice == "3":
                name = input("Product name: ").strip()
                product = store.find_product(name)
                if product is None:
                    print("Product not found!")
                    continue
                try:
                    quantity = int(input("Quantity: "))
                    cart.add_item(CartItem(product, quantity))
                    print("Product added to cart!")
                except ValueError as error:
                    print(error)
            elif choice == "4":
                cart.show_items()
                if cart.items:
                    print(f"Total: {cart.total():.2f}")
            elif choice == "5":
                name = input("Product name: ").strip()
                try:
                    quantity = int(input("New quantity: "))
                    if cart.update_quantity(name, quantity):
                        print("Cart quantity updated!")
                    else:
                        print("Product not found in cart!")
                except ValueError as error:
                    print(error)
            elif choice == "6":
                name = input("Product name: ").strip()
                if cart.remove_item(name):
                    print("Product removed from cart!")
                else:
                    print("Product not found in cart!")
            elif choice == "7":
                cart.checkout(customer, save_customer=user_manager.save_users)
            elif choice == "8":
                customer.show_purchase_history()
            elif choice == "9":
                _change_password(user_manager)
            elif choice == "10":
                user_manager.logout()
                return
            else:
                print("Invalid choice!")
    finally:
        # Any items not checked out are released back to the available stock.
        if cart.items:
            cart.cancel()
            print("Unpurchased cart items were returned to stock.")


def main() -> None:
    store = Store()
    user_manager = UserManager()

    while True:
        print("\n====== MINI STORE ======")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Name: ").strip()
            username = input("Username: ").strip()
            password = input("Password: ")
            phone = input("Phone: ").strip()
            try:
                user_manager.register_user(Customer(name, username, password, phone))
            except ValueError as error:
                print(error)
        elif choice == "2":
            username = input("Username: ").strip()
            password = input("Password: ")
            logged_in_user = user_manager.login(username, password)
            if isinstance(logged_in_user, Admin):
                admin_menu(store, user_manager)
            elif isinstance(logged_in_user, Customer):
                customer_menu(logged_in_user, store, user_manager)
        elif choice == "3":
            print("Thank you for using Mini Store!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
