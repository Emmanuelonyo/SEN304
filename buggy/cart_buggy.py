"""
cart_buggy.py  -  SEN 304 Debugging Exercise (INTENTIONALLY BUGGY)

A small shopping-cart / checkout module for a Nigerian online store.
This file contains DELIBERATE bugs for the debugging exercise:

    BUG-01  Syntax error   : missing colon in a function definition
    BUG-02  Runtime error  : ZeroDivisionError when the cart is empty
    BUG-03  Runtime error  : KeyError when removing an item that is not in the cart
    BUG-04  Runtime error  : TypeError when quantity is passed as a string ("2")
    BUG-05  Logical error  : discount boundary uses '>' instead of '>='
    BUG-06  Logical error  : subtotal loop skips the last item (off-by-one)
    BUG-07  Logical error  : discount tier is chosen from the VAT-inclusive amount

Do NOT use this file in production - see src/cart.py for the fixed version.
"""

VAT_RATE = 0.075  # Nigerian VAT, 7.5%


def add_item(cart, name, price, qty=1):
    # BUG-04: no validation; qty "2" (a string) breaks arithmetic later
    if name in cart:
        cart[name]["qty"] += qty
    else:
        cart[name] = {"price": price, "qty": qty}
    return cart


def remove_item(cart, name):
    # BUG-03: raises a raw KeyError if the item does not exist
    del cart[name]
    return cart


def subtotal(cart):
    items = list(cart.values())
    total = 0
    # BUG-06: range(len(items) - 1) skips the last item
    for item in items:
        total += item["price"] * item["qty"]
    return total


def discount_rate(amount):          # BUG-01: missing colon -> SyntaxError
    # BUG-05: '>' should be '>=' so that exactly 10,000 / 50,000 qualify%%%%%%%
    if amount > 50000:
        return 0.10
    elif amount > 10000:
        return 0.05
    return 0.0


def average_item_price(cart):
    total_qty = sum(item["qty"] for item in cart.values())
    # BUG-02: ZeroDivisionError when the cart is empty
    return subtotal(cart) / total_qty


def checkout(cart):
    sub = subtotal(cart)
    with_vat = sub + sub * VAT_RATE
    # BUG-07: tier is chosen from the VAT-inclusive amount, so a N47,000
    # order (N50,525 with VAT) wrongly gets the 10% tier instead of 5%
    total = with_vat - with_vat * discount_rate(with_vat)
    return round(total, 2)


if __name__ == "__main__":
    cart = {}
    add_item(cart, "Rice 50kg", 45000, 1)
    add_item(cart, "Palm Oil 5L", 5000, "2")   # triggers BUG-04
    print("Subtotal:", subtotal(cart))
    print("Average price:", average_item_price({}))  # triggers BUG-02
    remove_item(cart, "Beans")                         # triggers BUG-03
    print("Total:", checkout(cart))
