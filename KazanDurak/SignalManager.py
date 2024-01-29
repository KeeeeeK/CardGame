from typing import Callable, Any
from functools import wraps


class SignalManager:
    """
    Данный класс реализует паттерн издатель-подписчик посредством сигналов.
    Издатели испускают множество сигналов, подписчики подписываются на множество сигналов.
    Срабатывание эквивалентно верификации цепочки ```издатель -> сигнал -> подписчик```
    ---
    Это не очень безопасный класс. Кто угодно может подписываться на любые сигналы и публиковать любые сигналы.
    ---
    Сигналы являются простыми строчками.
    """

    def __init__(self):
        self.signals_by_pub: dict[Callable, list[str]] = {}
        self.subs_by_signal: dict[str, list[Callable]] = {}

    def pub(self, *pub_signals):
        def decorator(func):
            self._update_dict_with_list(self.signals_by_pub, func, pub_signals)

            @wraps(func)
            def real_func(*args, **kwargs):
                # TODO: у сигналов должна быть возможность останавливать ход исполнения управляющей функции
                # TODO: у сигналов подписчиков должна быть возможность сыграться до, после и во время действия издателя
                # Пока что сигналы не останавливают действий, а все дополнительные действия играются "во время"
                for signal in self.signals_by_pub[func]:
                    for sub in self.subs_by_signal[signal]:
                        sub(*args, **kwargs)
                return func(*args, **kwargs)

            return real_func

        return decorator

    def sub(self, *sub_signals):
        def decorator(func):
            for signal in sub_signals:
                self._update_dict_with_list(self.subs_by_signal, signal, [func])
            return func

        return decorator

    @staticmethod
    def _update_dict_with_list(dict_: dict[Any, list], key: Any, values: list | tuple):
        if key in dict_.keys():
            dict_[key] += list(values)
        else:
            dict_[key] = list(values)


signal_manager: SignalManager = SignalManager()
