"""Persistent product catalogue for Mini Store."""

import json
import os
from pathlib import Path

from models.product import Product

DATA_FILE = Path(__file__).resolve().parent / "data" / "products.json"


class Store:
    """Manage products and persist them in a JSON file."""

    def __init__(self) -> None:
        self.products: list[Product] = []
        self.load_products()

    def save_products(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        products_data = [
            {
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "category": product.category,
            }
            for product in self.products
        ]
        temporary_file = DATA_FILE.with_suffix(DATA_FILE.suffix + ".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(products_data, file, ensure_ascii=False, indent=4)
        os.replace(temporary_file, DATA_FILE)

    def load_products(self) -> None:
        if not DATA_FILE.exists():
            return
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                products_data = json.load(file)
            if not isinstance(products_data, list):
                raise ValueError("The products JSON must contain a list.")
            loaded_products = []
            for item in products_data:
                loaded_products.append(
                    Product(
                        item["name"],
                        item["price"],
                        item["stock"],
                        item.get("category", "General"),
                    )
                )
            self.products = loaded_products
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ValueError(f"Could not read product data from {DATA_FILE}: {error}") from error

    def add_product(
        self,
        name: str,
        price: float,
        stock: int,
        category: str = "General",
    ) -> bool:
        if self.find_product(name) is not None:
            print("A product with this name already exists!")
            return False
        new_product = Product(name, price, stock, category)
        self.products.append(new_product)
        try:
            self.save_products()
        except Exception:
            self.products.remove(new_product)
            raise
        print("Product added successfully!")
        return True

    def list_products(self) -> None:
        if not self.products:
            print("No products available.")
            return
        for product in self.products:
            product.show_info()
            print("-" * 30)

    def find_product(self, name: str) -> Product | None:
        normalized_name = name.strip().casefold()
        for product in self.products:
            if product.name.casefold() == normalized_name:
                return product
        return None

    def list_categories(self) -> list[str]:
        return sorted({product.category for product in self.products}, key=str.casefold)

    def list_products_by_category(self, category: str) -> bool:
        matching_products = [
            product for product in self.products
            if product.category.casefold() == category.strip().casefold()
        ]
        if not matching_products:
            print("No products found in this category.")
            return False
        for product in matching_products:
            product.show_info()
            print("-" * 30)
        return True

    def remove_product(self, name: str) -> bool:
        product = self.find_product(name)
        if product is None:
            print("Product not found!")
            return False
        self.products.remove(product)
        try:
            self.save_products()
        except Exception:
            self.products.append(product)
            raise
        print("Product removed successfully!")
        return True

    def update_stock(self, name: str, new_stock: int) -> bool:
        if type(new_stock) is not int or new_stock < 0:
            print("Stock must be a non-negative integer!")
            return False
        product = self.find_product(name)
        if product is None:
            print("Product not found!")
            return False
        old_stock = product.stock
        product.stock = new_stock
        try:
            self.save_products()
        except Exception:
            product.stock = old_stock
            raise
        print("Stock updated successfully!")
        return True
