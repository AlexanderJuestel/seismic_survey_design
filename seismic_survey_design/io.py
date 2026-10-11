
def _validate_string(
    arg: str | None,
    name: str,
) -> str | None:
    """Validate that an argument is a string or None."""
    if arg is None:
        return None

    if not isinstance(arg, str):
        raise TypeError(
            f"'{name}' must be a string or None, "
            f"got {type(arg).__name__}."
        )

    return arg


def _validate_float_int(
    arg: float | int | None,
    name: str,
    greater_than: float | int | None = None,
    smaller_than: float | int | None = None,
) -> float | int | None:
    """
    Validate a numeric argument and optional strict bounds.

    Args:
        arg: Numeric value to validate, or None.
        name: Parameter name used in error messages.
        greater_than: Optional exclusive lower bound.
        smaller_than: Optional exclusive upper bound.

    Returns:
        The original numeric value, or None.

    Raises:
        TypeError: If the value is not an int, float, or None,
            or if it is a boolean.
        ValueError: If the value violates either bound.
    """
    if arg is None:
        return None

    # bool is a subclass of int, so it must be rejected explicitly.
    if isinstance(arg, bool) or not isinstance(arg, (int, float)):
        raise TypeError(
            f"'{name}' must be a float, int or None, "
            f"got {type(arg).__name__}."
        )

    if greater_than is not None and arg <= greater_than:
        raise ValueError(
            f"'{name}' must be greater than {greater_than}"
        )

    if smaller_than is not None and arg >= smaller_than:
        raise ValueError(
            f"'{name}' must be smaller than {smaller_than}"
        )

    return arg
