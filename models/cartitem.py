"""Cart item model."""

from models.product import Product


class CartItem:
    """A product and the quantity reserved in a shopping cart."""

    def __init__(self, product: Product, quantity: int) -> None:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} units of {product.name} are available."
            )
        self.product = product
        self.quantity = quantity

    def calculate_total(self) -> float:
        return self.product.price * self.quantity
