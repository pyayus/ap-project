from datetime import datetime, timezone
from typing import Any, Callable, Iterable, TypeVar, List

T = TypeVar("T")


def retain(function: Callable[[T], Any], list_input: List[T]):
    i = 0
    for elem in list_input:
        if function(elem):
            list_input[i] = elem
            i += 1
    del list_input[i:]


def find_first(function: Callable[[T], Any], iterable: Iterable[T]) -> T | None:
    return next(filter(function, iterable), None)


def take_n(n: int, iterable: Iterable[T]) -> Iterable[T]:
    return map(lambda e: e[1], filter(lambda e: e[0] < n, enumerate(iterable)))


def timestamp_to_str(t):
    datetime.fromtimestamp(t).astimezone(timezone.utc).strftime(
        "%A, %B %d, %Y %H:%M:%S UTC"
    )
