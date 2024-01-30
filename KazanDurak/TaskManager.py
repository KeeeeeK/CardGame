from typing import Callable, Any
from functools import wraps, reduce


QualName = str
Decorator = Callable[[Callable], Callable]



class TaskManager:
    def __init__(self):
        self.subs: dict[QualName, list[Decorator]] = dict()

    def sub(self, trigger: Callable) -> Decorator:
        def decorator(subscriber: Decorator) -> Decorator:
            if trigger.__qualname__ not in self.subs.keys():
                self.subs[trigger.__qualname__] = []
            self.subs[trigger.__qualname__].append(subscriber)
            return subscriber

        return decorator

    def unsub(self, trigger: Callable, subscriber: Decorator) -> None:
        self.subs[trigger.__qualname__].remove(subscriber)
        if self.subs[trigger.__qualname__] == []:
            self.subs.pop(trigger.__qualname__)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def dynamically_decorated_func(*args, **kwargs):
            if func.__qualname__ not in self.subs.keys():
                return func(*args, **kwargs)
            decorated_func = self._massive_decoration(self.subs[func.__qualname__])(func)
            return decorated_func(*args, **kwargs)

        return dynamically_decorated_func

    @staticmethod
    def _massive_decoration(decorators):
        def compose(f, g):
            return lambda x: g(f(x))

        return reduce(compose, decorators, lambda x: x)


task_manager: TaskManager = TaskManager()
