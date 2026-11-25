"""Automated tests for Mini Store."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import store as store_module
import services.user_manager as user_manager_module
from models.cart import Cart
from models.cartitem import CartItem
from models.product import Product
from models.user import Customer
from services.user_manager import UserManager
from store import Store


class MiniStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.products_path = self.temp_path / "products.json"
        self.users_path = self.temp_path / "users.json"
        self.products_patch = patch.object(store_module, "DATA_FILE", self.products_path)
        self.users_patch = patch.object(user_manager_module, "USER_DATA_FILE", self.users_path)
        self.products_patch.start()
        self.users_patch.start()
        self.addCleanup(self.products_patch.stop)
        self.addCleanup(self.users_patch.stop)
        self.store = Store()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_product_validation(self):
        with self.assertRaises(ValueError):
            Product("", 1, 1)
        with self.assertRaises(ValueError):
            Product("Pen", -1, 1)
        with self.assertRaises(ValueError):
            Product("Pen", 1, -1)
        with self.assertRaises(ValueError):
            Product("Pen", 1, 1.5)

    def test_add_product_persists_category_and_stock(self):
        self.assertTrue(self.store.add_product("Laptop", 1000, 4, "Electronics"))
        reloaded = Store()
        product = reloaded.find_product("laptop")
        self.assertIsNotNone(product)
        self.assertEqual(product.category, "Electronics")
        self.assertEqual(product.stock, 4)

    def test_duplicate_product_is_rejected(self):
        self.store.add_product("Mouse", 20, 5, "Accessories")
        self.assertFalse(self.store.add_product("mouse", 22, 7, "Other"))
        self.assertEqual(len(self.store.products), 1)

    def test_category_listing(self):
        self.store.add_product("Mouse", 20, 5, "Accessories")
        self.store.add_product("Laptop", 1000, 2, "Electronics")
        self.assertEqual(self.store.list_categories(), ["Accessories", "Electronics"])
        self.assertTrue(self.store.list_products_by_category("accessories"))
        self.assertFalse(self.store.list_products_by_category("missing"))

    def test_update_and_remove_persist(self):
        self.store.add_product("Mouse", 20, 5)
        self.assertTrue(self.store.update_stock("Mouse", 9))
        self.assertEqual(Store().find_product("Mouse").stock, 9)
        self.assertTrue(self.store.remove_product("Mouse"))
        self.assertIsNone(Store().find_product("Mouse"))

    def test_cart_add_update_remove_and_cancel_restore_stock(self):
        self.store.add_product("Mouse", 20, 10)
        product = self.store.find_product("Mouse")
        cart = Cart(self.store)
        cart.add_item(CartItem(product, 3))
        self.assertEqual(product.stock, 7)
        self.assertTrue(cart.update_quantity("Mouse", 5))
        self.assertEqual(product.stock, 5)
        self.assertTrue(cart.update_quantity("Mouse", 2))
        self.assertEqual(product.stock, 8)
        self.assertTrue(cart.remove_item("Mouse"))
        self.assertEqual(product.stock, 10)
        cart.add_item(CartItem(product, 4))
        cart.cancel()
        self.assertEqual(product.stock, 10)
        self.assertEqual(cart.items, [])

    def test_cart_rejects_overstock_and_invalid_quantity(self):
        self.store.add_product("Mouse", 20, 2)
        product = self.store.find_product("Mouse")
        with self.assertRaises(ValueError):
            CartItem(product, 3)
        with self.assertRaises(ValueError):
            CartItem(product, 0)

    def test_checkout_persists_stock_and_purchase_history(self):
        self.store.add_product("Mouse", 20, 5, "Accessories")
        product = self.store.find_product("Mouse")
        cart = Cart(self.store)
        cart.add_item(CartItem(product, 2))
        customer = Customer("Test User", "test", "pass", "000")
        self.assertTrue(cart.checkout(customer))
        self.assertEqual(product.stock, 3)
        self.assertEqual(len(customer.purchase_history), 1)
        self.assertEqual(customer.purchase_history[0]["total"], 40)
        self.assertEqual(Store().find_product("Mouse").stock, 3)
        self.assertEqual(cart.items, [])

    def test_users_default_admin_registration_and_persistence(self):
        manager = UserManager()
        admin = manager.login("admin", "1234")
        self.assertIsNotNone(admin)
        self.assertTrue(manager.logout())
        customer = Customer("Test User", "testuser", "pass123", "000")
        self.assertTrue(manager.register_user(customer))
        self.assertFalse(manager.register_user(Customer("Other", "TESTUSER", "x", "111")))
        reloaded = UserManager()
        logged_in = reloaded.login("testuser", "pass123")
        self.assertIsNotNone(logged_in)
        self.assertEqual(logged_in.phone, "000")

    def test_password_change_persists(self):
        manager = UserManager()
        self.assertIsNotNone(manager.login("admin", "1234"))
        self.assertTrue(manager.change_password("1234", "newpass"))
        reloaded = UserManager()
        self.assertIsNotNone(reloaded.login("admin", "newpass"))
        self.assertIsNone(reloaded.login("admin", "1234"))

    def test_purchase_history_persists(self):
        manager = UserManager()
        customer = Customer("Test User", "buyer", "pass", "000")
        manager.register_user(customer)
        customer.purchase_history.append({"date": "today", "items": [], "total": 0})
        manager.save_users()
        reloaded = UserManager()
        buyer = reloaded.find_user("buyer")
        self.assertEqual(len(buyer.purchase_history), 1)
        self.assertEqual(buyer.purchase_history[0]["date"], "today")


if __name__ == "__main__":
    unittest.main()
