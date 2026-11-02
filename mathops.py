"""Synthetic Lot B fixture. Intentionally faulty implementation (expected RED CI)."""


def safe_add(a: int, b: int) -> int:
    """Intentionally accepts bool and neglects numerical bounds."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("operands must be integers")
    return a + b
