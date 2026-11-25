"""Shopping cart and checkout logic."""

from datetime import datetime
from typing import Callable, Optional

from models.cartitem import CartItem


class Cart:
    """Hold cart items and temporarily reserve their stock."""

    def __init__(self, store) -> None:
        self.store = store
        self.items: list[CartItem] = []

    def add_item(self, item: CartItem) -> None:
        """Reserve stock and add an item to the cart."""
        product = item.product
        if item.quantity > product.stock:
            raise ValueError(f"Only {product.stock} units of {product.name} are available.")

        for existing in self.items:
            if existing.product.name.casefold() == product.name.casefold():
                existing.quantity += item.quantity
                product.stock -= item.quantity
                return

        product.stock -= item.quantity
        self.items.append(item)

    def total(self) -> float:
        return sum(item.calculate_total() for item in self.items)

    def show_items(self) -> None:
        if not self.items:
            print("Your cart is empty!")
            return
        for item in self.items:
            print(
                f"Product: {item.product.name} | "
                f"Quantity: {item.quantity} | "
                f"Price: {item.product.price:.2f} | "
                f"Subtotal: {item.calculate_total():.2f}"
            )

    def update_quantity(self, product_name: str, new_quantity: int) -> bool:
        if type(new_quantity) is not int or new_quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        for item in self.items:
            if item.product.name.casefold() == product_name.strip().casefold():
                difference = new_quantity - item.quantity
                if difference > item.product.stock:
                    raise ValueError(
                        f"Only {item.product.stock} additional units of "
                        f"{item.product.name} are available."
                    )
                item.product.stock -= difference
                item.quantity = new_quantity
                return True
        return False

    def remove_item(self, product_name: str) -> bool:
        for item in self.items:
            if item.product.name.casefold() == product_name.strip().casefold():
                item.product.stock += item.quantity
                self.items.remove(item)
                return True
        return False

    def cancel(self) -> None:
        """Release all reserved stock if the cart is abandoned."""
        for item in self.items:
            item.product.stock += item.quantity
        self.items.clear()

    def checkout(
        self,
        customer,
        save_customer: Optional[Callable[[], None]] = None,
    ) -> bool:
        """Complete a purchase and persist stock and (optionally) customer data."""
        if not self.items:
            print("Your cart is empty!")
            return False

        purchase = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "items": [
                {
                    "product_name": item.product.name,
                    "category": item.product.category,
                    "quantity": item.quantity,
                    "price": item.product.price,
                    "subtotal": item.calculate_total(),
                }
                for item in self.items
            ],
            "total": self.total(),
        }

        customer.purchase_history.append(purchase)
        try:
            self.store.save_products()
            if save_customer is not None:
                save_customer()
        except Exception as error:
            customer.purchase_history.pop()
            self.cancel()
            # Persist the restored stock if the first save had already succeeded.
            try:
                self.store.save_products()
            except Exception:
                pass
            if save_customer is not None:
                try:
                    save_customer()
                except Exception:
                    pass
            print(f"Checkout could not be saved: {error}")
            return False

        print("\n====== RECEIPT ======")
        self.show_items()
        print(f"Total amount: {purchase['total']:.2f}")
        print("Purchase saved successfully. Thank you!")
        self.items.clear()
        return True
