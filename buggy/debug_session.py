"""
debug_session.py - driver used in VS Code to hunt the bugs in cart_buggy.py.

Fix BUG-01 (the missing colon) first, otherwise nothing will run.
Then set the breakpoints listed below and press F5.

  Breakpoint A : cart_buggy.py, the 'for i in range(...)' line in subtotal()
                 Watch: len(items), i, total          -> reveals BUG-06
  Breakpoint B : cart_buggy.py, first line of discount_rate()
                 Watch: amount, amount > 10000         -> reveals BUG-05
  Breakpoint C : cart_buggy.py, 'total = with_vat - ...' line in checkout()
                 Watch: sub, with_vat, discount_rate(with_vat) -> BUG-07
  Breakpoint D : cart_buggy.py, return line of average_item_price()
                 Watch: total_qty                      -> reveals BUG-02
"""
import cart_buggy as c

cart = {}
c.add_item(cart, "Rice 50kg", 45000, 1)
c.add_item(cart, "Palm Oil 5L", 5000, 2)
c.add_item(cart, "Garri", 1500, 1)

print("Subtotal (expect 56,500):", c.subtotal(cart))                 # BUG-06
print("Rate at 10,000 (expect 0.05):", c.discount_rate(10000))       # BUG-05
print("N47,000 checkout (expect 47,998.75):",
      c.checkout({"Bag": {"price": 47000, "qty": 1}}))               # BUG-07

for label, action in [
    ("average of empty cart", lambda: c.average_item_price({})),        # BUG-02
    ("remove missing item", lambda: c.remove_item(cart, "Beans")),       # BUG-03
    ("string quantity", lambda: c.subtotal(
        c.add_item(c.add_item({}, "Oil", 5000, "2"), "Yam", 100, 1))),  # BUG-04
]:
    try:
        action()
    except Exception as err:          # shows each runtime error without stopping
        print(f"{label}: {type(err).__name__}: {err}")
