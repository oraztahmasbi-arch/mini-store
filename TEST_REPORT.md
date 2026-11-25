# Mini Store test report

The project was checked with Python compilation, automated unit tests, and a command-line smoke test.

Automated tests cover product validation, product JSON persistence, category filtering, duplicate products, stock updates, cart reservation/release, quantity changes, checkout persistence, user registration/login, duplicate usernames, password changes, and saved purchase history.

Run the test suite yourself with:

```bash
py -m unittest discover -s tests -v
```

A successful run should report all tests as `OK`.
