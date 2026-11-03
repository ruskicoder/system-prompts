import time
from unittest.mock import MagicMock

def test_cart():
    repo = MagicMock()
    repo.get.return_value = MagicMock(items=[MagicMock(price=10, qty=2)])
    pricing = MagicMock()
    pricing.total.return_value = 20
    cart = CartService(repo, pricing)
    cart.checkout("c1")
    time.sleep(2)
    repo.get.assert_called_once_with("c1")
    pricing.total.assert_called_once()

def test_discount():
    try:
        apply_discount(-5)
    except Exception:
        pass
