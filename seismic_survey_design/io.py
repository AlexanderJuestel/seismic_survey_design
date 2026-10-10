

def _validate_string(arg: str | None,
                     name: str) -> str | None:
    if arg is not None and not isinstance(arg, str):
        raise TypeError(f"'{name}' must be a string or None, "
                        f"got {type(arg).__name__}."
        )

    return arg