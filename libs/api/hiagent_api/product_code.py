"""Product code validation and Header helpers."""

PRODUCT_CODE_HEADER = "X-Trace-Product-Code"


def normalize_product_code(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("product_code must not contain HTTP control characters")
    return value


def has_header(headers, name):
    return any(key.lower() == name.lower() for key in headers)
