from typing_extensions import Final
from re import Pattern

from js_regex import compile


RE: Final[str] = (
    r'/^[a-z][a-z0-9]*'
    r'(?:_[a-z][a-z0-9]*)*'
    r'(?:\.[a-z][a-z0-9]*(?:_[a-z][a-z0-9]*)*)*$/'
)


RE_C: Final[Pattern] = compile(RE)


def is_valid_name(name: str) -> bool:
    match = RE_C.match(name)

    return bool(match)


def ensure_tag_name(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError(
            f"Invalid trace span tag: Expected string, received {name}"
        )

    if is_valid_name(name):
        return name

    raise ValueError(
        "Invalid captured event name: Name should contain dot separated tokens that follow "
        f'"[a-z][a-z0-9]*" pattern. Received: {name}'
    )