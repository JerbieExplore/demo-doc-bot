# app.py

FREE_SHIPPING_THRESHOLD = 40.0  # lowered from 50.0
VAT_RATE = 0.10

def calculate_discount(price: float, is_member: bool = False) -> float:
    if is_member:
        return price * 0.80   # 20% for members
    return price * 0.90       # 10% for others

def qualifies_free_shipping(cart_total: float) -> bool:
    return cart_total >= FREE_SHIPPING_THRESHOLD
