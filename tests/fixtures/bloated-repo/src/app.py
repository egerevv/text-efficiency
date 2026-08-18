count = 0


def increment():
    # increment count by one
    global count
    count += 1


def charge(order):
    # Never retry this call: the payment vendor rate-limits retries and
    # will lock the merchant account after three rapid attempts.
    return _send(order)


def _send(order):
    return {"ok": True, "order": order}
