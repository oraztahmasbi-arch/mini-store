"""User registration, authentication, and JSON persistence."""

import json
import os
from pathlib import Path

from models.user import Admin, Customer

USER_DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "users.json"


class UserManager:
    def __init__(self) -> None:
        self.users: list[Admin | Customer] = []
        self.current_user = None
        self.load_users()
        self._ensure_default_admin()

    def load_users(self) -> None:
        if not USER_DATA_FILE.exists():
            return
        try:
            with USER_DATA_FILE.open("r", encoding="utf-8") as file:
                users_data = json.load(file)
            if not isinstance(users_data, list):
                raise ValueError("The users JSON must contain a list.")
            loaded_users = []
            for item in users_data:
                role = item.get("role")
                if role == "admin":
                    user = Admin(
                        item["name"], item["username"], item["password"],
                        item.get("employee_id", "")
                    )
                elif role == "customer":
                    user = Customer(
                        item["name"], item["username"], item["password"],
                        item.get("phone", ""), item.get("purchase_history", [])
                    )
                else:
                    raise ValueError(f"Unknown user role: {role}")
                loaded_users.append(user)
            self.users = loaded_users
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ValueError(f"Could not read user data from {USER_DATA_FILE}: {error}") from error

    def save_users(self) -> None:
        USER_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        users_data = []
        for user in self.users:
            if isinstance(user, Admin):
                users_data.append({
                    "role": "admin",
                    "name": user.name,
                    "username": user.username,
                    "password": user.password,
                    "employee_id": user.employee_id,
                })
            elif isinstance(user, Customer):
                users_data.append({
                    "role": "customer",
                    "name": user.name,
                    "username": user.username,
                    "password": user.password,
                    "phone": user.phone,
                    "purchase_history": user.purchase_history,
                })
        temporary_file = USER_DATA_FILE.with_suffix(USER_DATA_FILE.suffix + ".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(users_data, file, ensure_ascii=False, indent=4)
        os.replace(temporary_file, USER_DATA_FILE)

    def _ensure_default_admin(self) -> None:
        existing_admin = any(
            isinstance(user, Admin) and user.username.casefold() == "admin"
            for user in self.users
        )
        if not existing_admin:
            self.users.append(Admin("Manager", "admin", "1234", "A01"))
            self.save_users()

    def register_user(self, user: Customer) -> bool:
        if not isinstance(user, Customer):
            print("Only customer accounts can be registered here.")
            return False
        if self.find_user(user.username) is not None:
            print("Username already exists!")
            return False
        self.users.append(user)
        try:
            self.save_users()
        except Exception:
            self.users.remove(user)
            raise
        print("User registered successfully!")
        return True

    def find_user(self, username: str):
        normalized_username = username.strip().casefold()
        for user in self.users:
            if user.username.casefold() == normalized_username:
                return user
        return None

    def login(self, username: str, password: str):
        user = self.find_user(username)
        if user is None:
            print("User not found!")
            return None
        if user.password != password:
            print("Incorrect password!")
            return None
        self.current_user = user
        print(f"Welcome {user.name}!")
        return user

    def logout(self) -> bool:
        if self.current_user is None:
            print("No user is currently logged in!")
            return False
        print(f"Goodbye {self.current_user.name}!")
        self.current_user = None
        return True

    def change_password(self, old_password: str, new_password: str) -> bool:
        if self.current_user is None:
            print("Please login first.")
            return False
        if self.current_user.password != old_password:
            print("Old password is incorrect.")
            return False
        if not new_password.strip():
            print("New password cannot be empty!")
            return False
        old_value = self.current_user.password
        self.current_user.password = new_password
        try:
            self.save_users()
        except Exception:
            self.current_user.password = old_value
            raise
        print("Password changed successfully!")
        return True
