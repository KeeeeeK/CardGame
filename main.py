from abc import ABC, abstractmethod
from queue import SimpleQueue


def arg_plus_1(func):
    def real_behaviour(arg):
        return func(arg+1)
    return real_behaviour

@arg_plus_1
def print_a(a):
    print(a)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_a(1)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
