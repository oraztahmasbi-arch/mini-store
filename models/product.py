"""Product model for Mini Store."""

import math


class Product:
    """Represent a product available in the store."""

    def __init__(
        self,
        name: str,
        price: float,
        stock: int,
        category: str = "General",
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Product name cannot be empty.")
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise ValueError("Price must be a number.")
        if not math.isfinite(float(price)) or price < 0:
            raise ValueError("Price must be a finite non-negative number.")
        if type(stock) is not int or stock < 0:
            raise ValueError("Stock must be a non-negative integer.")
        if not isinstance(category, str):
            raise ValueError("Category must be text.")

        self.name = name.strip()
        self.price = float(price)
        self.stock = stock
        self.category = category.strip() or "General"

    def show_info(self) -> None:
        """Print product details."""
        print(f"Product: {self.name}")
        print(f"Category: {self.category}")
        print(f"Price: {self.price:.2f}")
        print(f"Stock: {self.stock}")
