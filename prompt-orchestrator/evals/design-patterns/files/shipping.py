def shipping_cost(order):
    if order.method == "standard":
        return 500 if order.weight_kg < 5 else 900
    elif order.method == "express":
        return 1500 + 200 * order.weight_kg
    elif order.method == "pickup":
        return 0
    raise ValueError(f"unknown method {order.method}")

def shipping_label(order):
    if order.method == "standard":
        return "STD"
    elif order.method == "express":
        return "EXP"
    elif order.method == "pickup":
        return "PCK"
    raise ValueError(f"unknown method {order.method}")
