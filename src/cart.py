"""
cart.py  -  SEN 304 (fixed version)

Shopping-cart / checkout module for a Nigerian online store.
All bugs from buggy/cart_buggy.py have been fixed and exception handling
has been added for every runtime error found during debugging.

Business rules
--------------
* Discount tiers on the subtotal (in Naira):
      0       - 9,999.99   ->  0 %
      10,000  - 49,999.99  ->  5 %
      50,000  and above    -> 10 %
* Coupon "MIVA10" takes an extra N1,000 off (after the tier discount).
* VAT of 7.5 % is charged on the amount AFTER discounts.
"""

from __future__ import annotations

VAT_RATE = 0.075
TIER_1 = 10_000
TIER_2 = 50_000
COUPONS = {"MIVA10": 1_000}


# --------------------------------------------------------------------------
# Custom exceptions (added while fixing BUG-02 and BUG-03)
# --------------------------------------------------------------------------
class CartError(Exception):
    """Base class for all cart errors."""


class ItemNotFoundError(CartError):
    """Raised when removing an item that is not in the cart."""


class EmptyCartError(CartError):
    """Raised when checking out an empty cart."""


class InvalidCouponError(CartError):
    """Raised when an unknown coupon code is used."""


# --------------------------------------------------------------------------
# Cart operations
# --------------------------------------------------------------------------
def add_item(cart: dict, name: str, price: float, qty: int = 1) -> dict:
    """Add *qty* units of *name* at *price* to *cart* (fix for BUG-04)."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Item name must be a non-empty string")
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise TypeError("Price must be a number")
    if price < 0:
        raise ValueError("Price cannot be negative")
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise TypeError("Quantity must be a whole number")
    if qty < 1:
        raise ValueError("Quantity must be at least 1")

    if name in cart:
        cart[name]["qty"] += qty
    else:
        cart[name] = {"price": price, "qty": qty}
    return cart


def remove_item(cart: dict, name: str) -> dict:
    """Remove *name* from *cart* (fix for BUG-03)."""
    try:
        del cart[name]
    except KeyError:
        raise ItemNotFoundError(f"'{name}' is not in the cart") from None
    return cart


def subtotal(cart: dict) -> float:
    """Sum of price x qty for EVERY item (fix for BUG-06)."""
    total = 0
    for item in cart.values():
        total += item["price"] * item["qty"]
    return total


def discount_rate(amount: float) -> float:
    """Return the tier discount rate for *amount* (fixes BUG-01 and BUG-05)."""
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if amount >= TIER_2:
        return 0.10
    if amount >= TIER_1:
        return 0.05
    return 0.0


def average_item_price(cart: dict) -> float:
    """Average price per unit; 0.0 for an empty cart (fix for BUG-02)."""
    total_qty = sum(item["qty"] for item in cart.values())
    try:
        return round(subtotal(cart) / total_qty, 2)
    except ZeroDivisionError:
        return 0.0


def checkout(cart: dict, coupon: str | None = None) -> float:
    """Final amount payable: discount -> coupon -> VAT.

    The tier is chosen from the PRE-VAT subtotal (fix for BUG-07).
    """
    if not cart:
        raise EmptyCartError("Cannot checkout an empty cart")

    sub = subtotal(cart)
    after_discount = sub - sub * discount_rate(sub)

    if coupon is not None:
        if coupon not in COUPONS:
            raise InvalidCouponError(f"Unknown coupon '{coupon}'")
        after_discount = max(after_discount - COUPONS[coupon], 0)

    total = after_discount + after_discount * VAT_RATE
    return round(total, 2)


if __name__ == "__main__":
    cart: dict = {}
    add_item(cart, "Rice 50kg", 45000, 1)
    add_item(cart, "Palm Oil 5L", 5000, 2)
    print(f"Subtotal        : N{subtotal(cart):,.2f}")
    print(f"Average price   : N{average_item_price(cart):,.2f}")
    print(f"Average (empty) : N{average_item_price({}):,.2f}")
    try:
        remove_item(cart, "Beans")
    except ItemNotFoundError as err:
        print(f"Handled error   : {err}")
    print(f"Total payable   : N{checkout(cart):,.2f}")
    print(f"With MIVA10     : N{checkout(cart, 'MIVA10'):,.2f}")
