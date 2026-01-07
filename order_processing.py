from typing import Optional


class Coupon:
    SAVE10 = "SAVE10"
    SAVE20 = "SAVE20"
    VIP = "VIP"

class Discount:
    SAVE10 = 0.10
    SAVE20 = 0.20
    SAVE20_MIN = 0.05
    SAVE20_THRESHOLD = 200
    VIP = 50
    VIP_MIN = 10
    VIP_THRESHOLD = 100


class Tax:
    RATE = 0.21


ORDER_SUFFIX = "X"


def parse_request(request: dict) -> tuple:
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def validate_request_data_for_none(user_id: int, items: list):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")


def validate_items_list(items: list):
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for it in items:
        if "price" not in it or "qty"not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items: list) -> int:
    return sum(it["price"] * it["qty"] for it in items)


def calculate_discount(coupon: Optional[str], subtotal: int) -> int:
    match coupon:
        case None:
            return 0
        case Coupon.SAVE10:
            return int(subtotal * Discount.SAVE10)
        case Coupon.SAVE20:
            return int(subtotal * Discount.SAVE20 if subtotal >= Discount.SAVE20_THRESHOLD
                       else subtotal * Discount.SAVE20_MIN)
        case Coupon.VIP:
            return int(Discount.VIP_MIN if subtotal < Discount.VIP_THRESHOLD else Discount.VIP)
        case _:
            raise ValueError("unknown coupon")


def calculate_tax(total_after_discount: int) -> int:
    return int(total_after_discount * Tax.RATE)


def generate_order_id(user_id: int, items_count: int):
    return f"{str(user_id)}-{str(items_count)}-{ORDER_SUFFIX}"


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    validate_request_data_for_none(user_id, items)
    validate_items_list(items)

    currency = currency or "USD"
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    total_after_discount = subtotal - discount

    tax = calculate_tax(total_after_discount)

    total = total_after_discount + tax

    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }