"""User, administrator, and customer models."""


class User:
    def __init__(self, name: str, username: str, password: str) -> None:
        if not name.strip() or not username.strip() or not password:
            raise ValueError("Name, username, and password are required.")
        self.name = name.strip()
        self.username = username.strip()
        self.password = password

    def show_info(self) -> None:
        print(f"Name: {self.name}")
        print(f"Username: {self.username}")


class Admin(User):
    def __init__(self, name: str, username: str, password: str, employee_id: str) -> None:
        super().__init__(name, username, password)
        self.employee_id = employee_id


class Customer(User):
    def __init__(
        self,
        name: str,
        username: str,
        password: str,
        phone: str,
        purchase_history: list | None = None,
    ) -> None:
        super().__init__(name, username, password)
        self.phone = phone
        self.purchase_history = list(purchase_history or [])

    def show_purchase_history(self) -> None:
        if not self.purchase_history:
            print("No purchase history found!")
            return

        print("\n====== PURCHASE HISTORY ======")
        for index, purchase in enumerate(self.purchase_history, start=1):
            print(f"\nPurchase #{index} - {purchase.get('date', 'Date unavailable')}")
            for item in purchase.get("items", []):
                print(
                    f"Product: {item.get('product_name', 'Unknown')} | "
                    f"Quantity: {item.get('quantity', 0)} | "
                    f"Price: {item.get('price', 0)} | "
                    f"Subtotal: {item.get('subtotal', 0)}"
                )
            print(f"Total: {purchase.get('total', 0)}")
