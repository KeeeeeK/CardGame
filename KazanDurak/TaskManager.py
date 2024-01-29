from typing import Callable
from functools import wraps, reduce


class TaskManager:
    def __init__(self):
        self.subs: dict[Callable, list[Callable]] = dict()

    def subscribe(self, trigger: Callable, subscriber: Callable) -> None:
        if trigger not in self.subs.keys():
            self.subs[trigger] = []
        self.subs[trigger].append(subscriber)

    def unsubscribe(self, trigger: Callable, subscriber: Callable) -> None:
        self.subs[trigger].remove(subscriber)
        if self.subs[trigger] == []:
            self.subs.pop(trigger)

    def __call__(self, func: Callable) -> Callable:
        decorated_func = func
        if func in self.subs.keys():
            decorated_func = self._massive_decoration(self.subs[func])(func)
        return wraps(func)(decorated_func)

    @classmethod
    def _massive_decoration(cls, decorators):
        def compose(f, g):
            return lambda x: g(f(x))

        return reduce(compose, decorators, lambda x: x)
