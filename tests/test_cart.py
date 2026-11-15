"""
test_cart.py  -  SEN 304 Part B: Unit testing with PyTest

Sections
  1. Black-box : Equivalence Partitioning (EP)
  2. Black-box : Boundary Value Analysis (BVA)
  3. White-box : Statement coverage
  4. White-box : Branch coverage
  5. White-box : Path coverage (checkout)
  6. Error handling and edge cases
"""

import pytest

from src.cart import (
    EmptyCartError,
    InvalidCouponError,
    ItemNotFoundError,
    add_item,
    average_item_price,
    checkout,
    discount_rate,
    remove_item,
    subtotal,
)


@pytest.fixture
def cart():
    """A cart with two items: subtotal = 45,000 + 2 x 5,000 = 55,000."""
    c = {}
    add_item(c, "Rice 50kg", 45000, 1)
    add_item(c, "Palm Oil 5L", 5000, 2)
    return c


# ==========================================================================
# 1. EQUIVALENCE PARTITIONING
#    discount_rate partitions: invalid (<0) | 0% | 5% | 10%
#    quantity partitions     : invalid (<1) | valid (>=1) | wrong type
# ==========================================================================
@pytest.mark.parametrize(
    "amount, expected",
    [
        (5_000, 0.0),    # partition: 0 - 9,999.99
        (25_000, 0.05),  # partition: 10,000 - 49,999.99
        (80_000, 0.10),  # partition: 50,000 and above
    ],
)
def test_ep_discount_valid_partitions(amount, expected):
    assert discount_rate(amount) == expected


def test_ep_discount_invalid_partition():
    with pytest.raises(ValueError):
        discount_rate(-500)


def test_ep_quantity_valid_partition():
    c = add_item({}, "Garri", 1500, 3)
    assert c["Garri"]["qty"] == 3


@pytest.mark.parametrize("qty", [0, -2])
def test_ep_quantity_invalid_partition(qty):
    with pytest.raises(ValueError):
        add_item({}, "Garri", 1500, qty)


@pytest.mark.parametrize("qty", ["2", 2.5, True])
def test_ep_quantity_wrong_type_partition(qty):
    with pytest.raises(TypeError):
        add_item({}, "Garri", 1500, qty)


# ==========================================================================
# 2. BOUNDARY VALUE ANALYSIS
#    Boundaries at 0, 10,000 and 50,000 (just below / on / just above)
# ==========================================================================
@pytest.mark.parametrize(
    "amount, expected",
    [
        (0, 0.0),
        (0.01, 0.0),
        (9_999.99, 0.0),
        (10_000, 0.05),     # would FAIL on the buggy version (BUG-05)
        (10_000.01, 0.05),
        (49_999.99, 0.05),
        (50_000, 0.10),     # would FAIL on the buggy version (BUG-05)
        (50_000.01, 0.10),
    ],
)
def test_bva_discount_boundaries(amount, expected):
    assert discount_rate(amount) == expected


def test_bva_just_below_zero():
    with pytest.raises(ValueError):
        discount_rate(-0.01)


@pytest.mark.parametrize("qty, ok", [(0, False), (1, True), (2, True)])
def test_bva_quantity_lower_boundary(qty, ok):
    if ok:
        assert add_item({}, "Yam", 2000, qty)["Yam"]["qty"] == qty
    else:
        with pytest.raises(ValueError):
            add_item({}, "Yam", 2000, qty)


@pytest.mark.parametrize("price, ok", [(-0.01, False), (0, True), (0.01, True)])
def test_bva_price_lower_boundary(price, ok):
    if ok:
        assert add_item({}, "Free sample", price)["Free sample"]["price"] == price
    else:
        with pytest.raises(ValueError):
            add_item({}, "Free sample", price)


# ==========================================================================
# 3. STATEMENT COVERAGE - every line of every function executes at least once
# ==========================================================================
def test_stmt_subtotal_counts_every_item(cart):
    # BUG-06 regression: the last item must be included
    assert subtotal(cart) == 55_000


def test_stmt_average_item_price(cart):
    assert average_item_price(cart) == round(55_000 / 3, 2)


def test_stmt_remove_item(cart):
    remove_item(cart, "Palm Oil 5L")
    assert "Palm Oil 5L" not in cart


def test_stmt_add_existing_item_increments_qty(cart):
    add_item(cart, "Rice 50kg", 45000, 2)
    assert cart["Rice 50kg"]["qty"] == 3


# ==========================================================================
# 4. BRANCH COVERAGE - every decision evaluated both True and False
# ==========================================================================
@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_branch_add_item_bad_name(name):
    with pytest.raises(ValueError):
        add_item({}, name, 100)


@pytest.mark.parametrize("price", ["100", None, False])
def test_branch_add_item_bad_price_type(price):
    with pytest.raises(TypeError):
        add_item({}, "Bread", price)


def test_branch_average_true_and_false(cart):
    assert average_item_price({}) == 0.0          # except branch
    assert average_item_price(cart) > 0           # try branch


def test_branch_coupon_reduces_to_zero_not_negative():
    c = add_item({}, "Sweet", 500)
    # 500 - 1,000 coupon would be negative -> clamped to 0
    assert checkout(c, "MIVA10") == 0.0


# ==========================================================================
# 5. PATH COVERAGE - checkout() has 4 independent paths
#    P1 empty cart -> EmptyCartError
#    P2 no coupon
#    P3 valid coupon
#    P4 invalid coupon -> InvalidCouponError
# ==========================================================================
def test_path1_empty_cart():
    with pytest.raises(EmptyCartError):
        checkout({})


def test_path2_no_coupon(cart):
    # 55,000 -> 10% off = 49,500 -> +7.5% VAT = 53,212.50
    assert checkout(cart) == 53_212.50


def test_path3_valid_coupon(cart):
    # 49,500 - 1,000 = 48,500 -> +7.5% VAT = 52,137.50
    assert checkout(cart, "MIVA10") == 52_137.50


def test_path4_invalid_coupon(cart):
    with pytest.raises(InvalidCouponError):
        checkout(cart, "FREE100")


# ==========================================================================
# 6. ERROR HANDLING & EDGE CASES
# ==========================================================================
def test_remove_missing_item_raises_custom_error(cart):
    with pytest.raises(ItemNotFoundError, match="Beans"):
        remove_item(cart, "Beans")


def test_tier_chosen_from_pre_vat_subtotal():
    # BUG-07 regression: N47,000 is in the 5% tier even though it is
    # N50,525 once VAT is added. 47,000 x 0.95 x 1.075 = 47,998.75
    # (the buggy version returned 45,472.50 by applying the 10% tier)
    c = add_item({}, "Laptop bag", 47_000)
    assert checkout(c) == 47_998.75


def test_large_order():
    c = add_item({}, "Generator", 1_000_000, 3)
    assert checkout(c) == round(3_000_000 * 0.9 * 1.075, 2)
