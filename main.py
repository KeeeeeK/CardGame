from abc import ABC, abstractmethod
from queue import SimpleQueue


def arg_plus_1(func):
    def real_behaviour(arg):
        return func(arg+1)
    return real_behaviour

@arg_plus_1
def print_a(a):
    print(a)

class MyException(Exception):
    pass

def bad_func():
    raise Exception('asdasd')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    match 1, 2:
        case 1, 2:
            print(1)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
