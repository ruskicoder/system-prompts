def process(data, send_email=True):
    # loop over items
    total = 0
    for i in data["items"]:
        total += i["price"] * i["qty"]
    if data["country"] == "DE":
        total = total * 1.19
    try:
        db.save({"customer": data["customer"], "total": total})
    except Exception:
        pass
    if send_email:
        smtp.send(data["email"], f"Your total is {total}")
    return total
