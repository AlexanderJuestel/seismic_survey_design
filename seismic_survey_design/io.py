def _validate_string(arg: str | None, name: str) -> str | None:
    if arg is None:
        return None
    if arg is not None and not isinstance(arg, str):
        raise TypeError(f"'{name}' must be a string or None, got {type(arg).__name__}.")

    return arg


def _validate_float_int(
    arg: float | int | None,
    name: str,
    greater_than: float | int | None = None,
    smaller_than: float | int | None = None,
) -> float | int | None:
    if arg is None:
        return None
    if isinstance(arg, bool) or not isinstance(arg, (float, int)):
        raise TypeError(
            f"'{name}' must be a float, int or None, got {type(arg).__name__}."
        )

    if greater_than is not None and arg <= greater_than:
        raise ValueError(f"'{name}' must be greater than {greater_than}")

    if smaller_than is not None and arg >= smaller_than:
        raise ValueError(f"'{name}' must be smaller than {smaller_than}")

    return arg
