# Lot B — synthetic safe integer addition contract

This fixture is intentionally non-sensitive. Do not use production code, credentials, accounts, API keys or customer data.

Implement `mathops.safe_add(a, b)` according to the following requirements:
- Accept **exact built-in ints only**, rejecting `bool`, float, Decimal, strings and objects with `TypeError`.
- Accept only `0 <= a <= 10000` and `0 <= b <= 10000`; reject out-of-domain operands with `ValueError`.
- Reject sums greater than `10000` with `ValueError`; never clamp or silently truncate.
- Return exactly a built-in `int`.
- Do not read environment variables, network, filesystem, user secrets or external processes.
- Use Python standard library only.
- Modify `mathops.py` ONLY; acceptance tests, workflow and specification are immutable to the agent.
- Initial baseline deliberately violates this spec. The first red CI is **expected**.

Examples:
- safe_add(3, 4) == 7
- safe_add(0, 0) == 0
- safe_add(10000, 0) == 10000
- safe_add(True, 1) -> TypeError
- safe_add(-1, 1) -> ValueError
- safe_add(8000, 3000) -> ValueError
