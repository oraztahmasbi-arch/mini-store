# Mini Store — Python OOP Project

A modular command-line store application built with Python, object-oriented programming, and JSON persistence.

## Requirements

- Python 3.10 or newer
- Python standard library only

## Run the application

Open a terminal in this directory and run:

```bash
python main.py
```

On Windows, `py main.py` is also supported.

## Demo administrator account

On first run, the application creates this local demo account if no administrator exists:

- Username: `admin`
- Password: `1234`

Change the demo password after logging in. This is an educational project: passwords are currently stored as plain text in the local JSON data file. Do not use this implementation with real users, real passwords, or sensitive customer information.

## Features

- Customer registration and login
- Default administrator account
- Product creation, listing, updating, and removal
- Product categories and category filtering
- Shopping cart with stock reservation and quantity updates
- Checkout receipt and purchase history
- JSON persistence for the product catalogue and local user records
- Automatic release of unpurchased cart items when a customer exits

## Project structure

```text
Mini_Store_Ready/
├── main.py
├── store.py
├── models/
│   ├── cart.py
│   ├── cartitem.py
│   ├── product.py
│   └── user.py
├── services/
│   └── user_manager.py
├── data/
│   └── products.json
└── tests/
    └── test_project.py
```

The local `data/users.json` file is created automatically and is intentionally excluded from Git because it can contain personal data and plaintext passwords. Product sample data is included in `data/products.json`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

Tests use temporary data files and do not modify your local store records.

## Limitations

This project is a learning exercise, not production commerce software. It does not implement secure password hashing, payment processing, concurrent inventory locking, or a web interface.
