# app.py

FREE_SHIPPING_THRESHOLD = 50.0  # EUR
VAT_RATE = 0.10                  # 10% VAT

def calculate_discount(price: float) -> float:
    """
    Business rule: Everyone gets 10% discount.
    """
    return price * 0.90

def qualifies_free_shipping(cart_total: float) -> bool:
    """
    Business rule: Free shipping for orders >= FREE_SHIPPING_THRESHOLD.
    """
    return cart_total >= FREE_SHIPPING_THRESHOLD
