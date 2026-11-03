class StripeClient:
    def charge(self, cents: int, token: str) -> str:
        ...

def checkout(order, token):
    client = StripeClient()
    charge_id = client.charge(order.total_cents, token)
    order.mark_paid(charge_id)
    return charge_id
