from typing import Any


def add_docs(docs: Any) -> Any:
    def wrapper(f: Any) -> Any:
        f.__doc__ = docs
        return f

    return wrapper
